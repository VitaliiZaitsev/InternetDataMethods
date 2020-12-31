from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from goodsparser.spiders.leroymerlinru import LeroymerlinruSpider
from goodsparser import settings


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search='диван')

    process.start()