import pytest
from nhltv_lib.requests_wrapper import get, post


@pytest.fixture(scope="function")
def mock_requests(mocker):
    return mocker.patch("nhltv_lib.requests_wrapper.requests")


def test_req_wrap_get(mocker, mock_requests):
    get("book")
    mock_requests.get.assert_called_once_with("book")


def test_req_wrap_get_kw(mocker, mock_requests):
    get(test="boom")
    mock_requests.get.assert_called_once_with(test="boom")


def test_req_wrap_get_both(mocker, mock_requests):
    get("book", test="boom")
    mock_requests.get.assert_called_once_with("book", test="boom")


def test_req_wrap_get_exception(mocker, mock_requests):
    m_slp = mocker.patch("nhltv_lib.requests_wrapper.sleep")
    mock_requests.get.side_effect = [ValueError, 1]
    assert get() == 1
    m_slp.assert_called_once_with(15)


def test_req_wrap_get_exception_exhaust(mocker, mock_requests):
    mocker.patch("nhltv_lib.requests_wrapper.sleep")
    mock_requests.get.side_effect = [
        ValueError,
        ValueError,
        ValueError,
        ValueError,
        ValueError,
    ]
    with pytest.raises(ValueError):
        get()


def test_req_wrap_post(mocker, mock_requests):
    post("book")
    mock_requests.post.assert_called_once_with("book")


def test_req_wrap_post_kw(mocker, mock_requests):
    post(test="boom")
    mock_requests.post.assert_called_once_with(test="boom")


def test_req_wrap_post_both(mocker, mock_requests):
    post("book", test="boom")
    mock_requests.post.assert_called_once_with("book", test="boom")


def test_req_wrap_post_exception(mocker, mock_requests):
    m_slp = mocker.patch("nhltv_lib.requests_wrapper.sleep")
    mock_requests.post.side_effect = [ValueError, 1]
    assert post() == 1
    m_slp.assert_called_once_with(15)


def test_req_wrap_post_exception_exhaust(mocker, mock_requests):
    mocker.patch("nhltv_lib.requests_wrapper.sleep")
    mock_requests.post.side_effect = [
        ValueError,
        ValueError,
        ValueError,
        ValueError,
        ValueError,
    ]
    with pytest.raises(ValueError):
        post()
