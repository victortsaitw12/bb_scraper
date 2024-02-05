# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class NownewsSpider(scrapy.Spider):
    name = "nownews"

    def start_requests(self):
        url = "https://www.nownews.com/cat/breaking/"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=5)


    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 8):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
        wait = WebDriverWait(driver, timeout=5)
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#moreNews"))

        driver.find_element(By.CSS_SELECTOR, "#moreNews").click()
        time.sleep(5)
        follow_links = []
        for list_block in driver.find_elements(By.CSS_SELECTOR, ".listBlk"):
            for link in list_block.find_elements(By.TAG_NAME, "li"):
                url = link.find_element(By.TAG_NAME, "a").get_attribute("href")
                follow_links.append(url)

        print('nownews all urls ', follow_links)

      
        for url in follow_links:
            time.sleep(3)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        date = driver.find_element(By.XPATH, '//meta[@itemprop="dateCreated"]').get_attribute('content')
        title = driver.find_element(By.XPATH, '//meta[@itemprop="alternativeHeadline"]').get_attribute('content')
        author = driver.find_element(By.XPATH, '//a[@data-sec="reporter"]').text
        
        content_block = driver.find_element(By.XPATH, '//article[@itemprop="articleBody"]')
        driver.execute_script('''
            var parent = arguments[0];
            var elements = parent.querySelectorAll('div.related-item');
            elements.forEach(function(element) {
                element.remove();
            });
        ''', content_block)
        content = content_block.text

        yield PostItem(
            name=self.name,
            title=title,
            content=content,
            date=date,
            author=author,
            url=driver.current_url)