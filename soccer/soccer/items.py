# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SoccerDataItem(scrapy.Item):
    # 球员个人信息
    # name = scrapy.Field()  # 球员名字
    # position = scrapy.Field()  # 场上位置
    # team_stand = scrapy.Field()  # 主客场标识

    # 球队比赛数据
    home_team = scrapy.Field()  # 主队队名
    away_team = scrapy.Field()  # 客队队名
    home_team_id = scrapy.Field()  # 主队ID
    away_team_id = scrapy.Field()  # 客队ID
    home_team_score = scrapy.Field()  # 主队进球数
    away_team_score = scrapy.Field()  # 客队进球数
    season = scrapy.Field()  # 赛季
    round = scrapy.Field()  # 轮次
    url = scrapy.Field()  # 比赛链接

    # 球员列表
    # home_player1 = scrapy.Field()
    # home_player2 = scrapy.Field()
    # home_player3 = scrapy.Field()
    # home_player4 = scrapy.Field()
    # home_player5 = scrapy.Field()
    # home_player6 = scrapy.Field()
    # home_player7 = scrapy.Field()
    # home_player8 = scrapy.Field()
    # home_player9 = scrapy.Field()
    # home_player10 = scrapy.Field()
    # home_player11 = scrapy.Field()
    # home_player12 = scrapy.Field()
    # home_player13 = scrapy.Field()
    # home_player14 = scrapy.Field()
    # home_player15 = scrapy.Field()
    # home_player16 = scrapy.Field()
    # home_player17 = scrapy.Field()
    # home_player18 = scrapy.Field()
    # away_player1 = scrapy.Field()
    # away_player2 = scrapy.Field()
    # away_player3 = scrapy.Field()
    # away_player4 = scrapy.Field()
    # away_player5 = scrapy.Field()
    # away_player6 = scrapy.Field()
    # away_player7 = scrapy.Field()
    # away_player8 = scrapy.Field()
    # away_player9 = scrapy.Field()
    # away_player10 = scrapy.Field()
    # away_player11 = scrapy.Field()
    # away_player12 = scrapy.Field()
    # away_player13 = scrapy.Field()
    # away_player14 = scrapy.Field()
    # away_player15 = scrapy.Field()
    # away_player16 = scrapy.Field()
    # away_player17 = scrapy.Field()
    # away_player18 = scrapy.Field()

    home_players = scrapy.Field()
    away_players = scrapy.Field()
    # players = scrapy.Field()
    pass
