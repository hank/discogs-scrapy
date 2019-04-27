# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class DiscogsRelease(Item):
    release_id = Field()
    low = Field()
    median = Field()
    high = Field()

class DiscogsListing(Item):
    link = Field()
    title = Field()
    condition = Field()
    format = Field()
    sleeve_condition = Field()
    price = Field()
    shipsfrom = Field()
    seller_rating = Field()
    num_seller_ratings = Field()
    item_description = Field()
    release_id = Field()