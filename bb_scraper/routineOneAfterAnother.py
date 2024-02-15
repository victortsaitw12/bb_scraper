from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
import argparse

parser = argparse.ArgumentParser(description='Describe MongoDB Connection and database')
parser.add_argument('--mongouri', type=str, help='The uri of mongodb')
parser.add_argument('--mongodb', type=str, help='The database of mongodb')

# Parse the arguments
args = parser.parse_args()

if args.mongouri is None:
    print("Error: Please pass --mongouri to give the mongodb conntection")
    exit(1)

if args.mongodb is None:
    print("Error: Please pass --mongodb to give the mongodb database")
    exit(1)

def load_spiders():
    from bb_scraper.spiders import ptt_gossip_spider
    from bb_scraper.spiders import ptt_HatePolitics_spider
    from bb_scraper.spiders import bccnews
    from bb_scraper.spiders import businessweekly
    from bb_scraper.spiders import ebc
    from bb_scraper.spiders import mirrormedia
    from bb_scraper.spiders import nownews
    from bb_scraper.spiders import rwnews
    from bb_scraper.spiders import storm
    from bb_scraper.spiders import tvbs


    return [
        # ptt_gossip_spider.PTTGossipSpider,
        # ptt_HatePolitics_spider.PTTHatePoliticsSpider,
        businessweekly.BusinessweeklySpider,
        bccnews.BbcNewsSpider,
        ebc.EbcSpider,
        mirrormedia.MirrormediaSpider,
        nownews.NownewsSpider,
        rwnews.RwnewsSpider,
        storm.StormSpider,
        tvbs.TVBSSpider
    ]

configure_logging()
settings = get_project_settings()
settings["MONGODB_URI"] = args.mongouri
settings["MONGODB_DATABASE"] = args.mongodb
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    for spider in load_spiders():
        yield runner.crawl(spider)
    reactor.stop()
crawl()
reactor.run()

