import json
from pathlib import Path
import pytest
from datetime import datetime, timedelta

from nhltv_lib.cache import (
    ensure_cache_directory,
    cache_json,
    load_cache_json,
    delete_cache,
)
from unittest.mock import MagicMock


@pytest.fixture
def prepare_cache(mocker):
    # Ensure the cache directory is created
    ensure_cache_directory()
    initial_time = datetime(2020, 1, 1, 12, 0, 0)
    dt = mocker.patch("nhltv_lib.cache.datetime")
    dt.now.return_value = initial_time
    dt.fromisoformat = (
        datetime.fromisoformat
    )  # Preserve the real fromisoformat
    return dt


def test_cache_json_and_load_cache_json(prepare_cache):
    dt = prepare_cache
    name = "test_cache"
    parameters = {"key": "value"}
    content = {"data": "test_data"}
    expires_in = 300  # 5 minutes

    # Cache the JSON
    cache_json(name, parameters, expires_in, content)
    cache_file_path = Path("cache") / f"{name}.json"

    # Check if the file was created
    assert (
        cache_file_path.exists()
    ), "Cache file should exist after cache_json call"

    # Load the cache and check the content
    cached_content = load_cache_json(name, parameters)
    assert (
        cached_content == content
    ), "Content retrieved from cache should match the original content"

    # Simulate time after expiration
    expired_time = datetime(
        2020, 1, 1, 12, 5, 1
    )  # 5 minutes and 1 second later
    dt.now.return_value = expired_time
    expired_content = load_cache_json(name, parameters)
    assert expired_content is None, "Should return None for expired cache"


def test_delete_cache(prepare_cache):
    # Test deletion of the cache
    name = "test_cache"
    cache_json(name, {"key": "value"}, 300, {"data": "test_data"})
    cache_file_path = Path("cache") / f"{name}.json"
    assert cache_file_path.exists(), "Cache file should exist before deleting"

    delete_cache(name)
    assert (
        not cache_file_path.exists()
    ), "Cache file should not exist after delete_cache call"


def test_ensure_cache_directory():
    # Ensure the cache directory is created
    ensure_cache_directory()
    cache_dir = Path("cache")
    assert (
        cache_dir.exists()
    ), "Cache directory should exist after ensure_cache_directory call"
