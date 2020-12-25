#!/usr/bin/env python

__author__ = "Зайцев Виталий Владимирович, Vitalii Zaitsev"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Vitalii Zaitsev"
__email__ = "vvzaisev79@gmail.com"
__status__ = "Education"


# Курс "Методы сбора и обработки данных из сети Интернет"
# Урок 5. Урок 5. Selenium в Python

# 2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
# Магазины можно выбрать свои.
# Главный критерий выбора: динамически загружаемые товары


# -------------------------------------------------------------------------------------
# Комментарии по реализации:
# - выбираем секцию карусели (спасибо за разбор!), в ней парсим товары, кликаем дальше, пока на очередном парсинге карусели НЕ иссякнут уникальные товары-хиты
# - "база данных" - здесь также просто складываем в список (пропустил лекции по Mongo, требуется больше времени)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import time
from pprint import pprint


chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get('https://www.mvideo.ru/')

    # карусель бесконечна, количество хитов-продуктов конечно
    # входим в бесконечный цикл,
    # на каждом шаге цикла (=анализа карусели) парсим хиты-продукты,
    # добавляем уникальные хиты-продукты в целевой список,
    # параллельно трекаем - были ли добавлены новые хиты-продукты за этот шаг
    # если новых продуктов за этот шаг добавлено НЕ было -
    # прекращаем крутить карусель и парсить продукты, выходим из цикла

    # правильная секция, первая загрузка карусели
    bestsellers = driver.find_element_by_xpath('//div[contains(text(),"Хиты продаж")]/ancestor::div[@class="section"]')

    # наш список распарсенных хитов-продуктов
    goods_list = []

    # и начинаем
    while True:

        known_hits_count = 0

        #
        #< div class ="fl-product-tile__picture-holder c-product-tile-picture__holder" >
        #< a href = "/products/smartfon-huawei-p40-lite-e-nfc-midnight-black-art-l29n-30050496"
        #class ="fl-product-tile-picture fl-product-tile-picture__link"
        #data - product - info = '{
        carousel_hits = bestsellers.find_elements_by_xpath(".//a[@class='fl-product-tile-picture fl-product-tile-picture__link']")

        # на странице есть шикарная json структура, испольуем её
        #data - product - info = '{
        #"productPriceLocal": "10990.00",
        #"productId": "30050496",
        #"productName": "Смартфон Huawei P40 Lite E NFC Midnight Black (ART-L29N)",
        #"productCategoryId": "cat2_cis_0000000357",
        #"productCategoryName": "Смартфоны",
        #"productVendorName": "Huawei",
        #"productGroupId": "cat1_cis_0000000012",
        #"Location": "block5260655",
        #"eventPosition": 1}'
        for hit in carousel_hits:
            product = hit.get_attribute('data-product-info')
            # чистим
            product = product.replace('\t', '')
            product = product.replace('\n', '')
            # из json в python
            product = json.loads(product)
            # минус "лишние" данные
            product.pop('Location')
            product.pop('eventPosition')
            product.pop('productGroupId')
            # добавляем уникальное, иначе увеличиваем счётчик (счётчик отражает уже найденные)
            if product not in goods_list:
                goods_list.append(product)
            else:
                known_hits_count += 1

        # если known_hits_count (количество уже известных хитов)
        # равно (больше или равно) длине списка хитов-продуктов goods_list
        # то всё, новых продуктов уже НЕ находим, можно выходить
        # иначе клик - новая прокрутка карусели, и дальнейший анализ
        if known_hits_count >= len(goods_list):
            break
        else:
            # next_button click
            next_button = WebDriverWait(bestsellers, 10).until(EC.presence_of_element_located((By.XPATH, ".//a[contains(@class, 'next-btn')]")))
            # Та же хр*нь, элемент "не кликабельный", код Click() НЕ работает
            # next_button.Click()
            # но не зря у нас есть индусские друзья https://stackoverflow.com/questions/26943847/check-whether-element-is-clickable-in-selenium
            driver.execute_script("arguments[0].click()", next_button)
            time.sleep(1)


    # Итоговые результаты
    print(f'Найдено товаров-хитов {len(goods_list)}')
    pprint(goods_list)

except NoSuchElementException as ns:
    print(f'Не найдена секция (хитов, продуктов) {str(ns)}')

except Exception as e:
    print(f'Произошла ошибка {str(e)}')

finally:
    driver.close()
