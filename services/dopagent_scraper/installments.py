from enum import Enum
from typing import Any

from pydantic import BaseModel
from toolz import first

from .auth import AuthToken
from .common import CommonRequest, DopagentException, call_scraper
from .config import Spider


class PayMode(str, Enum):
    CASH = "CASH"
    DOP_CHEQUE = "DOP_CHEQUE"
    NON_DOP_CHEQUE = "NON_DOP_CHEQUE"


class InstallmentAccount(BaseModel):
    account_no: str
    no_of_installments: int


class InstallmentsRequest(CommonRequest, spider=Spider.installments_spider):
    agent_id: str
    pay_mode: PayMode
    accounts: list[InstallmentAccount]

    # pylint: disable=no-self-argument
    def __init__(__pydantic_self__, auth_token: AuthToken, **kwargs: Any) -> None:
        super().__init__(
            auth_token.agent_enquire_screen_url,
            auth_token.referer_header,
            **kwargs,
        )


def prepare_installments(
    auth_token: AuthToken,
    agent_id: str,
    installment_accounts: list[InstallmentAccount],
    pay_mode: PayMode = PayMode.CASH,
) -> str:
    installments_request = InstallmentsRequest(
        auth_token,
        agent_id=agent_id,
        pay_mode=pay_mode,
        accounts=installment_accounts,
    )
    common_response = call_scraper(installments_request, data_item=dict)
    return common_response.map_response(
        lambda d: rn
        if d.items and (rn := first(d.items).get("reference_number"))
        else DopagentException.throw("Error preparing installments"),
        lambda e: DopagentException.throw("Error preparing installments", e),
    )
