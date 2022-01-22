import scrapy
from scrapy.spiders import SitemapSpider, CrawlSpider

class MrCommentScraperSpider(SitemapSpider, CrawlSpider):
    name = 'MR_comment_scraper'
    allowed_domains = ['motorcycleroads.com']
    sitemap_urls = ['https://www.motorcycleroads.com/sitemap.xml']
    sitemap_rules = [('/motorcycle-roads', 'parse')]

    def parse(self, response):
        parser_dict = {}

        #id information
        parser_dict['url'] = str(response.url)
        parser_dict['gpx_num'] = response.xpath("//*[@id='download_gpx']/a/@href").extract()[0].split('/')[-1]
        parser_dict['route_name'] = response.xpath('//*[@id="route_title"]/text()').extract()[0]

        #if the reviews aren't empty, then get all the comments (up to 3 per page)
        if not response.xpath('//section[@id="block-views-block-route-frontend-block-7"]//*[@class="view-empty"]'):
            parser_dict['comment1'] = response.xpath("//div[@class='review-detail']/div[@class='review-detail-comment' and position()=6]/text()").extract()[0]
            parser_dict['comment1_bike'] = response.xpath("//span[@class='star_color']/text()").extract()[0]
            parser_dict['comment1_stars'] = 5-len(response.xpath("//*[@id='block-views-block-route-frontend-block-7']/div/div/div[2]/div[1]//span[@class='field-content']//*[@class='starrating']/*[starts-with(@class,'rate-image star-off')]"))
            parser_dict['comment1_date'] = response.xpath('//*[@class="review-detail-created"]/text()').extract()[0]

            #handle comment slot 2
            try:
                parser_dict['comment2'] = response.xpath("//div[@class='review-detail']/div[@class='review-detail-comment' and position()=6]/text()").extract()[1]
                try:
                    parser_dict['comment2_bike'] = response.xpath("//span[@class='star_color']/text()").extract()[1]
                except Exception:
                    pass
                try:
                    parser_dict['comment2_stars'] = 5-len(response.xpath("//*[@id='block-views-block-route-frontend-block-7']/div/div/div[2]/div[2]//span[@class='field-content']//*[@class='starrating']/*[starts-with(@class,'rate-image star-off')]"))
                except Exception:
                    pass
                try:
                    parser_dict['comment2_date'] = response.xpath('//*[@class="review-detail-created"]/text()').extract()[1]
                except Exception:
                    pass
            except Exception:
                pass


            #handle comment slot 3
            try:
                parser_dict['comment3'] = response.xpath("//div[@class='review-detail']/div[@class='review-detail-comment' and position()=6]/text()").extract()[2]
                try:
                    parser_dict['comment3_bike'] = response.xpath("//span[@class='star_color']/text()").extract()[2]
                except Exception:
                    pass
                try:
                    parser_dict['comment3_stars'] = 5-len(response.xpath("//*[@id='block-views-block-route-frontend-block-7']/div/div/div[2]/div[3]//span[@class='field-content']//*[@class='starrating']/*[starts-with(@class,'rate-image star-off')]"))
                except Exception:
                    pass
                try:
                    parser_dict['comment3_date'] = response.xpath('//*[@class="review-detail-created"]/text()').extract()[2]
                except Exception:
                    pass
            except Exception:
                pass

        yield parser_dict

        # follow next page links
        head_url = response.xpath('//*[@rel="canonical"]/@href').extract()[0]
        next_page = response.xpath("//a[@title='Go to next page']/@href").extract()
        if next_page:
            next_href = next_page[0]
            next_page_url = head_url + next_href
            request = scrapy.Request(url=next_page_url, callback=self.parse)
            yield request
