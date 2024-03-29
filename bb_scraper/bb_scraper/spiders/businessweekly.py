# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class BusinessweeklySpider(scrapy.Spider):
    name = "businessweekly"

    def start_requests(self):
        url = "https://www.businessweekly.com.tw/latest?p=1"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
            
    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 3):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
        wait = WebDriverWait(driver, timeout=10)
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#LoadMore"))
        follow_links = []
        for article in driver.find_elements(By.CSS_SELECTOR, ".Article-figure"):
            # scrape the desired data from each product
            content = article.find_element(By.CSS_SELECTOR, ".Article-content")
            url = content.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            follow_links.append(url)
        
        print('businessweekly all urls ', len(follow_links))

        for url in follow_links:
            time.sleep(10)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=10)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        date = driver.find_element(By.XPATH, '//meta[@property="article:modified_time"]').get_attribute('content')
        author = driver.find_element(By.CSS_SELECTOR, ".Single-author-row-name")
        title = driver.find_element(By.CSS_SELECTOR, ".Single-title-main")
        content = driver.find_element(By.CSS_SELECTOR, ".Single-article")

        yield PostItem(
            name=self.name,
            title=title.text,
            content=content.text,
            date=date,
            author=author.text,
            url=driver.current_url)