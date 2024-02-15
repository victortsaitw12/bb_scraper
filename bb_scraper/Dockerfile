FROM ubuntu:bionic
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget vim

# install firefox
RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

#FROM python:3.6
# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# install xvfb
RUN apt-get install -yqq xvfb

# set display port and dbus env to avoid hanging
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# install selenium
#RUN pip install selenium==3.8.0

RUN mkdir -p /app
WORKDIR /app
ADD . /app
RUN apt-get update -y
RUN pip3 install -r requirements.txt
# RUN pip3 install selenium
RUN pip3 install pyvirtualdisplay
# RUN pip3 install nameko
# RUN pip3 install psutil
# RUN pip3 install beautifulsoup4
# RUN pip3 install scrapy
# RUN pip3 install pymongo
#RUN pip3 install html2text
# RUN pip3 install requests 
# RUN pip3 install twisted==18.9.0 
# RUN pip3 install pytesseract
# RUN pip3 install Pillow
# RUN pip3 install ftfy
# RUN pip3 install xlwt
# RUN pip3 install pandas
RUN pip3 install --upgrade fake-useragent
# RUN pip3 install CMRESHandler
# RUN pip3 install redis
RUN pip3 install proxybroker
# RUN pip3 install --upgrade google-api-python-client
# RUN pip3 install tweepy
# RUN pip3 install plurk_oauth
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1
# CMD ["nameko", "run", "--config", "config.yml", "server"]
CMD ["python", "rountineOneAfterAnother", "--mongouri", "mongodb+srv://{account}:{password}@cluster0.peqmrlo.mongodb.net/?retryWrites=true&w=majority", "--mongodb", "pbo"]
