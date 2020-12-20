from enum import Enum
from typing import Any, Callable, Generic, List, Optional, TypeVar

import requests
from pydantic import BaseModel, ValidationError, validator
from pydantic.generics import GenericModel

from .config import BASE_URL, Spider

DataT = TypeVar("DataT")


class HeadersField(BaseModel):
    Referer: str


class RequestField(BaseModel):
    url: str
    headers: HeadersField


class CommonRequest(BaseModel):
    request: RequestField
    spider_name: Spider

    @classmethod
    def __init_subclass__(cls, spider, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.spider_name = spider

    # pylint: disable=no-self-argument
    def __init__(__pydantic_self__, url, referer_header, **data: Any) -> None:
        request = RequestField(
            url=url,
            headers=HeadersField(Referer=referer_header),
        )
        super().__init__(
            request=request,
            spider_name=__pydantic_self__.spider_name,
            **data,
        )


class Status(str, Enum):
    OK = "ok"
    ERROR = "error"


class OkResponse(GenericModel, Generic[DataT]):
    status: Status
    spider_name: str
    items: List[DataT]
    items_dropped: list
    stats: dict


class ErrorResponse(BaseModel):
    status: Status
    code: Optional[int] = None
    message: Optional[str] = None


class CommonResponse(GenericModel, Generic[DataT]):
    data: Optional[OkResponse[DataT]] = None
    error: Optional[ErrorResponse] = None

    # pylint: disable=no-self-argument
    @validator("error", always=True)
    def check_consistency(cls, v, values):
        if v is not None and values["data"] is not None:
            raise ValueError("must not provide both data and error")
        if v is None and values.get("data") is None:
            raise ValueError("must provide data or error")
        return v

    def has_data(self):
        return self.data is not None

    def has_error(self):
        return self.error is not None

    def map_response(
        self,
        data_fn: Callable[[OkResponse[DataT]], Any],
        error_fn: Callable[[ErrorResponse], Any] = id,
    ):
        return data_fn(self.data) if self.has_data() else error_fn(self.error)


class DopagentException(Exception):
    def __init__(self, message: str = "Something went wrong", extra: Any = None):
        self.message = message
        self.extra = extra
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.extra}"

    @classmethod
    def throw(cls, *args, **kwargs):
        raise cls(*args, **kwargs)


def call_scraper(request_body: BaseModel, data_item: DataT) -> CommonResponse[DataT]:
    response = requests.post(BASE_URL, json=request_body.dict())

    try:
        return CommonResponse[data_item](
            data=OkResponse[data_item].parse_raw(response.text)
        )
    except ValidationError:
        pass

    try:
        return CommonResponse[data_item](error=ErrorResponse.parse_raw(response.text))
    except ValidationError:
        return CommonResponse[data_item](
            error=ErrorResponse(
                status=Status.ERROR,
                message=f"Unknown Error: {response.text}",
            )
        )
