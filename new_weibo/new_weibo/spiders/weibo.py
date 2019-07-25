# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com', 'weibo.cn', 's.weibo.com']


    def __init__(self, keyword=None, start_page=None, end_page=None, sort=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        try:
            self.start_page = int(start_page)
        except:
            self.start_page = None
        try:
            self.end_page = int(end_page)
        except:
            self.end_page = None
        self.sort = sort
        pass

    def start_requests(self):
        if not self.keyword:
            self.keyword = '食品安全'
        if not self.start_page:
            self.start_page = 1
        if not self.end_page:
            self.end_page = 200
        if self.end_page < self.start_page:
            self.end_page = self.start_page
        if not self.sort or (self.sort != 'time' and self.sort != 'hot'):
            self.sort = 'hot'

        # url = 'https://s.weibo.com/weibo?q={keyword}&xsort={sort}'.format(keyword=self.keyword, sort=self.sort)
        url = 'https://s.weibo.com/'
        print(url)
        yield Request(url, callback=self.parse)

    def parse(self, response):

        content = ''.join(response.xpath('//text()').extract())
        print(content)

    def parse_index(self, response):
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        for weibo in weibos:
            if bool(weibo.xpath('.//span[@class="cmt"]').extract_first()):
                detail_url = weibo.xpath('.//a[contains(., "原文评论[")]//@href').extract_first()
                yield Request(detail_url, callback=self.parse_detail)
                continue
            id = weibo.xpath('./@id').extract_first()
            id = re.search('M_([a-zA-Z0-9]+)', id).group(1)
            content = ''.join(weibo.xpath('.//text()').extract())
            content = re.search('.*?:(.*?)\xa0', content).group(1)
            comment_count = int(weibo.xpath('.//a[contains(., "评论[")]//text()').re_first('评论\[(.*?)\]', default=0))
            forward_count = int(weibo.xpath('.//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]', default=0))
            like_count = int(weibo.xpath('.//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]', default=0))
            posted_at = weibo.xpath('.//span[@class="ct"]//text()').extract_first(default=None)
            username = weibo.xpath('.//a[@class="nk"]/text()').extract_first(default=None)
            uid = weibo.xpath('.//a[@class="nk"]/@href').re_first('weibo.cn/(.*)', default=None)
            is_v = bool(weibo.xpath('.//img[@alt="V"]').extract_first())
            is_vip = bool(weibo.xpath('.//img[@alt="M"]').extract_first())
            # print(id, content, comment_count, forward_count, like_count, posted_at, username, uid, is_v, is_vip)
            weibo_item = WeiboItem()
            for field in weibo_item.fields:
                try:
                    weibo_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield weibo_item