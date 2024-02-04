# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem
from selenium.webdriver.support import expected_conditions as EC
import json
import undetected_chromedriver as uc

class RwnewsSpider(scrapy.Spider):
    name = "rwnews"

    def __init__(self):
        self.chrome = uc.Chrome()

    def start_requests(self):
        url = "https://rwnews.tw/js/viewlistnews.json"
        yield SeleniumRequest(url=url, 
                              callback=self.parse, 
                              wait_time=10
                            )


    def parse(self, response):
        driver = response.request.meta["driver"]
        text = driver.find_element(By.TAG_NAME, "body").text
        follow_links = []
        j_object = json.loads(text)
        for i, data in enumerate(j_object):
            utm_campaign = data['typemain_utm_campaign'] 
            if data['typesecond_utm_campaign'] != '' \
                and data['typesecond_utm_campaign'] != None \
                    and data['typesecond_utm_campaign'] != 'undefined':
                utm_campaign = data['typesecond_utm_campaign']
            newsUTM = '&utm_source=rwnews&utm_medium=news&utm_campaign=' + utm_campaign + '&utm_content=news'
            url = 'article.php?news=' + data['id'] + newsUTM
            follow_links.append('https://rwnews.tw/' + url)
            if i > 5:
                break
        print('rwnews all urls ', follow_links)
        for url in follow_links:
            print(url)
            self.chrome.get(url)
            time.sleep(5)
            # yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)
    # def parse_detail(self, response):
    #     driver = response.request.meta["driver"]
            title = self.chrome.find_element(By.XPATH, '//meta[@property="og:title"]').get_attribute('content')
            date = self.chrome.find_element(By.CSS_SELECTOR, ".yp_flex.art_tools_time .article_time").text
            content = self.chrome.find_element(By.CSS_SELECTOR, "#article_text").text
            yield PostItem(
                name=self.name,
                title=title,
                content=content,
                date=date,
                author=self.name,
                url=url)
        self.chrome.quit()