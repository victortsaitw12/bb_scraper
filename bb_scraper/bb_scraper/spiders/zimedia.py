# -*- coding: utf-8 -*-
import scrapy
import traceback, sys
from dateutil.parser import parse as date_parser
from scraper.items import NewsItem
from .redis_spiders import RedisSpider
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import re

class ZimediaSpider(RedisSpider):
#class ZimediaSpider(scrapy.Spider):
    name = "zimedia"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "zimedia",
            "name": "zimedia",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            "url": "https://zi.media/category/Trip",
            "scrapy_key": "zimedia:start_urls",
            "priority": 1
        }]
        for request in requests:
            yield scrapy.Request(request['url'],
                    meta=request,
                    dont_filter=True,
                    callback=self.parse)
 

    def parse(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = self.parse_links(soup)
        next_page = self.parse_next_page(soup)
        latest_datetime = self.parse_latest_post_date(links[0])

        for url in links:
           yield scrapy.Request(url,
                   meta = meta,
                   callback=self.parse_article)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
           return

        yield scrapy.Request(next_page,
                meta=meta,
                dont_filter=True,
                callback=self.parse)

    def parse_next_page(self, soup):
        link_prefix = 'https://zi.media'
        if soup.find('ul', class_='zi_gl-pagination') is not None:
            np = soup.find('ul', class_='zi_gl-pagination')
            next_page = np.find_all('li')[-1]
            if (next_page.get('class') == None):
                next_page_link = link_prefix + next_page.find('a').get('href')
        return next_page_link

    def parse_links(self, soup):
       links = []
       link_prefix = 'https://zi.media'
       for element in soup.find_all('div', class_='zi_fz18'):
           link = element.find('a').get('href')
           links.append( link_prefix + link )
       return links

    def parse_latest_post_date(self, first_link):
        res = requests.get(first_link).text
        soup = BeautifulSoup(res, 'html.parser')
        info = soup.find('div', class_='gl_mc-outer1000 zi_ae2-article-outer')
        time_ = info.get('data-published-time')
        if '+' in time_:
            dt = datetime.strptime(time_.split('+')[0], '%Y-%m-%dT%H:%M:%S')
            dt = dt + timedelta(hours = 8)
        else:
            dt = datetime.strptime(time_.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return dt
    

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
        item['media'] = 'zimedia'
        item['proto'] =  'ZIMEDIA_PARSE_ITEM'
        return item

    def parse_author(self, soup):
        try:
            info = soup.find('div', class_='gl_mc-outer1000 zi_ae2-article-outer')
            authors = info.get('data-author')
        except:
            authors = ''
            pass
        return authors

    def parse_datetime(self, soup):
        info = soup.find('div', class_='gl_mc-outer1000 zi_ae2-article-outer')
        time_ = info.get('data-published-time')
        if '+' in time_:
            dt = datetime.strptime(time_.split('+')[0], '%Y-%m-%dT%H:%M:%S')
            dt = dt + timedelta(hours = 8)
        else:
            dt = datetime.strptime(time_.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return dt.strftime('%Y-%m-%dT%H:%M:%S+0800')

    def parse_metadata(self, soup):
        
        metadata = {
            'category': '',
            'tag': []
        }
        
        entry_crumb = soup.find('ul', class_='zi_breadcrumbs').find_all('a')
        entry = [x.get_text(strip=True) for x in entry_crumb]
        entry = list(dict.fromkeys(entry))
        
        if  soup.find('div', class_='zi_ae2-tag-wrap cl-118FAA') is not None:
            keywords = soup.find('div', class_='zi_ae2-tag-wrap cl-118FAA').find_all('a')
            kword = [x.get_text(strip=True) for x in keywords]
            metadata['tag'] = kword
        
        metadata['category'] = entry[-1]
        
        return metadata

    def parse_title(self, soup):
        board = soup.find('h1', class_='zi_fz24')
        title = board.get_text(strip=True)
        return title

    def parse_content(self, soup):
        contents = soup.find(itemprop="articleBody").get_text(strip=True)
        return contents
    
