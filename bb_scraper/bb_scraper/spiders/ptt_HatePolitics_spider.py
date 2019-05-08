import scrapy
from datetime import datetime
import html2text
import re
import requests
from bb_scraper.items import PostItem

class PTTGossipSpider(scrapy.Spider):
    name = "ptt_hate_politics"
    board = "HatePolitics"

    def start_requests(self):
        last_page = PTTGossipSpider.getLastPage()
        url = 'https://www.ptt.cc/bbs/%s/index%s.html' % (PTTGossipSpider.board, last_page)
        yield scrapy.Request(url=url, callback=self.parse_page, cookies={'over18': '1'}, method='get')
      
    def parse_page(self, response):
        for div in response.css('div.r-ent'):
            item = {
                'push': div.css('div.nrec > span.h1::text').extract_first(),
                'title': div.css('div.title > a::text').extract_first(),
                'href': div.css('div.title > a::attr(href)').extract_first(),
                'date': div.css('div.meta > div.date ::text').extract_first(),
                'author': div.css('div.meta > div.author ::text').extract_first()
            }
            url = response.urljoin(item['href'])
            yield scrapy.Request(url, callback=self.parse_post, cookies={'over18': '1'}, method='get')

    def parse_post(self, response):
        item = PostItem()
        item['title'] = response.xpath(
            '//meta[@property="og:title"]/@content')[0].extract()
        item['author'] = response.xpath(
            '//div[@class="article-metaline"]/span[text()="作者"]/following-sibling::span[1]/text()')[
                0].extract().split(' ')[0]
        datetime_str = response.xpath(
            '//div[@class="article-metaline"]/span[text()="時間"]/following-sibling::span[1]/text()')[
                0].extract()
        item['date'] = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')

        converter = html2text.HTML2Text()
        converter.ignore_links = True
        item['content'] = converter.handle(response.xpath('//div[@id="main-content"]')[ 0].extract())

        comments = []
        total_score = 0
        for comment in response.xpath('//div[@class="push"]'):
            push_tag = comment.css('span.push-tag::text')[0].extract()
            push_user = comment.css('span.push-userid::text')[0].extract()
            push_content = comment.css('span.push-content::text')[0].extract()

            if '推' in push_tag:
                score = 1
            elif '噓' in push_tag:
                score = -1
            else:
                score = 0

            total_score += score

            comments.append({'user': push_user,
                             'content': push_content,
                             'score': score})

        item['comments'] = comments
        item['score'] = total_score
        item['url'] = response.url
        yield item

    @staticmethod
    def getLastPage():
        content = requests.get(
            url= 'https://www.ptt.cc/bbs/%s/index.html' % PTTGossipSpider.board,
            cookies={'over18': '1'}, timeout=3
        ).content.decode('utf-8')
        first_page = re.search(r'href="/bbs/%s/index(\d+).html">&lsaquo;' % PTTGossipSpider.board, content)
        if first_page is None:
            return 1
        return int(first_page.group(1)) + 1
