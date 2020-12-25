#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# source https://github.com/gil9red/SimplePyScripts/blob/f7b5f7562a86064e8c04fb62206af257efab7345/selenium__examples/hello_world.py#L26

# https://pypi.python.org/pypi/selenium


# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#
# geckodriver: https://github.com/Mozilla/geckodriver/releases
#
# Если на этой строке исключение "Message: 'geckodriver' executable needs to be in PATH."
# Нужно:
#   * Из репозитория https://github.com/mozilla/geckodriver скачать geckodriver.exe
#   * Сохранить в папку, например: C:\Program Files\geckodriver\geckodriver.exe
#   * Добавить в системную переменную PATH путь к папке
#
# OR: driver = webdriver.Firefox(executable_path=r"C:\Program Files\geckodriver\geckodriver.exe")
driver = webdriver.Chrome(executable_path=r"C:\Program Files\chromedriver_win32\chromedriver.exe")
driver.get('https://yahoo.com')
print('Title: "{}"'.format(driver.title))

search_box = driver.find_element_by_id('uh-search-box')
search_box.send_keys('Hello World!' + Keys.RETURN)

# Делаем скриншот результата
driver.save_screenshot('before_search.png')

wait = WebDriverWait(driver, timeout=10)

elem = wait.until(
    EC.presence_of_element_located((By.ID, 'web'))
)
elem.screenshot('search_content.png')

print('Title: "{}"'.format(driver.title))

# Делаем скриншот результата
driver.save_screenshot('after_search.png')

driver.quit()