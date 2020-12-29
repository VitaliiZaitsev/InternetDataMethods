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
# * новая ветка
# * копипаст парсинга из предыдущего урока
# + мин салари и макс салари
# + id
# + подключение монго и запись в монго
# + функция поиска вакансий по зарплате
# + функция дозаписи новых вакансий