# 執行方式

### 建立虛擬環境

```python3 -m venv myenv```

### 進入虛擬環境
* on Windows
```myenv\Scripts\active```
* on macOS and Linux
```source myenv/bin/activate```

### 進入 bb_scraper 資料夾
```cd bb_scraper```

### 安裝爬蟲所需要的套件
```pip install -r requirements.txt```

### 修改 scrapy-selenium middleware
1. 查看 lib path
```pip3 show scrapy-selenium```

2. 進去修改
例如路徑為
C:\Users\{account}\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12\LocalCache\local-packages\Python312\site-packages\scrapy_selenium\middlewares.py

更改如下:


    """This module contains the ``SeleniumMiddleware`` scrapy middleware"""

    from importlib import import_module

    from scrapy import signals
    from scrapy.exceptions import NotConfigured
    from scrapy.http import HtmlResponse
    from selenium.webdriver.support.ui import WebDriverWait

    from .http import SeleniumRequest

    class SeleniumMiddleware:
        """Scrapy middleware handling the requests using selenium"""

        def __init__(self, driver_name, driver_executable_path,
            browser_executable_path, command_executor, driver_arguments):
            """Initialize the selenium webdriver

            Parameters
            ----------
            driver_name: str
                The selenium ``WebDriver`` to use
            driver_executable_path: str
                The path of the executable binary of the driver
            driver_arguments: list
                A list of arguments to initialize the driver
            browser_executable_path: str
                The path of the executable binary of the browser
            command_executor: str
                Selenium remote server endpoint
            """

            webdriver_base_path = f'selenium.webdriver.{driver_name}'

            driver_klass_module = import_module(f'{webdriver_base_path}.webdriver')
            driver_klass = getattr(driver_klass_module, 'WebDriver')

            driver_options_module = import_module(f'{webdriver_base_path}.options')
            driver_options_klass = getattr(driver_options_module, 'Options')

            driver_options = driver_options_klass()

            if browser_executable_path:
                driver_options.binary_location = browser_executable_path
            for argument in driver_arguments:
                driver_options.add_argument(argument)

            driver_kwargs = {
                'executable_path': driver_executable_path,
                f'{driver_name}_options': driver_options
            }

            # locally installed driver
            if driver_executable_path is not None:
                driver_kwargs = {
                    'executable_path': driver_executable_path,
                    f'{driver_name}_options': driver_options
                }
                self.driver = driver_klass(**driver_kwargs)
            # remote driver
            elif command_executor is not None:
                from selenium import webdriver
                capabilities = driver_options.to_capabilities()
                self.driver = webdriver.Remote(command_executor=command_executor,
                                            desired_capabilities=capabilities)
            # webdriver-manager
            else:
                # selenium4+ & webdriver-manager
                from selenium import webdriver
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                if driver_name and driver_name.lower() == 'chrome':
                    # options = webdriver.ChromeOptions()
                    # options.add_argument(o)
                    self.driver = webdriver.Chrome(options=driver_options,
                                                service=ChromeService(ChromeDriverManager().install()))

        @classmethod
        def from_crawler(cls, crawler):
            """Initialize the middleware with the crawler settings"""

            driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
            driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
            browser_executable_path = crawler.settings.get('SELENIUM_BROWSER_EXECUTABLE_PATH')
            command_executor = crawler.settings.get('SELENIUM_COMMAND_EXECUTOR')
            driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')

            if driver_name is None:
                raise NotConfigured('SELENIUM_DRIVER_NAME must be set')

            # let's use webdriver-manager when nothing specified instead | RN just for Chrome
            if (driver_name.lower() != 'chrome') and (driver_executable_path is None and command_executor is None):
                raise NotConfigured('Either SELENIUM_DRIVER_EXECUTABLE_PATH '
                                    'or SELENIUM_COMMAND_EXECUTOR must be set')

            middleware = cls(
                driver_name=driver_name,
                driver_executable_path=driver_executable_path,
                browser_executable_path=browser_executable_path,
                command_executor=command_executor,
                driver_arguments=driver_arguments
            )

            crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

            return middleware

        def process_request(self, request, spider):
            """Process a request using the selenium driver if applicable"""

            if not isinstance(request, SeleniumRequest):
                return None

            self.driver.get(request.url)

            for cookie_name, cookie_value in request.cookies.items():
                self.driver.add_cookie(
                    {
                        'name': cookie_name,
                        'value': cookie_value
                    }
                )

            if request.wait_until:
                WebDriverWait(self.driver, request.wait_time).until(
                    request.wait_until
                )

            if request.screenshot:
                request.meta['screenshot'] = self.driver.get_screenshot_as_png()

            if request.script:
                self.driver.execute_script(request.script)

            body = str.encode(self.driver.page_source)

            # Expose the driver via the "meta" attribute
            request.meta.update({'driver': self.driver})

            return HtmlResponse(
                self.driver.current_url,
                body=body,
                encoding='utf-8',
                request=request
            )

        def spider_closed(self):
            """Shutdown the driver when spider is closed"""

            self.driver.quit()



### 執行爬蟲程式
```python --mongouri={mongoDB uri} --mongodb={database} rountineOneAfterAnother.py```

### 離開虛擬環境
```deactivate```


# 網站對應一覽表
| 網站名稱  | 程式檔名  |
| -------- | --------- |
| 中廣 | bccnews.py |
| 商周 | businessweekly.py |
| 東森新聞 | ebc.py |
| 自由時報 | ltn.py |
| 鏡周刊 | mirrormedia.py |
| 今日新聞 | nownews.py |
| PTT八卦版 | ptt_gossip_spider.py |
| PTT黑特版 | ptt_HatPolitics_spider.py |
| 菱傳媒 | rwnews.py |
| 風傳媒 | storm.py |
| TVBS | tvbs.py |



