from hyrule_football.utils import get_logger
from functools import wraps
from typing import Dict, Optional
from copy import deepcopy
import httpx

logger = get_logger(__name__)


async def try_request(httpx_coroutine):
    try:
        response = await httpx_coroutine
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"❌ request failed: {e}")
        raise e


def httpx_defaults(*, headers: Optional[Dict] = None, params: Optional[Dict] = None):
    headers = deepcopy(headers) if headers else {}
    params = deepcopy(params) if params else {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_headers = kwargs.get("headers") or {}
            user_params = kwargs.get("params") or {}

            kwargs["headers"] = {**headers, **user_headers}
            kwargs["params"] = {**params, **user_params}

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def trace_httpx_request(request: httpx.Request):
    logger.info(f"{request.method} {request.url}")

    # if request.headers:
    #     print("Headers:")
    #     for k, v in request.headers.items():
    #         print(f"  {k}: {v}")

    if request.content:
        try:
            body = request.content.decode()
            logger.info(f"Body: {body}")
        except Exception:
            logger.info(f"Body (binary): {len(request.content)} bytes")
