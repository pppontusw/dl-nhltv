from typing import Optional, Any, List
import os
from time import time
import pickle
from http.cookiejar import MozillaCookieJar, Cookie
from requests.cookies import RequestsCookieJar

from nhltv_lib.common import touch

COOKIE_FILE = "auth_cookie"


def save_cookies_to_txt(cookies: List[Any], filename: str) -> None:
    # Ensure the cookie file exists
    if not os.path.isfile(filename):
        touch(filename)

    cjar = MozillaCookieJar(filename)
    for cookie in cookies:
        cjar.set_cookie(cookie)
    cjar.save(ignore_discard=False)


def load_cookie() -> List[Optional[Any]]:
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIE_FILE):
        touch(COOKIE_FILE)

    with open(COOKIE_FILE, "rb") as f:
        try:
            return pickle.load(f)
        except EOFError:
            return []


def save_cookie(cookies: RequestsCookieJar) -> None:
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIE_FILE):
        touch(COOKIE_FILE)

    with open(COOKIE_FILE, "wb") as f:
        return pickle.dump(cookies, f)


def create_nhl_cookie(name: str, value: str) -> Cookie:
    return Cookie(
        version=None,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=".nhl.com",
        domain_specified=False,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        discard=False,
        comment="TestCookie",
        comment_url=None,
        expires=(int(time()) + 7500),
        rest={},
    )
