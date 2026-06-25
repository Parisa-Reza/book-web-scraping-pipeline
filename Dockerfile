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

# Mount two volumes /etc/scrapyd/ for Configuration and /var/lib/scrapyd/ for Scrapyd data, jobs, logs, eggs
VOLUME /etc/scrapyd/ /var/lib/scrapyd/

# Copy scrapyd.conf inside container
COPY ./scrapyd.conf /etc/scrapyd/
RUN mkdir -p /src/eggs/books_web_scraping 
COPY --from=build-stage /workdir/books_web_scraping.egg /src/eggs/books_web_scraping/1.egg 
# Scrapyd stores project versions as egg files like 1.egg, 2.egg

EXPOSE 6800
ENTRYPOINT ["scrapyd", "--pidfile="]