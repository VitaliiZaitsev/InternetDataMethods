#!/usr/bin/env python

__author__ = "Зайцев Виталий Владимирович, Vitalii Zaitsev"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Vitalii Zaitsev"
__email__ = "vvzaisev79@gmail.com"
__status__ = "Education"


# Курс "Методы сбора и обработки данных из сети Интернет"
# Урок 3. Системы управления базами данных MongoDB и SQLite в Python

# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, з
# аписывающую собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# Поиск должен происходить по 2-ум полям (минимальной и максимальной зарплате)
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.


# -------------------------------------------------------------------------------------
# Комментарии по реализации:
# - новая ветка lesson-3
# - копипаст парсинга из предыдущего урока lesson-2
# - добавлены +мин салари и макс салари, валюта
# - добавлен id, берём НЕ из урла, а из data аттрибута
# - подключён Монго
# - запись в Монго: по update_many с upsert=True, повторный запуск производит только дозапись новых позиций
# - добавлена функция поиска вакансий по зарплате


from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
from pymongo import MongoClient
import re

# ---------------------------------------------------------------------
# Функция сбора позиций с hh
# ---------------------------------------------------------------------
def hh_vacancies_collect(main_url, vacancy_search_str, page_count):

    # пустой список позиций, его будем наполнять
    vacancies = []

    # делаем запрос и обрабатываем выдачу, наполняем список позиций
    # запрашиваем page_count страниц, поэтому на каждой текущей странице придётся парсить кнопку перехода на следующие страницы
    # и придётся постить новые запросы

    # делаем первый запрос
    # на основе примера поисковой строки
    # https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=html-%D0%B2%D0%B5%D1%80%D1%81%D1%82%D0%B0%D0%BB%D1%8C%D1%89%D0%B8%D0%BA

    # &only_with_salary=true
    # https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=html-%D0%B2%D0%B5%D1%80%D1%81%D1%82%D0%B0%D0%BB%D1%8C%D1%89%D0%B8%D0%BA

    # представляемся Google Chrome
    headers = {'User-agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    # постим реквест
    html = requests.get(
        main_url + '/search/vacancy?clusters=true&enable_snippets=true&text=' + vacancy_search_str + '&only_with_salary=true&st=searchVacancy&showClusters=true',
        headers=headers).text

    # парсим
    parsed_html = bs(html, 'html.parser')

    # по перечню страниц
    for i in range(page_count):
        # описание вакансий
        vacancies_block = parsed_html.find('div',{'class':'vacancy-serp'})
        vacancies_list = vacancies_block.findChildren(recursive=False)
        for vacancy in vacancies_list:
            # промежуточный словарь, потому что удобнее смотреть значения при отладке
            vacancy_data = {}
            req = vacancy.find('span', {'class': 'g-user-content'})

            if req is not None:
                main_info = req.findChild()
                # наполняем
                vacancy_data['name'] = main_info.getText()
                vacancy_data['link'] = main_info['href']

                # интересно с id
                # есть конкретный атрибут 'data-vacancy-id' со значением id вакансии '40908861'
                # полагаю, что его использовать - предпочтительнее, чем вычленять из урла
                # потому что url вакансии может меняться, например, на cdn урл 'https://hhcdn.ru/click?b=199890&place=36'
                vacancy_data['_id'] = main_info['data-vacancy-id']

                vacancy_data['site'] = main_url

                # class ="bloko-section-header-3 bloko-section-header-3_lite" data-qa="vacancy-serp__vacancy-compensation" > от 62 & nbsp;000 руб.< / span >
                # общая строка денежного вознаграждения
                # её целиком положим в базу и её же будем парсить
                compensation = vacancy.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text.replace(u'\xa0', u' ') # replaced with space
                vacancy_data['compensation'] = compensation

                # ищем salary_min и salary_max
                # (ищем и находим, в обмен на 2 часа своей жизни)
                salary = compensation
                if not salary:
                    vacancy_data['salary_min'] = 0
                    vacancy_data['salary_max'] = 0
                else:
                    salary = salary.replace(u'\xa0', u'')
                    salaries = salary.split('-')
                    salaries[0] = re.sub(r'[^0-9]', '', salaries[0])
                    vacancy_data['salary_min'] = float(salaries[0])
                    if len(salaries) > 1:
                        salaries[1] = re.sub(r'[^0-9]', '', salaries[1])
                        vacancy_data['salary_max'] = float(salaries[1])
                    else:
                        vacancy_data['salary_max'] = 0

                    # и валюту
                    # вхождение 'руб.' или 'USD'
                    if salary.find('руб') >= 0:
                        vacancy_data['currency'] = 'руб.'
                    elif salary.find('USD') >= 0:
                        vacancy_data['currency'] = 'USD'
                    else:
                        vacancy_data['currency'] = ''
                # завершение salary = compensation приключения

                # +обработанная вакансия
                vacancies.append(vacancy_data)


        # вычленяем кнопку перехода к следующей странице
        # ищем по классу оформления кнопки "Дальше": 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'
        next_btn_block=parsed_html.find('a', {'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link=next_btn_block['href']
        html = requests.get(main_url+next_btn_link,headers=headers).text
        parsed_html = bs(html, 'html.parser')

    # вывод результатов
    print(f'Ресурс {main_url}, по поисковому запросу {vacancy_search_str} найдено {len(vacancies)} вакансий:')
    pprint(vacancies)
    return vacancies


# ---------------------------------------------------------------------
# Запись в Монго
# ---------------------------------------------------------------------
def FlushtoMongo(vacancies_list, vacancy_db_collection):
    # коллеги показали хороший способ, уместно использовать
    try:
        if len(vacancies_list) > 0:
            for vacancy in vacancies_list:
                vacancy_db_collection.update_many({'_id': vacancy['_id']}, {'$set': vacancy}, upsert=True)
            return True
        else:
            return False
    except Exception as e:
        return e

# ----------------------------------------------------------------------------
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# Поиск должен происходить по 2-ум полям (минимальной и максимальной зарплате)
# ----------------------------------------------------------------------------
def search_positions(vacancy_db_collection, salary_limit):
    # пример OR
    #db.collection.find({'$or': [{field1: "hi"}, {field1: "hello"}]} )

    vacancies_list = []
    try:
        salary_limit = float(salary_limit)
        for vacancy in vacancy_db_collection.find({'$or': [{'salary_min': {'$gt': salary_limit}}, {'salary_max': {'$gt': salary_limit}}]}).sort('salary_min'):
            vacancies_list.append(vacancy)
        return vacancies_list
    except ValueError:
        print('Error. Value is not valid')
        return None
    except Exception as e:
        return e


# -----------------------------
# конец секции описания функций
# -----------------------------

# Базовые параметры поиска
required_vacancy = 'Backend разработчик'
page_count = 1

#hh_vacancies_collect('https://hh.ru', required_vacancy, page_count)

# Базовые настройки подключения к Монго
client = MongoClient('localhost', 27017)
db = client['HHJobParser']
collection = db.test_collection

# Ищем вакансии
vacancies_list = hh_vacancies_collect('https://hh.ru', required_vacancy, page_count)
# Грузим в Монго
FlushtoMongo(vacancies_list, collection)

# ищем вакансии с зп больше минимально желаемой
required_salary_limit = 100000.0
interesting_positions = search_positions(collection, required_salary_limit)
# вывод результатов
print(f'С зарплатой более {required_salary_limit} найдено {len(interesting_positions)} вакансий:')
pprint(interesting_positions)
