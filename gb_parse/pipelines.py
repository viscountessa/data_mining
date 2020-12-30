# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from .loaders import stopcheck, treemaker, pathfinder
db_name = 'parse_gb_hands_new'

class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb_11_2']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for img_url in item.get('images', []):
            yield Request(img_url)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        return item

class GbParseHandsh:
    def __init__(self):
        self.db = MongoClient()[db_name]

    def process_item(self, item, spider):
        if spider.name == 'handshake':
            collection = self.db[spider.name]
            if item['follow_id'] == spider.target['user_id']:
                stopcheck(item, collection, spider)
            if spider.stop == 'stop':
                if item['follow_id'] == spider.target['user_id']:
                    treemaker(collection, self.db)
                    pathfinder(self.db, spider.target)

        return item

