# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CommentItem(scrapy.Item):
    route_name = scrapy.Field()
    comments = scrapy.Field()


class RouteScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    gpx_files = scrapy.Field()
    files = scrapy.Field
