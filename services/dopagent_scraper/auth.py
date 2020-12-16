from pydantic import BaseModel

from .common import Spider, call_scraper


class AuthRequest(BaseModel):
    start_requests: str = True
    spider_name: str = Spider.auth_spider
    agent_id: str
    password: str


class AuthToken(BaseModel):
    first_name: str
    last_name: str
    dashboard_url: str
    change_password_url: str
    accounts_url: str
    agent_enquire_screen_url: str
    reports_url: str
    referer_header: str


def get_auth_token(agent_id: str, password: str) -> AuthToken:
    auth_request = AuthRequest(agent_id=agent_id, password=password)
    auth_response = call_scraper(auth_request)
    return AuthToken.parse_obj(auth_response.items[0])
