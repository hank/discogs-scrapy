# -*- coding: utf-8 -*-
import scrapy

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
        self.start_urls = urls + master_urls
        super().__init__(self, *args, **kwargs)

    def parse(self, response):
        # Skip header
        rows = response.css("table.mpitems tr")[1:]
        for row in rows:
            shipsfrom = None
            seller_info = row.css("td.seller_info ul li")
            for sel in seller_info:
                if "Ships" in sel.xpath("span/text()").get():
                    shipsfrom = sel.xpath("span/following-sibling::text()").get()
            yield {
                'title': row.css("a.item_description_title::text").get(),
                'condition': row.css("i.icon").xpath("@data-condition").get(),
                'format': row.css("i.icon").xpath("@data-format").get(),
                'sleeve_condition': row.css("span.item_sleeve_condition::text").get(),
                'release_link': row.css("a.item_release_link").xpath("@href").get(),
                'price': row.css("td.item_price span.price::text").get(),
                'shipterms': row.css("a.show-terms-link").xpath("@href").get(),
                'shipsfrom': shipsfrom,
            }

        next_page_url = response.css("a.pagination_next").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))