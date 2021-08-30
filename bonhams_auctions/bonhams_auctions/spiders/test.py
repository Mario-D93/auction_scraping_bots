import scrapy
import json

class TestSpider(scrapy.Spider):
    name = 'test'
    #allowed_domains = ['www.bonhams.com']
    start_urls = ['https://www.bonhams.com/api/v1/search_json/?content=sale&date_range=past&exclude_sale_type=3&length=12&page=83&randomise=False']

    def parse(self, response):
        resp = json.loads(response.body)

        print(type(resp))
        
        
