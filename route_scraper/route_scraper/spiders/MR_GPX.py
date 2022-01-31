import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from route_scraper.items import RouteScraperItem
import pandas as pd

# gpx_file_nums = pd.read_pickle('/Users/kevinweingarten/OneDrive - University of Kansas/Data Science/sunday-driver/route_scraper/route_scraper/spiders/gpx_file_nums.pkl')

class MrGpxSpider(CrawlSpider):
    name = 'MR_GPX'
    allowed_domains = ['www.motorcycleroads.com']
    start_urls = ['https://www.motorcycleroads.com/downloadgpx/35288']#[f'http://www.motorcycleroads.com/downloadgpx/{row}' for row in gpx_file_nums]

    # rules = (
    #     Rule(LinkExtractor(allow=[f'downloadgpx/{row}' for row in gpx_file_nums]), callback='parse_item', follow=True),
    # )

    def parse_item(self, response):
        item = response.text
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        print(item)
