# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Remove white spaces from string
        field_names = adapter.field_names()
        for field_name in  field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                if isinstance(value, str):
                    adapter[field_name] = value.strip()

        # Coverting product category from uppercase to lower case
        lowercase_keys=["category","product_type","stars"]
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key]=value.lower()

        # Convert price to float from £
        price_keys = ["price", "price_excl_tax", "price_incl_tax", "tax"]
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace("£","")
            adapter[price_key]= float(value)

        # Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])


        # Reviews, converting to integer
        reviews_string = adapter.get("number_of_reviews")
        adapter["number_of_reviews"] = int(reviews_string)

        # Convert string numbers to an actual integer number
        rating = adapter.get("stars")
        rating_string = rating.split(" ")
        word_rating_string = rating_string[1]

        if word_rating_string == "one":
            adapter["stars"] = 1
        elif word_rating_string == "two":
            adapter["stars"] = 2
        elif word_rating_string == "three":
            adapter["stars"] = 3
        elif word_rating_string == "four":
            adapter["stars"] = 4
        elif word_rating_string == "five":
            adapter["stars"] = 5
        else:
            0

        return item


import mysql.connector
class SaveToMysqlPipeline:
    # connect to mysql db
    def __init__(self):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database ="books"
        )

        #using cursor, create a table
        self.cur = self.mydb.cursor()

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS books(
                id INT AUTO_INCREMENT NOT NULL,
                url VARCHAR(255),
                title VARCHAR(255),
                product_type VARCHAR(255),
                price_excl_tax DECIMAL(8, 2),
                price_incl_tax DECIMAL(8, 2),
                tax DECIMAL(8, 2),
                availability VARCHAR(255),
                number_of_reviews INT,
                stars INT,
                category VARCHAR(50),
                description  TEXT,
                price DECIMAL(8,2),
                upc VARCHAR(255),
                PRIMARY KEY(id)
            )"""
        )

    def process_item(self, item, spider):
        self.cur.execute(
            """
            INSERT INTO books(
                url,
                title,
                product_type,
                price_excl_tax,
                price_incl_tax,
                tax,
                availability,
                number_of_reviews,
                stars,
                category ,
                description,
                price,
                upc
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """
            ,(
                item["url"],
                item["title"],
                item["product_type"],
                item["price_excl_tax"],
                item["price_incl_tax"],
                item["tax"],
                item["availability"],
                item["number_of_reviews"],
                item["stars"],
                item["category"],
                str(item["description"][0]),
                item["price"],
                item["upc"],
            )
        )
        self.mydb.commit()
        return item
    def close_spider(self):
        self.cur.close()
        self.mydb.close()

