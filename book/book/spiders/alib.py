import scrapy
from datetime import datetime
import hashlib

class AlibSpider(scrapy.Spider):
    name = 'alib'
    allowed_domains = ['alib.ru']
    start_urls = ['https://www.alib.ru/kat.phtml/']

    site = "Alib"
    site_slug = "alib"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
    }

    def parse_book(self, response):
        title = response.xpath('//tr/td/p/b/text()').extract_first()
        ISBN = response.xpath('//tr/td/p/text()').extract()
        img = response.xpath('//tr/td/p/a[@target="_blank"]/@href').extract_first()
        price = response.xpath('//tr/td/p/text()').extract()

        if title and price and ISBN:
            title = title.replace("  ", " ")
            title = title.strip(' \t\n\r')

            ISBN = ''.join(ISBN)
            ISBN = re.search(r'ISBN:(.*?)/', description)
            ISBN = ISBN.group(1).strip(' \t\n\r')

            price = ''.join(description)
            price = re.search(r'Цена:(.*?)руб.', alib_price)
            price = price.group(1).strip(' \t\n\r')

            yield {
                "title": title,
                "isbn": ISBN,
                "img": img,
                "price": int(price),
                "site": self.site,
                "slug": self.site_slug,
                "url": response.request.url,
                "time": datetime.now().strftime('%Y-%m-%d'),
                "hash": hashlib.md5(response.request.url.encode('utf-8')).hexdigest()
            }

    def parse_list(self, response):
        items = response.xpath('//a[contains(.//b, "Купить")]/@href').extract()
        for item in items:
            yield scrapy.Request(url=item, callback=self.parse_book)

    def parse_catalog(self, response):
        next_page = 'https:' + str(response.xpath('//b/a/text()').extract())
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_list)

    def parse(self, response):
        main_urls = response.xpath('//tr/td/ul/li/a/@href').extract()

        for item in main_urls:
            if item:
                yield scrapy.Request(url=item, callback=self.parse_catalog)
