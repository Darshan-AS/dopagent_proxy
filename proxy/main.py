from typing import List, Optional

from fastapi import FastAPI, Header, status
from fastapi.params import Body, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic.main import BaseModel
from requests.sessions import Request
from starlette.responses import JSONResponse

import services.dopagent_scraper as scraper

from .routers import accounts, installments, reports

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(accounts.router, prefix="/accounts")
app.include_router(installments.router, prefix="/installments")
app.include_router(reports.router, prefix="/reports")


@app.exception_handler(scraper.DopagentException)
def dopagent_exception_handler(_: Request, exception: scraper.DopagentException):
    return JSONResponse(
        status_code=500,
        content={"message": exception.message, "extra": exception.extra},
    )
