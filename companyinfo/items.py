import scrapy

class CompanyInfoItem(scrapy.Item):
    domain = scrapy.Field()
    company_name = scrapy.Field()
    manufactures_in_house = scrapy.Field()
    in_house_details = scrapy.Field()
    outsourced = scrapy.Field()
    outsourcing_partners = scrapy.Field()
    parent_company = scrapy.Field()
    affiliate_companies = scrapy.Field()
    last_updated = scrapy.Field()
    raw_text = scrapy.Field()
    extraction_status = scrapy.Field() 