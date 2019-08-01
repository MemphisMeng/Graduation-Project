# -*- coding: utf-8 -*-

import scrapy
from football.items import FootballItem
import json


class ChampdasSpider(scrapy.Spider):
    name = 'champdas'
    years = [2014, 2015, 2016, 2017, 2018]
    max_round = 30
    start_urls = 'http://data.champdas.com/match/scheduleDetail-1-{year}-{round}.html'

    def start_requests(self):
        for year in self.years:
            for match_round in range(1, self.max_round + 1):
                yield scrapy.Request(url=self.start_urls.format(year=year, round=match_round),
                                     meta={'year': year},
                                     callback=self.parse_url)

    def parse_url(self, response):
        year = response.meta['year']
        match_reports = response.xpath('//span[@class="matchNote"]/a')
        for match_report in match_reports:
            url = match_report.xpath('./@href').extract_first(default='')
            full_url = response.urljoin(url)
            yield scrapy.Request(url=full_url, meta={'year': year},
                                 callback=self.parse_website)

    def parse_website(self, response):
        year = response.meta['year']
        matchid = response.xpath('//input[@id="matchId"]/@value').extract_first(default='').strip()
        if matchid:
            return scrapy.FormRequest(
                url='http://data.champdas.com/getMatchPersonAjax.html',
                formdata={'matchId': matchid},
                meta={'year': year},
                callback=self.parse_data_site)

    def parse_data_site(self, response):
        content = json.loads(response.text)
        try:
            for player in content:
                item = FootballItem()
                item['id'] = int(player['personId'])
                item['name'] = player['personName']
                item['goals'] = player['goals']
                item['assists'] = player['assists']
                item['shots'] = player['shots']
                item['shots_on_target'] = player['shotsOnTarget']
                item['passes'] = player['passes']
                item['succ_passes'] = player['succPasses']
                item['fouls'] = player['fouls']
                item['possession_time'] = int(player['ballPossession'])
                item['touches'] = player['catchBall']
                item['key_passes'] = int(player['keyPass'])
                item['crosses'] = player['center']
                item['dribbles'] = player['breakThrows']
                item['foulsconceded'] = player['foulsConceded']
                item['offsides'] = player['offsides']
                item['tackles'] = player['tackles']
                item['interceptions'] = player['interceptions']
                item['clearances'] = player['clearances']
                item['blocked_passes'] = player['blocksPasses']
                item['blocked_shots'] = player['blocksShots']
                item['yellow_cards'] = player['yellowCard']
                item['red_cards'] = player['redCard']
                item['short_passes'] = player['passShorts']
                item['succ_short_passes'] = player['succPassShorts']
                item['long_passes'] = player['passLong']
                item['succ_long_passes'] = player['succPassLong']
                item['through_passes'] = player['passThrough']
                item['lateral_passes'] = player['passLateral']
                item['diagonal_passes'] = player['passDiagonal']
                item['back_passes'] = player['passBack']
                item['minutesPlayed'] = int(player['minutesPlayed'])
                item['saves'] = player['saves']
                item['season'] = response.meta['year']
                item['position'] = player['personPosition']
                yield item
        except Exception as e:
            self.logger.exception(e)
            open('text.json', 'w').write(response.text)

