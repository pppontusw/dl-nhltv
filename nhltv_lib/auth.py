from typing import Optional
from datetime import datetime
import nhltv_lib.requests_wrapper as requests
from nhltv_lib.arguments import get_arguments
from nhltv_lib.constants import HEADERS
from nhltv_lib.cookies import load_cookie, save_cookie
from nhltv_lib.common import tprint, verify_request_200
from nhltv_lib.urls import LOGIN_URL
from nhltv_lib.types import NHLTVUser


def login_and_save_cookie() -> None:
    """
    Logs in to NHLTV.com and saves the auth cookie for later use
    """

    user = _get_username_and_password()

    authorization = get_auth_cookie_value()
    if authorization:
        HEADERS.update({"Authorization": authorization})

    login_data = {"email": user.username, "password": user.password}

    tprint("Logging in to NHL.com..")

    req = requests.post(
        LOGIN_URL,
        headers={**HEADERS, "Authorization": authorization},
        json=login_data,
        timeout=15,
    )

    verify_request_200(req, "Failed to login to NHLTV.com")

    save_cookie(req.cookies)


def _get_username_and_password() -> NHLTVUser:
    """
    Get username and password as NHLTVUser tuple
    """
    arguments = get_arguments()
    return NHLTVUser(arguments.username, arguments.password)


def get_auth_cookie_value() -> Optional[str]:
    """
    Returns Authorization field from any cookie, if none exist or all are
    expired then returns None
    """
    cookiejar = load_cookie()

    for cookie in cookiejar:
        if cookie and cookie.name == "token" and not cookie.is_expired():
            return cookie.value

    return None


def get_auth_cookie_value_login_if_needed() -> str:
    """
    This gets the value of the Authorization cookie, if it's not set
    it will log us in and then try again until the cookie is available
    """
    authorization: Optional[str] = get_auth_cookie_value()
    if not authorization:
        login_and_save_cookie()
        return get_auth_cookie_value_login_if_needed()
    return authorization


def get_auth_cookie_expires_in_minutes() -> Optional[float]:
    """
    Returns the number of minutes until Authorization cookie expires
    """

    cookiejar = load_cookie()

    for cookie in cookiejar:
        if cookie and cookie.name == "token" and not cookie.is_expired():
            expires = datetime.fromtimestamp(cookie.expires)
            time_remaining = expires - datetime.now()

            return time_remaining.seconds / 60

    return None
