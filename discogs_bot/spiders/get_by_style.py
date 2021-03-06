# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class GetByStyleSpider(scrapy.Spider):
    name = 'get_by_style'
    allowed_domains = ['discogs.com']

    def __init__(self, style="Rock", *args, **kwargs):
        super(GetByStyleSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://discogs.com/search/?genre_exact={style}&type=release']

    def parse(self, response):
        links = response.xpath('//*[contains(@class, "card card_large")]/h4/a/@href').extract()
        for link in links:
            # Remove artists and bands from 'Releases'
            if 'artist' not in link:
                album_link = 'http://www.discogs.com' + link
                yield Request(album_link, callback=self.parse_album, meta={'Album URL': album_link})

        
        next_url = response.xpath('//*[contains(@rel, "next")]/@href').extract_first()
        absolute_next_url = 'http://discogs.com/' + next_url
        yield Request(absolute_next_url, callback=self.parse)

    def parse_album(self, response):
        # Album info
        album_url = response.meta.get('Album URL')
        band = response.xpath('//span[@itemprop="byArtist"]/*/a/text()').extract_first()
        album = response.xpath('//h1[@id="profile_title"]/*[position()=2]/text()').extract_first().strip()
        label = response.xpath('//div[@class="profile"]/div[2]/a/text()').extract_first()
        release_date = response.xpath('//div[@class="profile"]/div[8]/a/text()').extract_first().strip()
        genre = response.xpath('//div[@itemprop="genre"]/a/text()').extract_first()
        style = response.xpath('//div[@class="profile"]/div[12]/a/text()').extract_first()

        # Statistics
        have = response.xpath('//a[@class="coll_num"]/text()').extract_first()
        want = response.xpath('//a[@class="want_num"]/text()').extract_first()
        average_rating = response.xpath('//span[@class="rating_value"]/text()').extract_first() + ' / 5'
        
        # Tracklist
        tracks = []
        tracklist = response.xpath('//tr[contains(@class, "tracklist_track track")]')
        # TODO Fix track listing
        for track in tracklist:
            position = track.xpath('//td[@class="tracklist_track_pos"]/text()').extract_first()
            name = track.xpath('//span[@class="tracklist_track_title"]/text()').extract_first()

            tracks.append({'position': position, 'name': name})



        yield {
            'album_url': album_url,
            'band': band,
            'album': album,
            'label': label,
            'release_date': release_date,
            'genre': genre,
            'style': style,
            'have': have,
            'want': want,
            'average_rating': average_rating,
            'tracks': tracks,
        }