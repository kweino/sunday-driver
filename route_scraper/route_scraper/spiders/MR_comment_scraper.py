import scrapy
from scrapy.spiders import SitemapSpider, CrawlSpider

class MrCommentScraperSpider(SitemapSpider, CrawlSpider):
    name = 'MR_comment_scraper'
    allowed_domains = ['motorcycleroads.com']
    sitemap_urls = ['https://www.motorcycleroads.com/sitemap.xml']
    sitemap_rules = [('/motorcycle-roads', 'parse')]

    def parse(self, response):

        head_url = response.xpath('//link[@rel="canonical"]/@href').extract()[0]
        gpx_num = response.xpath("//*[@id='download_gpx']/a/@href").extract()[0].split('/')[-1]
        route_name = response.xpath('//*[@id="route_title"]/text()').extract()[0]
        comments = response.xpath("//div[@class='review-detail']/div[@class='review-detail-comment' and position()=6]/text()").extract()
        yield {
            'gpx_num' : gpx_num,
            'route_name' : route_name,
            'comments' : comments
        }

        # follow next page links
        next_page = response.xpath("//a[@title='Go to next page']/@href").extract()
        if next_page:
            next_href = next_page[0]
            next_page_url = head_url + next_href
            request = scrapy.Request(url=next_page_url, callback=self.parse)
            yield request
