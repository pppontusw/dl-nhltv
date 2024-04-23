import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional


def ensure_cache_directory() -> None:
    """Ensure that the 'cache' directory exists."""
    os.makedirs("cache", exist_ok=True)


def cache_json(
    name: str, parameters: Dict, expires_in: int, content: Dict
) -> None:
    """Cache JSON content with expiration time.

    Args:
        name (str): The name of the cache file.
        parameters (Dict): Parameters to match for cache to be valid.
        expires_in (int): Expiration time in seconds.
        content (Dict): Content to be cached.
    """
    ensure_cache_directory()
    cache_data = {
        "parameters": parameters,
        "expires": (
            datetime.now() + timedelta(seconds=expires_in)
        ).isoformat(),
        "content": content,
    }
    cache_file_path = Path("cache") / f"{name}.json"
    with open(cache_file_path, "w") as f:
        json.dump(cache_data, f)


def load_cache_json(name: str, parameters: Dict) -> Optional[Dict]:
    """Load content from cache if parameters match and it hasn't expired.

    Args:
        name (str): The name of the cache file.
        parameters (Dict): Parameters to validate against cached data.

    Returns:
        Optional[Dict]: The cached content if conditions are met, otherwise None.
    """
    cache_file_path = Path("cache") / f"{name}.json"
    if not cache_file_path.exists():
        return None

    with open(cache_file_path, "r") as f:
        cached = json.load(f)

    if (
        cached["parameters"] == parameters
        and datetime.fromisoformat(cached["expires"]) > datetime.now()
    ):
        return cached["content"]

    return None


def delete_cache(name: str):
    """Delete a specific cache file.

    Args:
        name (str): The name of the cache file to delete.
    """
    cache_file_path = Path("cache") / f"{name}.json"
    if cache_file_path.exists():
        cache_file_path.unlink()
        print(f"Cache file '{name}.json' deleted successfully.")
    else:
        print(f"Cache file '{name}.json' does not exist.")
