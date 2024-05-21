import os
from shutil import rmtree
from typing import Dict, Optional
from streamlink import Streamlink

from nhltv_lib import game_tracking
import nhltv_lib.requests_wrapper as requests
from nhltv_lib.auth import get_auth_cookie_value_login_if_needed
from nhltv_lib.common import (
    dump_json_if_debug_enabled,
    tprint,
)
from nhltv_lib.constants import HEADERS, UA_NHLTV
from nhltv_lib.exceptions import (
    AuthenticationFailed,
)
from nhltv_lib.models import GameStatus
from nhltv_lib.stream import get_shorten_video
from nhltv_lib.types import Download, NHLStream
from nhltv_lib.urls import get_session_key_url, get_stream_url


def download_game(stream: NHLStream) -> Download:
    download = _get_download_from_stream(stream)
    clean_up_download(stream.game_id)
    _create_download_folder(stream.game_id)

    tprint(
        f"Starting download of game {download.game_id} ({download.game_info})"
    )
    game_tracking.update_game_status(download.game_id, GameStatus.downloading)
    game_tracking.download_started(download.game_id)
    game_tracking.set_game_info(download.game_id, download.game_info)

    session = Streamlink()
    session.set_option(
        "http-headers", {**HEADERS, **get_extra_headers(download.session_key)}
    )
    best_stream = session.streams(download.stream_url)["best"]

    if get_shorten_video():
        best_stream.duration = (
            15 * 60
        )  # download only 15 minutes when --debug-short is enabled

    # Open a file to write the stream data
    raw_file_name = _get_raw_file_name(download.game_id)
    with open(raw_file_name, "wb") as file_out:
        fd = best_stream.open()
        try:
            while True:
                data = fd.read(1024)
                if not data:
                    break
                file_out.write(data)
        finally:
            fd.close()

    tprint(f"Stream has been saved to {raw_file_name}", debug_only=True)
    game_tracking.download_finished(download.game_id)

    return download


def _get_download_from_stream(stream: NHLStream) -> Download:
    session_key = _get_session_key(stream)

    extra_headers = get_extra_headers(session_key)

    stream_rsp = requests.post(
        get_stream_url(stream.player_settings),
        headers={**HEADERS, **extra_headers},
    )

    stream_json = stream_rsp.json()
    dump_json_if_debug_enabled(stream_json)
    _verify_nhltv_request_status_succeeded(stream_json)

    stream_url: str = _extract_stream_url(stream_json)
    pretty_game_str: str = _extract_pretty_game_str(stream)

    return Download(stream.game_id, pretty_game_str, stream_url, session_key)


def _verify_nhltv_request_status_succeeded(nhltv_json: dict) -> None:
    """
    Takes a response from the session key URL and raises
    AuthenticationFailed if authentication failed
    """
    if nhltv_json.get("status") != "success":
        raise AuthenticationFailed(nhltv_json)


def _get_session_key(stream: NHLStream) -> str:
    """
    Gets the session key for a stream
    """
    extra_headers: Dict[str, Optional[str]] = {
        "Authorization": get_auth_cookie_value_login_if_needed(),
    }

    session_rsp = requests.post(
        get_session_key_url(stream.player_settings),
        headers={**HEADERS, **extra_headers},
    )
    if session_rsp.status_code != 200:
        raise AuthenticationFailed(session_rsp.json())
    session_json = session_rsp.json()


    dump_json_if_debug_enabled(session_json)

    return _extract_session_key(session_json)


def _extract_session_key(session_json: dict) -> str:
    """
    Gets the session key from a session_json
    """
    return str(session_json["data"])


def _extract_stream_url(stream_json: dict) -> str:
    return stream_json["data"]["stream"]


def _extract_pretty_game_str(stream: NHLStream) -> str:
    """
    Gets a string with name and teams
    """

    date = stream.stream["startTime"].split("T")[0]
    title = stream.player_settings["title"].replace(" ", "_")
    return f"{date}_{title}"


def _get_raw_file_name(game_id: int) -> str:
    return f"{game_id}_raw.mkv"


def get_extra_headers(session_key: str) -> Dict[str, str]:
    return {
        "Authorization": session_key,
        "User-agent": UA_NHLTV,
    }


def _create_download_folder(game_id: int) -> None:
    if not os.path.exists(f"{game_id}"):
        os.makedirs(f"{game_id}")


def clean_up_download(game_id: int) -> None:
    dl_directory: str = f"{game_id}"
    if os.path.isdir(dl_directory):
        rmtree(dl_directory)
    for file_name in os.listdir():
        if file_name.startswith(str(game_id)) and file_name.endswith(".mkv"):
            file_path = os.path.join(file_name)
            os.remove(file_path)
