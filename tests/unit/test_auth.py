from unittest.mock import PropertyMock
from http.cookiejar import Cookie, CookieJar
from datetime import datetime, timedelta
import pytest
import requests_mock
from nhltv_lib.auth import (
    login_and_save_cookie,
    get_auth_cookie_value,
    _get_access_token,
    _get_username_and_password,
    NHLTVUser,
    verify_request_200,
)
from nhltv_lib.exceptions import AuthenticationFailed, RequestFailed
from nhltv_lib.urls import TOKEN_URL, LOGIN_URL, get_session_key_url


def test_login(mocker):
    mocker.patch(
        "nhltv_lib.auth._get_username_and_password",
        return_value=NHLTVUser("foo", "bar"),
    )
    mocker.patch("nhltv_lib.auth.load_cookie", return_value=[])
    mock_save_cookie = mocker.patch("nhltv_lib.auth.save_cookie")
    mock_cookie = {"authorization": "foo"}

    with requests_mock.Mocker() as mock_req:
        mock_req.post(TOKEN_URL, json={"access_token": "bar"})
        mock_req.post(LOGIN_URL, cookies=mock_cookie)

        login_and_save_cookie()
        mock_save_cookie.assert_called_once_with(mock_cookie)


def test_get_username_pw():
    assert _get_username_and_password() == NHLTVUser("username", "password")


def test_get_auth_cookie_value(mocker):
    mocker.patch("nhltv_lib.auth.load_cookie", return_value=[])
    assert get_auth_cookie_value() is None


def test_get_auth_cookie_value_with_jar(mocker):
    mock_cookiejar = CookieJar()

    # Cookie(version, name, value, port, port_specified, domain,
    # domain_specified, domain_initial_dot, path, path_specified,
    # secure, discard, comment, comment_url, rest)
    c = Cookie(
        None,
        "Authorization",
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
    c.expires = (datetime.now() + timedelta(hours=12)).timestamp()
    mock_cookiejar.set_cookie(c)

    mocker.patch("nhltv_lib.auth.load_cookie", return_value=mock_cookiejar)
    assert get_auth_cookie_value() == "bar"


def test_get_access_token():
    with requests_mock.Mocker() as mock_req:
        mock_req.post(TOKEN_URL, json={"access_token": "bar"})
        assert _get_access_token() == "bar"


def test_verify_request_200_201():
    req = PropertyMock()
    req.status_code = 201
    with pytest.raises(RequestFailed):
        verify_request_200(req)


def test_verify_request_200_401():
    req = PropertyMock()
    req.status_code = 401
    with pytest.raises(AuthenticationFailed):
        verify_request_200(req)

