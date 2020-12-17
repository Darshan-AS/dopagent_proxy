from enum import Enum

BASE_URL = "http://localhost:9080/crawl.json"


class Spider(str, Enum):
    auth_spider = 'auth'
    accounts_spider = 'accounts'
    installments_spider = 'installments'
    reports_spider = 'reports'
