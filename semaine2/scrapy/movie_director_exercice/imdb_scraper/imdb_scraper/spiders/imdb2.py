import scrapy


class Imdb2Spider(scrapy.Spider):
    name = "imdb2"
    allowed_domains = ["imdb.com"]
    start_urls = ["https://imdb.com"]

    def parse(self, response):
        pass
