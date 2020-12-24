from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from toolz import first

from .auth import AuthToken
from .common import CommonRequest, DopagentException, call_scraper
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


class ReportsRequest(CommonRequest, spider=Spider.reports_spider):
    agent_id: str
    report_type: ReportType
    reference_number: str

    # pylint: disable=no-self-argument
    def __init__(__pydantic_self__, auth_token: AuthToken, **kwargs: Any) -> None:
        super().__init__(
            auth_token.reports_url,
            auth_token.referer_header,
            **kwargs,
        )


def get_report(
    auth_token: AuthToken,
    agent_id: str,
    reference_number: str,
    report_type: ReportType = ReportType.PDF,
) -> Report:
    reports_request = ReportsRequest(
        auth_token,
        agent_id=agent_id,
        report_type=report_type,
        reference_number=reference_number,
    )
    common_response = call_scraper(reports_request, data_item=Report)
    print(common_response)
    return common_response.map_response(
        lambda d: first(d.items)
        if d.items
        else DopagentException.throw("Error fetching report"),
        lambda e: DopagentException.throw("Error fetching report", e),
    )
