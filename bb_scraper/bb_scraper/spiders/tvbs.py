# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem
from selenium.common.exceptions import NoSuchElementException

class EbcSpider(scrapy.Spider):
    name = "tvbs"

    def start_requests(self):
        url = "https://news.tvbs.com.tw/realtime"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)

        # url = "https://news.tvbs.com.tw/entertainment/2387860"    
        # yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse(self, response):
        driver = response.request.meta["driver"]
        time.sleep(10)
        for _ in range(0, 3):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
            time.sleep(2)

        # wait = WebDriverWait(driver, timeout=100)
        # wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, ".list > li"))

        follow_links = []
        article_block = driver.find_element(By.CSS_SELECTOR, "div.news_list > div.list")
        for artcle in article_block.find_elements(By.CSS_SELECTOR, "li"):
            # print(artcle.get_attribute('outerHTML'))
            try:
                url = artcle.find_element(By.CSS_SELECTOR, "a")
                # print(url.get_attribute('outerHTML'))
                # print(url.get_attribute("href"))
                follow_links.append(url.get_attribute("href"))
            except NoSuchElementException:
                continue

        print("TVBS urls ", follow_links)

        for url in follow_links:
            time.sleep(3)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)

    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        title = driver.find_element(By.XPATH, '//meta[@app="tvbsapp"]').get_attribute('newstitle')
        author_block = driver.find_element(By.CSS_SELECTOR, "div.author")
        author = "".join([name.text for name in author_block.find_elements(By.CSS_SELECTOR, "a")])
        date = author_block.get_attribute("textContent")        
        content = driver.find_element(By.CSS_SELECTOR, '#news_detail_div').text
        yield PostItem(
            name=self.name,
            title=title,
            content=content,
            date=date,
            author=author,
            url=driver.current_url)