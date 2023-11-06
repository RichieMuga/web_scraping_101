import scrapy


class BookspiderSpider(scrapy.Spider):
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            yield{
                'name':book.css("h3 a::text").get(),
                'price':book.css('.product_price .price_color::text').get(),
                'url': book.css('h3 a').attrib["href"]
            }
        next_page = response.css('li.next a').attrib['href']

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = f'https://books.toscrape.com/{next_page}'
            else:
                next_page_url = f'https://books.toscrape.com/{next_page}'
        yield response.follow(next_page_url, callback=self.parse)

