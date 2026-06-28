# Book Web Scraping Pipeline

## Project Overview

This project has been built to scrape book data from `books.toscrape.com`. The data has been collected by a Scrapy spider, cleaned by a pipeline, exported into JSON, CSV, and XML files, and saved into a SQLite database.

## Features

- Book categories have been discovered automatically.
- Category pagination has been followed.
- Five random books have been selected from each category.
- Book data has been exported in JSON, CSV, and XML format.
- The scraped data has been stored in SQLite.
- Scrapyd deployment has been configured.
- Docker support has been added for running Scrapyd in a container.

## Tech Stack

- Python 3
- Scrapy
- Scrapyd
- Scrapyd Client
- SQLite
- Docker

## Installation Guide

### > Without Docker, this setup has been followed.

Step 1: Clone And Enter

```bash
git clone https://github.com/Parisa-Reza/book-web-scraping-pipeline
```

```bash
cd book-web-scraping-pipeline
```

Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
python3 -m pip install -r requirements.txt
```

## Environment Setup

No extra `.env` file has been required. After the spider has been run, local folders are created automatically or used if they already exist.

The normal local output has been kept here:

```text
output/books.json
output/books.csv
output/books.xml
data/scraped_books_vault.db
```

For Docker, mounted folders have been used:

```text
docker-output/
docker-data/
```

## Running the Spider 

Step 4: Run The Spider

```bash
python3 -m scrapy crawl book_spider
```

This creates:

```text
output/books.json
output/books.csv
output/books.xml
data/scraped_books_vault.db
```

Step 5: Check Outputs

```bash
ls -lh output data
```


### Scrapyd Deployment Guide

Step 6: Test Scrapyd Deployment

Terminal 1, start Scrapyd:

```bash
source .venv/bin/activate
```

```bash
scrapyd --pidfile=
```

Terminal 2, deploy:

```bash
source .venv/bin/activate
```

```bash
scrapyd-deploy local_target
```

Check deployed project:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:6800/listprojects.json').read().decode())"
```

Check versions:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:6800/listversions.json?project=books_web_scraping').read().decode())"
```

Check spiders:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:6800/listspiders.json?project=books_web_scraping').read().decode())"
```

Step 7: Run Spider Through Scrapyd

```bash
python -c "import urllib.request, urllib.parse; data=urllib.parse.urlencode({'project':'books_web_scraping','spider':'book_spider'}).encode(); print(urllib.request.urlopen('http://127.0.0.1:6800/schedule.json', data=data).read().decode())"
```

Then check jobs:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:6800/listjobs.json?project=books_web_scraping').read().decode())"
```
The ignored folders are generated locally after crawling .

---

### > Docker Setup Guide



Step 1: Clone And Enter

```bash
git clone https://github.com/Parisa-Reza/book-web-scraping-pipeline
```

```bash
cd book-web-scraping-pipeline
```


Step 2: Create Local Output Folders

```bash
mkdir -p docker-output docker-data
```

Step 3: Build 

```bash
docker build -t books-web-scraping .
```

Step 4: Run Container

```bash
docker run -d \
  --name books-scrapyd \
  -p 6800:6800 \
  -v "$PWD/docker-output:/app/output" \
  -v "$PWD/docker-data:/app/data" \
  books-web-scraping
```

Step 5: Check Scrapyd

```bash
curl http://localhost:6800/daemonstatus.json
```

Step 7: Check Project

```bash
curl http://localhost:6800/listprojects.json
```

This project name must be used:

```text
books_web_scraping
```


Step 8: Start Crawling with API

```bash
curl http://localhost:6800/schedule.json \
  -d project=books_web_scraping \
  -d spider=book_spider
```

Step 9: Watch Logs

```bash
docker logs -f books-scrapyd
```

Wait until `Process finished` has been shown.

Step 10: Check Output

```bash
ls docker-output
```

You should get:

```text
books.csv
books.json
books.xml
```

Check database:

```bash
ls docker-data
```

You should get:

```text
scraped_books_vault.db
```

To check whether the Scrapy project has been deployed inside Scrapyd, these commands have been used in order.

First check Scrapyd is running:

```bash
curl http://localhost:6800/daemonstatus.json
```

Good result looks like:

```json
{"status":"ok","running":0,"pending":0,"finished":0}
```

Now check deployed projects:

```bash
curl http://localhost:6800/listprojects.json
```

Good result should include:

```json
{"status":"ok","projects":["books_web_scraping"]}
```

Then check spiders inside that project:

```bash
curl "http://localhost:6800/listspiders.json?project=books_web_scraping"
```

Good result should include:

```json
{"status":"ok","spiders":["book_spider"]}
```

If `books_web_scraping` and `book_spider` are shown, deployment is OK.


## Output Format Description

Each exported item contains:

- `title`
- `price`
- `availability`
- `category`
- `product_url`
- `image_url`

The JSON file has been written as a list of scraped book objects. The CSV file has been written as rows and columns. The XML file has been written as item nodes. The SQLite database stores the same records in the `books` table.

## Database Configuration

The database path has been configured in `books_web_scraping/settings.py`:

```text
data/scraped_books_vault.db
```

The table name has been set as:

```text
books
```

The table has been recreated on each crawl, so old data is replaced by the latest crawl result.

## Architecture Diagram

```text
books.toscrape.com
        |
        v
book_spider
        |
        v
BooksWebScrapingItem
        |
        v
BooksWebScrapingPipeline
        |
        +--> output/books.json
        +--> output/books.csv
        +--> output/books.xml
        +--> data/scraped_books_vault.db
```

## Folder Structure

```text
book-web-scraping-pipeline/
├── books_web_scraping/
│   ├── spiders/
│   │   └── book_spider.py
│   ├── items.py
│   ├── pipelines.py
│   └── settings.py
├── Dockerfile
├── requirements.txt
├── scrapy.cfg
├── scrapyd.conf
└── setup.py
```

## Design Decisions

- Scrapy has been used because crawling, parsing, and exporting are supported well.
- Category pages have been crawled first, and pagination has been followed before random books are selected.
- Five books have been selected from each category so the output stays small and easy to check.
- SQLite has been used because no separate database server is needed.
- Scrapyd has been added so the spider can be scheduled through an HTTP API.
- Docker has been used so Scrapyd can be run in the same way on another machine.

## Known Limitations

- The spider has been written only for `books.toscrape.com`. If the website structure changes, the CSS selectors may need to be updated.
- Only five random books have been selected from each category. Because of this, the output may be different every time the spider is run.
- The database table has been dropped and recreated on each crawl. Old scraped records are not kept as history.
- Duplicate checking has not been added outside the current database reset process.

- Error retry rules have not been customized much beyond the default Scrapy behavior.
- The project has been built for learning and local testing, not for large production crawling.
- No authentication, proxy rotation, or advanced anti-blocking setup has been added.
- Docker must already be installed on the machine before the Docker setup is used.
- Scrapyd must be running before deployment or scheduling commands are used.
- The generated output folders are ignored locally, so they may not appear until the spider has been run.

## License

This project has been made for learning purpose assigned by W3 Engineers Ltd.
