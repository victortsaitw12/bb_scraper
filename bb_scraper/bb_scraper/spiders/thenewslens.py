# -*- coding: utf-8 -*-
import scrapy
import traceback, sys
from dateutil.parser import parse as date_parser
from scraper.items import NewsItem
from .redis_spiders import RedisSpider
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import re

class ThenewslensSpider(RedisSpider):
#class ThenewslensSpider(scrapy.Spider):
    name = "thenewslens"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "thenewslens",
            "name": "thenewslens",
            "enabled": True,
            "days_limit": 3600 * 24 * 3,
            "interval": 3600,
            "url": "https://www.thenewslens.com/news?page=1",
            "scrapy_key": "thenewslens:start_urls",
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

        article_body = soup.find('article', {'itemprop':'articleBody'})

        posts_date = []
        for article in article_body.find_all('div', class_='list-container'):
            url = article.find('div', class_='img-box').find('a')['href']
            if 'article' in url or 'feature' in url:
                article_date = article.find('span', class_='time').text.replace('|', '').strip()
                posts_date.append(datetime.strptime(article_date, '%Y/%m/%d'))
                yield scrapy.Request(url,
                        meta=meta,
                        callback=self.parse_article)


        if len(posts_date) == 0:
            return

        latest_datetime = max(posts_date)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
            return

        current_page = re.search("page=(\d+)", response.url).group(1)
        next_page = re.sub("page=(\d+)", "page={}".format(int(current_page) + 1), response.url)

        yield scrapy.Request(next_page,
                dont_filter=True,
                meta=meta,
                callback=self.parse)
    

    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        item = NewsItem()

        if 'article' in response.url:
            author = self.parse_author(soup)
            article_title = self.parse_title(soup)
            content = self.parse_content(soup)
            date = self.parse_datetime(soup)
            metadata = self.parse_metadata(soup)

        elif 'feature' in response.url:
            author = ''.join(soup.find('div','author').text.split())
            article_title = soup.find('div','article-component-section')['data-seo-title']
            content = self.parse_content_feature(soup)
            date = self.parse_datetime_feature(soup)
            metadata = self.parse_metadata_feature(soup)

        item['url'] = response.url
        item['author'] = author
        item['article_title'] = article_title
        item['author_url'] = []
        item['content'] = content
        item['comment'] = []
        item['date'] = date
        item['metadata'] = metadata
        item['content_type'] = 0
        item['media'] = 'thenewslens'
        item['proto'] =  'THENEWSLENS_PARSE_ITEM'
        return item

    def parse_datetime(self, soup):
        article = soup.find('div', class_='article-info').text.split(',')[0]
        article = article.replace('SPONSORED', '').strip()
        return datetime.strptime(article, '%Y/%m/%d').strftime('%Y-%m-%dT%H:%M:%S+0800')
    
    def parse_datetime_feature(self, soup):
        return datetime.strptime(soup.find('span','time').text.replace('SPONSORED', '').strip(), '%Y/%m/%d').strftime('%Y-%m-%dT%H:%M:%S+0800')
    

    def parse_author(self, soup):
        au = soup.find('div', {'class':'article-author'}).find_all('a')[1].text.strip()
        if not au:
            au = 'SPONSORED'
        return au
    
    def parse_title(self, soup):
        return soup.find('h1', {'class':'article-title'}).text.strip()    
    
    def parse_content(self, soup):
        for tags in soup.find_all('script',{'type':'text/javascript'}):
            tags.decompose()
        content = soup.find('article', {'itemprop':'articleBody'}).text.replace('\n', '').strip()
        content = content.split('延伸閱讀')[0]
        return content
    
    def parse_content_feature(self, soup):
        for tags in soup.find_all('script',{'type':'text/javascript'}):
            tags.decompose()
        content = soup.find('div', 'article-content').text.replace('\n', '').strip()
        content = content.split('延伸閱讀')[0]
        return content

    def parse_metadata(self, soup):
        cat = soup.find('div', {'class':'article-info'}).text.split(',')[1].strip()
        
        try:
            tag = soup.find('ul', {'class':'tags'}).text.strip().split(' ')
        except:
            tag = ''
        
        try:
            sh = soup.find('li', {'class':'share-count'}).text.strip()
        except:
            sh = ''
       
        return {'category': cat,
                'tag': tag,
                'share_count': sh
                }

    def parse_metadata_feature(self, soup):
        cat = soup.find('div','article-component-section')['data-category-keywords'].strip()
        
        try:
            tag = soup.find('div','article-component-section')['data-tag-keywords'].split()
        except:
            tag = ''
       
        return {'category': cat,
                'tag': tag,
                'share_count': ''
                }
    
    
