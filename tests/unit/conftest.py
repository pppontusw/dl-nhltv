import pytest


@pytest.fixture(scope="function", autouse=True)
def mocked_logger(mocker):
    with mocker.patch("logging.getLogger"):
        yield


@pytest.fixture(scope="function", autouse=True)
def mocked_subprocess(mocker):
    return mocker.patch("subprocess.Popen")


@pytest.fixture(scope="function", autouse=True)
def mocked_verify_deps(mocker):
    return mocker.patch("nhltv_lib.main.verify_dependencies")


@pytest.fixture(scope="function", autouse=True)
def mocked_setup_logging(mocker):
    return mocker.patch("nhltv_lib.main.setup_logging")
