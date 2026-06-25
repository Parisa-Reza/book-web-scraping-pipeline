import scrapy
import random
from books_web_scraping.items import BooksWebScrapingItem

class BookSpider(scrapy.Spider):
    """
    A spider that crawls category pages completely, follows pagination, randomly samples 5 books, and extracts data elements 
    """
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response):
        """
        Dynamically extract category links from the sidebar menu.
        """
        self.logger.info("Discovering categories from homepage...")
        category_links = response.css(".side_categories ul li ul li a::attr(href)").getall()
       
        for link in category_links:
            absolute_category_link = response.urljoin(link)
            yield scrapy.Request(url=absolute_category_link, callback=self.parse_category)
    
    def parse_category(self, response):
        """
        Collect all book html selector card objects across pagination. Once all pages are collected, we pick 5 random cards and extract fields.
        """
  
        all_book_cards = response.meta.get('accumulated_cards', [])
        
        # category name from the main header text
        category_name = response.css(".page-header h1::text").get()
        if category_name:
            category_name = category_name.strip()

        #  all book article cards on this specific page
        current_page_cards = response.css("article.product_pod")
        
        # Store the actual HTML response snippet for each card so we can parse them later
        for card in current_page_cards:
            all_book_cards.append({
                'html_snippet': card.get(),
                'base_url': response.url,
                'category': category_name
            })

        # Checking for the next pagination link
        next_page = response.css("li.next a::attr(href)").get()
        
        if next_page:
            absolute_next_url = response.urljoin(next_page)
            yield scrapy.Request(
                url=absolute_next_url, 
                callback=self.parse_category,
                meta={'accumulated_cards': all_book_cards, 'category_name': category_name}
            )
        else:
            # End of pagination pages
            if not category_name:
                category_name = response.meta.get('category_name', 'Unknown')

            self.logger.info(f"Total books found in category '{category_name}': {len(all_book_cards)}")

            # Randomly select exactly 5 book cards from our total collection
            sample_size = min(5, len(all_book_cards))
            selected_cards = random.sample(all_book_cards, sample_size)

            self.logger.info(f"Randomly selected {sample_size} books from '{category_name}'")
            
            # Extract the 6 fields from the selected card elements
            for card_data in selected_cards:
              
                card_selector = scrapy.Selector(text=card_data['html_snippet'])
                
                item = BooksWebScrapingItem()
                item["category"] = card_data['category']

                item["title"] = card_selector.css("h3 a::attr(title)").get()

               
                item["price"] = card_selector.css(".product_price p.price_color::text").get()

              
                raw_avail = card_selector.css("p.instock.availability::text").getall()
                item["availability"] = "".join(raw_avail).strip() if raw_avail else None

              
                raw_href = card_selector.css("h3 a::attr(href)").get()
                item["product_url"] = scrapy.utils.url.urljoin_rfc(card_data['base_url'], raw_href) if raw_href else None

    
                raw_img = card_selector.css(".image_container img::attr(src)").get()
                item["image_url"] = scrapy.utils.url.urljoin_rfc(card_data['base_url'], raw_img) if raw_img else None

                yield item