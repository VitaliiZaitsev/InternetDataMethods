# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:

    # инициализация Монго
    def __init__(self):
        client = MongoClient('localhost', 27017)
        # db = client['test_database']
        self.mongo_base = client['Scrapy_JobParsers_VitaliiZaitsev']


    #def __init__(self):
    #    self.vacancies_list = []

    def process_item(self, item, spider):
        # Монго
        collection = self.mongo_base[spider.name]

        if spider.name == 'hhru':
            # vacancy = response.xpath("//h1/text()").extract_first()
            # salary = response.xpath("//p[@class='vacancy-salary']//span/text()").extract()
            # site = 'https://hh.ru/'
            # link = response.url
            # yield JobparserItem(vacancy=vacancy, salary=salary, site=site, link=link)
            # ----------------------
            #_id = scrapy.Field()
            #vacancy = scrapy.Field()
            #salary = scrapy.Field()
            #salary_min = scrapy.Field()
            #salary_max = scrapy.Field()
            #currency = scrapy.Field()
            #link = scrapy.Field()
            #site = scrapy.Field()

            item['_id'] = self.hh_process_id(item['link'])
            item['salary_min'] = self.hh_process_salary_min(item['salary'])
            item['salary_max'] = self.hh_process_salary_max(item['salary'])
            item['currency'] = self.hh_process_currency(item['salary'])
        else:
            # По нашему коду сюда приходит только SuperJob
            item['_id'] = self.sj_process_id(item['link'])
            item['salary_min'] = self.sj_process_salary_min(item['salary'])
            item['salary_max'] = self.sj_process_salary_max(item['salary'])
            item['currency'] = self.sj_process_currency(item['salary'])


        del(item['salary'])
        collection.insert_one(item)
        #self.vacancies_list.append(item)
        return item

    def sj_process_id(self, input_string):
        # находим id вакансии, берём его из урла
        # https://www.superjob.ru/vakansii/konsultant-po-informacionnym-tehnologiyam-i-telekommunikaciyam-35356196.html
        try:
            # отбрасываем .html
            url_parts_1 = input_string.split('.html')
            # сплитим по - и берём последний элемент
            url_parts_2 = url_parts_1[0].split('-')
            return url_parts_2[len(url_parts_2) - 1]
        except Exception as e:
            print(e)
            return None

    def sj_process_salary_min(self, input_list):
        try:
            # вычленяем минимальную зарплату из общего листа значений строки зарплаты
            # По договорённости
            # до 140 000 руб./месяц
            # 45 000 — 55 000 руб./месяц
            # от 60 000 руб./месяц
            # до 150 000 руб./месяц

            #['от ', '50\xa0000', ' до ', '90\xa0000', ' ', 'руб.', ' на руки']

            # ищем минимальную зарплату,
            # ищем слово 'от' и берём следующий элемент списка
            # [1, 2, 3, 2].index(2)  # => 1
            i = input_list.index('от')

            salary_min_string = input_list[i + 1]
            salary_min_string = salary_min_string.replace('\xa0', '')
            return float(salary_min_string)

        except ValueError as ve:
            return 0
        except Exception as e:
            return 0


    def sj_process_salary_max(self, input_list):
        try:
            # вычленяем МАКСИМАЛЬНУЮ зарплату из общего листа значений строки зарплаты
            i = input_list.index('до')

            salary_max_string = input_list[i + 2]
            salary_max_string = salary_max_string.replace('\xa0', '')
            salary_max_string = salary_max_string.replace('руб.', '')
            salary_max_string = salary_max_string.replace('USD', '')
            return float(salary_max_string)
        except ValueError as ve:
            return 0
        except Exception as e:
            return 0

    def sj_process_currency(self, input_list):
        try:
            # ищем валюту
            # вхождение 'руб.' или 'USD'
            for value in input_list:
                if 'руб.' in value:
                    return 'руб.'
                elif 'USD' in value:
                    return 'USD'
            return None
        except Exception as e:
            return None



    def hh_process_salary_min(self, input_list):
        try:
            # вычленяем минимальную зарплату из общего листа значений строки зарплаты
            # от 200 000 до 240 000 руб. на руки
            # от 4 000 USD на руки
            # до 220 000 руб. на руки
            # з/п не указана

            #['от ', '50\xa0000', ' до ', '90\xa0000', ' ', 'руб.', ' на руки']

            # ищем минимальную зарплату,
            # ищем слово 'от ' и берём следующий элемент списка
            # [1, 2, 3, 2].index(2)  # => 1
            i = input_list.index('от ')

            salary_min_string = input_list[i + 1]
            salary_min_string = salary_min_string.replace('\xa0', '')
            return float(salary_min_string)

        except ValueError as ve:
            #Как работает функция Index()?
            # Требуется один аргумент, который является элементом, для которого вы хотите найти индекс или позицию в качестве результата.
            # Этот метод ищет элемент в списке и возвращает индекс, соответствующий его значению, в противном случае возникает ошибка ValueError.
            # При поиске подстрок возникает следующая ошибка."Substring not found"
            return 0
        except Exception as e:
            #
            return 0

    def hh_process_salary_max(self, input_list):
        try:
            # вычленяем МАКСИМАЛЬНУЮ зарплату из общего листа значений строки зарплаты
            # от 200 000 до 240 000 руб. на руки
            # от 4 000 USD на руки
            # до 220 000 руб. на руки
            # з/п не указана

            #['от ', '50\xa0000', ' до ', '90\xa0000', ' ', 'руб.', ' на руки']

            # ищем МАКСИМАЛЬНУЮ зарплату,
            # ищем слово 'до ' и берём следующий элемент списка
            # [1, 2, 3, 2].index(2)  # => 1
            i = input_list.index(' до ')

            salary_max_string = input_list[i + 1]
            salary_max_string = salary_max_string.replace('\xa0', '')
            return float(salary_max_string)

        except ValueError as ve:
            #Как работает функция Index()?
            # Требуется один аргумент, который является элементом, для которого вы хотите найти индекс или позицию в качестве результата.
            # Этот метод ищет элемент в списке и возвращает индекс, соответствующий его значению, в противном случае возникает ошибка ValueError.
            # При поиске подстрок возникает следующая ошибка."Substring not found"
            return 0
        except Exception as e:
            #
            return 0

    def hh_process_currency(self, input_list):
        try:
            # вычленяем валюту из общего листа значений строки зарплаты
            # от 200 000 до 240 000 руб. на руки
            # от 4 000 USD на руки
            # до 220 000 руб. на руки
            # з/п не указана

            #['от ', '50\xa0000', ' до ', '90\xa0000', ' ', 'руб.', ' на руки']

            # ищем валюту
            # просто перебор на 'руб.' или 'USD'
            for value in input_list:
                if value == 'руб.' or value == 'USD':
                    return value
            return None
        except Exception as e:
            #
            return None

    def hh_process_id(self, input_string):
        # находим id вакансии, берём его из урла
        # str = 'https://hh.ru/vacancy/41169951?query=python'
        # до https://hh.ru/vacancy/41169951
        # url_parts_1 = str.split('?')
        # до https: hh.ru vacancy 41169951
        # url_parts_2 = url_parts_1[0].split('/')
        # возвращаем последний 41169951
        try:
            url_parts_1 = input_string.split('?')
            url_parts_2 = url_parts_1[0].split('/')
            return url_parts_2[len(url_parts_2) - 1]
        except Exception as e:
            print(e)
            return None
