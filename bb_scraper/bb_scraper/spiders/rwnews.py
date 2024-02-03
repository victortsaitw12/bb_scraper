# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem
from selenium.webdriver.support import expected_conditions as EC

class RwnewsSpider(scrapy.Spider):
    name = "rwnews"

    def start_requests(self):
        url = "https://rwnews.tw/index.php?type=2"
        yield SeleniumRequest(url=url, 
                              callback=self.parse, 
                              wait_time=10
                            #   wait_until=EC.element_to_be_clickable((By.ID, 'pageButtonNext'))
                            )
            
    def parse(self, response):
        driver = response.request.meta["driver"]
        time.sleep(100)
        # wait = WebDriverWait(driver, timeout=10)
        # wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#pageButtonNext"))

        # for _ in range(0, 3):
        #     ActionChains(driver) \
        #         .scroll_by_amount(0, 1000) \
        #         .perform()
        # wait = WebDriverWait(driver, timeout=10)
        # wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#pageButtonNext"))

        # follow_links = []
        # article_block = driver.find_element(By.CSS_SELECTOR, "ul.cat_list_le_l")
        # for link in article_block.find_elements(By.CSS_SELECTOR, "li > a"):
        #     url = link.get_attribute("href")
        #     follow_links.append(url)

        # print('rwnews all urls ', follow_links)
        # for url in follow_links:
        #     time.sleep(3)
        #     yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)
