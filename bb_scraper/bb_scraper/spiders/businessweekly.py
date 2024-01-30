import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
import time
from selenium.webdriver.common.by import By

class BusinessweeklySpider(scrapy.Spider):
    name = "businessweekly"

    def start_requests(self):
        url = "https://www.businessweekly.com.tw/latest?p=1"
        yield SeleniumRequest(url=url, callback=self.parse)
      
    def parse(self, response):
        driver = response.request.meta["driver"]
        # scroll to the end of the page 10 times
        for x in range(0, 10):
            # scroll down by 10000 pixels
            ActionChains(driver) \
                .scroll_by_amount(0, 10000) \
                .perform()

            # waiting 2 seconds for the products to load
            time.sleep(2)

        # select all product elements and iterate over them
        for product in driver.find_elements(By.CSS_SELECTOR, ".Article-figure"):
            # scrape the desired data from each product
            content = product.find_element(By.CSS_SELECTOR, ".Article-content")
            url = content.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            title = content.text
            author = product.find_element(By.CSS_SELECTOR, ".Article-author").text
            created_dt = product.find_element(By.CSS_SELECTOR, ".Article-date").text

            # add the data to the list of scraped items
            yield {
                "url": url,
                "title": title,
                "author": author,
                "date": created_dt
            }