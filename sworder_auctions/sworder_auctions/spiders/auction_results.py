import scrapy


class AuctionResultsSpider(scrapy.Spider):
    name = 'auction_results'
    allowed_domains = ['www.sworder.co.uk']
    #start_urls = ['httpd://www.sworder.co.uk/results/']

    def start_requests(self):
        yield scrapy.Request(
            url = 'https://www.sworder.co.uk/results/',
            callback = self.parse
        )

    def parse(self, response):
        auctions = response.xpath("//div[@class='auction-calendar']/div[@class='auction-calendar-item calendar-quarter']")
        
        for auction in auctions:
            auction_url = auction.xpath(".//a/@href").get()
            full_auction_url = f"https://www.sworder.co.uk{auction_url}"

            auction_name = auction.xpath("normalize-space(.//div[@class='auction-calendar-text ']/a/h4/text())").get()
            auction_date = auction.xpath("normalize-space(.//div[@class='auction-calendar-text ']/div/a/strong[contains(text(),'Date')]/text())").get()
            sale_number = auction.xpath("normalize-space(.//div[@class='auction-calendar-text ']/div/a/strong[contains(text(),'ale num')]/text())").get().replace("Sale number:","")
            
            
            yield scrapy.Request(
                url = full_auction_url,
                callback = self.parse_auction,
                meta={
                    'auction_name':auction_name,
                    'auction_date':auction_date,
                    'sale_number':sale_number
                }
            )



    def parse_auction(self, response):
        auction_name = response.meta['auction_name']
        auction_date = response.meta['auction_date']
        sale_number = response.meta['sale_number']
        auction_url = response.url

        total_lots = response.xpath("normalize-space(//li[@role='presentation']/a/text())").get().replace("Past lots","").replace("(","").replace(")","")
        
        lots = response.xpath("//div[@id = 'sold']/div[@class = 'auction-lot']")
        for lot in lots:
            #item name
            item_name = lot.xpath(".//div[@class='auction-lot-text ']/p/a/span/text()").get()


            #sold status
            sold = lot.xpath(".//div[@class='auction-lot-text ']/img")
            if sold:
                sold_status = True
            else:
                sold_status = False


            #sold price or estimated value
            sold_price = lot.xpath(".//div/p/strong[contains(text(),'Sold for')]/text()").get()
            if sold_price:
                sold_price = sold_price.replace("Sold for","")
            else:
                sold_price = lot.xpath(".//div/p/strong[contains(text(),'Estimated')]/text()").get()


            #lot number
            item_lot = lot.xpath("normalize-space(.//div/p[@class='auction-lot-title'][2]/text())").get()
            if item_lot:
                item_lot = item_lot[0:7].replace(")","").replace("Lot","").replace(" ","")
           

            #lot url
            lot_url = lot.xpath(".//div[@class='auction-lot-text ']/p/a/@href").get()
            full_lot_url = f"https://www.sworder.co.uk{lot_url}"


            yield scrapy.Request(
                url = full_lot_url,
                callback = self.parse_lot,
                meta={
                    'auction_name':auction_name,
                    'auction_date':auction_date,
                    'sale_number':sale_number,
                    'total_lots':total_lots,
                    'sold_status':sold_status,
                    'item_name':item_name,
                    'sold_price':sold_price,
                    'item_lot':item_lot,
                    'auction_url':auction_url
                }
            )



    def parse_lot(self, response):
        auction_name = response.meta['auction_name']
        auction_date = response.meta['auction_date']
        sale_number = response.meta['sale_number']
        total_lots = response.meta['total_lots']
        sold_status = response.meta['sold_status']
        item_name = response.meta['item_name']
        sold_price = response.meta['sold_price']
        item_lot = response.meta['item_lot']
        auction_url = response.meta['auction_url']

        #full lot description
        item_desc_one = response.xpath("normalize-space(//div[@class='lot-desc'][1]/p/strong/text())").get()
        item_desc_two = response.xpath("normalize-space(//div[@class='lot-desc'][1]/p/text())").get()
        item_description = f"{item_desc_one} {item_desc_two}"

        

        yield{
            'auction_name':auction_name,
            'auction_date':auction_date,
            'sale_number':sale_number,
            'total_lots':total_lots,
            'sold_status':sold_status,
            'auction_url' : auction_url,
            'item_name':item_name,
            'sold_price':sold_price,
            'item_lot':item_lot,
            'item_description':item_description,
            'image_urls':response.xpath("//ul[@id='lotGallery']/li/a/img/@src").extract()
            
        }



