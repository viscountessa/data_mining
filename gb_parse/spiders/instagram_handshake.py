import scrapy
import pymongo
import requests
import datetime as dt
import json
from ..items import InstaTag, InstaPost, InstaSubject, InstaFollow2, InstaUser


class InstagramHandshakeSpider(scrapy.Spider):
    name = 'instagram_handshake'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    stop = ''
    user_list = []

    query_hash = {
        'tag_posts': "845e0309ad78bd16fc862c04ff9d8939",
        'foll': 'c76146de99bb02f6415203be841dd25a',
        'subs': 'd04b0a864b4b54837c0d870b0e77e076'
    }

    def __init__(self, login, enc_password, users_list, *args, **kwargs):
        self.login = login
        self.enc_password = enc_password
        self.start_user = users_list[0]
        self.target_user = users_list[1]
        self.target = {
            'user_id': '',
            'user_name': ''
        }

        self.limit_follow = 500
        super(InstagramHandshakeSpider, self).__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_gb_11'][self.name]

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                print('OK!')
        user_data = {
            'user_id': None,
            'user_name': None,
            'parent_id': None,
            'parent_name': None,
            'target': False,
        }
        yield response.follow(f'/{self.start_user}', callback=self.user_parse, cb_kwargs={'user_data': user_data})
        target_data = user_data.copy()
        target_data['target'] = True
        yield response.follow(f'/{self.target_user}', callback=self.user_parse, cb_kwargs={'user_data': target_data})

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])

    def user_parse(self, response, user_data):
        if self.stop != 'stop':
            user_data_extract = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
            user_data['user_id'] = user_data_extract['id']
            user_data['user_name'] = user_data_extract['username']
            foll_by = user_data_extract['edge_followed_by']['count']
            follow = user_data_extract['edge_follow']['count']
            if user_data['target']:
                self.target['user_id'] = user_data['user_id']
                self.target['user_name'] = user_data['user_name']
            else:
                if foll_by < self.limit_follow and follow < self.limit_follow:
                    if user_data['user_id'] not in self.user_list:
                        self.user_list.append(user_data['user_id'])
                        yield from self.get_f_s_user(user_data, response)

    def get_f_s_user(self, user_data, response):
        variables = {"id": user_data['user_id'],
                     "first": 100}
        url_f = f'{self.api_url}?query_hash={self.query_hash["foll"]}&variables={json.dumps(variables)}'
        if self.stop != 'stop':
            yield response.follow(url=url_f, callback=self.get_api_foll, cb_kwargs={'user_data': user_data})
        url_s = f'{self.api_url}?query_hash={self.query_hash["subs"]}&variables={json.dumps(variables)}'
        if self.stop != 'stop':
            yield response.follow(url=url_s, callback=self.get_api_subs, cb_kwargs={'user_data': user_data})

    def get_api_subs(self, response, user_data):
        subs_data = response.json()['data']['user']['edge_follow']
        if self.stop != 'stop':
            yield from self.get_subscr_item(user_data, subs_data['edges'], response)

        if subs_data['page_info']['has_next_page']:
            variables = {"id": user_data['user_id'],
                         "first": 100,
                         'after': subs_data['page_info']['end_cursor'],
                         }
            url = f'{self.api_url}?query_hash={self.query_hash["subs"]}&variables={json.dumps(variables)}'
            if self.stop != 'stop':
                yield response.follow(url=url, callback=self.get_api_subs, cb_kwargs={'user_data': user_data})

    def get_api_foll(self, response, user_data):
        foll_data = response.json()['data']['user']['edge_followed_by']
        if self.stop != 'stop':
            yield from self.get_follow_item(user_data, foll_data['edges'], response)

        if foll_data['page_info']['has_next_page']:
            variables = {"id": user_data['user_id'],
                         "first": 100,
                         'after': foll_data['page_info']['end_cursor'],
                         }
            url = f'{self.api_url}?query_hash={self.query_hash["foll"]}&variables={json.dumps(variables)}'
            if self.stop != 'stop':
                yield response.follow(url=url, callback=self.get_api_foll, cb_kwargs={'user_data': user_data})

    def get_follow_item(self, user_data, follow_user_data, response):
        for user in follow_user_data:
            if self.stop != 'stop':
                yield InstaFollow2(
                    index='follow',
                    user_id=user_data['user_id'],
                    user_name=user_data['user_name'],
                    parent_id=user_data['parent_id'],
                    parent_name=user_data['parent_name'],
                    follow_id=user['node']['id'],
                    follow_name=user['node']['username'],
                )
                udf = user_data.copy()
                udf['parent_name'] = user_data['user_name']
                udf['parent_id'] = user_data['user_id']
            if self.stop != 'stop':
                yield response.follow(f"/{user['node']['username']}", callback=self.user_parse,
                                      cb_kwargs={'user_data': udf})

    def get_subscr_item(self, user_data, subscr_user_data, response):
        for user in subscr_user_data:
            if self.stop != 'stop':
                yield InstaSubject(
                    index='subs',
                    user_id=user_data['user_id'],
                    user_name=user_data['user_name'],
                    parent_id=user_data['parent_id'],
                    parent_name=user_data['parent_name'],
                    follow_id=user['node']['id'],
                    follow_name=user['node']['username'],
                )
                uds = user_data.copy()
                uds['parent_name'] = user_data['user_name']
                uds['parent_id'] = user_data['user_id']
            if self.stop != 'stop':
                yield response.follow(f"/{user['node']['username']}", callback=self.user_parse,
                                      cb_kwargs={'user_data': uds})