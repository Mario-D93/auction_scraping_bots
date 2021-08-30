# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst

class SworderAuctionsItem(scrapy.Item):

    auction_name = scrapy.Field(
        output_processor = TakeFirst()
    )

    auction_date = scrapy.Field(
        output_processor = TakeFirst()
    )

    sale_number = scrapy.Field(
        output_processor = TakeFirst()
    )

    total_lots = scrapy.Field(
        output_processor = TakeFirst()
    )

    item_lot = scrapy.Field(
        output_processor = TakeFirst()
    )

    item_name = scrapy.Field(
        output_processor = TakeFirst()
    )

    sold = scrapy.Field(
        output_processor = TakeFirst
    )

    sold_price = scrapy.Field(
        output_processor = TakeFirst()
    )

    item_picture = scrapy.Field(
        output_processor = TakeFirst()
    )

    item_description = scrapy.Field(
        output_processor = TakeFirst()
    )