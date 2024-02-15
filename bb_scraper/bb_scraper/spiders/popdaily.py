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

class PopdailySpider(RedisSpider):
#class PopdailySpider(scrapy.Spider):
    name = "popdaily"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "popdaily",
            "name": "popdaily",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            "url": "https://www.popdaily.com.tw/explore/new",
            "post_url": 'https://www.popdaily.com.tw/api/list/post',
            "scrapy_key": "popdaily:start_urls",
            "priority": 1,
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
                'Referer': 'https://www.popdaily.com.tw/explore/life',
            },
            "data": {
                'clas': 'new',
                'type':'explore',
                'token':'guest.5564632.8e38305c-37c3-4461-9c8c-7ca247159e0d', #get from cookie
                'page': '9999999999999',
                'score': '99999',
            }
        }]

        for req in requests:
            yield scrapy.Request(
                    url=req['url'],
                    meta=req,
                    callback=self.parse)

    def parse(self, response):
        meta = response.meta
        yield scrapy.FormRequest(
            url=meta['post_url'],
            headers=meta['headers'],
            formdata=meta['data'],
            method='POST',
            meta=meta,
            dont_filter=True,
            callback=self.parse_list)
 

    def parse_list(self, response):
        meta = response.meta
        js = json.loads(response.text)
        # the final page
        if js['list']==[]:
            return

        article_list = []
        for i in range(len(js['list'])):
            prefix = 'https://www.popdaily.com.tw'
            postID = js['list'][i]['postID'].split('.')
            postID.insert(0, prefix)
            article_list.append({
                'url': ('/').join(postID),
                'newScore': js['list'][i]['newScore'],
                't': js['list'][i]['t'],
                'like': js['list'][i]['like']
            })

        # get latest_datetime
        sec = article_list[0]['t']
        latest_datetime = datetime.fromtimestamp(int(sec/1000))

        # crawl article
        for url in article_list:
            meta['like'] = url['like']
            yield scrapy.Request(url['url'],
                    meta=meta,
                    callback=self.parse_article)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
            return

        # crawl next page
        page = article_list[-1]['t']
        score = article_list[0]['newScore']
        meta['data']['page'] = str(page)
        meta['data']['score'] = str(score)
        
        yield scrapy.FormRequest(
                url=meta['post_url'],
                headers=meta['headers'],
                formdata=meta['data'],
                method='POST',
                meta=meta,
                dont_filter=True,
                callback=self.parse_list)
    

    def parse_article(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.body, 'lxml')
        js = soup.findAll('script', type='application/ld+json')[-1]
        js = json.loads(js.text)
        item = NewsItem()
        item['url'] = response.url
        item['author'] = self.parse_author(js)
        item['article_title'] = self.parse_title(js)
        item['author_url'] = self.parse_author_url(response.text)
        item['content'] = self.parse_content(js)
        item['comment'] = []
        item['date'] = self.parse_datetime(js)
        item['metadata'] = self.parse_metadata(js,response.url)
        item['metadata']['like_count'] = meta['like']
        item['content_type'] = 0
        item['media'] = 'popdaily'
        item['proto'] = 'POPDAILY_PARSE_ITEM'
        return item

    def parse_datetime(self, js):
        timestamp = js['datePublished'].split('.')[0]
        date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        date = date + timedelta(hours = 8)
        return date.strftime('%Y-%m-%dT%H:%M:%S+0800')

    def parse_metadata(self, js, url):
        metadata = {
            'tag':js['keywords'],
            'category':url.split('/')[-2]
        }
        return metadata

    def parse_author_url(self,html):
        prefix = 'https://www.popdaily.com.tw/user/'
        ind = html.find('%22%2C%22name')
        return [prefix + html[(ind-6):ind]]
    
    def parse_author(self,js):
        return ','.join(js['author']) 
        
    def parse_title(self,js):
        return js['headline'].split('｜')[0]

    def parse_content(self,js):
        return js['articleBody']
    
