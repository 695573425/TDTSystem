# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import  Request

from weibosearch.items import FoodItem

class FoodSpider(scrapy.Spider):
    name = 'food'
    allowed_domains = ['down.foodmate.net']
    start_url = 'http://down.foodmate.net/d/keywords_standard.php'

    def start_requests(self):
        for i in range(1262):
            url = '{url}?page={id}'.format(url=self.start_url, id=str(i+1))
            yield Request(url, callback=self.parse)



    def parse(self, response):

        tbody = response.xpath('//td[@width="20%"]')
        for td in tbody:
            data = td.xpath('.//text()').extract()
            key = data[0]
            num = int(re.search("\d+", data[1]).group())
            print(key, num)

            food_item = FoodItem()
            for field in food_item.fields:
                try:
                    food_item[field] = eval(field)
                except NameError:
                    self.logger.debug('Field is Not Defined' + field)
            yield food_item

