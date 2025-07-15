import csv
import scrapy
from scrapy import Request
from dotenv import load_dotenv
from companyinfo.items import CompanyInfoItem
from companyinfo.google_search import search_company 

class CompanySpider(scrapy.Spider):
    name = 'company_spider'

    def start_requests(self):
        load_dotenv()
        # Read input CSV, handle BOM if present
        with open('input/input.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract fields safely
                company = row.get('company_name', '').strip()
                provided_domain = row.get('domain', '').strip()

                if provided_domain:
                    # If domain explicitly provided, use it directly
                    url = provided_domain if provided_domain.startswith('http') else f'https://{provided_domain}'
                    domain = url.split('/')[2]
                    item = CompanyInfoItem(domain=domain, company_name=company or domain, raw_text='')
                    yield Request(url, self.parse_page, meta={'item': item, 'source': 'provided'})
                else:
                    if not company:
                        self.logger.warning(f"Row missing both company_name and domain: {row}")
                        continue
                    # Perform Google CSE search
                    results = search(company, num=5)
                    if not results:
                        self.logger.warning(f'No search results for {company}')
                        continue
                    # Top result is the official site
                    top_url = results[0]['link']
                    domain = top_url.split('/')[2]
                    item = CompanyInfoItem(domain=domain, company_name=company, raw_text='')
                    yield Request(top_url, self.parse_page, meta={'item': item, 'source': 'official'})

                    # Optionally scrape Amazon/Walmart pages if found
                    for res in results[1:5]:
                        url = res.get('link', '')
                        if 'amazon.com' in url or 'walmart.com' in url:
                            yield Request(url, self.parse_page, meta={'item': item, 'source': 'third_party'})

    def parse_page(self, response):
        item = response.meta['item']
        source = response.meta.get('source', 'official')
        # Extract visible text nodes
        texts = response.xpath('//body//*[not(self::script or self::style)]//text()').getall()
        page_text = ' '.join(t.strip() for t in texts if t.strip())
        # Append to raw_text for LLM processing
        item['raw_text'] += f"{page_text}"
        # Once pages are processed, yield the item
        yield item