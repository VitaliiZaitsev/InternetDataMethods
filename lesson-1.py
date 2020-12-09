#!/usr/bin/env python

__author__ = "Зайцев Виталий Владимирович, Vitalii Zaitsev"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Vitalii Zaitsev"
__email__ = "vvzaisev79@gmail.com"
__status__ = "Education"


# Курс "Методы сбора и обработки данных из сети Интернет"
# Урок 1. Основы клиент-серверного взаимодействия. Парсинг API

# Задание Урок-1:
# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

#2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.
# Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
# Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.


# --------------------------------------------------------------------------------------------------------------------
# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

# Комментарии по решению:
# Никакой обработки ошибок, фильтрации элементов и прочего
# Просто get запрос к требуемому GitHub API для выбранного пользователя VitaliiZaitsev, десериализация и запись в файл

# Аналог решения с curl:
# curl https://api.github.com/users/VitaliiZaitsev/repos

import requests
import json

response = requests.get('https://api.github.com/users/VitaliiZaitsev/repos')
with open('VitaliiZaitsev_GitHub_repos.json', 'w', encoding='utf-8') as f:
    json.dump(json.loads(response.text), f, ensure_ascii=False, indent=4)


# --------------------------------------------------------------------------------------------------------------------
#2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.

# Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
# Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны
# # Ответ сервера записать в файл


# Комментарии по решению:
# https://api.nasa.gov/index.html#main-content
# Получите данные об астероидах, галактиках и многом другом.

# https://api.nasa.gov/planetary/apod?api_key=qQa5NzKl3LhPyVE1UIRLhFc8MyOzoObRttKB1Pll
# Getting Astronomy Picture of the Day
# main_link = 'https://api.nasa.gov/planetary/apod?api_key=qQa5NzKl3LhPyVE1UIRLhFc8MyOzoObRttKB1Pll'

# https://api.nasa.gov/index.html#browseAPI APOD
api_key = 'qQa5NzKl3LhPyVE1UIRLhFc8MyOzoObRttKB1Pll'
date = '2020-01-01' # YYYY-MM-DD

main_link = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={date}'

response = requests.get(main_link)
j_data = response.json()

print(f"{j_data['title']} - это {j_data['explanation']}")
print(f"Скачать можно по адресу {j_data['url']}")

# По условию задания также выгрузить response в файл (пусть в удобоваримом json-читаемом виде)
with open('api_nasa_gov.json', 'w', encoding='utf-8') as f:
    json.dump(json.loads(response.text), f, ensure_ascii=False, indent=4)