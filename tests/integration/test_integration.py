import os
import pytest
from nhltv_lib.main import main


@pytest.mark.no_cover
@pytest.mark.skip
def test_app_runs(mocker, parsed_arguments):
    """
    It should run without error
    """
    if os.path.exists("downloaded_games.json"):
        os.remove("downloaded_games.json")
    if os.path.exists("archive_waitlist.json"):
        os.remove("archive_waitlist.json")
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )

    mock_logger = mocker.patch("logging.getLogger")
    mock_verify_deps = mocker.patch("nhltv_lib.main.verify_dependencies")
    main()
    mock_logger.assert_called()
    mock_verify_deps.assert_called()
    os.remove("downloaded_games.json")
    os.remove("archive_waitlist.json")
