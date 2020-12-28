import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    # python, Москва
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        vacancies_links = response.xpath("//a[contains(@class,'icMQ_ _6AfZ9')]/@href").extract()

        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)

        next_page = response.xpath("//a[contains(@data-qa,'pager-next')]/@href").extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        # //h1[contains(text(),'Консультант по информационным технологиям и телеко')]
        vacancy = response.xpath("//h1/text()").extract_first()

        # <span class="_3mfro _2Wp8I PlM3e _2JVkc">до<!-- -->&nbsp;<!-- -->150&nbsp;000&nbsp;руб.</span>
        salary = response.xpath("//span[@class='_1OuF_ ZON4b']//span[contains(@class,'_2Wp8I')]/text()").extract()

        site = 'https://superjob.ru/'

        link = response.url

        yield JobparserItem(vacancy=vacancy, salary=salary, site=site, link=link)