#!/usr/bin/env python

__author__ = "Зайцев Виталий Владимирович, Vitalii Zaitsev"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Vitalii Zaitsev"
__email__ = "vvzaisev79@gmail.com"
__status__ = "Education"


# Курс "Методы сбора и обработки данных из сети Интернет"
# Урок 2. Парсинг HTML. BeautifulSoup, MongoDB

#Необходимо собрать информацию о вакансиях на вводимую должность
#(используем input или через аргументы) с сайтов Superjob и HH.
#Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
#Получившийся список должен содержать в себе минимум:
#* Наименование вакансии.
#* Предлагаемую зарплату (отдельно минимальную, максимальную и валюту).
#* Ссылку на саму вакансию.
#* Сайт, откуда собрана вакансия.

#По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
#Структура должна быть одинаковая для вакансий с обоих сайтов.
#Общий результат можно вывести с помощью dataFrame через pandas.


# -------------------------------------------------------------------------------------
# Комментарии по реализации:
# - только сайт hh.ru
# - не сделал (не успел) отдельный парсинг минимальную зарплату, максимальную зарпалту, валюту
# - 'dataFrame через pandas' - не использовал


from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests



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

    # представляемся Google Chrome, взял свежую строку отсюда: http://useragentstring.com/pages/useragentstring.php?name=Chrome
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

            if req != None:
                main_info = req.findChild()
                # наполняем
                vacancy_data['name'] = main_info.getText()
                vacancy_data['link'] = main_info['href']
                vacancy_data['site'] = main_url

                # class ="bloko-section-header-3 bloko-section-header-3_lite" data-qa="vacancy-serp__vacancy-compensation" > от 62 & nbsp;000 руб.< / span >
                # вот здесь у меня fail - не распарсил на min salary, max salary, валюту
                # поэтому просто сумма и валюта
                #vacancy_data['compensation'] = vacancy.find('div', {'class': 'vacancy-serp__vacancy-compensation'})
                vacancy_data['compensation'] = vacancy.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text.replace(u'\xa0', u' ') # replaced with space

                # +обработанная вакансия
                vacancies.append(vacancy_data)


        # вычленяем кнопку перехода к следующей странице
        # ищем по классу оформления кнопки "Дальше": 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'
        next_btn_block=parsed_html.find('a',{'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link=next_btn_block['href']
        html = requests.get(main_url+next_btn_link,headers=headers).text
        parsed_html = bs(html, 'html.parser')

    # вывод результатов
    print(f'Ресурс {main_url}, по поисковому запросу {vacancy_search_str} найдено {len(vacancies)} вакансий:')
    pprint(vacancies)
    return vacancies


#required_vacancy = 'html-верстальщик'
required_vacancy = 'Backend разработчик'
page_count = 1

hh_vacancies_collect('https://hh.ru', required_vacancy, page_count)
