import warnings
from sklearn import preprocessing
from sklearn.utils import shuffle
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold

warnings.filterwarnings('ignore')
dataset = pd.read_csv(r'PCA.csv')

BATCH_START = 0  # 建立 batch data 时候的 index
TIME_STEPS = 10  # backpropagation through time 的 time_steps
BATCH_SIZE = 10
INPUT_SIZE = 9  # sin 数据输入 size
OUTPUT_SIZE = 1  # cos 数据输出 size
CELL_SIZE = 10  # RNN 的 hidden unit size
LR = 0.006  # learning rate


class LSTMRNN(object):
    def __init__(self, n_steps, input_size, output_size, cell_size, batch_size):
        '''
        :param n_steps: 每批数据总包含多少时间刻度
        :param input_size: 输入数据的维度
        :param output_size: 输出数据的维度
        :param cell_size: cell的大小
        :param batch_size: 每批次训练数据的数量
        '''
        self.n_steps = n_steps
        self.input_size = input_size
        self.output_size = output_size
        self.cell_size = cell_size
        self.batch_size = batch_size
        with tf.name_scope('inputs'):
            self.xs = tf.placeholder(tf.float32, [None, n_steps, input_size], name='xs')  # xs 有三个维度
            self.ys = tf.placeholder(tf.float32, [None, n_steps, output_size], name='ys')  # ys 有三个维度
        with tf.variable_scope('in_hidden'):
            self.add_input_layer()
        with tf.variable_scope('LSTM_cell'):
            self.add_cell()
        with tf.variable_scope('out_hidden'):
            self.add_output_layer()
        with tf.name_scope('cost'):
            self.compute_cost()
        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(LR).minimize(self.cost)
        with tf.name_scope('std'):
            self.standard_var()

    # 增加一个输入层
    def add_input_layer(self, ):
        l_in_x = tf.reshape(self.xs, [-1, self.input_size], name='2_2D')  # -1 表示任意行数
        Ws_in = self._weight_variable([self.input_size, self.cell_size])
        bs_in = self._bias_variable([self.cell_size, ])
        with tf.name_scope('Wx_plus_b'):
            l_in_y = tf.matmul(l_in_x, Ws_in) + bs_in
        self.l_in_y = tf.reshape(l_in_y, [-1, self.n_steps, self.cell_size], name='2_3D')

    # 多时刻的状态叠加层
    def add_cell(self):
        # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True)
        # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True,
        #                                                  activation=tf.nn.relu)
        # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True,
        #                                          activation=tf.nn.softsign)
        # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True,
        #                                          activation=tf.nn.softplus)
        # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True,
        #                                          activation=tf.nn.sigmoid)
        lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True,
                                                 activation=tf.nn.elu)
        with tf.name_scope('initial_state'):
            self.cell_init_state = lstm_cell.zero_state(self.batch_size, dtype=tf.float32)
        # time_major=False 表示时间主线不是第一列batch
        self.cell_outputs, self.cell_final_state = tf.nn.dynamic_rnn(
            lstm_cell, self.l_in_y, initial_state=self.cell_init_state, time_major=False)

    # 增加一个输出层
    def add_output_layer(self):
        l_out_x = tf.reshape(self.cell_outputs, [-1, self.cell_size], name='2_2D')
        Ws_out = self._weight_variable([self.cell_size, self.output_size])
        bs_out = self._bias_variable([self.output_size, ])
        with tf.name_scope('Wx_plus_b'):
            self.pred = tf.matmul(l_out_x, Ws_out) + bs_out  # 预测结果

    def compute_cost(self):
        losses = tf.nn.seq2seq.sequence_loss_by_example(
            [tf.reshape(self.pred, [-1], name='reshape_pred')],
            [tf.reshape(self.ys, [-1], name='reshape_target')],
            [tf.ones([self.batch_size * self.n_steps], dtype=tf.float32)],
            average_across_timesteps=True,
            softmax_loss_function=self.ms_error_square,
            name='losses'
        )
        with tf.name_scope('average_cost'):
            self.cost = pow(tf.div(
                tf.reduce_sum(losses, name='losses_sum'),
                self.batch_size,
                name='average_cost'), 0.5)
            tf.scalar_summary('cost', self.cost)

    def ms_error(self, y_pre, y_target):
        return tf.sub(y_pre, y_target)

    def ms_error_square(self, y_pre, y_target):
        return tf.square(tf.sub(y_pre, y_target))

    def _weight_variable(self, shape, name='weights'):
        initializer = tf.random_normal_initializer(mean=0., stddev=1., )
        return tf.get_variable(shape=shape, initializer=initializer, name=name)

    def _bias_variable(self, shape, name='biases'):
        initializer = tf.constant_initializer(0.1)
        return tf.get_variable(name=name, shape=shape, initializer=initializer)

    def standard_var(self):
        losses = tf.nn.seq2seq.sequence_loss_by_example(
            [tf.reshape(self.pred, [-1], name='reshape_pred')],
            [tf.reshape(self.ys, [-1], name='reshape_target')],
            [tf.ones([self.batch_size * self.n_steps], dtype=tf.float32)],
            average_across_timesteps=True,
            softmax_loss_function=self.ms_error,
            name='losses'
        )
        with tf.name_scope('standard_var'):
            self.std = pow(tf.div(
                tf.reduce_sum(tf.square(tf.sub(losses, tf.reduce_mean(losses))), name='deviation_sum'),
                self.batch_size,
                name='var'
            ), 0.5)
            tf.scalar_summary('std', self.std)


