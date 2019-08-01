# -*- coding: utf-8 -*-
import json
from soccer_data.items import SoccerDataItem
import scrapy


class ChampdasSpider(scrapy.Spider):
    name = 'champdas_2'

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
        name_dict = {}
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
        for home_substitute in response.xpath(
                "//ul[@class='starting_lineup match_logo']/li[@class='pl10']"):
            name = home_substitute.xpath(
                "./div[@class='ml10']/text()").extract_first(
                    default='').strip().split('\xa0\xa0')[-1]
            if not name:
                continue
            item['home_players'][name] = {'is_startup': 0, 'is_subs_up': 0}

        for away_substitute in response.xpath(
                "//ul[@class='starting_lineup match_logo']/li[@class='pr10']"):
            name = away_substitute.xpath(
                "./div[@class='mr10']/text()").extract_first(
                    default='').strip().split('\xa0\xa0')[0]
            if not name:
                continue
            item['away_players'][name] = {'is_startup': 0, 'is_subs_up': 0}

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
            name_dict[personid] = name
            item['home_players'][name] = {
                'is_startup': 1,
                'subs_down_time': subs_down_time,
                'position': position,
                'is_subs_down': bool(subs_down_time)
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
            name_dict[personid] = name
            item['home_players'][name] = {
                'personid': personid,
                'is_subs_up': 1,
                'position': position,
                'subs_up_time': subs_up_time,
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
            position = away_startup_player.xpath(
                "./span[2]/text()").extract_first(default='').strip()

            name_dict[personid] = name
            item['away_players'][name] = {
                'personid': personid,
                'is_startup': 1,
                'position': position,
                'subs_down_time': subs_down_time,
                'is_subs_down': bool(subs_down_time)
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
            name_dict[personid] = name
            item['away_players'][name] = {
                'personid':personid,
                'is_subs_up': 1,
                'position': position,
                'subs_up_time': subs_up_time,
            }
        matchid = response.xpath(
            "//input[@id='matchId']/@value").extract_first(default='').strip()
        if matchid:
            return scrapy.FormRequest(
                url='http://data.champdas.com/getMatchPersonAjax.html',
                formdata={'matchId': matchid},
                meta={'item': item, 'name_dict':name_dict},
                callback=self.parse_person_page)

    def parse_person_page(self, response):
        item, name_dict = response.meta['item'], response.meta['name_dict']
        content = json.loads(response.text)
        try:
            for player in content:
                team_player = item['home_players'] if player['teamId'] == item[
                    'home_team_id'] else item['away_players']
                if player['personId'] in name_dict:
                    name = name_dict[player['personId']]
                elif player['personName'] in team_player:
                    name = player['personName']
                elif player['personNameEn'] in team_player:
                    name = player['personNameEn']
                team_player[name]['goal'] = player['goals']
                team_player[name]['assist'] = player['assists']
                team_player[name]['shot'] = player['shots']
                team_player[name]['shot_on_target'] = player['shotsOnTarget']
                team_player[name]['passes'] = player['passes']
                team_player[name]['pass_accuracy'] = player['passesAccuracy']
                team_player[name]['foul'] = player['fouls']
                team_player[name]['possession_time'] = player['ballPossession']
                team_player[name]['touch'] = player['touchBall']
                team_player[name]['key_pass'] = player['keyPass']
                team_player[name]['cross'] = player['center']
                team_player[name]['dribble'] = player['breakThrows']
                team_player[name]['fouled'] = player['foulsConceded']
                team_player[name]['offside'] = player['offsides']
                team_player[name]['tackle'] = player['tackles']
                team_player[name]['intercept'] = player['interceptions']
                team_player[name]['clearance'] = player['clearances']
                team_player[name]['blocked_shot'] = player['blocksShots']
                team_player[name]['steal'] = player['blocksPasses']
                team_player[name]['yellow_card'] = player['yellowCard']
                team_player[name]['red_card'] = player['redCard']
                team_player[name]['short_pass'] = player['passShorts']
                team_player[name]['succ_short_pass'] = player['succPassShorts']
                team_player[name]['long_pass'] = player['passLong']
                team_player[name]['succ_long_pass'] = player['succPassLong']
                team_player[name]['through_ball'] = player['passThrough']
                team_player[name]['lateral_pass'] = player['passLateral']
                team_player[name]['diagonal_pass'] = player['passDiagonal']
                team_player[name]['back_pass'] = player['passBack']
                team_player[name]['teamId'] = player['teamId']
        except Exception as e:
            self.logger.exception(e)
            open('text.json','w').write(response.text)

        for index, name in enumerate(item['home_players']):
            item['home_player{}'.format(index+1)] = item['home_players'][name]
            item['home_player{}'.format(index+1)].update({'name': name})
        for index, name in enumerate(item['away_players']):
            item['away_player{}'.format(index+1)] = item['away_players'][name]
            item['away_player{}'.format(index+1)].update({'name': name})

        del item['home_players']
        del item['away_players']
        return item
