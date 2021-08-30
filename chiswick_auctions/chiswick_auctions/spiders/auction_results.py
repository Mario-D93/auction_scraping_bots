import scrapy
import re
from scrapy import loader
# from ..items import ChiswickAuctionsItem
from scrapy.loader import ItemLoader
import json


class AuctionResultsSpider(scrapy.Spider):
    name = 'auction_results'
    allowed_domains = ['www.chiswickauctions.co.uk']

    def start_requests(self):
        yield scrapy.Request(
            url = 'https://www.chiswickauctions.co.uk/results/',
            callback = self.parse
        )

    def parse(self, response):

        #loader = ItemLoader(item=ChiswickAuctionsItem())

        auctions = response.xpath("//div[@class = 'auction-calendar']/div[@class='auction-calendar-item calendar-third']")
        counter = 0
        for auction in auctions:
            counter+=1
            auction_url = auction.xpath(".//a/@href").get()
            full_auction_url = f"https://www.chiswickauctions.co.uk{auction_url}"
            yield scrapy.Request(
                url = full_auction_url,
                callback = self.parse_auction

            )


    
    def parse_auction(self, response):
        auction_lots = response.xpath("//div[@class='auction-grid agh']/div")
        counter = 0
        for lot in auction_lots:
            counter+=1
            lot_url = lot.xpath(".//div/div/p/a/@href").get()
            full_lot_url = f"https://www.chiswickauctions.co.uk{lot_url}"
            yield scrapy.Request(
                url = full_lot_url,
                callback=self.parse_auction_lot,
                meta = {'i_response':response}
            )


    def parse_auction_lot(self, response):
        i_response = response.meta['i_response']
        sold = response.xpath("//p/strong[contains(text(),'Sold for')]")
        if sold:
            sold_status = True
        else:
            sold_status = False

        item_desc = response.xpath("normalize-space(//div[@class='lot col-sm-6']/div[@class='lot-desc']/p/text())").get()
        item_description = re.sub("([^\x00-\x7F])+"," ",item_desc)
        

        yield {
            'auction_name': i_response.xpath("normalize-space(//div[@id='AuctionDetails']/h2/text())").extract_first(),
            'auction_date':(i_response.xpath("normalize-space(//div[@id='AuctionDetails']/div/strong[contains(text(),'Date')]/text())").extract_first()).replace("Date: ",""),
            'sale_number':(i_response.xpath("normalize-space(//div[@id='AuctionDetails']/div/strong[contains(text(),'ale num')]/text())").extract_first()).replace("Sale number: ",""),
            'total_lots':(i_response.xpath("normalize-space(//div[@id='AuctionDetails']/div/strong[contains(text(),'Lots')]/text())").extract_first()).replace("Lots: ",""),
            'item_lot' : (response.xpath("normalize-space(//p[@class='lot-number']/text())").extract_first()).replace("Lot ",""),
            'item_name' : response.xpath("normalize-space((//h1[contains(@class,'lot-title')]/text())[1])").extract_first(),
            'sold':sold_status,
            'sold_price' : (response.xpath("normalize-space(//p/strong[contains(text(),'Sold')]/text())").extract_first()).replace("Sold for ",""),
            'item_description' : item_description,
            'image_urls' : response.xpath("//ul[@id='lotGallery']/li/a/@data-image").extract()
        }




