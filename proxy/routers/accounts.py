from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

import services.dopagent_scraper as scraper

from ..dependencies import get_auth_token

router = APIRouter()


class AccountsResponse(BaseModel):
    accounts: list[scraper.Account]


@router.get("/")
def fetch_all_accounts(
    account_counter: int = 1,
    auth_token: scraper.AuthToken = Depends(get_auth_token),
):
    accounts = scraper.fetch_accounts(auth_token, account_counter)
    return AccountsResponse(accounts=accounts)
