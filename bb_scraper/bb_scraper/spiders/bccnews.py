# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class BbcNewsSpider(scrapy.Spider):
    name = "bccnews"

    def start_requests(self):
        url = "https://bccnews.com.tw/archives/category/%e5%8d%b3%e6%99%82"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)

    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 3):
            ActionChains(driver) \
                .scroll_by_amount(0, 1100) \
                .perform()
            time.sleep(3)
        wait = WebDriverWait(driver, timeout=5)
        wait.until(lambda driver: driver.find_element(By.XPATH, "//a[@aria-label='next-page']"))
        follow_links = []
        for article in driver.find_elements(By.CSS_SELECTOR, ".td-module-container"):
            content = article.find_element(By.CSS_SELECTOR, ".td-module-thumb")
            url = content.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            follow_links.append(url)

        print('bccnews all urls ', len(follow_links))

        for url in follow_links:
            time.sleep(5)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        date = driver.find_element(By.XPATH, '//meta[@property="article:modified_time"]').get_attribute('content')
        title = driver.find_element(By.CSS_SELECTOR, ".tdb-title-text")
        content = driver.find_element(By.XPATH, "//div[contains(@class,'tdb_single_content')]/div[contains(@class, 'tdb-block-inner')]")

        yield PostItem(
            name=self.name, 
            title=title.text, 
            content=content.text,
            date=date,
            author=self.name,
            url=driver.current_url)