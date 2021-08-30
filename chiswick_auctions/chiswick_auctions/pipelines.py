# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from urllib.parse import urlparse
import os


class ChiswickAuctionsPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'auction_name':item.get('auction_name'), 'item_name':item.get('item_name'), 'item_lot':item.get('item_lot')}) for x in item.get(self.images_urls_field, [])]


    def file_path(self, request, response=None, info=None, *, item=None):

        #file name(a lot images)
        item_name = request.meta['item_name'].replace(" ","_").lower()
        item_lot = request.meta['item_lot'].replace(" ","").lower()
        
        return f'images/{item_name+"_"+item_lot}/' + os.path.basename(urlparse(request.url).path)


    def item_completed(self, results, item, info):
        item = {key: val for key, val in item.items() if key != 'image_urls'}
        return item


    
