import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import hashlib
import re

class BookvoedSpider(scrapy.Spider):
    name = 'bookvoed'
    allowed_domains = ['bookvoed.ru']
    start_urls = ['https://www.bookvoed.ru/books?genre=2']
    site = "Буквоед"
    site_slug = "bookvoed"
    url = 'https://www.bookvoed.ru'

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
    }

    def parse_book(self, response):
        title = response.xpath('//h1/span[@itemprop="name"]/text()').extract_first()
        author = response.xpath('//span[@class="lw mw"]/a/text()').extract_first()
        description = response.xpath('//div[@class="Kw Ws"]/text()').extract()
        ISBN = response.xpath('//tr/td[contains(text(),"ISBN")]/../td[@class="Vw"]/text()').extract_first()
        img = BookvoedSpider.url + response.xpath('//a/img[@itemprop="image"]/@src').extract_first()
        price = response.xpath('//*[@id="book_buttons"]/div/div/div/text()').extract_first()

        if title and price and author:
            title = title.strip(' \t\n\r')
            description = ''.join(description)
            yield {
                "title": title,
                "author": author.strip(' \t\n\r,'),
                "description": description.strip(' \t\n\r'),
                "isbn": ISBN.strip(' \t\n\r'),
                "img": img,
                "price": int(price.strip(' \t\n\rpуб.')),
                "site": self.site,
                "slug": self.site_slug,
                "url": response.request.url,
                "time": datetime.now().strftime('%Y-%m-%d'),
                "hash": hashlib.md5(response.request.url.encode('utf-8')).hexdigest()
            }

    def parse_list(self, response):
        items = response.xpath('//div/a[@class="cHb cq"]/@href').extract()
        for item in items:
            yield scrapy.Request(url=item, callback=self.parse_book)

    # ходит по инфинити пейджес каталога
    def parse_catalog(self, response):
        offset = 60
        page = 2

        for i in range(1, 17):
            link_genre = str(response.request.url)
            genre = re.search(r'genre=(.*)', link_genre)
            genre = genre.group(1).strip(' \t\n\r')

            cur_url = f'https://www.bookvoed.ru/books?genre={genre}&offset={offset}&pages=17&page={page}&_part=books'
            offset += 60
            page += 1

            yield scrapy.Request(url=cur_url, callback=self.parse_list)

    # ходит по категориям
    def parse(self, response, **kwargs):
        main_urls = response.xpath('//*[@id="catalog"]/li[1]/ul/li/ul/li/a/@href').extract()

        for item in main_urls:
            if item:
                yield scrapy.Request(url=item, callback=self.parse_catalog)
