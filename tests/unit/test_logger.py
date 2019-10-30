from nhltv_lib.logger import setup_logging


def test_setup_logging(mocker):
    mocked_logger = mocker.patch("logging.getLogger")
    setup_logging()
    mocked_logger.assert_called()
