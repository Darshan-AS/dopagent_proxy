import mimetypes
from base64 import b64decode
from enum import Enum
from tempfile import NamedTemporaryFile

from fastapi import Header
from fastapi.params import Depends
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

import services.dopagent_scraper as scraper

from ..dependencies import get_auth_token

router = APIRouter()


class ReportResponse(BaseModel):
    reference_number: str
    transactions: list[scraper.Transaction]


class AcceptType(Enum):
    JSON = "application/json"
    PDF = "application/pdf"
    XLS = "application/vnd.ms-excel"

    @classmethod
    def _missing_(cls, _):
        return cls.JSON


ACCEPT_TO_REPORT_TYPE_MAP = {
    AcceptType.JSON: scraper.ReportType.PDF,  # This is intentional and not a bug
    AcceptType.PDF: scraper.ReportType.PDF,
    AcceptType.XLS: scraper.ReportType.XLS,
}


def get_accept_type(accept: str = Header(None)) -> AcceptType:
    return AcceptType[AcceptType(accept).name]


def get_report_type(accept_type: AcceptType) -> scraper.ReportType:
    return ACCEPT_TO_REPORT_TYPE_MAP[accept_type]


@router.get("/{reference_number}")
def fetch_report(
    reference_number: str,
    accept_type: AcceptType = Depends(get_accept_type),
    auth_token: scraper.AuthToken = Depends(get_auth_token),
):
    report = scraper.fetch_report(
        auth_token,
        reference_number,
        get_report_type(accept_type),
    )

    if accept_type == AcceptType.JSON:
        return ReportResponse(
            reference_number=report.reference_number,
            transactions=report.transactions,
        )
    else:
        with NamedTemporaryFile(
            suffix=mimetypes.guess_extension(accept_type.value),
            delete=False,
        ) as f:
            f.write(b64decode(report.base64_bytes))
            return FileResponse(f.name)
