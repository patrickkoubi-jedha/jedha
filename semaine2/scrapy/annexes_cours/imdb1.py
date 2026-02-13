import os, logging, scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin

class imdb_spider(scrapy.Spider):
    # Name of your spider
    name = "imdb"

    # Url to start your spider from 
    start_urls  = ["https://www.imdb.com/chart/boxoffice"]

    # Callback function that will be called when starting your spider
    # It will get text, author and tags of the first <div> with class="quote"
    def parse(self, response):

            # ----------  XPaths Updated for may 2025 -----------------
            base_li = '/html/body/div[2]/main//section//ul/li[1]'   

            title = response.xpath(f'{base_li}//h3/text()').get()
            if not title:
                self.logger.warning("⚠️  XPath to the title Outdated – "
                                    "Look in the HTML IMDb.")
                return {}

            url_rel = response.xpath(
                f'{base_li}//a[contains(@class,"ipc-title-link-wrapper")]/@href'
            ).get()
            total  = response.xpath(
                f'{base_li}//ul/li[2]/span[2]/text()'
            ).get(default="N/A")

            rating = response.xpath(
                f'{base_li}//span[contains(@class,"ipc-rating-star__rating")]/text()'
            ).get(default="N/A")

            votes_raw = response.xpath(
                f'{base_li}//span[contains(@class,"ipc-rating-star__rating-count")]/text()'
            ).get()
            nb_votes = votes_raw.replace('\u00a0', '').strip('() ') if votes_raw else "N/A"

            #Return the features
            return {
            "ranking": "1",                 
            "title":   title.strip(),
            "url":     urljoin(response.url, url_rel) if url_rel else "N/A",
            "total_earnings": total,
            "rating":  rating,
            "nb_voters": nb_votes,
        }

# Name of the file where the results will be saved
filename = "imdb1.json"

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