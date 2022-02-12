import scrapy
from urllib.parse import urljoin

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'https://wiki.aalto.fi/display/ITSP/',
    ]

    def parse(self, response):
        for quote in response.xpath('//div[@class="innerCell"]//a/@href'):
            yield {
                'link': urljoin(self.start_urls[0], quote.get())
            }
        #
        # next_page = response.css('li.next a::attr("href")').get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)