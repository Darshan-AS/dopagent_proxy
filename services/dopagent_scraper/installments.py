from enum import Enum

from pydantic import BaseModel
from toolz import first

from .auth import AuthToken
from .common import CommonHeaderField, CommonRequestField, call_scraper
from .config import Spider


class PayMode(str, Enum):
    CASH = "CASH"
    DOP_CHEQUE = "DOP_CHEQUE"
    NON_DOP_CHEQUE = "NON_DOP_CHEQUE"


class InstallmentAccount(BaseModel):
    account_no: str
    no_of_installments: int


class InstallmentsRequest(BaseModel):
    request: CommonRequestField
    spider_name: str = Spider.installments_spider
    agent_id: str
    pay_mode: PayMode
    accounts: list[InstallmentAccount]


def prepare_installments(
    auth_token: AuthToken,
    agent_id: str,
    installment_accounts: list[InstallmentAccount],
    pay_mode: PayMode = PayMode.CASH,
) -> str:
    installments_request = InstallmentsRequest(
        request=CommonRequestField(
            url=auth_token.agent_enquire_screen_url,
            headers=CommonHeaderField(Referer=auth_token.referer_header),
        ),
        agent_id=agent_id,
        pay_mode=pay_mode,
        accounts=installment_accounts,
    )
    common_response = call_scraper(installments_request)
    return first(common_response.items)['reference_number']
