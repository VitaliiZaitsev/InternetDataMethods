# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект
    # нужно извлечь имя, id, фото (остальные данные по желанию).
    # (Фото скачивать НЕ будем)

    target_user = scrapy.Field() #целевой пользователь, для которого собираем информацию
    target_user_id = scrapy.Field() #id целевого пользователя
    f_user = scrapy.Field() #имя follower/following
    _id = scrapy.Field() #follower/following ID
    f_photo_link = scrapy.Field() #линк на follower/following photo

    # отношение целевой пользователь с f_пользователем
    # с точки зрения целевой пользователь target_user
    # followers: target_user имеет этого f_user в подписчиках
    # following: target_user сам подписан на f_user
    target_user_to_f_user_relation = scrapy.Field()

    #user_id = scrapy.Field()
    #photo = scrapy.Field()
    #likes = scrapy.Field()
    #post_data = scrapy.Field()

