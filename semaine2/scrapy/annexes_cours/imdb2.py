import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess

class imdb_spider(scrapy.Spider):
    # Name of your spider
    name = "imdb2"

    # Url to start your spider from 
    start_urls = ["https://www.imdb.com/chart/boxoffice"]

    # Callback function that will be called when starting your spider
    def parse(self, response):
        movies_xpath = '/html/body/div[2]/main//section//ul/li'
        all_li = response.xpath(movies_xpath)

        real_movies = [li for li in all_li if li.xpath('.//h3/text()').get()]

        for idx, movie in enumerate(real_movies, start=1):

            raw_title = movie.xpath('.//h3/text()').get()
            if "." in raw_title:
                ranking, title = raw_title.split(".", 1)
                ranking, title = ranking.strip(), title.strip()
            else:
                ranking, title = str(idx), raw_title.strip()

            url_rel = movie.xpath('.//a[contains(@class,"ipc-title-link-wrapper")]/@href').get()
            url     = response.urljoin(url_rel) if url_rel else "N/A"

            total_earnings = movie.xpath('.//ul/li[2]/span[2]/text()').get(default="N/A")

            rating = movie.xpath(
                './/span[contains(@class,"ipc-rating-star__rating")]/text()'
            ).get(default="N/A")

            votes_raw = movie.xpath(
                './/span[contains(@class,"ipc-rating-star__rating-count")]/text()'
            ).get()
            nb_voters = votes_raw.replace('\u00a0', '').strip('() ') if votes_raw else "N/A"

            yield {
                "ranking": ranking,
                "title":   title,
                "url":     url,
                "total_earnings": total_earnings,
                "rating":  rating,
                "nb_voters": nb_voters,
            }


# Name of the file where the results will be saved
filename = "imdb2.json"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('01-Become_a_movie_director/'):
        os.remove('01-Become_a_movie_director/' + filename)

# Declare a new CrawlerProcess with some settings
## USER_AGENT => Simulates a browser on an OS
## LOG_LEVEL => Minimal Level of Log 
## FEEDS => Where the file will be stored 
## More info on built-in settings => https://docs.scrapy.org/en/latest/topics/settings.html?highlight=settings#settings
process = CrawlerProcess(settings = {
    "USER_AGENT": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0 Safari/124.0"),
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        '01-Become_a_movie_director/' + filename : {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(imdb_spider)
process.start()