from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

def load_spiders():
    from bb_scraper.spiders import ptt_gossip_spider
    from bb_scraper.spiders import ptt_HatePolitics_spider
    return [
        ptt_gossip_spider.PTTGossipSpider,
        ptt_HatePolitics_spider.PTTHatePoliticsSpider
    ]


def crawl():
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    for spider in load_spiders():
        runner.crawl(spider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == '__main__':
   crawl()
