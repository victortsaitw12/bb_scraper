# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class RwnewsSpider(scrapy.Spider):
    name = "rwnews"

    def start_requests(self):
        url = "https://rwnews.tw/index.php?type=2"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
            
    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 3):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
        wait = WebDriverWait(driver, timeout=10)
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#pageButtonNext"))