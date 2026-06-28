import os
from pathlib import Path

BASE_DIR = Path(os.environ.get("SCRAPY_OUTPUT_BASE", Path.cwd())).resolve()
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"

BOT_NAME = "books_web_scraping"

SPIDER_MODULES = ["books_web_scraping.spiders"]
NEWSPIDER_MODULE = "books_web_scraping.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 0.25  # 

TELNETCONSOLE_ENABLED = False



ITEM_PIPELINES = {
    "books_web_scraping.pipelines.BooksWebScrapingPipeline": 300,
}

FEEDS = {
    str(OUTPUT_DIR / "books.json"): {"format": "json", "overwrite": True},
    str(OUTPUT_DIR / "books.csv"): {"format": "csv", "overwrite": True},
    str(OUTPUT_DIR / "books.xml"): {"format": "xml", "overwrite": True},
}

SQLITE_DB_PATH = str(DATA_DIR / "scraped_books_vault.db")

FEED_EXPORT_ENCODING = "utf-8"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
