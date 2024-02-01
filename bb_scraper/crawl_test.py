import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait

import time

service = Service("C:\Windows\chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://www.businessweekly.com.tw/latest?p=1")

def loadPage():
    for x in range(0, 5):
        # scroll down by 10000 pixels
        ActionChains(driver) \
            .scroll_by_amount(0, 500) \
            .perform()
        time.sleep(5)
        print('wait')

for x in range(0, 10):
    loadPage()
    # wait = WebDriverWait(driver, timeout=10)
    # wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#LoadMore").is_displayed())
    print('click')
    load_more = driver.find_element(By.CSS_SELECTOR, "#LoadMore")
    driver.execute_script("$(arguments[0]).click()", load_more)
    time.sleep(10)

# driver.quit()



