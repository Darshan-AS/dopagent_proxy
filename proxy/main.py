from typing import List

from fastapi import FastAPI, status
from fastapi.params import Body, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic.main import BaseModel
from requests.sessions import Request
from starlette.responses import JSONResponse

import services.dopagent_scraper as scraper

app = FastAPI()
security = HTTPBasic()


@app.exception_handler(scraper.DopagentException)
def dopagent_exception_handler(request: Request, exception: scraper.DopagentException):
    return JSONResponse(
        status_code=500,
        content={"message": exception.message, "extra": exception.extra},
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    return scraper.get_auth_token(credentials.username, credentials.password)


@app.get("/accounts")
def fetch_all_accounts(
    account_counter: int = 1,
    auth_token: scraper.AuthToken = Depends(authenticate),
):
    accounts = scraper.fetch_accounts(auth_token, account_counter)
    return {"accounts": accounts}


@app.put("/installments", status_code=status.HTTP_201_CREATED)
def make_installments(
    installments: List[scraper.InstallmentAccount],
    payMode: scraper.PayMode = Body(scraper.PayMode.CASH),
    auth_token: scraper.AuthToken = Depends(authenticate),
):
    reference_number = scraper.prepare_installments(
        auth_token,
        installments,
        payMode,
    )
    return {"reference_number": reference_number}


@app.get("/reports/{reference_number}")
def fetch_report(
    reference_number: str,
    auth_token: scraper.AuthToken = Depends(authenticate),
):
    report = scraper.fetch_report(auth_token, reference_number)
    return report
