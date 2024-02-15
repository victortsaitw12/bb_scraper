# -*- coding: utf-8 -*-
import scrapy
import traceback, sys
from dateutil.parser import parse as date_parser
from scraper.items import NewsItem
from .redis_spiders import RedisSpider
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json
import re

class UpmediaSpider(RedisSpider):
#class UpmediaSpider(scrapy.Spider):
    name = "upmedia"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "upmedia",
            "name": "upmedia",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            #"url": "https://www.upmedia.mg/news_list.php?Type=2",
            "url": "https://www.upmedia.mg/news_list.php?Type=130",
            "scrapy_key": "upmedia:start_urls",
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
        links = self.parse_links(soup)
        next_page = self.parse_next_page(soup)
        latest_datetime = self.parse_latest_post_date(soup)

        for url in links:
            yield response.follow(url,
                    meta = meta,
                    callback=self.parse_article)

        if next_page is None:
            return

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
            return

        yield scrapy.Request(next_page,
                dont_filter=True,
                meta=meta,
                callback=self.parse)

    def parse_links(self, soup):
        links = soup.find('div',{'id':'news-list'})
        try:
            for tags in soup.find_all('div','tag'):
                tags.decompose()
        except:
            pass
        try:
            for tags in soup.find_all('div',{'id':'banner_index'}):
                tags.decompose()
        except:
            pass
        
        links = links.find_all('dd')
        return [li.find('a')['href'] for li in links]
    
    def parse_next_page(self, soup):
        upmedia_list_url = 'https://www.upmedia.mg/news_list.php'
        try:
            next_page = soup.find('a',text = '»')['href']
            next_page = upmedia_list_url + next_page
        except:
            next_page = None
        return next_page
    
    def parse_latest_post_date(self, soup):
        pub_date = soup.find('div',{'id':'news-list'})
        pub_date = pub_date.find_all('dd')
        link_date = []
        # main
        for auth in pub_date[0].find('div','author').find_all('a'):
            auth.decompose()
        pub_date_main = pub_date[0].find('div','author').text
        pub_date_main = pub_date_main.replace('、','')
        pub_date_main = pub_date_main.strip()
        link_date.append( datetime.strptime(pub_date_main, '%Y年%m月%d日 %H:%M') )
        # others
        for date in pub_date[1:]:
            date = datetime.strptime( date.find('div','time').text.strip() , '%Y年%m月%d日 %H:%M')
            link_date.append(date)
        # latest_post_date
        latest_post_date = max(link_date)
        return latest_post_date
    

    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        location = soup.find_all('script')[-1]
        if 'location.href' in location.text:
            new_location = re.search(r'location.href=\'(.*?)\';',location.text.strip()).group(1)
            return scrapy.Request(new_location, callback=self.parse_article)
            
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
        item['media'] = 'upmedia'
        item['proto'] =  'UPMEDIA_PARSE_ITEM'
        return item

    def parse_title(self, soup):
        title = soup.find('title').text
        title = ' '.join(title.split())
        title = title.split('--')[0]
        return title
    
    def parse_datetime(self, soup):     
        date = soup.find('head').find('meta',{'name':"pubdate"})['content']
        date = datetime.strptime( date , '%Y-%m-%dT%H:%M:%S')
        date = date.strftime('%Y-%m-%dT%H:%M:%S+0800')
        return date
    
    def parse_author(self, soup):
        try:
            author = soup.find('div','author').find_all('a')
            author = ','.join(x.text for x in author)
            if author.find('／') != -1:
                author = re.split('／', author)[1]
        except:
            author = ''
        return author
    
    def parse_content(self, soup):
        content = soup.find('div','editor')
        for rss_close in content.find_all('div','rss_close'):
            rss_close.decompose()
        for ad in content.find_all('a'):
            ad.decompose()
        for ad in content.find_all('div',{'id':'divider_ad'}):
            ad.decompose()
        for script in content.find_all('script'):
            script.decompose() 
        content = '\n'.join(content.text.split())
        content = content.replace('（）','')
        return content
    
    def parse_metadata(self, soup):
        keywords = soup.find('head').find('meta',{'name':'keywords'})['content']
        keywords = re.split(',', keywords)
        category = soup.find('meta',{'itemprop':'articleSection'})['content']
        return {
            'tag':keywords,
            'category':category,
            'fb_like_count':''
        }
