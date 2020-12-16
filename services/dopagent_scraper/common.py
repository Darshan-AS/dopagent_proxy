from enum import Enum

import requests
from pydantic import BaseModel

from .config import BASE_URL


class Spider(str, Enum):
    auth_spider = 'auth'
    accounts_spider = 'accounts'
    installments_spider = 'installments'
    reports_spider = 'reports'


class CommonResponse(BaseModel):
    status: str
    spider_name: str
    items: list
    items_dropped: list
    stats: dict


def call_scraper(request_body: BaseModel) -> CommonResponse:
    response = requests.post(BASE_URL, json=request_body.dict())
    return CommonResponse.parse_raw(response.text)
