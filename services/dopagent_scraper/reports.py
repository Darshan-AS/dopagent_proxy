from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from toolz import first

from .auth import AuthToken
from .common import CommonHeaderField, CommonRequestField, call_scraper
from .config import Spider


class ReportType(str, Enum):
    PDF = "PDF"
    XLS = "XLS"


class Transaction(BaseModel):
    reference_number: str
    account_number: str
    total_deposit_amount: float
    no_of_installments: int
    rebate: float
    default_fee: float
    status: str
    last_created_date_and_time: datetime


class Report(BaseModel):
    reference_number: str
    report_type: ReportType
    transactions: list[Transaction]
    base64_bytes: bytes


class ReportsRequest(BaseModel):
    request: CommonRequestField
    spider_name: str = Spider.reports_spider
    agent_id: str
    report_type: ReportType
    reference_number: str


def get_report(
    auth_token: AuthToken,
    agent_id: str,
    reference_number: str,
    report_type: ReportType = ReportType.PDF,
) -> Report:
    reports_request = ReportsRequest(
        request=CommonRequestField(
            url=auth_token.reports_url,
            headers=CommonHeaderField(Referer=auth_token.referer_header),
        ),
        agent_id=agent_id,
        report_type=report_type,
        reference_number=reference_number,
    )
    common_response = call_scraper(reports_request)
    return Report.parse_obj(first(common_response.items))
