from datetime import datetime
from collections import namedtuple
import logging
import requests
from nhltv_lib.arguments import get_arguments
from nhltv_lib.constants import TOKEN_AUTH_HEADERS, HEADERS
from nhltv_lib.cookies import load_cookie, save_cookie
from nhltv_lib.exceptions import AuthenticationFailed, RequestFailed
from nhltv_lib.urls import TOKEN_URL, LOGIN_URL

logger = logging.getLogger("nhltv")

NHLTVUser = namedtuple("NHLTVUser", ["username", "password"])


def login_and_save_cookie():
    """
    Logs in to NHLTV.com and saves the auth cookie for later use
    """

    user = _get_username_and_password()

    access_token = _get_access_token()

    authorization = get_auth_cookie_value()
    if not authorization:
        authorization = access_token

    login_data = {
        "nhlCredentials": {"email": user.username, "password": user.password}
    }

    logger.debug("Logging in to NHL.com..")

    req = requests.post(
        LOGIN_URL,
        headers={**HEADERS, "Authorization": authorization},
        json=login_data,
    )

    verify_request_200(req)

    save_cookie(req.cookies)


def _get_username_and_password():
    """
    Get username and password as NHLTVUser tuple
    """
    arguments = get_arguments()
    return NHLTVUser(arguments.username, arguments.password)


def get_auth_cookie_value():
    """
    Returns Authorization field from any cookie, if none exist or all are
    expired then returns None
    """
    cookiejar = load_cookie()

    for cookie in cookiejar:
        if cookie.name == "Authorization" and not cookie.is_expired():
            return cookie.value

    return None


def get_auth_cookie_expires_in_minutes():
    """
    Returns the number of minutes until Authorization cookie expires
    """

    cookiejar = load_cookie()

    for cookie in cookiejar:
        if cookie.name == "Authorization" and not cookie.is_expired():
            expires = datetime.fromtimestamp(cookie.expires)
            time_remaining = expires - datetime.now()

            return time_remaining.seconds / 60


def _get_access_token():
    """
    Returns an NHLTV access token
    """
    return (
        requests.post(TOKEN_URL, headers=TOKEN_AUTH_HEADERS)
        .json()
        .get("access_token")
    )


def verify_request_200(req):
    """
    Validates that the request was successful (200) or
    raises appropriate Exception
    """
    if req.status_code != 200:
        logger.error("There was an error with the request")
        if req.status_code == 401:
            msg = "Your username and password is likely incorrect"
            logger.error(msg)
            raise AuthenticationFailed(msg)
        raise RequestFailed
