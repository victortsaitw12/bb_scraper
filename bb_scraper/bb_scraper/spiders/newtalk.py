# -*- coding: utf-8 -*-
import scrapy
import traceback, sys
from dateutil.parser import parse as date_parser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import re

class NewtalkSpider(scrapy.Spider):
    name = "newtalk"

    def start_requests(self):
        requests = [{
            "media": "newtalk",
            "name": "newtalk",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            "url": "https://newtalk.tw/news/subcategory/2/%E6%94%BF%E6%B2%BB/1",
            "scrapy_key": "newtalk:start_urls",
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

        posts_date = []
        for post in soup.find_all('div', class_='news-list-item clearfix'):
            _str_date = post.find('div', class_='news_date').text
            date = datetime.strptime(_str_date , '發布%Y.%m.%d | %H:%M ')
            posts_date.append(date)

            url = post.find('a').get('href')
            yield scrapy.Request(url,
                    meta=meta,
                    callback=self.parse_article)



        latest_datetime = max(posts_date)


        past = datetime.now() - timedelta(seconds=meta['days_limit'])

        if latest_datetime < past:
            return

        next_page = self.parse_next_page(soup)

        if next_page is None:
            return

        yield scrapy.Request(next_page,
                dont_filter=True,
                meta=meta,
                callback=self.parse)

    
    def parse_next_page(self,soup):
        try:
            next_page = soup.find('div','pages-container').find('a',text = '下一頁')['href']
        except:
            next_page = None
        return next_page
    

    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
    #     item = NewsItem()
    #     item['url'] = response.url
    #     item['author'] = self.parse_author(soup)
    #     item['article_title'] = self.parse_title(soup)
    #     item['author_url'] = []
    #     item['content'] = self.parse_content(soup)
    #     item['comment'] = []
    #     item['date'] = self.parse_datetime(soup)
    #     item['metadata'] = self.parse_metadata(soup)
    #     item['content_type'] = 0
    #     item['media'] = 'newtalk'
    #     item['proto'] = 'ENEWTALK_PARSE_ITEM'
    #     return item

    # def parse_datetime(self, soup):
    #     date = soup.find('div','content_date').text.strip()
    #     date = datetime.strptime( date , '發布 %Y.%m.%d | %H:%M')
    #     return date.strftime('%Y-%m-%dT%H:%M:%S+0800')
    
    # def parse_author(self, soup):
    #     author = soup.find('div','content_reporter').find('a').text
    #     return author
    
    # def parse_title(self, soup):
    #     title = soup.find('h1','content_title').text
    #     title = ' '.join(title.split())
    #     return title
    
    # def parse_content(self, soup):
    #     content = soup.find('div',{'itemprop':'articleBody'})

    #     for script in content.find_all('script'):
    #         script.clear()

    #     content = content.find_all('p')
        
    #     for cont in content:
    #         try:
    #             cont.find('a').clear()
    #         except:
    #             pass
        
    #     content = '\n'.join(x.text for x in content)
    #     content = re.split(r'延伸閱讀',content)[0]
    #     return content

    # def parse_metadata(self, soup):
    #     keywords = soup.find('head').find('meta',{'name':'keywords'})['content']
    #     keywords = re.split(',',keywords)
    #     category = soup.find('meta',{'property':'article:section'})['content']
    #     metadata = {'tag':keywords, 'category':category, 'fb_like_count':''}
    #     return metadata
    
