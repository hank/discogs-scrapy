import os
import discogs_client
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from discogs_bot.spiders.get_pricing import DiscogsForSaleReleaseSpider

with open("discogs_token.private.txt", "r") as f:
    usertoken = f.read().strip()
with open("discogs_user.private.txt", "r") as f:
    user = f.read().strip()
d = discogs_client.Client('WantListClient/0.1', user_token=usertoken)
user = d.user(user)
master_ids = []
ids = []
for a in user.wantlist:
    # If we have any release specified, pull the master
    if a.notes and "any release" in a.notes.lower() and a.release.master is not None:
        master_ids.append(str(a.release.master.id))
    # Otherwise, be specific
    else:
        ids.append(str(a.release.id))

print(ids)
print(master_ids)

print("\nCrawling!")
settings = get_project_settings()
print(settings)
process = CrawlerProcess(settings)

process.crawl(DiscogsForSaleReleaseSpider, ids=" ".join(ids), master_ids=" ".join(master_ids))
process.start() # the script will block here until the crawling is finished