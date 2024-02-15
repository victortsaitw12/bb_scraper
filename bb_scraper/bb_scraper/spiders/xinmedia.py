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

class XinmediaSpider(scrapy.Spider):
    name = "xinmedia"

    def __init__(self):
        self.chrome = uc.Chrome()

    def start_requests(self):
        url = "https://www.xinmedia.com/"
        yield SeleniumRequest(url=url, 
                              callback=self.parse, 
                              wait_time=10
                            )


    def parse(self, response):
        driver = response.request.meta["driver"]
        url = driver.current_url

        for _ in range(100):
            self.chrome.get(url)
            # for _ in range(0, 3):
            #     ActionChains(self.chrome) \
            #         .scroll_by_amount(0, 1000) \
            #         .perform()
            #     time.sleep(2)
            # self.chrome.quit()
            time.sleep(3)