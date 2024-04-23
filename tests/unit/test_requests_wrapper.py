import pytest
from nhltv_lib.requests_wrapper import get, post


@pytest.fixture(scope="function")
def mock_requests(mocker):
    return mocker.patch("nhltv_lib.requests_wrapper.requests")


@pytest.fixture(scope="function")
def mock_sleep(mocker):
    return mocker.patch("nhltv_lib.requests_wrapper.sleep")


def test_req_wrap_get(mocker, mock_requests):
    get(1)
    mock_requests.get.assert_called_once_with(1)


def test_req_wrap_get_kw(mocker, mock_requests):
    get(test=1)
    mock_requests.get.assert_called_once_with(test=1)


def test_req_wrap_get_both(mocker, mock_requests):
    get(1, test=2)
    mock_requests.get.assert_called_once_with(1, test=2)


def test_req_wrap_get_exception(mocker, mock_requests, mock_sleep):
    mock_requests.get.side_effect = [ValueError, 1]
    assert get() == 1
    mock_sleep.assert_called_once_with(5)


def test_req_wrap_get_exception_exhaust(mocker, mock_requests, mock_sleep):
    mock_requests.get.side_effect = [
        ValueError,
        ValueError,
        ValueError,
        ValueError,
        ValueError,
    ]
    with pytest.raises(ValueError):
        get()


def test_req_wrap_post(mocker, mock_requests, mock_sleep):
    post(1)
    mock_requests.post.assert_called_once_with(1)


def test_req_wrap_post_kw(mocker, mock_requests):
    post(test=1)
    mock_requests.post.assert_called_once_with(test=1)


def test_req_wrap_post_both(mocker, mock_requests):
    post(1, test=2)
    mock_requests.post.assert_called_once_with(1, test=2)


def test_req_wrap_post_exception(mocker, mock_requests, mock_sleep):
    mock_requests.post.side_effect = [ValueError, 1]
    assert post() == 1
    mock_sleep.assert_called_once_with(5)


def test_req_wrap_post_exception_exhaust(mocker, mock_requests, mock_sleep):
    mock_requests.post.side_effect = [
        ValueError,
        ValueError,
        ValueError,
        ValueError,
        ValueError,
    ]
    with pytest.raises(ValueError):
        post()
