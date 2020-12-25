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

# 1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172


# -------------------------------------------------------------------------------------
# Комментарии по реализации:
# - аутентифицируемся
# - понравился подсмотренный подход открыть первое письмо и переходить к следующему по кнопке "Следующее"
# - "база данных" - здесь это простоскладываем в список (пропустил лекции по Mongo, требуется больше времени)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

driver = webdriver.Chrome()

try:
    driver.get('https://mail.ru')

    # Код аутентификации в селениум в общем очень прост
    # driver.find_element_by_id('IDOFLOGIN').sendKeys('YOUR LOGIN')
    # driver.find_element_by_id('PASSOFLOGIN').sendKeys('YOUR PASSWORD')
    # driver.find_element_by_id('login button').click()
    # Но для mail.ru требуется сначала запостить логин, далее дождаться и запостить пароль
    # Поэтому так:
    driver.find_element_by_name('login').send_keys('study.ai_172@mail.ru', Keys.ENTER)
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys('NextPassword172', Keys.ENTER)
    time.sleep(1)

    # Открываем первое письмо
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'llc')][1]")))
    driver.get(element.get_attribute('href'))
    time.sleep(1)

    # список для складывания emails
    emails_list = []

    # опросим первые target_emails_count писем или меньше, предусмотрим досрочное завершение
    # (бесконечные условия - моветон, постоянно ddos-ящие скрипты - зло, их создатели должны гореть в аду)
    # P.S.
    # В общем понятно, что можно и while true воткнуть

    emails_counter = 1
    target_emails_count = 3
    while emails_counter <= target_emails_count:
        # словарь для наполнения списка: от кого, дата отправки, тема письма, текст письма полный
        email = dict()

        # отправитель
        email['from'] = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-contact'))).text
        # дата отправки
        email['send_date'] = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'letter__date'))).text
        # тема письма
        email['subject'] = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h2'))).text
        # текст письма полный
        email['body'] = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-body'))).text
        # +1 email в список
        emails_list.append(email)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(@data-title-shortcut, 'Ctrl+↓')]")))

            # -----------------
            # Убито 3 часа времени, чтобы понять проблему и заставить кликнуть ныне НЕкликабельный элемент
            # спасибо индусам https://stackoverflow.com/questions/26943847/check-whether-element-is-clickable-in-selenium
            # element.Click()
            driver.execute_script("arguments[0].click()", element)
            # -----------------

            time.sleep(1)

        except NoSuchElementException:
            emails_counter = target_emails_count + 1

        emails_counter += 1

    print(f'Обработано {len(emails_list)} писем')
    for email in emails_list:
        print(email)

except Exception as e:
    print(f'Произошла ошибка {str(e)}')

finally:
    driver.close()
