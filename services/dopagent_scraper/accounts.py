from datetime import date
from typing import Any

from pydantic import BaseModel

from .auth import AuthToken
from .common import CommonRequest, DopagentException, call_scraper
from .config import Spider


class Account(BaseModel):
    account_no: str
    name: str
    opening_date: date
    denomination: float
    total_deposit_amount: float
    month_paid_upto: int
    next_installment_due_date: date
    date_of_last_deposit: date
    rebate_paid: float
    default_fee: float
    default_installments: int
    pending_installments: int


class AccountsRequest(CommonRequest, spider=Spider.accounts_spider):
    agent_id: str
    account_counter: int

    # pylint: disable=no-self-argument
    def __init__(__pydantic_self__, auth_token: AuthToken, **kwargs: Any) -> None:
        super().__init__(
            auth_token.agent_enquire_screen_url,
            auth_token.referer_header,
            **kwargs,
        )


def fetch_accounts(
    auth_token: AuthToken,
    account_counter: int = 1,
) -> list[Account]:
    accounts_request = AccountsRequest(
        auth_token,
        agent_id=auth_token.agent_id,
        account_counter=account_counter,
    )
    common_response = call_scraper(accounts_request, data_item=Account)
    return common_response.map_response(
        lambda d: d.items,
        lambda e: DopagentException.throw("Error fetching accounts", e),
    )
