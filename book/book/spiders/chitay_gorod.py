import scrapy
from datetime import datetime
import hashlib


class ChitayGorodSpider(scrapy.Spider):
    name = 'chitay_gorod'
    allowed_domains = ['chitai-gorod.ru']
    start_urls = ['https://www.chitai-gorod.ru/catalog/books']
    site = "Читай город"
    site_slug = "chitay_gorod"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
    }

    def parse_book(self, response):
        title = response.css(".product__header > h1::text").extract_first()
        author = response.css(".product__header > a.product__author::text").extract_first()
        description = response.xpath('//div[@itemprop="description"]/text()').extract()
        ISBN = response.xpath('//div[@class="product-prop__isbn_item"]/text()').extract_first()
        img = response.css(
            'body > div.page-wrap > main > div.product.js-analytic-product-page.js_product > div:nth-child(1) > '
            'div.product__main.js__product_card_detail >'
            ' div.product__media-block > div.product__image.js__show_gallery > img::attr("data-src")').extract_first()
        price = response.css('div.product__price > div.price::text').extract_first()

        if title and price and author:
            title = title.strip(' \t\n\r')
            description = ''.join(description)
            yield {
                "title": title,
                "author": author.strip(' \t\n\r,'),
                "description": description.strip(' \t\n\r'),
                "isbn": ISBN.strip(' \t\n\r'),
                "img": img,
                "price": int(price.strip(' \t\n\r₽')),
                "site": self.site,
                "slug": self.site_slug,
                "url": response.request.url,
                "time": datetime.now().strftime('%Y-%m-%d'),
                "hash": hashlib.md5(response.request.url.encode('utf-8')).hexdigest()
            }

    def parse_list(self, response):
        items = response.xpath('//div[@class="product-card__info"]/a/@href').extract()
        for item in items:
            url = f"https://www.chitai-gorod.ru{item}"
            yield scrapy.Request(url=url, callback=self.parse_book)

    # ходит по страницам категорий
    def parse_catalog(self, response):
        urls = response.css("a.pagination-item::text").extract()
        total_pages = 0
        for url in urls:
            if url.isnumeric():
                url = int(url)
                if url > 7:
                    total_pages = url
        for i in range(1, total_pages):
            cur_url = response.request.url + f"?page={i}"
            yield scrapy.Request(url=cur_url, callback=self.parse_list)

    # ходит по категориям
    def parse(self, response, **kwargs):
        main_urls = response.css(
            'body > div.page-wrap > main > div.catalog > div > div.container__leftside > div > ul:nth-child(4) > li > a::attr("href")').extract()

        for item in main_urls:
            if item:
                yield scrapy.Request(url="https://www.chitai-gorod.ru" + item, callback=self.parse_catalog)
