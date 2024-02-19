# -*- coding: utf-8 -*-
import scrapy
import traceback, sys
from dateutil.parser import parse as date_parser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import re

class TtvSpider(scrapy.Spider):
    name = "ttv"

    def start_requests(self):

        requests = [{
            "media": "ttv",
            "name": "ttv",
            "enabled": True,
            "days_limit": 3600 * 24 ,
            "interval": 3600,
            "url": "https://www.ttv.com.tw/news/",
            "url_pattern": "https://www.ttv.com.tw/news/catlist.asp?page={page}&Cat=&NewsDay={news_date}",
            "scrapy_key": "ttv:start_urls",
            "priority": 1
        }]
        for request in requests:
            yield scrapy.Request(request['url'],
                    meta=request,
                    dont_filter=True,
                    callback=self.parse)

    def parse(self, response):
        meta = response.meta
        now = datetime.now()
        
        past = now - timedelta(seconds=meta['days_limit'])
        
        while now >= past:
            meta['news_date'] = now.strftime('%Y/%m/%d')
            meta['page'] = 1
            url = meta['url_pattern'].format(
                page=meta['page'],
                news_date = meta['news_date']
            )
            yield scrapy.Request(url,
                    meta=meta,
                    dont_filter=True,
                    callback=self.parse_list)

            now = now - timedelta(days=1)

    def parse_list(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.body, 'html.parser')

        elements = soup.find_all('li', class_='ellipsis newsText large')

        if len(elements) == 0:
            return

        for element in elements:
            url = element.find('a').get('href')
            yield response.follow(url,
                    meta = meta,
                    callback=self.parse_article)

        meta['page'] = meta['page'] + 1
        url = meta['url_pattern'].format(
            page=meta['page'],
            news_date = meta['news_date']
        )
        yield scrapy.Request(url,
                dont_filter=True,
                meta=meta,
                callback=self.parse_list)


    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
    #     item = NewsItem()
    #     item['url'] = response.url
    #     item['author'] = None
    #     item['article_title'] = self.parse_title(soup)
    #     item['author_url'] = []
    #     item['content'] = self.parse_content(soup)
    #     item['comment'] = []
    #     item['date'] = self.parse_datetime(soup)
    #     item['metadata'] = self.parse_metadata(soup)
    #     item['content_type'] = 0
    #     item['media'] = 'ttv'
    #     item['proto'] =  'TTV_PARSE_ITEM'
    #     return item

    # def parse_datetime(self,soup):
    #     post_time = soup.find('div', class_='ReportDate middle').find('a')
    #     date = datetime.strptime(post_time.text, '%Y-%m-%d')
    #     return date.strftime('%Y-%m-%dT%H:%M:%S+0800')

    # def parse_title(self,soup):
    #     return soup.find('h1', class_='title').text

    # def parse_content(self,soup):
    #     content = []
    #     segment = soup.find('div', class_='br')
    #     try:    # remove ADs
    #         segment.style.decompose()
    #     except:
    #         pass
    #     content = ''.join(segment.text.split())
    #     return content

    # def parse_metadata(self,soup):

    #     def parse_category(soup):
    #         return soup.find('span', 'glyphicon glyphicon-file r2p').parent.text
        
    #     def parse_tag(soup):
    #         tags_content = []
    #         tags = soup.find('div', class_='br4x middle')
    #         for element in tags.find_all('a'):
    #             tags_content.append(element.text)
    #         return tags_content

    #     # 文章分類、關鍵字、按讚數
    #     metadata = {
    #         'category': parse_category(soup),
    #         'tag': parse_tag(soup),
    #         'fb_like_count': '',
    #     }
    #     return metadata
