import requests
from pydantic import BaseModel

from .config import BASE_URL


class CommonHeaderField(BaseModel):
    Referer: str


class CommonRequestField(BaseModel):
    url: str
    headers: CommonHeaderField


class CommonResponse(BaseModel):
    status: str
    spider_name: str
    items: list
    items_dropped: list
    stats: dict


def call_scraper(request_body: BaseModel) -> CommonResponse:
    response = requests.post(BASE_URL, json=request_body.dict())
    return CommonResponse.parse_raw(response.text)
