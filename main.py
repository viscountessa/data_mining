import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.auto_parse import AutoParseSpider
from gb_parse.spiders.instagram import InstagramSpider
from gb_parse.spiders.instagram_handshake import InstagramHandshakeSpider

import dotenv

# from gb_parse import settings
dotenv.load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramHandshakeSpider, login=os.getenv('LOGIN'), enc_password=os.getenv('PASSWORD'), users_list=['viscountessa_studio', 'yurydud'])
    crawl_proc.start()
