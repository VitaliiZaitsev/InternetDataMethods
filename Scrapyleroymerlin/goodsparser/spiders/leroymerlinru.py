import scrapy
from scrapy.http import HtmlResponse
from goodsparser.items import GoodsparserItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinruspider'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super(LeroymerlinruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        goods_links = response.xpath("//a[@class='plp-item__info__title']/@href").extract()

        for link in goods_links:
            yield response.follow(link, callback=self.goods_parse)

        next_page = response.xpath("//a[contains(@class,'next-paginator-button')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def goods_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=GoodsparserItem(), response=response)
        loader.add_xpath('_id', "//span[@slot='article']/text()")
        loader.add_xpath('name', "//h1/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('images', "//source[contains(@media, '1024px')]/@srcset")
        loader.add_xpath('description_key', "//dl/div/dt/text()")
        loader.add_xpath('description_item', "//dl/div/dd/text()")
        yield loader.load_item()


        # Артикул-SKU <span slot="article" itemprop="sku" content="82576239" xpath="1">Арт. 82576239</span>
        #_id = response.xpath("//span[@slot='article']/text()")
        #name = response.xpath("//h1/text()").extract_first()
        #link = response.url
        # <span slot="price" xpath="1">14 448</span>
        #price = response.xpath("//span[@slot='price']/text()").extract_first()

        # <dl class="def-list" xpath="1">
        #         <div class="def-list__group">
        #             <dt class="def-list__term">Вес, кг</dt>
        #             <dd class="def-list__definition">
        #                 33.0
        #             </dd>
        #         </div>
        #         ....
        #description = response.xpath("//dl/div").extract()

        #<img slot="thumbs" src="https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/90118660.jpg" alt="image thumb"/>
        #            <picture slot="pictures">
        #                <source media=" only screen and (min-width: 1024px)" itemprop="image" srcset="https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/90118660.jpg" data-origin="https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/90118660.jpg"/>
        #images = response.xpath("//source[contains(@media, '1024px')]/@srcset").extract()

        #yield GoodsparserItem(_id=id, name=name, link=link, price=price, description=description, images=images)
