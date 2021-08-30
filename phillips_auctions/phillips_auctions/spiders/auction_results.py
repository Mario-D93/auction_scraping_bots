import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
import time

from selenium.webdriver.common.keys import Keys

class AuctionResultsSpider(scrapy.Spider):
    name = 'auction_results'
    # start_urls = ['https://www.phillips.com/auctions/past']


    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.phillips.com/auctions/past',
            wait_time=3,
            callback=self.parse,
            script = "window.scrollTo(0, document.body.scrollHeight);"
            )

    def parse(self, response):
        scroll_pause_time = 0.5
        driver = response.meta['driver']
        
        #current auctions
        auctions = response.xpath("//ul[@id='main-list-backbone']/li[@class='has-image auction col-sm-2']")
        page_auctions = len(auctions)

        while True:
           
            #load the next 10 results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_html = driver.page_source
            resp_obj = Selector(text=new_html)

            #updated auctions after scrolling
            new_auctions = resp_obj.xpath("//ul[@id='main-list-backbone']/li[@class='has-image auction col-sm-2']")
            new_page_auctions = len(new_auctions)


            if new_page_auctions > page_auctions:
                page_auctions += 10
                continue

            else:
                driver.close()
                break
        driver.close()
        
        auction_list = auctions
        #auction_list = resp_obj.xpath("//ul[@id='main-list-backbone']/li[@class='has-image auction col-sm-2']")
        #limiting iteration for the first 3 auctions
        for auction in auction_list[0:3]:
            auction_link = auction.xpath(".//div/h2/a/@href").get()
            full_auction_link = f"https://www.phillips.com{auction_link}"

            yield scrapy.Request(
                url=full_auction_link,
                callback=self.parse_auctions,
                
            )
        
    def parse_auctions(self, response):
        auction_name = response.xpath("//h1[@class='auction-page__hero__title']/text()").get()
        auction_date = response.xpath("//div[@class='auction-details']/p/text()").getall()
        #auction_details = response.xpath("normalize-space(//div[@class='auction-details-blurb']/text())").getall()
        auction_details = response.xpath("normalize-space(//span[@class='auction-page__hero__date']/text()[1])").get()
        list_lots = response.xpath("//div[@class='auction-page__grid']/ul/li")
        total_lots = (response.xpath("//div[@class='auction-page__grid__nav__info']/text()").get()).replace("Showing","").replace("lots","").replace(" ","")


        #limiting for 10 lots
        for lot in list_lots[0:10]:
            lot_url = lot.xpath(".//a/@href").get()
            lot_num = lot.xpath(".//div/a/p/span/strong/text()").get()

            yield SeleniumRequest(
                wait_time=3,
                url = lot_url,
                callback = self.parse_lot,
                meta={
                    'auction_name':auction_name,
                    'auction_date':auction_date,
                    'total_lots':total_lots,
                    'lot_num':lot_num,
                }
            )

    def parse_lot(self, response):
        auction_name = response.meta['auction_name']
        auction_date = response.meta['auction_date']
        total_lots = response.meta['total_lots']
        lot_num = response.meta['lot_num']

        lot_name = response.xpath("//h1[@class='lot-page__lot__maker__name']/text()").get()
        sold_price = response.xpath("//p[@class='lot-page__lot__sold']/text()[3]").get()
        if sold_price:
            sold = True
        else:
            sold = False

        image_url = response.xpath("//div[@class='phillips-image main-lot-image']/img/@src").get()        
        item_description = response.xpath("//li[@class='lot-page__details__list__item']/div/p/text()").getall()



        yield{
            'auction_name':auction_name,
            'auction_date':auction_date[1],
            'total_auction_lots':total_lots,
            'lot_num':lot_num,
            'lot_name':lot_name,
            'sold':sold,
            'sold_price':sold_price,
            'lot_description':item_description,
            'image_urls':image_url,
            'lot_url':response.url
        }