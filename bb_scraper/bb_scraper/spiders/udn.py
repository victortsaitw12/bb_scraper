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

class UDNSpider(RedisSpider):
    name = "udn"

    def start_requests(self):
        if isinstance(self, RedisSpider):
            return
        requests = [{
            "media": "udn",
            "name": "udn",
            "enabled": True,
            "days_limit": 3600 * 24,
            "interval": 3600,
            "url": "https://udn.com/rank/ajax_newest/2/6638/1",
            "scrapy_key": "udn:start_urls",
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

        if links==[]:
            return

        next_page = self.parse_next_page(response.url)
        latest_datetime = self.parse_latest_post_date(links[0]['url'])

        for url in links:
            yield scrapy.Request(url['url'],
                    meta = meta,
                    callback=self.parse_article)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
            return

        yield scrapy.Request(next_page,
                dont_filter=True,
                meta=meta,
                callback=self.parse)

    def parse_latest_post_date(self, first_link):
        print(first_link)
        html = requests.get(first_link).text
        soup = BeautifulSoup(html,'lxml')
        date_org = soup.find('div', class_ = 'story_bady_info_author').find('span').text   
        date = datetime.strptime(date_org, '%Y-%m-%d %H:%M')
        return date
    
    def parse_links(self, soup):
        links = soup.find_all('h2')
        links = [ {'url':li.find('a')['href'],'metadata':[]} for li in links] 
        return links
    
    def parse_next_page(self, current_page):
        url_split = re.split('/',current_page)
        url_split[-1] = str(int(url_split[-1])+1)
        next_page = '/'.join(url_split)
        return next_page
    
    def parse_article(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        item = NewsItem()
        item['url'] = response.url
        item['date'] = self.parse_datetime(soup)
        item['content'] = self.parse_content(soup)
        item['author'] = self.parse_author(soup)
        item['article_title'] = self.parse_title(soup)
        item['author_url'] = []
        item['comment'] = []
        item['metadata'] = self.parse_metadata(soup)
        item['content_type'] = 0
        item['media'] = 'udn'
        item['proto'] = 'UDN_PARSE_ITEM'
        yield item

        # crawl and parse comment
        url = "https://func.udn.com/funcap/discuss/disList.jsp"
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "0b516666-c0f2-4bd3-be57-e74257f024fa"
        }
        fp = 1

        while True:
            querystring = {
                "article_id": response.url.split('/')[-1],
                "channel_id": "2",
                "fp": str(fp)
            }
            discuss_section = requests.request("GET", url, data="", headers=headers, params=querystring)
            fp+=1
            
            if re.search(r'var dislist\= \[ (.*?)] ;', discuss_section.text) == None: #the end of comments
                break

            dislist = re.search(r'var dislist\= \[ (.*?)] ;', discuss_section.text).group(1)
            dislist = dislist.split('} , {')
            for i in range(len(dislist)):

                if len(dislist) == 1:
                    raw = json.loads(dislist[i])

                elif i == 0:        
                    raw = json.loads(dislist[i] + '}')

                elif i == len(dislist) - 1:
                    raw = json.loads('{' + dislist[i])

                else:
                    raw = json.loads('{' + dislist[i] + '}')

                comment_date = datetime.strptime(raw['postDate'], '%Y/%m/%d %H:%M:%S')
                comment_date = comment_date.strftime('%Y-%m-%dT%H:%M:%S+0800')
                item = NewsItem()
                item['url'] = response.url
                item['metadata'] = {}
                item['article_title'] = self.parse_title(soup)
                item['author'] = raw['nickname']
                item['author_url'] = []
                item['date'] = comment_date
                item['content'] = ''.join(raw['content'].split())
                item['content_type'] = 1
                item['media'] = 'udn'
                item['proto'] = 'UDN_PARSE_ITEM'
                item['comment'] = []
                yield item


    def parse_datetime(self, soup):
        date_org = soup.find('div', class_ = 'story_bady_info_author').find('span').text   
        date = datetime.strptime(date_org, '%Y-%m-%d %H:%M').strftime('%Y-%m-%dT%H:%M:%S+0800')
        return date
    
    def parse_title(self, soup):
        return soup.find('h1', class_ = 'story_art_title').text
            
    def parse_content(self, soup):
        content = ''.join([ent.text for ent in soup.find_all('p')]).replace('\n', '').replace('      500字以內，目前輸入 0 字      ', '')
        if '【相關閱讀】' in content:
            content = content.split('【相關閱讀】')[0]
        return content
    
    def parse_author(self, soup):
        # author_info = soup.find('div', class_ = 'story_bady_info_author')
        # for span in author_info.find_all('span'):
        #     span.clear()
        # author = author_info.text
        
        date_org = soup.find('div', class_ = 'story_bady_info_author').find('span').text
        content = ''.join([ent.text for ent in soup.find_all('p')]).replace('\n', '').replace('      500字以內，目前輸入 0 字      ', '')
        try:
            author = soup.find('div', class_ = 'story_bady_info_author').find('a').text
        except AttributeError:
            author = soup.find('div', class_ = 'story_bady_info_author').text.replace(date_org,'')   
            author = [i  for i in author.split(' ') if '報' not in i if '新聞' not in i if '運動' not in i]
            if len(author) > 0 :
                author = ' '.join(author)
            elif author == []:
                author = ''
            else:
                author = author[0]                       
        
        reg = re.compile(r'【 \D+[／：/:]\D*】', re.VERBOSE)
        tmp = reg.findall(content[:51])        
        if tmp != []:
            author = tmp[0]
        return author    
    
    def parse_metadata(self, soup, fb_like_count_html=None):
        metadata = {'tag':[], 'category':'','fb_like_count':''}
        try: 
            metadata['tag'] = soup.find('div', id = 'story_tags').text.split('﹒')    
        except AttributeError:
            pass  
        #metadata['fb_like_count'] = fb_like_count_html.find('span',{'id':'u_0_3'}).text
        metadata['category'] = soup.find('div',{'id':'nav','class':'only_web'}).find_all('a')[-1].text
        return metadata
