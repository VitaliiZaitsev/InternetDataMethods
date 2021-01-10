import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']

    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    #inst_login = 'onliskill_udm'
    #inst_password = '#PWD_INSTAGRAM_BROWSER:10:1609263010:ATJQAPqKmtGZ19Fn4BZ/v+eELkPeTQQlk9gkHv7EDI9INjpa27aGhsoTI+zCVETPoE3wd7unPgHAvWDBF3ppF5XHm6syn2lY1Y8OkAIH3zu90Ph20xK5eLO9Y4TQJktQUnu8PgxOwtJMJvnszA=='
    # Предоставленные креды НЕ работают
    # Личные креды использовать не хочу
    # Создал новый аккаунт, работает
    # креды от аккаунта - здесь фейковые, настоящие креды доступны в моей папке курса
    inst_login = 'secret'
    inst_password = 'secret'

    # parse_user = 'ai_machine_learning'
    #parse_user_list = ['ai_machine_learning']

    # пара открытых инстааккаунтов любителей котиков
    # https://www.instagram.com/maengsooon/
    # https://www.instagram.com/catvacay_/
    parse_user_list = ['maengsooon', 'catvacay_']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '003056d32c2554def87228bc3fd9668a'

    # хеши "подсмотрел" из своих запросов
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback= self.user_login,
            formdata={'username': self.inst_login, 'enc_password':self.inst_password},
            headers= {'X-CSRFToken':csrf_token}
        )

    def user_login(self, response:HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            # точка развилки #1
            # в цикле for будем вызывать yield response.follow для каждого пользователя
            # из списка target пользователей
            for parse_user in self.parse_user_list:
                yield response.follow(
                    f'/{parse_user}',
                    callback= self.user_data_parse,
                    cb_kwargs={'username': parse_user}
                )


    def user_data_parse(self, response:HtmlResponse, username):
        # точка развилки #2
        # собираем followers и following для username
        # query_hash=followers_hash - запускаем метод 1
        # query_hash=following_hash - запускаем метод 2

        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id, 'first': 12}

        #url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'

        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )
        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )
        #yield response.follow(
        #    url_posts,
        #    callback=self.user_posts_parse,
        #    cb_kwargs={'username':username,
        #               'user_id': user_id,
        #               'variables': deepcopy(variables)}
        #)

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        # ------------
        # folloWERS!!!
        # ------------
        #     target_user = scrapy.Field() #целевой пользователь, для которого собираем информацию
        #     target_user_id = scrapy.Field() #id целевого пользователя
        #     f_user = scrapy.Field() #имя follower/following
        #     _id = scrapy.Field() #follower/following ID
        #     f_photo_link = scrapy.Field() #линк на follower/following photo
        #
        #     # отношение целевой пользователь с f_пользователем
        #     # с точки зрения целевой пользователь target_user
        #     # followers: target_user имеет этого f_user в подписчиках
        #     # following: target_user сам подписан на f_user
        #     target_user_to_f_user_relation = scrapy.Field()

        j_data = response.json()
        # folloWERS!!!
        # Внимание к структуре
        # {data: {user: {edge_followed_by: {count: 209, page_info: {has_next_page: true,…},…}}}, status: "ok"}
        # data: {user: {edge_followed_by: {count: 209, page_info: {has_next_page: true,…},…}}}
        # user: {edge_followed_by: {count: 209, page_info: {has_next_page: true,…},…}}
        # edge_followed_by: {count: 209, page_info: {has_next_page: true,…},…}
        # count: 209
        # edges: [{node: {id: "1633193638", username: "alenasnake996", full_name: "Алена Ламкова",…}},…]
        # page_info: {has_next_page: true,…}
        # status: "ok"

        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')

            url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )


        followers_list = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers_list:
            item = InstaparserItem(
                # folloWERS!!!
                target_user = username,
                target_user_id = user_id,
                _id = follower.get('node').get('id'),
                f_user = follower.get('node').get('username'),
                f_photo_link = follower.get('node').get('profile_pic_url'),
                #     # followers: target_user имеет этого f_user в подписчиках
                #     # following: target_user сам подписан на f_user
                target_user_to_f_user_relation = 'followers'
            )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        # ------------
        # folloWING!!!
        # ------------
        #     target_user = scrapy.Field() #целевой пользователь, для которого собираем информацию
        #     target_user_id = scrapy.Field() #id целевого пользователя
        #     f_user = scrapy.Field() #имя follower/following
        #     _id = scrapy.Field() #follower/following ID
        #     f_photo_link = scrapy.Field() #линк на follower/following photo
        #
        #     # отношение целевой пользователь с f_пользователем
        #     # с точки зрения целевой пользователь target_user
        #     # followers: target_user имеет этого f_user в подписчиках
        #     # following: target_user сам подписан на f_user
        #     target_user_to_f_user_relation = scrapy.Field()

        j_data = response.json()
        # folloWING!!!
        # Внимание к структуре
        # {data: {user: {edge_follow: {count: 248, page_info: {has_next_page: true,…},…}}}, status: "ok"}
        # data: {user: {edge_follow: {count: 248, page_info: {has_next_page: true,…},…}}}
        # user: {edge_follow: {count: 248, page_info: {has_next_page: true,…},…}}
        # edge_follow: {count: 248, page_info: {has_next_page: true,…},…}
        # count: 248
        # edges: [{node: {id: "518234568", username: "stylist.fm", full_name: "КРИСТИНА",…}},…]
        # page_info: {has_next_page: true,…}
        # status: "ok"

        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')

            # following_hash!!!!
            url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            # user_following_parse!!!
            yield response.follow(
                url_posts,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        following_list = j_data.get('data').get('user').get('edge_follow').get('edges')
        for follower in following_list:
            item = InstaparserItem(
                # folloWING!!!
                target_user=username,
                target_user_id=user_id,
                _id=follower.get('node').get('id'),
                f_user=follower.get('node').get('username'),
                f_photo_link=follower.get('node').get('profile_pic_url'),
                #     # followers: target_user имеет этого f_user в подписчиках
                #     # following: target_user сам подписан на f_user
                target_user_to_f_user_relation='following'
            )
            yield item


    #def user_posts_parse(self, response:HtmlResponse, username, user_id, variables):
    #    j_data = response.json()
    #    page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
    #    if page_info.get('has_next_page'):
    #        variables['after'] = page_info.get('end_cursor')

    #        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
    #        yield response.follow(
    #            url_posts,
    #            callback=self.user_posts_parse,
    #            cb_kwargs={'username': username,
    #                       'user_id': user_id,
    #                       'variables': deepcopy(variables)}
    #        )

    #    posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
    #    for post in posts:
    #        item = InstaparserItem(
    #            user_id = user_id,
    #            photo = post.get('node').get('display_url'),
    #            likes = post.get('node').get('edge_media_preview_like').get('count'),
    #            post_data = post.get('node')
    #        )
    #        yield item

    # #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')