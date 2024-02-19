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

class DcardSpider(scrapy.Spider):
    name = "dcard"

    def __init__(self):
        self.chrome = uc.Chrome()

    def start_requests(self):
        url = "https://www.dcard.tw/"
        yield SeleniumRequest(url=url, 
                              callback=self.parse, 
                              wait_time=10
                            )


    def parse(self, response):
        driver = response.request.meta["driver"]
        time.sleep(1000)