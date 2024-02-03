# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class EbcSpider(scrapy.Spider):
    name = "ebc"

    def start_requests(self):
        url = "https://news.ebc.net.tw/realtime"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
            
    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 5):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
            time.sleep(1)
        wait = WebDriverWait(driver, timeout=5)
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, ".white-btn"))

        follow_links = []
        article_block = driver.find_element(By.CSS_SELECTOR, ".news-list-box")
        for article in article_block.find_elements(By.CSS_SELECTOR, ".white-box"):
            url = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            follow_links.append(url)

        print('ebc all urls ', len(follow_links))

        for url in follow_links:
            time.sleep(5)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        content_block = driver.find_element(By.CSS_SELECTOR, "#main_content")
        info_block = content_block.find_element(By.CSS_SELECTOR, ".info")
        info = info_block.find_element(By.CSS_SELECTOR, ".small-gray-text")
        title = content_block.find_element(By.TAG_NAME, "h1")
        content = content_block.find_element(By.CSS_SELECTOR, ".raw-style")

        yield PostItem(
            name=self.name,
            title=title.text,
            content=content.text,
            date=info.text,
            author=info.text,
            url=driver.current_url)