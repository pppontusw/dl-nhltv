import pytest
from nhltv_lib.main import main


@pytest.mark.no_cover
def test_app_runs(mocker, parsed_arguments):
    """
    It should run without error
    """
    mocker.patch("nhltv_lib.main.parse_args", return_value=parsed_arguments)

    mock_logger = mocker.patch("logging.getLogger")
    main()
    mock_logger.assert_called()
