import scrapy
import json
import re

class AuctionResultsSpider(scrapy.Spider):
    name = 'auction_results'
    allowed_domains = ['bonhams.com','www.bonhams.com','api01.bonhams.com']
    #start_urls = ['http://www.bonhams.com/results/']

    auction_main_page = 1
    auction_item_page = 1
    


    def start_requests(self):
        yield scrapy.Request(
            url = 'https://www.bonhams.com/api/v1/search_json/?content=sale&date_range=past&exclude_sale_type=3&length=12&main_index_key=sale&page=1&randomise=False',
            callback = self.parse
        )



    def parse(self, response):
        resp_dict = json.loads(response.body)

        auction_list = resp_dict.get('model_results').get('sale').get('items')
        for auction in auction_list:
            auction_link = auction.get('url').replace('auctions','auction')
            auction_api_link = f"https://api01.bonhams.com/api/search{auction_link}?page=1&page_size=12"

            auction_status = auction.get('status')
            auction_name = auction.get('name_text')

            yield scrapy.Request(
                url=auction_api_link,
                callback=self.parse_auction,
                dont_filter=True,
                meta={
                    'auction_status':auction_status,
                    'auction_name':auction_name,
                }
                #meta={'auction_status':item['auction_status']}
            )

        #pagination
        if len(resp_dict) > 0:
            self.auction_main_page += 1
            next_page = f"https://www.bonhams.com/api/v1/search_json/?content=sale&date_range=past&exclude_sale_type=3&length=12&main_index_key=sale&page={self.auction_main_page}&randomise=False"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )


    def parse_auction(self, response):
        auction_status = response.meta['auction_status']
        auction_name = response.meta['auction_name']
        resp_dict = json.loads(response.body)
        
        items = resp_dict.get('results')
        for item in items:
            item_name = item.get('sDesc')
            price_est_high = item.get('dEstimateHigh')
            price_est_low = item.get('dEstimateLow')
            sold_price = item.get('dHammerPremium')
            starting_bid_amount = item.get('dStartingBidAmt')
            lot_status = item.get('sLotStatus')
            item_lot_num = item.get('iSaleLotNo')
            item_sale_num = item.get('iSaleItemNo')
            item_sale_num_unique = item.get('iSaleLotNoUnique')
            sale_num = item.get('iSaleNo').get('iSaleNo')
            start_date = item.get('iSaleNo').get('daStartDate')
            end_date = item.get('iSaleNo').get('daEndDate')
            venue_location = item.get('iSaleNo').get('sVenue')
            sale_type = item.get('iSaleNo').get('sSaleType')
            
            image_url = item.get('images')[0].get('image_url')
            image_urls = []
            image_urls.append(image_url)
            
            #text cleaning
            raw_item_desc = item.get('sCatalogDesc')
            cleanr = re.compile('<.*?>')
            item_desc = re.sub(cleanr, '', raw_item_desc)



            yield{
                'item_name' : item_name,
                'sold_price':sold_price,
                'price_est_high' : price_est_high,
                'price_est_low' : price_est_low,
                'starting_bid_amount' : starting_bid_amount,
                'auction_name':auction_name,
                'auction_status':auction_status,
                'lot_status' : lot_status,
                'item_lot_num' : item_lot_num,
                'item_sale_num' : item_sale_num,
                'item_sale_num_unique' : item_sale_num_unique,
                'sale_num' : sale_num,
                'start_date' : start_date,
                'end_date' : end_date,
                'venue_location' : venue_location,
                'sale_type' : sale_type,
                'item_desc' : item_desc,
                'image_urls' : image_urls
            }
            





