# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import traceback, sys
from datetime import datetime, timedelta
import re
from dateutil.parser import parse as date_parser
from scraper.items import NewsItem
import json
from .redis_spiders import RedisSpider

class SetnSpider(RedisSpider):
    name = "setn"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "setn",
            "name": "setn",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            "url": "https://www.setn.com/ViewAll.aspx?p=1",
            "scrapy_key": "setn:start_urls",
            "priority": 1
        }]
        for request in requests:
            yield scrapy.Request(request['url'],
                    meta=request,
                    dont_filter=True,
                    callback=self.parse)
 

    def parse(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.body, 'html.parser')
        links, latest_datetime = self.parse_links_dates(soup)

        for url in links:
            yield scrapy.Request(url,
                    meta = meta,
                    callback=self.parse_article)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])

        if latest_datetime < past:
            return

        current_page = re.search("p=(\d+)", response.url).group(1)
        next_page = re.sub("p=(\d+)", "p={}".format(int(current_page) + 1), response.url)
        yield scrapy.Request(next_page,
                meta=meta,
                dont_filter=True,
                callback=self.parse)


    def parse_links_dates(self, soup):
        prefix_html = 'https://www.setn.com/'
        links = []
        dt_list = []

        year = datetime.today().year
        for ind in soup.find_all("div", "row NewsList"):
            for time_ in ind.find_all("time", {"style": "color: #a2a2a2;"}):
                dt = datetime.strptime(str(year) + time_.text, '%Y%m/%d %H:%M')
                dt_list.append(dt)

            for url_ in ind.find_all("a", "gt"):
                suffix = url_["href"]
                if re.search("https", suffix):
                    link = suffix
                else:
                    link = prefix_html + suffix
                links.append(link)

        return links, max(dt_list)

    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        item = NewsItem()
        item['url'] = response.url
        item['author'] = self.parse_author(soup)
        item['article_title'] = self.parse_title(soup)
        item['author_url'] = []
        item['content'] = self.parse_content(soup)
        item['comment'] = []
        item['date'] = self.parse_datetime(soup)
        item['metadata'] = self.parse_metadata(soup)
        item['content_type'] = 0
        item['media'] = 'setn'
        item['proto'] =  'SETN_PARSE_ITEM'
        return item

    def parse_datetime(self, soup):
        published_time = soup.find(
                "meta", {"property": "article:published_time"})["content"]
        published_time = published_time + "+0800"
        return published_time

    def parse_author(self, soup):
        try:
            p1 = soup.find("div", {"id": "Content1"}).find("p").text
            writer = re.search("記者([\u4E00-\u9FFF]+)", p1).group(1)
        except:
            writer = ''
        return writer

    def parse_title(self, soup):
        return soup.h1.text.strip().replace(u'\u3000',
            u' ').replace(u'\xa0', u' ')

    def parse_content(self, soup):
        result = ""
        content = soup.find("div",{"itemprop":"articleBody"}).find_all("p")
        for ind in range(1, len(content), 1):
            if not re.search("▲", content[ind].text):
                result += content[ind].text

        return result

    def parse_metadata(self, soup ,fb_like_soup=None):
        keys = []
        try:
            updated_time = soup.find(
                "meta", {"property": "article:modified_time"})["content"]
            # print(updated_time)
            updated_time = updated_time + "+0800"
        except:
            updated_time = ''

        try:
            for tag in soup.find_all("strong"):
                keys.append(tag.text)
        except:
            pass
        #fb_like_count = fb_like_soup.find('span',{'id':'u_0_3'}).text
        category = soup.find('meta',{'property':'article:section'})['content']
        return {
            'tag': keys,
            "update_time": updated_time,
            'category':category,
            'fb_like_count': ''
        }

