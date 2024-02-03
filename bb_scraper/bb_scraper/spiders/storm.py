# -*- coding: utf-8 -*-

import scrapy
from scrapy_selenium import SeleniumRequest
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bb_scraper.items import PostItem

class StormSpider(scrapy.Spider):
    name = "storm"

    def start_requests(self):
        url = "https://www.storm.mg/articles"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)
            
    def parse(self, response):
        driver = response.request.meta["driver"]
        for _ in range(0, 3):
            ActionChains(driver) \
                .scroll_by_amount(0, 1000) \
                .perform()
        wait = WebDriverWait(driver, timeout=10)
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#next"))

        follow_links = []

        for article in driver.find_elements(By.CSS_SELECTOR, ".category_card"):
            url = article.find_element(By.CSS_SELECTOR, ".card_link").get_attribute("href")
            follow_links.append(url)

        print('storm all urls ', follow_links)

        # Go to 2 page
        # driver.find_element(By.CSS_SELECTOR, "#next").click()
        # for article in driver.find_elements(By.CSS_SELECTOR, ".category_card"):
        #     url = article.find_element(By.CSS_SELECTOR, ".card_link").get_attribute("href")
        #     follow_links.append(url)

        for url in follow_links:
            time.sleep(3)
            yield SeleniumRequest(url=url, callback=self.parse_detail, wait_time=5)


    def parse_detail(self, response):
        driver = response.request.meta["driver"]
        date = driver.find_element(By.XPATH, '//meta[@itemprop="datePublished"]').get_attribute('content')
        author = driver.find_element(By.XPATH, '//meta[@property="dable:author"]').get_attribute('content')
        title = driver.find_element(By.CSS_SELECTOR, '#article_title').text
        content = driver.find_element(By.CSS_SELECTOR, '.article_content_inner').text
        yield PostItem(
            name=self.name,
            title=title,
            content=content,
            date=date,
            author=author,
            url=driver.current_url)