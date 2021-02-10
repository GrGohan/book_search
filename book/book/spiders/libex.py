import scrapy
from datetime import datetime
import hashlib


class LibexSpider(scrapy.Spider):
    name = 'libex'
    allowed_domains = ['libex.ru']
    start_urls = ['https://www.libex.ru/']
    site = "Libex"
    site_slug = "libex"
    url = 'https://www.libex.ru'

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
     }

    def parse_book(self, response):
        title = response.xpath('//h1[@class="nomargin"]/text()').extract_first()
        author = response.xpath('//h3[@class="nomargin"]/a/text()').extract_first()
        description = response.xpath('//h3[contains(text(),"Аннотация")]/../p/text()').extract()
        ISBN = response.xpath('//a[contains(text(),"ISBN")]/../text()').extract_first()
        img = response.xpath('//td[@rowspan="8"]/a/img/@src').extract_first()
        if img is not None:
            img = LibexSpider.url + img
        price = response.xpath('//div[@align="right"]/big/text()').extract_first()

        if title and price and author:
            title = title.strip(' \t\n\r')
            description = ''.join(description)
            yield {
                "title": title,
                "author": author.strip(' \t\n\r,'),
                "description": description.strip(' \t\n\r'),
                "isbn": ISBN.strip(' \t\n\r:;'),
                "img": img,
                "price": int(price.strip(' \t\n\r₽')),
                "site": self.site,
                "slug": self.site_slug,
                "url": response.request.url,
                "time": datetime.now().strftime('%Y-%m-%d'),
                "hash": hashlib.md5(response.request.url.encode('utf-8')).hexdigest()
            }

    def parse_list(self, response):
        items = response.xpath('//tr/td/big/a/@href').extract()
        for item in items:
            url = f"https://www.libex.ru{item}"
            yield scrapy.Request(url=url, callback=self.parse_book)

    def parse_catalog(self, response):
        pages = response.xpath('//tr/th[4]/a/@href').extract_first()
        total_pages = pages.strip(' \t\n\r?pg=')

        for i in range(1, int(total_pages)):
            cur_url = response.request.url + f"?pg={i}"
            yield scrapy.Request(url=cur_url, callback=self.parse_list)

    def parse(self, response):
        main_urls = response.xpath('//tr/td[@valign="top"]/../td/a[contains(@href, "/cat/")]/@href').extract()

        for item in main_urls:
            if item:
                yield scrapy.Request(url="https://www.libex.ru" + item, callback=self.parse_catalog)