from fastapi.params import Depends
from fastapi.security.http import HTTPBasic, HTTPBasicCredentials

import services.dopagent_scraper as scraper

security = HTTPBasic()


def get_auth_token(
    credentials: HTTPBasicCredentials = Depends(security),
) -> scraper.AuthToken:
    return scraper.get_auth_token(credentials.username, credentials.password)
