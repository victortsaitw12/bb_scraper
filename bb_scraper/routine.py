from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


def load_spiders():
    from bb_scraper.spiders import ptt_gossip_spider
    from bb_scraper.spiders import ptt_HatePolitics_spider
    return [
        ptt_gossip_spider.PTTGossipSpider,
        ptt_HatePolitics_spider.PTTHatePoliticsSpider
    ]


def crawl_job():
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    for spider in load_spiders():
        runner.crawl(spider)
    return runner.join()


def crawl():
    d = crawl_job()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

if __name__ == '__main__':
    crawl()
