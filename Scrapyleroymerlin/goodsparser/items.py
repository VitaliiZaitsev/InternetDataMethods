# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
import re


def process_to_int(value):
    if value is not None:
        value = int(re.search(r'\d+', f"{value.replace(' ', '')}").group())
    return value


class GoodsparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field(input_processor=MapCompose(process_to_int), output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_to_int), output_processor=TakeFirst())
    images = scrapy.Field(input_processor=MapCompose())
    description = scrapy.Field()
    description_key = scrapy.Field(output_processor=MapCompose())
    description_item = scrapy.Field(output_processor=MapCompose())

    # 1) Взять любую категорию товаров на сайте Леруа Мерлен. Собрать с использованием ItemLoader следующие данные:
    # ● название;
    # ● все фото;
    # ● параметры товара в объявлении;
    # ● ссылка;
    # ● цена.
    #_id = scrapy.Field()
    #name = scrapy.Field()
    #link = scrapy.Field()
    #price = scrapy.Field()
    #description = scrapy.Field()
    #images = scrapy.Field()
