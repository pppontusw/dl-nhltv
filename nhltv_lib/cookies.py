import os
from time import time
import pickle
from http.cookiejar import MozillaCookieJar

import requests

from nhltv_lib.common import touch

COOKIE_FILE = "auth_cookie"


def save_cookies_to_txt(cookies, filename):
    # Ensure the cookie file exists
    if not os.path.isfile(filename):
        touch(filename)

    cjar = MozillaCookieJar(filename)
    for cookie in cookies:
        cjar.set_cookie(cookie)
    cjar.save(ignore_discard=False)


def load_cookie():
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIE_FILE):
        touch(COOKIE_FILE)

    with open(COOKIE_FILE, "rb") as f:
        try:
            return pickle.load(f)
        except EOFError:
            return []


def save_cookie(cookies):
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIE_FILE):
        touch(COOKIE_FILE)

    with open(COOKIE_FILE, "wb") as f:
        return pickle.dump(cookies, f)


def create_nhl_cookie(name, value):
    return requests.cookies.create_cookie(
        name,
        value,
        port=None,
        domain=".nhl.com",
        path="/",
        secure=False,
        expires=(int(time()) + 7500),
        discard=False,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )
