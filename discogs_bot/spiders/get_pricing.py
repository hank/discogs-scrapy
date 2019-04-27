# -*- coding: utf-8 -*-
import re
import urllib
import scrapy
from discogs_bot.items import DiscogsListing, DiscogsRelease

def price_convert(_price):
    return float(re.sub(r'[^0-9.]', '', _price))

class DiscogsForSaleReleaseSpider(scrapy.Spider):
    name = "discogs-forsale-release"
    def __init__(self, *args, **kwargs):
        # Create URLs from ids
        print(args)
        print(kwargs)
        ids = kwargs.pop('ids', "") 
        master_ids = kwargs.pop('master_ids', "") 
        urls = []
        master_urls = []
        if ids:
            for i in ids.split(" "):
                urls.append(f"https://www.discogs.com/sell/release/{i}?ev=rb")
        if master_ids:
            for m in master_ids.split(" "):
                master_urls.append(f"https://www.discogs.com/sell/list?master_id={m}&ev=mb")
        # Set up parameters for each listing URL
        params = urllib.parse.urlencode({'sort': 'listed,desc', 'limit': 250})
        master_urls = [a + "&" + params for a in master_urls]
        urls = [a + "&" + params for a in urls]
        self.start_urls = urls + master_urls
        super().__init__(self, *args, **kwargs)

    def parse(self, response):
        # Skip header
        rows = response.css("table.mpitems tr")[1:]
        # Pull the listing stats
        release_id = 0
        low = 0
        median = 0
        high = 0
        if '/list' not in response.request.url:
            release_id = int(response.request.url.split('/')[-1].split('?')[0])
            try:
                _, _, low, median, high = response.css("div.statistics div.section_content ul.last li h4").xpath('following-sibling::text()').getall()
                low = float(low.strip().replace('$',''))
                median = float(median.strip().replace('$',''))
                high = float(high.strip().replace('$',''))
            except:
                pass
        # Create record for release
        yield DiscogsRelease({
            'release_id': release_id,
            'low': low,
            'median': median,
            'high': high,
        })
        # Create records for listings
        for row in rows:
            shipsfrom = 'Unknown'
            seller_rating = 0
            num_seller_ratings = 0
            seller_info = row.css("td.seller_info ul li")
            for sel in seller_info:
                if "Ships" in sel.xpath("span/text()").get():
                    shipsfrom = sel.xpath("span/following-sibling::text()").get()
                else:
                    rating = sel.xpath("span[@class='star_rating']/following-sibling::strong/text()").get()
                    if rating is not None:
                        seller_rating = float(rating.strip().replace('%', ''))
                    nsr = sel.xpath("span[@class='star_rating']/following-sibling::a/text()").get()
                    if nsr is not None:
                        num_seller_ratings = int(nsr.strip().replace(' ratings', '').replace(' rating', '').replace(',', ''))
            yield DiscogsListing({
                'link': row.css("a.item_description_title").xpath("@href").get(),
                'title': row.css("a.item_description_title::text").get(),
                'condition': row.css("i.icon").xpath("@data-condition").get(),
                'format': row.css("i.icon").xpath("@data-format").get(),
                'sleeve_condition': row.css("span.item_sleeve_condition::text").get(),
                'price': price_convert(row.css("td.item_price span.price::text").get()),
                'seller_rating': seller_rating,
                'num_seller_ratings': num_seller_ratings,
                'item_description': row.css("td.item_description").xpath("p[@class='item_condition']/following-sibling::p/text()").get().strip(),
                'shipsfrom': shipsfrom,
                'release_id': release_id,
            })

        next_page_url = response.css("a.pagination_next").xpath("@href").get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))