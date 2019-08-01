# -*- coding: utf-8 -*-
import json
from soccer_data.items import SoccerDataItem
import scrapy
import re
from pandas import *


class ChampdasSpider(scrapy.Spider):
    name = 'champdas_3'

    def start_requests(self):
        url_base = 'http://data.champdas.com/match/scheduleDetail-1-{year}-{round}.html'
        for year in [2014, 2015, 2016, 2017, 2018]:
            for match_round in range(1, 31):
                url = url_base.format(year=year, round=match_round)
                yield scrapy.Request(
                    url=url,
                    meta={
                        'year': year,
                        'match_round': match_round
                    },
                    callback=self.parse_schedule_page)

    def parse_schedule_page(self, response):
        year = response.meta['year']
        match_round = response.meta['match_round']
        match_reports = response.xpath('//span[@class="matchNote"]/a')
        for match_report in match_reports:
            url = match_report.xpath('./@href').extract_first(default='')
            full_url = response.urljoin(url)
            yield scrapy.Request(
                url=full_url,
                meta={
                    'year': year,
                    'match_round': match_round
                },
                callback=self.parse_match_data_page)

    def parse_match_data_page(self, response):
        item = SoccerDataItem()
        ID_dict = {}
        item['season'] = response.meta['year']
        item['round'] = response.meta['match_round']
        item['url'] = response.url

        item['home_team'] = response.xpath(
            '//div[@class="l_team"]/p/text()').extract_first(default='')
        item['away_team'] = response.xpath(
            '//div[@class="r_team"]/p/text()').extract_first(default='')

        item['home_team_score'] = int(
            response.xpath('//div[@class="match_score"]/span[1]/text()')
            .extract_first(default=-1))
        item['away_team_score'] = int(
            response.xpath('//div[@class="match_score"]/span[2]/text()')
            .extract_first(default=-1))

        item['home_team_id'] = response.xpath(
            "//input[@id='hometeamId']/@value").extract_first('')
        item['away_team_id'] = response.xpath(
            "//input[@id='guestteamId']/@value").extract_first('')
        item['home_players'] = {}
        item['away_players'] = {}
        # for home_substitute in response.xpath(
        #         "//ul[@class='starting_lineup match_logo']/li[@class='pl10']"):
        #     name = home_substitute.xpath(
        #         "./div[@class='ml10']/text()").extract_first(
        #             default='').strip().split('\xa0\xa0')[-1]
        #     if not name:
        #         continue
        #     item['home_players'][name] = {'is_startup': 0, 'is_subs_up': 0}
        #
        # for away_substitute in response.xpath(
        #         "//ul[@class='starting_lineup match_logo']/li[@class='pr10']"):
        #     name = away_substitute.xpath(
        #         "./div[@class='mr10']/text()").extract_first(
        #             default='').strip().split('\xa0\xa0')[0]
        #     if not name:
        #         continue
        #     item['away_players'][name] = {'is_startup': 0, 'is_subs_up': 0}

        for home_startup_player in response.xpath(
                "//div[@id='tab5']/div[@class='football_court']/div[@class='left hotspot_left']/ul[@class='hotspot match_logo']/li[position()<13][position()>1]/label[@class='checkbox']"
        ):
            personid = home_startup_player.xpath(
                "./input/@value").extract_first(default=0).strip()
            name = home_startup_player.xpath(
                "./p[@class='font']/text()"
            ).extract_first(default='').strip()
            if not name:
                continue
            position = home_startup_player.xpath(
                "./span[2]/text()").extract_first(default='').strip()
            subs_down_time = home_startup_player.xpath(
                "./span[@class='ctime']/text()").extract_first(
                    default='').strip()
            played_time = int(''.join(re.findall(r'(\d{1,2})\'\d{1,2}', subs_down_time))) if subs_down_time else 90
            ID_dict[name] = personid
            item['home_players'][personid] = {
                'is_startup': 1,
                'played_time': played_time,
                'position': position,
                'team_id': item['home_team_id']
            }

        for home_substitute in response.xpath(
                "//div[@id='tab5']/div[@class='football_court']/div[@class='left hotspot_left']/ul[@class='hotspot match_logo']/li[position()>13]/label[@class='checkbox']"
        ):
            personid = home_substitute.xpath("./input/@value").extract_first(
                default=0).strip()
            name = home_substitute.xpath(
                "./p[@class='font']/text()").extract_first(default='').strip()
            if not name:
                continue
            position = home_substitute.xpath("./span[2]/text()").extract_first(
                default='').strip()
            subs_up_time = home_substitute.xpath(
                ".//span[@class='ctime']/text()").extract_first(
                    default='').strip()
            played_time = 90 - int(''.join(re.findall(r'(\d{1,2})\'\d{1,2}', subs_up_time))) + 1
            ID_dict[name] = personid
            item['home_players'][personid] = {
                'is_startup': 0,
                'position': position,
                'played_time': played_time,
                'team_id': item['home_team_id']
            }

        for away_startup_player in response.xpath(
                "//div[@id='tab5']/div[@class='football_court']/div[@class='right hotspot_right']/ul[@class='hotspot match_logo']/li[position()>1][position()<13]/label[@class='checkbox']"
        ):
            personid = away_startup_player.xpath(
                "./input/@value").extract_first(default=0).strip()
            name = away_startup_player.xpath(
                "./p[@class='font']/text()").extract_first(default='').strip()
            if not name:
                continue
            subs_down_time = away_startup_player.xpath(
                "./span[@class='ctime']/text()").extract_first(
                    default='').strip()
            played_time = int(''.join(re.findall(r'(\d{1,2})\'\d{1,2}', subs_down_time))) if subs_down_time else 90
            position = away_startup_player.xpath(
                "./span[2]/text()").extract_first(default='').strip()
            ID_dict[name] = personid
            item['away_players'][personid] = {
                'is_startup': 1,
                'position': position,
                'played_time': played_time,
                'team_id': item['away_team_id']
            }

        for away_substitute in response.xpath(
                "//div[@id='tab5']/div[@class='football_court']/div[@class='right hotspot_right']/ul[@class='hotspot match_logo']/li[position()>13]/label[@class='checkbox']"
        ):
            personid = away_substitute.xpath("./input/@value").extract_first(
                default=0).strip()
            name = away_substitute.xpath(
                "./p[@class='font']/text()").extract_first(default='').strip()
            if not name:
                continue
            position = away_substitute.xpath("./span[2]/text()").extract_first(
                default='').strip()
            subs_up_time = away_substitute.xpath(
                ".//span[@class='ctime']/text()").extract_first(
                    default='').strip()
            played_time = 90 - int(''.join(re.findall(r'(\d{1,2})\'\d{1,2}', subs_up_time)))+ 1
            ID_dict[name] = personid
            item['away_players'][personid] = {
                'is_startup': 0,
                'position': position,
                'played_time': played_time,
                'team_id': item['away_team_id']
            }
        matchid = response.xpath(
            "//input[@id='matchId']/@value").extract_first(default='').strip()
        if matchid:
            return scrapy.FormRequest(
                url='http://data.champdas.com/getMatchPersonAjax.html',
                formdata={'matchId': matchid},
                meta={'item': item, 'ID_dict': ID_dict},
                callback=self.parse_person_page)

    def parse_person_page(self, response):
        item, ID_dict = response.meta['item'], response.meta['ID_dict']
        content = json.loads(response.text)
        try:
            for player in content:
                team_player = item['home_players'] if player['teamId'] == item[
                    'home_team_id'] else item['away_players']
                if player['personName'] in ID_dict:
                    personid = ID_dict[player['personName']]
                elif player['personNameEn'] in ID_dict:
                    personid = ID_dict[player['personNameEn']]
                elif player['personId'] in team_player:
                    personid = player['personId']
                team_player[personid]['goal'] = player['goals']
                team_player[personid]['assist'] = player['assists']
                team_player[personid]['shot'] = player['shots']
                team_player[personid]['shot_on_target'] = player['shotsOnTarget']
                team_player[personid]['passes'] = player['passes']
                team_player[personid]['pass_accuracy'] = float(player['passesAccuracy'])
                team_player[personid]['foul'] = player['fouls']
                team_player[personid]['possession_time'] = int(player['ballPossession'])
                team_player[personid]['key_pass'] = int(player['keyPass'])
                team_player[personid]['cross'] = player['center']
                team_player[personid]['dribble'] = player['breakThrows']
                team_player[personid]['fouled'] = player['foulsConceded']
                team_player[personid]['offside'] = player['offsides']
                team_player[personid]['tackle'] = player['tackles']
                team_player[personid]['intercept'] = player['interceptions']
                team_player[personid]['clearance'] = player['clearances']
                team_player[personid]['blocked_shot'] = player['blocksShots']
                team_player[personid]['steal'] = player['blocksPasses']
                team_player[personid]['yellow_card'] = player['yellowCard']
                team_player[personid]['red_card'] = player['redCard']
                team_player[personid]['short_pass'] = player['passShorts']
                team_player[personid]['succ_short_pass'] = player['succPassShorts']
                team_player[personid]['long_pass'] = player['passLong']
                team_player[personid]['succ_long_pass'] = player['succPassLong']
                team_player[personid]['through_ball'] = player['passThrough']
                team_player[personid]['lateral_pass'] = player['passLateral']
                team_player[personid]['diagonal_pass'] = player['passDiagonal']
                team_player[personid]['back_pass'] = player['passBack']
        except Exception as e:
            self.logger.exception(e)
            open('text.json', 'w').write(response.text)

        matrix = []

        for index, personid in enumerate(item['home_players']):
            item['home_player{}'.format(index+1)] = item['home_players'][personid]
            # item['home_player{}'.format(index+1)].update({'name': name})
            matrix = matrix.append(pandas.DataFrame(item['home_player{}'.format(index+1)]))
        for index, personid in enumerate(item['away_players']):
            item['away_player{}'.format(index+1)] = item['away_players'][personid]
            matrix = matrix.append(pandas.DataFrame(item['away_player{}'.format(index+1)]))
            # item['away_player{}'.format(index+1)].update({'name': name})

        # del item['home_players']
        # del item['away_players']

        # players = dict(item['home_players'].items() + item['away_players'].items())
        # players_matrix = pandas.DataFrame(players)
        return item
