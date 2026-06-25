import scrapy
class BooksWebScrapingItem(scrapy.Item):
    """
    This class acts as a clear structural blueprint (or schema) for a single book.
    """
    title= scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
    
