
"""
Helper module for calling Google Custom Search JSON API.
This file must reside inside the `companyinfo/` package so Scrapy can import it.
"""
from googleapiclient.discovery import build
from .config import settings

service = build('customsearch', 'v1', developerKey=settings.GOOGLE_API_KEY)

def search_company(query: str, num: int = 5) -> list:
    """
    Query Google CSE for `query` and return a list of result dicts.
    Each dict has keys: 'title', 'link', 'snippet'.
    """
    resp = service.cse().list(
        q=query,
        cx=settings.GOOGLE_CSE_ID,
        num=num
    ).execute()
    return resp.get('items', []) or []