from time import time
import pytest

from nhltv_lib.cookies import (
    create_nhl_cookie,
    save_cookie,
    load_cookie,
    save_cookies_to_txt,
)


@pytest.fixture(scope="function")
def mock_time(mocker):
    t = time()
    mocktime = mocker.patch("nhltv_lib.cookies.time")
    mocktime.return_value = t
    return t


@pytest.fixture(scope="function", autouse=True)
def mock_path(mocker):
    mocker.patch("os.path.isfile", return_value=True)


@pytest.fixture(scope="function")
def mock_touch(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    return mocker.patch("nhltv_lib.cookies.touch")


@pytest.fixture(scope="function")
def mockop(mocker):
    with open("tests/data/pickle_foobar", "rb") as f:
        mo = mocker.mock_open(read_data=f.read())
        mocker.patch("nhltv_lib.cookies.open", mo)
        return mo


@pytest.fixture(scope="function")
def mock_cookiejar(mocker):
    return mocker.patch("nhltv_lib.cookies.MozillaCookieJar.set_cookie")


def test_create_nhl_cookie(mock_time):
    assert create_nhl_cookie("foo", "bar").name == "foo"
    assert create_nhl_cookie("foo", "bar").value == "bar"
    assert create_nhl_cookie("foo", "bar").expires == int(mock_time + 7500)


def test_save_cookie(mocker, mockop):
    mpick = mocker.patch("pickle.dump")
    save_cookie({"foo": "bar"})
    mockop.assert_called_once_with("auth_cookie", "wb")
    mpick.assert_called_once_with({"foo": "bar"}, mockop())


def test_load_cookie(mock_path, mockop):
    assert load_cookie() == {"foo": "bar"}


def test_load_cookie_empty(mocker, mock_path):
    mo = mocker.mock_open(read_data=b"")
    mocker.patch("nhltv_lib.cookies.open", mo)
    assert load_cookie() == []


def test_load_cookie_touches(mock_touch, mockop):
    load_cookie()
    mock_touch.assert_called_once_with("auth_cookie")


def test_save_cookie_touches(mock_touch, mockop):
    save_cookie({"no": "op"})
    mock_touch.assert_called_once_with("auth_cookie")


def test_save_cookies_touches(mock_touch, mock_cookiejar):
    save_cookies_to_txt(["bar", "baz"], "foo")
    mock_touch.assert_called_once_with("foo")


def test_save_cookies_to_txt(mocker, mock_path, mock_cookiejar):
    call = mocker.call
    save_cookies_to_txt(["bar", "baz"], "foo")
    calls = [call("bar"), call("baz")]
    mock_cookiejar.assert_has_calls(calls)
