### 建立虛擬環境

```python3 -m venv myenv```

### 進入虛擬環境
* on Windows
```myenv\Scripts\active```
* on macOS and Linux
```source myenv/bin/activate```

### 安裝爬蟲所需要的套件
```pip install -r requirements.txt```

### 修改 scrapy-selenium middleware
1. 查看 lib path
```pip3 show scrapy-selenium```

2. 進去修改
例如路徑為C:\Users\{account}\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12\LocalCache\local-packages\Python312\site-packages\scrapy_selenium\middlewares.py
```

```

### 執行爬蟲程式
```python --mongouri={mongoDB uri} --mongodb={database} rountineOneAfterAnother.py```

### 離開虛擬環境
```deactivate```
