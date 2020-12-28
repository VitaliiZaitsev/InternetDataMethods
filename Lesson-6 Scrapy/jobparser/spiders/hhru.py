import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    # python, Москва, за последние 7 дней, постоянная работа, полный день
    start_urls = ['https://hh.ru/search/vacancy?st=searchVacancy&text=python&area=1&salary=&currency_code=RUR&experience=doesNotMatter&employment=full&schedule=fullDay&order_by=relevance&search_period=7&items_on_page=50&no_magic=true&L_save_area=true']

    def parse(self, response: HtmlResponse, **kwargs):
        vacancies_links = response.xpath("//div[@class='vacancy-serp-item__info']//a/@href").extract()

        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)

        next_page = response.xpath("//a[contains(@class,'HH-Pager-Controls-Next')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        vacancy = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']//span/text()").extract()
        site = 'https://hh.ru/'
        link = response.url
        yield JobparserItem(vacancy=vacancy, salary=salary, site=site, link=link)
