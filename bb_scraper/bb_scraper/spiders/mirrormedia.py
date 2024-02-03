# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem
from selenium.common.exceptions import NoSuchElementException

class MirrormediaSpider(scrapy.Spider):
    name = "mirrormedia"

    def start_requests(self):
        url = "https://www.mirrormedia.mg/"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
            
        # url = "https://www.mirrormedia.mg/external/setn_1422582"
        # yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=10)

    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 5):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
            time.sleep(1)

        follow_links = []
        # 編輯精選
        for article in driver.find_elements(By.CSS_SELECTOR, ".GTM-editorchoice-list"):
            url = article.get_attribute("href")
            follow_links.append(url)
        # 最新文章
        for article in driver.find_elements(By.CSS_SELECTOR, ".GTM-homepage-latest-list"):
            url = article.get_attribute("href")
            follow_links.append(url)

        print('mirrormedia all urls ', follow_links)

        for url in follow_links:
            time.sleep(5)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 5):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
            time.sleep(1)
        
        category = ''
        try:
            category = driver.find_element(By.XPATH, '//meta[@property="section:name"]').get_attribute('content')
        except NoSuchElementException:
            category = ''

        if category != '' and category != '會員專區':
            date = driver.find_element(By.XPATH, '//meta[@property="article:published_time"]').get_attribute('content')
            author = driver.find_element(By.XPATH, '//meta[@property="article:author"]').get_attribute('content')
            title = driver.find_element(By.XPATH, "//article/h1")
            content = driver.find_element(By.XPATH, '//span[@data-text="true"]').text
            content += " "
            for content_block in driver.find_elements(By.XPATH, '//div[@data-contents="true"]'):
                content += content_block.text

            yield PostItem(
                name=self.name,
                title=title.text,
                content=content,
                date=date,
                author=author,
                url=driver.current_url)
        elif category == '':
            date = driver.find_element(By.CSS_SELECTOR, '[class^="external-article-info__Date"]').get_attribute("textContent")
            title = driver.find_element(By.XPATH, "//article/h1")
            try:
                content = driver.find_element(By.XPATH, '//span[@data-text="true"]').text
            except NoSuchElementException:
                content = ""
            content = " "
            content = driver.find_element(By.CSS_SELECTOR, '[class^="external-article-content"]').text

            yield PostItem(
                name=self.name,
                title=title.text,
                content=content,
                date=date,
                author=self.name,
                url=driver.current_url)
