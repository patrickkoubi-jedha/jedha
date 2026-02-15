import scrapy


class BookingSpider(scrapy.Spider):
    name = "booking"
    allowed_domains = ["booking.com"]
    start_urls = ["https://booking.com"]

    def parse(self, response):
        hotel_name = response.css("").get()
        hotel_url = response.css("").get()
        latitude = response.css("").get()
        longitude = response.css("").get() 
        score = response.css("").get()
        yield {
            "hotel_name": hotel_name,
            "hotel_url": hotel_url,
            "latitude": latitude,
            "longitude": longitude,
            "score": score,
        }
