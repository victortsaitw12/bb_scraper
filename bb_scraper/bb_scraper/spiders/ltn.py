# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem
from selenium.common.exceptions import NoSuchElementException
import json
import re

class LtnSpider(scrapy.Spider):
    name = "ltn"

    def start_requests(self):
        url = "https://news.ltn.com.tw/ajax/breakingnews/all/1"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10, meta={"page": 1})
            
        # url = "https://estate.ltn.com.tw/article/19613"
        # yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=10)

    def parse(self, response):
        driver = response.request.meta["driver"]
        page = response.request.meta["page"]
        print("page ", page)
    
        text = driver.find_element(By.TAG_NAME, "body").text
        j_object = json.loads(text)
        follow_links = []
        # 編輯精選
        for article in j_object['data']:
            url = article["url"]
            follow_links.append(url)

        print('ltn all urls ', follow_links)

        for url in follow_links:
            time.sleep(5)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)
        
        if page < 5:
            page = page + 1
            url = f"https://news.ltn.com.tw/ajax/breakingnews/all/{page}"
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=10, meta={"page": page})

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        url = driver.current_url
        if re.search(r'estate', url):
            title = driver.find_element(By.XPATH, '//meta[@name="title"]').get_attribute('content')
            author = driver.find_element(By.CSS_SELECTOR, 'div.function.boxTitle.boxText p.author')
            # author = article.find_element(By.CSS_SELECTOR, 'p.author')
            date = author.find_element(By.CSS_SELECTOR, 'span.time').text
            content_block = driver.find_element(By.CSS_SELECTOR, 'div.text')
            content = " ".join([x.text for x in content_block.find_elements(By.TAG_NAME, 'p')])
            author = author.text
        else:
            article = driver.find_element(By.XPATH, '//div[@itemprop="articleBody"]').text
            title = article.find_element(By.TAG_NAME, 'h1').text
            date = article.find_element(By.CSS_SELECTOR, 'span.time').text
            content = " ".join([x.text for x in article.find_elements(By.TAG_NAME, 'p')])
            author = self.name
        yield PostItem(
            name=self.name,
            title=title,
            content=content,
            date=date,
            author=author,
            url=url
        )