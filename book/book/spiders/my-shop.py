import scrapy
from datetime import datetime
import hashlib


class MyShopSpider(scrapy.Spider):
    name = 'my-shop'
    allowed_domains = ['www.my-shop.ru']
    start_urls = ['https://my-shop.ru/shop/catalogue/3/sort/a/page/1.html']
    site = "My-shop"
    site_slug = "my-shop"
    url = 'https://my-shop.ru'

    def parse_book(self, response):
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first()
        author = response.xpath('').extract_first()
        description = response.xpath('').extract()
        ISBN = response.xpath('').extract_first()
        img = response.xpath('').extract_first()
        price = response.xpath('').extract_first()

        if title and price and author:
            title = title.strip(' \t\n\r')
            description = ''.join(description)
            yield {
                "title": title,
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
        pass

    def parse_catalog(self, response):
        pass

    categoty_list = []

    def parse(self, response):
        json = response.css('script::text').extract()

        pattern = r'"href":"(\/shop\/catalogue\/.*?\.html)"'
        json_data = re.findall(pattern, str(json))

        for item in json_data:
            if item:
                category_list.append(item)
                yield scrapy.Request(url=url + item, callback=self.parse)
            else:
                break

        for item in categoty_list:
            if item:
                yield scrapy.Request(url=url + item, callback=self.parse_catalog)
