from datetime import date

from pydantic import BaseModel

from .auth import AuthToken
from .common import CommonHeaderField, CommonRequestField, call_scraper
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


class AccountsRequest(BaseModel):
    request: CommonRequestField
    spider_name: str = Spider.accounts_spider
    agent_id: str
    account_counter: int


def fetch_accounts(
    auth_token: AuthToken, agent_id: str, account_counter: int = 1
) -> list[Account]:
    accounts_request = AccountsRequest(
        request=CommonRequestField(
            url=auth_token.agent_enquire_screen_url,
            headers=CommonHeaderField(Referer=auth_token.referer_header),
        ),
        agent_id=agent_id,
        account_counter=account_counter,
    )
    common_response = call_scraper(accounts_request)
    return list(map(Account.parse_obj, common_response.items))
