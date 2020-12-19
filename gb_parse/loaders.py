from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from .items import HHVacancyItem


def get_specifications_out(data):
    result = {}
    for itm in data:
        result.update(itm)
    return result


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()