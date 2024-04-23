from unittest.mock import PropertyMock
from http.cookiejar import Cookie, CookieJar
from datetime import datetime, timedelta
import pytest
import requests_mock
from nhltv_lib.auth import (
    login_and_save_cookie,
    get_auth_cookie_value,
    _get_username_and_password,
    NHLTVUser,
    get_auth_cookie_expires_in_minutes,
    get_auth_cookie_value_login_if_needed,
)
from nhltv_lib.common import verify_request_200
from nhltv_lib.exceptions import AuthenticationFailed, RequestFailed
from nhltv_lib.urls import LOGIN_URL
from nhltv_lib.constants import HEADERS


@pytest.fixture
def mock_load_cookie(mocker):
    return mocker.patch("nhltv_lib.auth.load_cookie", return_value=[])


@pytest.fixture
def mock_get_auth_cookie_value(mocker):
    return mocker.patch(
        "nhltv_lib.auth.get_auth_cookie_value", return_value="bar"
    )


def test_get_auth_cookie_value_login_if_needed(
    mocker, mock_get_auth_cookie_value
):
    assert get_auth_cookie_value_login_if_needed() == "bar"
    mocker.patch("nhltv_lib.auth.login_and_save_cookie")


def test_get_auth_cookie_value_login_if_needed_w_login(
    mocker, mock_get_auth_cookie_value
):
    mock_get_auth_cookie_value.side_effect = [None, "bar"]
    ml = mocker.patch("nhltv_lib.auth.login_and_save_cookie")
    assert get_auth_cookie_value_login_if_needed() == "bar"
    ml.assert_called_once()


def test_login(mocker, mock_load_cookie):
    mocker.patch(
        "nhltv_lib.auth._get_username_and_password",
        return_value=NHLTVUser("foo", "bar"),
    )
    mock_save_cookie = mocker.patch("nhltv_lib.auth.save_cookie")
    mock_cookie = {"authorization": "foo"}

    with requests_mock.Mocker() as mock_req:
        mock_req.post(LOGIN_URL, cookies=mock_cookie)

        login_and_save_cookie()
        mock_save_cookie.assert_called_once_with(mock_cookie)


def test_login_w_cookie(mocker, mock_load_cookie, mock_get_auth_cookie_value):
    mocker.patch(
        "nhltv_lib.auth._get_username_and_password",
        return_value=NHLTVUser("foo", "bar"),
    )
    mock_save_cookie = mocker.patch("nhltv_lib.auth.save_cookie")
    mock_cookie = {"authorization": "foo"}

    with requests_mock.Mocker() as mock_req:
        mock_req.post(
            LOGIN_URL,
            cookies=mock_cookie,
            headers={**HEADERS, "Authorization": "bar"},
        )

        login_and_save_cookie()
        mock_save_cookie.assert_called_once_with(mock_cookie)


def test_get_username_pw():
    assert _get_username_and_password() == NHLTVUser("username", "password")


def test_get_auth_cookie_expires_in_minutes(mocker, mock_load_cookie):
    get_auth_cookie_expires_in_minutes() is None


def test_get_auth_cookie_expires_with_jar(mocker, mock_load_cookie):
    mock_cookiejar = CookieJar()
    da = datetime.now()

    # Cookie(version, name, value, port, port_specified, domain,
    # domain_specified, domain_initial_dot, path, path_specified,
    # secure, discard, comment, comment_url, rest)
    c = Cookie(
        None,
        "token",
        "bar",
        "80",
        "80",
        "www.foo.bar",
        None,
        None,
        "/",
        None,
        False,
        False,
        "TestCookie",
        None,
        None,
        None,
    )
    c.expires = (da + timedelta(minutes=12)).timestamp()
    mock_cookiejar.set_cookie(c)

    mockdate = mocker.patch("nhltv_lib.auth.datetime")
    mockdate.now.return_value = da
    mockdate.fromtimestamp.return_value = da + timedelta(minutes=12)
    mock_load_cookie.return_value = mock_cookiejar

    assert get_auth_cookie_expires_in_minutes() == 12


def test_get_auth_cookie_value(mocker, mock_load_cookie):
    assert get_auth_cookie_value() is None


def test_verify_request_200_201():
    req = PropertyMock()
    req.status_code = 201
    with pytest.raises(RequestFailed):
        verify_request_200(req, "test")


def test_verify_request_200_401():
    req = PropertyMock()
    req.status_code = 401
    with pytest.raises(AuthenticationFailed):
        verify_request_200(req, "test")