if __name__ == '__main__':
    model = LSTMRNN(TIME_STEPS, INPUT_SIZE, OUTPUT_SIZE, CELL_SIZE, BATCH_SIZE)
    x = dataset.as_matrix(
        ['organization', 'attack', 'goalkeeping', 'key_pass', 'defence', 'defending_skills', 'wing_back',
         'central_back', 'discipline'])
    y = dataset.as_matrix(['Rating'])
    train_x, test_x, train_y, test_y = train_test_split(x, y, train_size=0.8, random_state=33)

    np.random.seed(1)
    train_x = pd.DataFrame(train_x)
    train_y = pd.DataFrame(train_y)
    train_rmse = [0 for i in range(5)]
    test_rmse = [0 for i in range(5)]
    train_std_list = [0 for i in range(5)]
    test_std_list = [0 for i in range(5)]
    idx = 0
    kf = KFold(n_splits=5, shuffle=True)
    for train_index, test_index in kf.split(train_x):
        train_x_2, test_x_2 = train_x.iloc[train_index], train_x.iloc[test_index]
        train_y_2, test_y_2 = train_y.iloc[train_index], train_y.iloc[test_index]
        mm_x = preprocessing.MinMaxScaler()
        train_x_2 = mm_x.fit_transform(train_x_2)
        test_x_2 = mm_x.fit_transform(test_x_2)
        mm_y = preprocessing.MinMaxScaler()
        train_y_2 = mm_y.fit_transform(train_y_2.values.reshape(-1, 1))
        test_y_2 = mm_y.fit_transform(test_y_2.values.reshape(-1, 1))

        sess = tf.Session()
        sess.run(tf.global_variables_initializer())

        for j in range(100):  # 训练100次
            pred_res = None
            for i in range(125):  # 把整个训练数据集分为202个时间段
                # 数据归一化
                x_part1 = train_x_2[BATCH_START: BATCH_START + TIME_STEPS * BATCH_SIZE]
                y_part1 = train_y_2[BATCH_START: BATCH_START + TIME_STEPS * BATCH_SIZE]
                print('时间段=', BATCH_START, BATCH_START + TIME_STEPS * BATCH_SIZE)
                seq = x_part1.reshape((BATCH_SIZE, TIME_STEPS, INPUT_SIZE))
                res = y_part1.reshape((BATCH_SIZE, TIME_STEPS, 1))
                BATCH_START += TIME_STEPS
                if i == 0:
                    feed_dict = {
                        model.xs: seq,
                        model.ys: res,
                        # create initial state
                    }
                else:
                    feed_dict = {
                        model.xs: seq,
                        model.ys: res,
                        model.cell_init_state: state  # use last state as the initial state for this run
                    }
                _, cost, std, state, pred = sess.run(
                    [model.train_op, model.cost, model.std, model.cell_final_state, model.pred],
                    feed_dict=feed_dict)
            pred_res = pred
            final_state = sess.run(model.cell_final_state, feed_dict)
            train_rmse[idx] = cost
            train_std_list[idx] = std
            print('第{0}次建模集{1}  RMSE: '.format(j+1, idx+1), round(cost, 8))
            print('第{0}次建模集{1}  std: '.format(j+1, idx+1), round(std, 8))
            BATCH_START = 0

        x_part2 = test_x_2[BATCH_START: BATCH_START + TIME_STEPS * BATCH_SIZE]
        y_part2 = test_y_2[BATCH_START: BATCH_START + TIME_STEPS * BATCH_SIZE]
        print('时间段=', BATCH_START, BATCH_START + TIME_STEPS * BATCH_SIZE)
        seq_2 = x_part2.reshape((BATCH_SIZE, TIME_STEPS, INPUT_SIZE))
        res_2 = y_part2.reshape((BATCH_SIZE, TIME_STEPS, 1))
        BATCH_START += TIME_STEPS

        feed_dict = {
            model.xs: seq_2,
            model.ys: res_2,
            model.cell_init_state: final_state
        }
        test_cost, test_std = sess.run([model.cost, model.std], feed_dict=feed_dict)
        test_rmse[idx] = test_cost
        test_std_list[idx] = test_std
        idx += 1
        BATCH_START = 0
    print(np.mean(train_rmse), np.mean(test_rmse), np.mean(train_std_list), np.mean(test_std_list))
