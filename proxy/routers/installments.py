from typing import List

from fastapi import status
from fastapi.params import Body, Depends
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

import services.dopagent_scraper as scraper

from ..dependencies import get_auth_token

router = APIRouter()


class InstallmentsResponse(BaseModel):
    reference_number: str


@router.put("/", status_code=status.HTTP_201_CREATED)
def make_installments(
    installments: List[scraper.InstallmentAccount],
    payMode: scraper.PayMode = Body(scraper.PayMode.CASH),
    auth_token: scraper.AuthToken = Depends(get_auth_token),
):
    reference_number = scraper.prepare_installments(
        auth_token,
        installments,
        payMode,
    )
    return InstallmentsResponse(reference_number=reference_number)
