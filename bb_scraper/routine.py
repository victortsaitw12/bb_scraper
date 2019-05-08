from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


def load_spiders():
    from bb_scraper.spiders import ptt_gossip_spider
    from bb_scraper.spiders import ptt_HatePolitics_spider
    return spiders


def crawl_job():
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    for spider in load_spiders():
        runner.crawl(spider)
    return runner.join()


def crawl():
        

if __nme__ == '__main__':
    reactor.run()
