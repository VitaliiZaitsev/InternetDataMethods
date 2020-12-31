# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import hashlib
from scrapy.utils.python import to_bytes


class ImagesparserPipeLine(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['images']:
            for img in item['images']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'full/{item["_id"]}/{image_guid}.jpg'


class GoodsparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client['leroymerlin']

    def process_item(self, item, spider):
        t = len(item['description_key'])
        item['description'] = {}
        item['description'] = self.process_info(item['description'], item['description_key'], item['description_item'], t)
        del item['description_key']
        del item['description_item']
        self.db.collection['leroymerlin_2020_12_31'].insert_one(item)
        return item

    def process_info(self, desc_list, desc_key, desc_item, t):
        desc_list = {}
        for el in range(t):
            desc_list.update({desc_key[el].replace('\n', '').replace('  ', ''): desc_item[el].replace('\n', '').replace('  ', '')})
        return desc_list
