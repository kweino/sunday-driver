from scrapy.spiders import SitemapSpider
from route_scraper.items import RouteScraperItem
from bs4 import BeautifulSoup
import re

class MotorcycleRoadsSpider(SitemapSpider):
    name = 'motoRoads'
    allowed_domains = ['motorcycleroads.com']
    sitemap_urls = ['https://www.motorcycleroads.com/sitemap.xml']
    sitemap_rules = [('/motorcycle-roads', 'parse')]


    def parse(self, response):

        numbers = re.compile(r'\d+(?:\.\d+)?')
        soup = BeautifulSoup(response.text, 'lxml')
        yield {
            'gpx_file_num': soup.select('#download_gpx a')[0]['href'].split('/')[-1],
            'name': soup.select('#route_title')[0].text,
            'state': soup.select('span.rank-text a')[0].text,
            'route_length': int(numbers.findall(response.xpath("//*[@id='mile']/strong").get())[0]),
            'user_rating': soup.select('span.field_rating')[0].text,
            'num_user_reviews': soup.select('div.overall-rate')[1].text.split(' ')[0],
            'num_users_rode': soup.select('#t_ride strong')[0].text,
            'num_users_want2ride': soup.select('#t_rode strong')[0].text,
            'scenery_rating': len(soup.select('div.Scenery span.star1-on')),
            'drive_enjoyment_rating': len(soup.select('div.drive span.star1-on')),
            'tourism_rating': len(soup.select('div.tourism span.star1-on')),
            'state_rank': soup.select('span.rank-number')[0].text,
            'num_state_routes': int(numbers.findall(response.xpath("//*[@class='rank-text']/text()").getall()[-1])[0]),
            'author': response.xpath("//*[@class='name']/a/text()").get(),
            'author_points': int(numbers.findall(response.xpath("//*[@class='name']/text()").getall()[-1])[0]),
            'scenery_description' : soup.select('div.Scenery span.rdata')[0].text,
            'drive_enjoyment_description' : soup.select('div.drive span.rdata')[0].text,
            'tourism_description' : soup.select('div.tourism span.rdata')[0].text
        }
