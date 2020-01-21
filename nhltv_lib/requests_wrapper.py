from typing import Any, Callable
from time import sleep
import requests

max_retries = 5


def retry_function(function: Callable, *args, **kwargs) -> Any:
    for i in range(max_retries):
        try:
            req = function(*args, **kwargs)
            return req
        except Exception as e:
            if i == max_retries - 1:
                raise e
            else:
                sleep(15)


def get(*args, **kwargs) -> Any:
    return retry_function(requests.get, *args, **kwargs)


def post(*args, **kwargs) -> Any:
    return retry_function(requests.post, *args, **kwargs)
