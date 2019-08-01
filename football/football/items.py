# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FootballItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    id = scrapy.Field()
    goals = scrapy.Field()
    assists = scrapy.Field()
    shots = scrapy.Field()
    shots_on_target = scrapy.Field()
    passes = scrapy.Field()
    succ_passes = scrapy.Field()
    fouls = scrapy.Field()
    possession_time = scrapy.Field()
    key_passes = scrapy.Field()
    touches = scrapy.Field()
    crosses = scrapy.Field()
    dribbles = scrapy.Field()
    foulsconceded = scrapy.Field()
    offsides = scrapy.Field()
    tackles = scrapy.Field()
    interceptions = scrapy.Field()
    clearances = scrapy.Field()
    blocked_passes = scrapy.Field()
    blocked_shots = scrapy.Field()
    yellow_cards = scrapy.Field()
    red_cards = scrapy.Field()
    short_passes = scrapy.Field()
    succ_short_passes = scrapy.Field()
    long_passes = scrapy.Field()
    succ_long_passes = scrapy.Field()
    through_passes = scrapy.Field()
    lateral_passes = scrapy.Field()
    diagonal_passes = scrapy.Field()
    back_passes = scrapy.Field()
    minutesPlayed = scrapy.Field()
    saves = scrapy.Field()
    season = scrapy.Field()
    position = scrapy.Field()
    pass
