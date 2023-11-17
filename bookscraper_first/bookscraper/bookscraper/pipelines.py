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

        # Availability, split and only use the integer
        availability_string = adapter.get("availability")
        print(availability_string)
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter["availability"] = 0
        else:
            availability_array = split_string_array[1].split(" ")
            adapter["availability"]=int(availability_array[0])

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

class SaveToMsqlPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "books"
        )

        # Create cur used to execute commands
        self.cur = self.conn.cursor()

        self.cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books(
        Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        title VARCHAR(255),
        product_type VARCHAR(255),
        upc VARCHAR(255),
        price_excl_tax DECIMAL,
        price_incl_tax DECIMAL,
        tax DECIMAL,
        availability INT,
        number_of_reviews INT,
        stars INT,
        category VARCHAR(255),
        description TEXT,
        price DECIMAL
        )
        """
        )

    def insert_into(self,item,spider):
        print(f"Connecting to database: {self.conn}")
        # Insert into statement
        self.cur.execute(
        """
            INSERT INTO books (
            url,
            title,
            product_type,
            upc,
            price_excl_tax,
            price_incl_tax,
            tax,
            availability,
            number_of_reviews,
            stars,
            category,
            description,
            price
            )
        VALUES(
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )""",
        (
            item['url'],
            item["title"],
            item["product_type"],
            item["upc"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["availability"],
            item["number_of_reviews"],
            item["stars"],
            item["category"],
            item["description"],
            item["price"]
        )
        )

    # Execute insert into command
        self.conn.commit()

        return item

    def close_spider(self,spider):

    # Close spider and connection cur
        self.cur.close()
        self.conn.close()

