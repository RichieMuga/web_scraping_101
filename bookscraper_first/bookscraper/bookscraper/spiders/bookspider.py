import scrapy
from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response):
        books = response.css('article.product_pod')
        #Going into each individual book and getting title, description and rating
        for book in books:
            url_for_individual_book = book.css('h3 a').attrib['href']
            if 'catalogue/' in url_for_individual_book:
                book_url = f'https://books.toscrape.com/{url_for_individual_book}'
            else:
                book_url = f'https://books.toscrape.com/catalogue/{url_for_individual_book}'
            yield response.follow(book_url, callback=self.parse_book_page)

        # Going to the next page
        next_page=response.css("li.next a ::attr(href)").get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = f'https://books.toscrape.com/{next_page}'
            else:
                next_page_url = f'https://books.toscrape.com/catalogue/{next_page}'
            yield response.follow(next_page_url, callback=self.parse)


    def parse_book_page (self, response):
        table_rows = response.css("table tr")

        book_item = BookItem()


        book_item['url'] = response.url
        book_item["title"] = response.css(".product_main h1::text").get()
        book_item["product_type"] = table_rows[1].css("td ::text").get()
        book_item["upc"] = table_rows[0].css("td ::text").get()
        book_item["price_excl_tax"] = table_rows[2].css("td ::text").get()
        book_item["price_incl_tax"] = table_rows[3].css("td ::text").get()
        book_item["tax"] = table_rows[4].css("td ::text").get()
        book_item["availability"] = table_rows[5].css("td ::text").get()
        book_item["number_of_reviews"] = table_rows[6].css("td ::text").get()
        book_item["stars"] = response.css("p.star-rating").attrib["class"]
        book_item["category"] =  response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item["description"] =  response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item["price"]=response.css("p.price_color ::text").get()


        yield book_item
