# -*- coding: utf-8 -*-
import numpy as np
import scrapy
from itertools import chain
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

class AppledailySpider(scrapy.Spider):
    name = 'appledaily'

    def start_requests(self):

        request = {
            "url": 'https://tw.appledaily.com/new/realtime/1',
            "priority": 3,
            "interval": 3600 * 2,
            "days_limit": 3600 * 24 * 2,
            'scrapy_key': 'appledaily:start_urls',
            'media': 'appledaily',
            'name': 'appledaily',
            'enabled': True,
        }
        yield scrapy.Request(request['url'],
                dont_filter=True,
                meta = request)

    def parse(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.body, "lxml")
    
        if 'alert' in soup.text:
            raise Exception('Show Alert from Appledaily')

        url = soup.find("meta",  property="og:url")['content']
        current_page = re.search("(\d+)", response.url).group(1)
        next_page = re.sub("(\d+)", str(int(current_page) + 1), url)
            
        time = [s.findAll("time") for s in soup.findAll("ul", {"class": "rtddd slvl"})]
        day = [d.text for d in soup.findAll("h1", {"class": "dddd"})]
            
        for i in range(len(day)):
            time[i] = [datetime.strptime(day[i] + ' ' + t.text, '%Y / %m / %d %H:%M') for t in time[i]]

        latest_datetime = max(list(chain(*time)))
            
        links = list(chain(*[s.findAll("a") for s in soup.findAll("ul", {"class": "rtddd slvl"})]))

        for url in [link['href'] for link in links if 'micromovie' not in link['href']]:
            yield scrapy.Request(url,
                    callback=self.parse_article,
                    #dont_filter=True,
                    meta=meta)

        past = datetime.now() - timedelta(seconds=meta['days_limit'])
        if latest_datetime < past:
            return

        yield scrapy.Request(next_page,
                callback=self.parse,
                meta=meta,
                dont_filter=True)

     
    def parse_article(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        charged_bool = '每月只120元* 即可成為「升級壹會員」' in str(soup)
        response.meta['soup'] = soup
        if charged_bool==True:
            item = self.parse_charged_detail(response)
        else:
            item = self.parse_free_detail(response)
        return item

    def parse_charged_detail(self, response):
            
        def parse_content(soup):
            content = soup.find('div','ndArticle_contentBox').find('div','ndArticle_margin').find('p').text
            content = '\n'.join(content.split())
            return content
            
        def parse_author(content):
            content = content.replace('(','（')
            content = content.replace(')','）')
                
            end_indx = []
            for m in re.finditer('報導）', content):
                end_indx.append(m.start())            
                
            start_indx = []
            for m in re.finditer('（', content):
                start_indx.append(m.end())
                
            if len(end_indx)!=1 or len(start_indx)==0:
                author = ''
            else:
                find_close = end_indx[0] - np.array(start_indx)
                start_indx = start_indx[ np.where( find_close == min(find_close[find_close>0]) )[0][0] ]
                author = re.split('／',content[start_indx:end_indx[0]])[0]
            return author
            
        def parse_date(soup):
            date = soup.find('div','ndArticle_creat').text
            date = re.split('：',date)[1]  
            date = datetime.strptime(date , '%Y/%m/%d %H:%M')
            date = date + timedelta(hours=8)
            return date.strftime('%Y-%m-%dT%H:%M:%S+0800')
            
        def parse_keywords(soup):
            try:
                keywords = soup.find('div','ndgKeyword').find_all('h3')
                keywords = [x.text for x in keywords]
            except:
                keywords = ''
            return keywords

        detail_html = response.meta['soup']

    #     item = NewsItem()
    #     item['url'] = response.url
    #     title = detail_html.find('article','ndArticle_leftColumn').find('h1').text
    #     title = ' '.join(title.split())
    #     item['article_title'] = title
    #     item['metadata'] = {
    #         'keywords': parse_keywords(detail_html),
    #         'category': detail_html.find('div','ndgNav_floatList twlist').find('a','current').text
    #     }
    #     item['date'] = parse_date(detail_html)    
    #     item['content'] = parse_content(detail_html)  
    #     item['author'] = parse_author(detail_html.text)
    #     item['author_url'] = []
    #     item['comment'] = []
    #     item['media'] = 'appledaily'
    #     item['content_type'] = 0
    #     item['proto'] = 'PTT_PARSE_ITEM'
    #     return item

            
    # def parse_free_detail(self, response):
    
    #     def parse_content(soup):
    #         raw_json = soup.find_all('script',{'type':'application/javascript'})
    #         raw_json = [ r for r in raw_json if 'raw_html' in str(r)]
    #         raw_json = str(raw_json[0])
                
    #         content = re.search(r'content":"(.*?)"}', raw_json).group(1)  
    #         content = BeautifulSoup(content, 'html.parser')
    #         content = ''.join(content.text.split())
                
    #         return content
            
    #     def parse_author(content):
    #         content = content.replace('(','（')
    #         content = content.replace(')','）')
                
    #         end_indx = []
    #         for m in re.finditer('報導）', content):
    #             end_indx.append(m.start())            
                
    #         start_indx = []
    #         for m in re.finditer('（', content):
    #             start_indx.append(m.end())
                
    #         if len(end_indx)!=1 or len(start_indx)==0:
    #             author = ''
    #         else:
    #             find_close = end_indx[0] - np.array(start_indx)
    #             start_indx = start_indx[ np.where( find_close == min(find_close[find_close>0]) )[0][0] ]
    #             author = re.split('／',content[start_indx:end_indx[0]])[0]
    #         return author
            
    #     def parse_date(soup):
    #         raw_json = soup.find_all('script',{'type':'application/javascript'})
    #         raw_json = [ r for r in raw_json if 'raw_html' in str(r)]
    #         raw_json = str(raw_json[0])
    #         date = re.search(r'created_date":"(.*?)",', raw_json).group(1)  
    #         date = datetime.strptime(date.split('.')[0].split('Z')[0] , '%Y-%m-%dT%H:%M:%S')
    #         date = date + timedelta(hours=8)
    #         return date.strftime('%Y-%m-%dT%H:%M:%S+0800')
                
    #     detail_html = response.meta['soup']

    #     item = NewsItem()
    #     item['url'] = response.url
    #     item['article_title'] = ' '.join(detail_html.find('meta',{'property':'twitter:title'})['content'].split())
    #     item['metadata'] = {
    #         'keywords': detail_html.find('meta',{'name':'keywords'})['content'].split(','),
    #         'category': detail_html.find('div', {'class': re.compile(r'section-name-container section-name-container-underscore')}).find('a').text
    #     }
    #     item['date'] = parse_date(detail_html)    
    #     item['content'] = parse_content(detail_html)  
    #     item['author'] = parse_author(detail_html.text)
    #     item['author_url'] = []
    #     item['comment'] = []
    #     item['media'] = 'appledaily'
    #     item['content_type'] = 0
    #     item['proto'] = 'PTT_PARSE_ITEM'
    #     return item
