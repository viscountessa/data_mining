import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoYoulaItem, HHVacancyItem

# from .items import InstTagItem, InstDataItem


def get_autor(js_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, js_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


def get_specifications(itm):
    tag = Selector(text=itm)
    result = {tag.css('.AdvertSpecs_label__2JHnS::text').get(): tag.css(
        '.AdvertSpecs_data__xK2Qx::text').get() or tag.css('a::text').get()}
    return result


def specifications_out(data: list):
    result = {}
    for itm in data:
        result.update(itm)
    return result


class AutoYoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_out = TakeFirst()
    autor_in = MapCompose(get_autor)
    autor_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = specifications_out


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()


# for handshake

def stopcheck(item, collection, spider):
    if item['index'] == 'follow':
        if collection['subs'].find({'user_id': item['user_id'], 'follow_id': item['follow_id']}).count() != 0:
            spider.stop = 'stop'
    elif item['index'] == 'subs':
        if collection['follow'].find({'user_id': item['user_id'], 'follow_id': item['follow_id']}).count() != 0:
            spider.stop = 'stop'

def treemaker(collection, db):
    data = collection['follow'].find()
    user_node_list = set()
    for i in data:
        user_node_list.add(i['user_id'])

    for user in user_node_list:
        f = collection['follow'].find({'user_id': user})
        s = collection['subs'].find({'user_id': user})
        f_list = [el1['follow_id'] for el1 in f]
        itog = [el2['follow_id'] for el2 in s if el2['follow_id'] in f_list]
        coll = db['tree']
        user_data = collection['follow'].find_one({'user_id': user})
        item = {
            'user_id': user,
            'user_name': user_data['user_name'],
            'parent_id': user_data['parent_id'],
            'parent_name': user_data['parent_name'],
            'handsh': itog
        }
        coll.insert_one(item)

def pathfinder(db, target):
    coll = db['tree']
    find_path = db['path']
    def pather(id, coll):
        user = coll.find_one({'user_id': id})
        if user['parent_id'] is not None:
            path.append(
                {
                    'user_id': user['user_id'],
                    'user_name': user['user_name']
                }
            )
            pather(user['parent_id'], coll)
        else:
            path.append(
                {
                    'user_id': user['user_id'],
                    'user_name': user['user_name']
                }
            )
    data = coll.find()
    path = []
    for user in data:
        if target['user_id'] in user['handsh']:
            path.append(
                {
                    'user_id': target['user_id'],
                    'user_name': target['user_name']
                }
            )
            pather(user['user_id'], coll)
            path.reverse()
            break
    find_path.insert_one({'path':path})