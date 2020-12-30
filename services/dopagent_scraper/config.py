from enum import Enum

BASE_URL = "http://scraper:9080/crawl.json" # TODO: Check this


class Spider(str, Enum):
    auth_spider = "auth"
    accounts_spider = "accounts"
    installments_spider = "installments"
    reports_spider = "reports"
