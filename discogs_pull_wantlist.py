import discogs_client
import scrapy
from scrapy.crawler import CrawlerProcess
from discogs_bot.spiders.get_pricing import DiscogsForSaleReleaseSpider

with open("discogs_token.private.txt", "r") as f:
    usertoken = f.read().strip()
d = discogs_client.Client('WantListClient/0.1', user_token=usertoken)
user = d.user("walrusface")
master_ids = []
ids = []
for a in user.wantlist:
    # If we have any release specified, pull the master
    if a.notes and "any release" in a.notes.lower() and a.release.master is not None:
        master_ids.append(str(a.release.master.id))
    # Otherwise, be specific
    else:
        ids.append(str(a.release.id))
    print(".", end="")

print(ids)
print(master_ids)

print("\nCrawling!")
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(DiscogsForSaleReleaseSpider, ids=" ".join(ids), master_ids=" ".join(master_ids))
process.start() # the script will block here until the crawling is finished