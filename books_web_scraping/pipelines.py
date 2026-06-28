import sqlite3
import logging
from pathlib import Path
from scrapy.exceptions import DropItem

class BooksWebScrapingPipeline:
    """
    This pipeline intercepts every book item yielded by the spider whivh cleans up text whitespace, handles currency conversion, standardizes availability 
    into a boolean flag writes records into a local SQLite database file.
    """

    def __init__(self, db_path):
        """
       connect to SQLite database file and build  structured tables dynamically.
        """
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        

        self.cursor.execute("DROP TABLE IF EXISTS books")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price REAL,
                availability TEXT,
                category TEXT,
                product_url TEXT,
                image_url TEXT
            )
        """)
        self.conn.commit()
        logging.info("SQLite database table initialized successfully.")

    @classmethod
    def from_crawler(cls, crawler):
        output_dir = crawler.settings.get("OUTPUT_DIR")
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        db_path = crawler.settings.get("SQLITE_DB_PATH", "data/scraped_books_vault.db")
        return cls(db_path)

    def process_item(self, item, spider):
        """
        Runs automatically for every individual book item extracted by the spider and fulfills all the text standardization and parsing rules 
        """
        if not item.get("title"):
            raise DropItem("this item is missing a title so Dropping it.")

        for field in ["title", "category", "product_url", "image_url"]:
            if item.get(field):
                item[field] = item[field].strip()

        if item.get("price"):
            clean_price = item["price"].replace("£", "").replace("$", "").strip()
            item["price"] = float(clean_price)

        if item.get("availability"):
            status_text = item["availability"].strip().lower()
            item["availability"] = True if "in stock" in status_text else False
        else:
            item["availability"] = False

        db_availability = "true" if item.get("availability") else "false"
        self.cursor.execute("""
            INSERT INTO books (title, price, availability, category, product_url, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item.get("title"),
            item.get("price"),
            db_availability,
            item.get("category"),
            item.get("product_url"),
            item.get("image_url")
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        """
        Runs automatically when the spider finishes crawling all categories. disconnect from our SQLite database.
        """
        self.conn.close()
        logging.info("SQLite database connection closed cleanly.")
