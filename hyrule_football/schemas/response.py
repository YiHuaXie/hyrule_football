from typing import Any, TypeVar, Generic
from pydantic import BaseModel

# 定义一个类型变量，用于泛型
T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    status: bool = False
    message: str = ""
    data: T = None  # 使用泛型类型 T 来表示 data 的类型

    @classmethod
    def success(cls, message: str = "", data: T = None) -> "Response[T]":
        return cls(status=True, message=message, data=data)

    @classmethod
    def failed(cls, message: str, data: T = None) -> "Response[T]":
        return cls(status=False, message=message, data=data)
