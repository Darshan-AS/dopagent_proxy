from pydantic import BaseModel
from toolz import first

from .common import DopagentException, call_scraper
from .config import Spider


class AuthRequest(BaseModel):
    start_requests: str = True
    spider_name: str = Spider.auth_spider
    agent_id: str
    password: str


class AuthToken(BaseModel):
    first_name: str
    last_name: str
    agent_id: str
    dashboard_url: str
    change_password_url: str
    accounts_url: str
    agent_enquire_screen_url: str
    reports_url: str
    referer_header: str


def get_auth_token(agent_id: str, password: str) -> AuthToken:
    auth_request = AuthRequest(agent_id=agent_id, password=password)
    common_response = call_scraper(auth_request, data_item=AuthToken)
    return common_response.map_response(
        lambda d: first(d.items)
        if d.items
        else DopagentException.throw("Unauthorized"),
        lambda e: DopagentException.throw("Unauthorized", e),
    )
