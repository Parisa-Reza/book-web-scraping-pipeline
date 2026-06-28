# multistage docker build project

# stage 1 : building the deployable packages with .egg file
FROM python:3.11 AS build-stage
RUN pip install --no-cache-dir scrapyd-client
WORKDIR /workdir
COPY . .
ENV PYTHONPATH=/workdir
RUN scrapyd-deploy local_target --build-egg=books_web_scraping.egg

#  stage 2 : Build clean production container with alpine
FROM python:3.11-alpine

# Install Scrapy compiling dependencies and remove them immediately after pip install
RUN apk --no-cache add --virtual build-dependencies \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libxml2-dev \
    libxslt-dev \
 && pip install --no-cache-dir \
    scrapy \
    scrapyd \
 && apk del build-dependencies \
 && apk add \
    openssl \
    libxml2 \
    libxslt

WORKDIR /app

ENV SCRAPY_OUTPUT_BASE=/app

COPY ./scrapyd.conf /etc/scrapyd/scrapyd.conf

RUN sed -i "s/bind_address = 127.0.0.1/bind_address = 0.0.0.0/" /etc/scrapyd/scrapyd.conf \
 && sed -i "s|items_dir = .scrapyd/items|items_dir =|" /etc/scrapyd/scrapyd.conf \
 && mkdir -p \
    /app/.scrapyd/eggs/books_web_scraping \
    /app/.scrapyd/logs \
    /app/.scrapyd/dbs \
    /app/output \
    /app/data

COPY --from=build-stage /workdir/books_web_scraping.egg /app/.scrapyd/eggs/books_web_scraping/1.egg

EXPOSE 6800
ENTRYPOINT ["scrapyd", "--pidfile="]