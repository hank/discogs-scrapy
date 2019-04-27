# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import pymongo
import logging
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
from discogs_bot.items import DiscogsListing, DiscogsRelease
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class MongoDBPipeline(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.listing_collection = db[settings['MONGODB_COLLECTION_LISTINGS']]
        self.listing_collection.create_index([("link", pymongo.DESCENDING)], unique=True)
        self.release_collection = db[settings['MONGODB_COLLECTION_RELEASES']]
        self.release_collection.create_index([("release_id", pymongo.DESCENDING)], unique=True)

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem(f"Missing {data}!")
        if valid:
            # Deal with releases and listings differently
            if isinstance(item, DiscogsListing):
                query = {'link': item['link']}
                update_result = self.listing_collection.replace_one(query, dict(item), upsert=True)
                if update_result.upserted_id is not None:
                    self._logger.debug(f"Listing {update_result.upserted_id} updated in MongoDB database!")
                else:
                    self._logger.debug(f"Listing added in MongoDB database!")
            elif isinstance(item, DiscogsRelease):
                query = {'release_id': item['release_id']}
                update_result = self.release_collection.replace_one(query, dict(item), upsert=True)
                if update_result.upserted_id is not None:
                    self._logger.debug(f"Release {update_result.upserted_id} updated in MongoDB database!")
                else:
                    self._logger.debug(f"Release added in MongoDB database!")
        return item