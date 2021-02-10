import hashlib
from datetime import datetime
import re
import scrapy
from scrapy.spiders import SitemapSpider

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['www.labirint.ru']
    start_urls = ['https://www.labirint.ru/books/']
    site = "Лабиринт"
    site_slug = "labirint"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        # "USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) "
        #               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }

    def parse_book(self, response):
        title = response.xpath('//*[@id="product-title"]/h1/text()').extract_first()
        author = response.xpath('//div[@class="authors"]/a/text()').extract_first()
        description = response.xpath('//*[@id="product-about"]/p/text()').extract()
        ISBN = response.xpath('//div[@class="isbn"]/text()').extract_first()
        img = response.xpath('//div[@id="product-image"]/img/@data-src').extract_first()
        price = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').extract_first()

        if title and price and author:
            title = re.search(r':(.*)', title)
            description = ''.join(description)
            yield {
                "title": title.group(1).strip(' \t\n\r'),
                "author": author.strip(' \t\n\r,'),
                "description": description.strip(' \t\n\r'),
                "isbn": ISBN.strip(' \t\n\rISBN: '),
                "img": img,
                "price": int(price.strip(' \t\n\r')),
                "site": self.site,
                "slug": self.site_slug,
                "url": response.request.url,
                "time": datetime.now().strftime('%Y-%m-%d'),
                "hash": hashlib.md5(response.request.url.encode('utf-8')).hexdigest()
            }

    def parse_list(self, response):
        items = response.xpath('//a[@class="product-title-link"]/@href').extract()
        for item in items:
            url = f"https://www.labirint.ru{item}"
            yield scrapy.Request(url=url, callback=self.parse_book)

    def parse_catalog(self, response):
        total_pages = 0
        urls = response.xpath('//div[@class="pagination-number"]/a/text()').extract()

        for url in urls:
            if url.isnumeric():
                url = int(url)
                if url > total_pages:
                    total_pages = url
        for i in range(1, total_pages):
            cur_url = response.request.url + f"?page={i}"
            yield scrapy.Request(url=cur_url, callback=self.parse_list)

    def parse(self, response):
        main_urls = set(response.xpath('//*[@id="header-genres"]/div/ul/li/a/@href').extract())
        main_branched_urls = set(response.xpath('//*[@id="header-genres"]/div/ul/li/ul/li/a/@href').extract())

        for item in main_urls:
            if item:
                yield scrapy.Request(url="https://www.labirint.ru" + item, callback=self.parse_catalog)
        for item in main_branched_urls:
            if item:
                yield scrapy.Request(url="https://www.labirint.ru" + item, callback=self.parse_catalog)
