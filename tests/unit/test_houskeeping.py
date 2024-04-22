import os
import pytest
from unittest.mock import patch, mock_open
import datetime
from nhltv_lib.housekeeping import do_housekeeping

@pytest.fixture
def mock_os_functions():
    with patch("os.listdir") as mock_listdir, \
         patch("os.remove") as mock_remove:
        yield mock_listdir, mock_remove

@pytest.fixture
def mock_settings():
    with patch("nhltv_lib.settings.get_download_folder") as mock_get_download_folder, \
         patch("nhltv_lib.settings.get_retentiondays") as mock_get_retention_days:
        mock_get_download_folder.return_value = os.getcwd()
        mock_get_retention_days.return_value = 30
        yield

@pytest.fixture
def mock_datetime():
    with patch("nhltv_lib.housekeeping.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2024, 5, 1)
        mock_datetime.strptime.side_effect = lambda d, fmt: datetime.datetime.strptime(d, fmt)
        yield mock_datetime

def test_do_housekeeping_deletes_old_files(mock_os_functions, mock_settings, mock_datetime):
    mock_listdir, mock_remove = mock_os_functions
    mock_listdir.return_value = [
        "2024-04-01_NASHVILLE_PREDATORS_@_PITTSBURGH_PENGUINS.mkv",
        "2024-04-29_CHICAGO_BLACKHAWKS_@_LOS_ANGELES_KINGS.mkv",
        "invalidfile.txt"
    ]
    
    do_housekeeping()
    
    mock_remove.assert_called_once_with(os.getcwd() + "/test/2024-04-01_NASHVILLE_PREDATORS_@_PITTSBURGH_PENGUINS.mkv")
    assert mock_remove.call_count == 1

def test_do_housekeeping_keeps_recent_files(mock_os_functions, mock_settings, mock_datetime):
    mock_listdir, mock_remove = mock_os_functions
    mock_listdir.return_value = [
        "2024-04-29_CHICAGO_BLACKHAWKS_@_LOS_ANGELES_KINGS.mkv",
        "2024-05-01_NEW_YORK_ISLANDERS_@_CAROLINA_HURRICANES.mkv"
    ]
    
    do_housekeeping()
    
    mock_remove.assert_not_called()
