# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

'''class HHVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()'''

class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstaTag(Insta):
    pass


class InstaPost(Insta):
    pass


class InstaUser(Insta):
    pass


class InstaFollow(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    follow_name = scrapy.Field()
    follow_id = scrapy.Field()