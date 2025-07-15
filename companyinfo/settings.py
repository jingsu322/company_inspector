BOT_NAME = 'companyinfo'
SPIDER_MODULES = ['companyinfo.spiders']
NEWSPIDER_MODULE = 'companyinfo.spiders'

ITEM_PIPELINES = {
    'companyinfo.pipelines.CompanyInfoPipeline': 300,
}

FEEDS = {
    'output/company_data.json': {'format':'json','indent':4},
    'output/company_data.csv': {'format':'csv'}
}