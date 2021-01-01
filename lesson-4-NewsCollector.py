#!/usr/bin/env python

__author__ = "Зайцев Виталий Владимирович, Vitalii Zaitsev"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Vitalii Zaitsev"
__email__ = "vvzaisev79@gmail.com"
__status__ = "Education"


# Курс "Методы сбора и обработки данных из сети Интернет"
# Урок 4. Парсинг HTML. XPath

# 1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2. Сложить собранные данные в БД


# -------------------------------------------------------------------------------------
# Комментарии по реализации:
# 1. Цель приложения: снять моментальный новостной слепок с main страниц новостных ресурсов
# Полагаю, что чем меньше запросов к ресурсу, тем лучше
# 2. Один ресурс НЕ имеет дата публикации новости на главной странице, потребуется пройти по детальным страницам новостей
# https://news.mail.ru/ - на main странице НЕТ даты времени публикации (дата есть на детальной странице новости)
# https://lenta.ru/ - на main странице ЕСТЬ дата публикации новости
# https://yandex.ru/news - на main странице ЕСТЬ дата публикации новости
# 3. Особых условий на сбор данных в БД нет - используем Монго базу, коллекция по дате-времени запуска


from datetime import datetime
from pymongo import MongoClient
import requests
from lxml import html


def mailru_news_snapshot():
    mailru_news_list = []
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        url = 'https://news.mail.ru/'
        response = requests.get(url, headers=header)
        dom = html.fromstring(response.text)

        # у news.mail.ru новости оформлены несколькими подразновидностями блоков
        # соберём самые заметные
        detailed_news_pagelinks_list = dom.xpath("//a[contains(@class,'js-topnews__item')]/@href")
        detailed_news_pagelinks_list = detailed_news_pagelinks_list + dom.xpath("//a[@class='list__text']/@href")

        for news_pagelink in detailed_news_pagelinks_list:
            news = {}
            response = requests.get(news_pagelink, headers=header)
            dom = html.fromstring(response.text)

            # Mail.ru - агрегатор
            # поэтому Mail.ru + source источника новости
            source = 'Mail.ru News -> ' + dom.xpath("//a[contains(@class,'breadcrumbs__link')]/span/text()")[0]

            datetime = dom.xpath("//span[contains(@class,'note__text')]/@datetime")[0]
            title = dom.xpath("//h1/text()")[0]

            news['source'] = source
            news['title'] = title
            news['link'] = news_pagelink
            news['publication_date'] = datetime

            mailru_news_list.append(news)
        return mailru_news_list
    except Exception as e:
        print(e)


def yandex_news_snapshot():
    yandex_news_list = []
    try:
        url = 'https://yandex.ru/news/'
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        response = requests.get(url, headers=header)
        dom = html.fromstring(response.text)
        headline_sections_list = dom.xpath("//div[contains(@class,'news-top-stories')]//article")

        for headline_section in headline_sections_list:
            news = {}
            # Яндекс - агрегатор
            # поэтому source - это не просто 'Яндекс', а также указываем source из источника новости
            source = 'Яндекс News -> ' + headline_section.xpath(".//a/text()")[0]
            title = headline_section.xpath(".//h2/text()")[0]
            link = headline_section.xpath(".//a/@href")[0]

            # у яндекса - только время, даты нет 8-/
            # надо ли подсыпать Now дату?
            # ок, пусть будет только время
            publication_date = headline_section.xpath(".//span[@class='mg-card-source__time']/text()")[0]

            news['source'] = source
            news['title'] = title
            news['link'] = link
            news['publication_date'] = publication_date

            yandex_news_list.append(news)
        return yandex_news_list
    except Exception as e:
        print(e)


def lenta_news_snapshot():
    lenta_news_list = []
    try:
        url = 'https://lenta.ru/'
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        response = requests.get(url, headers=header)
        dom = html.fromstring(response.text)

        # Специфика lenta.ru: ссылки на новости начинаются с /
        # поэтому отбрасываем / у 'https://lenta.ru/'
        url = url[:-1]

        # Вот здесь любопытно:
        # 1) кто-то идёт по структуре
        #headline_sections_list = dom.xpath("//section[contains(@class, 'b-top7-for-main')]/div/div[contains(@class, 'item')]//a[@href and ./time]")
        # 2) на разборе ДЗ был дан хороший пример по спец классу //time[@class='g-time']/../..
        #headline_sections_list = dom.xpath("//time[@class='g-time']/../..")
        # 3) и даже вот такой мини xpath вполне себе рабочий
        headline_sections_list = dom.xpath("//a[./time]")

        for headline_section in headline_sections_list:
            news = {}
            title = headline_section.xpath("./text()")
            link = headline_section.xpath("./@href")
            publication_date = headline_section.xpath("./time/@datetime")

            news['source'] = 'Lenta.ru'
            news['title'] = title[0].replace('\xa0', ' ')

            # Вот здесь интересно: возможны ссылки на другие внешние источники-новости
            # Видимо, это настраивается через GTM
            # Такие новости появляются нерегулярно
            # Обработаем этот кейс: если наш линк начинается с 'http' то считаем его внешней ссылкой
            # иначе конструируем путь из лента-урла и лента-относительной ссылки
            if link[0][:4] != 'http':
                news['link'] = f"{url}{link[0]}"
            else:
                news['link'] = link[0]

            news['publication_date'] = publication_date[0]
            lenta_news_list.append(news)
        return lenta_news_list
    except Exception as e:
        print(e)


# -----------------------------
# Конец секции описания функций
# -----------------------------

# Базовые настройки подключения к Монго, каждый раз уникальная коллекция по дате-времени запуска
client = MongoClient('localhost', 27017)
db = client['News_snapshot_db']
collection = db[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

# Свои обработчики на каждый новостной ресурс, здесь просто заливаем в базу
# если что-то упало - зовём разработчика )))))
collection.insert_many(yandex_news_snapshot())
collection.insert_many(mailru_news_snapshot())
collection.insert_many(lenta_news_snapshot())
