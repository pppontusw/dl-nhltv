from typing import Optional, Dict, Match, Tuple, List, Union
from datetime import datetime
from shutil import move
import os
import re
from glob import iglob
from shutil import rmtree

import requests

from nhltv_lib.auth import get_auth_cookie_value_login_if_needed
from nhltv_lib.constants import HEADERS, UA_NHL, UA_PC
from nhltv_lib.common import (
    print_progress_bar,
    dump_json_if_debug_enabled,
    write_lines_to_file,
    read_lines_from_file,
    dump_pickle_if_debug_enabled,
    tprint,
)
from nhltv_lib.exceptions import (
    AuthenticationFailed,
    BlackoutRestriction,
    DownloadError,
    ExternalProgramError,
    DecodeError,
)
from nhltv_lib.ffmpeg import concat_video
from nhltv_lib.process import (
    call_subprocess_and_raise_on_error,
    call_subprocess_and_get_stdout_iterator,
)
from nhltv_lib.stream import get_quality, get_shorten_video
from nhltv_lib.urls import get_referer, get_session_key_url, get_stream_url
from nhltv_lib.cookies import create_nhl_cookie, save_cookies_to_txt
from nhltv_lib.types import Download, Stream


def download_game(stream: Stream) -> Download:
    download = _get_download_from_stream(stream)

    clean_up_download(download.game_id)
    _create_download_folder(download.game_id)

    tprint("Starting download of game {download.game_info}")

    _download_master_file(download)

    _download_quality_file(download.game_id, _get_quality_url(download))

    download_file_contents, decode_hashes = _parse_quality_file(download)

    write_lines_to_file(
        download_file_contents, f"{download.game_id}/download_file.txt"
    )

    #  for testing only shorten it to 100
    if get_shorten_video():
        _shorten_video(download.game_id)
        decode_hashes = decode_hashes[:45]

    _download_individual_video_files(download, len(decode_hashes))

    concat_file_content = _decode_video_and_get_concat_file_content(
        download, decode_hashes
    )

    write_lines_to_file(
        concat_file_content, _get_concat_file_name(download.game_id)
    )

    _merge_fragments_to_single_video(download.game_id)

    _remove_ts_files(download.game_id)

    return download


def _get_download_from_stream(stream: Stream) -> Download:
    authorization: str = get_auth_cookie_value_login_if_needed()

    extra_headers: Dict[str, str] = {
        "Authorization": authorization,
        "User-Agent": UA_NHL,
    }

    session_key = _get_session_key(stream)

    stream_rsp = requests.get(
        get_stream_url(stream.content_id, session_key),
        headers={**HEADERS, **extra_headers},
    )

    stream_json = stream_rsp.json()

    dump_json_if_debug_enabled(stream_json)

    _verify_nhltv_request_status_succeeded(stream_json)
    _verify_game_is_not_blacked_out(stream_json)

    stream_url: str = _extract_stream_url(stream_json)
    media_auth: str = _extract_media_auth(stream_json)
    pretty_game_str: str = _extract_pretty_game_str(stream_json)

    media_auth_cookie = create_nhl_cookie(
        "mediaAuth", media_auth.replace("mediaAuth=", "")
    )

    auth_cookie = create_nhl_cookie("Authorization", authorization)

    save_cookies_to_txt(
        [media_auth_cookie, auth_cookie], f"{stream.game_id}.txt"
    )

    return Download(stream.game_id, pretty_game_str, stream_url, session_key)


def _verify_nhltv_request_status_succeeded(nhltv_json: dict) -> None:
    """
    Takes a response from the session key URL and raises
    AuthenticationFailed if authentication failed
    """
    # Expecting negative values to always be bad i.e.:
    # -3500 is Sign-on restriction:
    # Too many usage attempts
    if nhltv_json["status_code"] < 0:
        tprint(nhltv_json["status_message"])
        raise AuthenticationFailed(nhltv_json["status_message"])


def _verify_game_is_not_blacked_out(nhltv_json: dict) -> None:
    """
    Takes a response from the session key URL and raises
    BlackoutRestriction if the game is blacked out
    """
    if nhltv_json["status_code"] == 1 and (
        nhltv_json["user_verified_event"][0]["user_verified_content"][0][
            "user_verified_media_item"
        ][0]["blackout_status"]["status"]
        == "BlackedOutStatus"
    ):
        msg = "This game is affected by blackout restrictions."
        tprint(msg)
        raise BlackoutRestriction(msg)


def _get_session_key(stream: Stream) -> str:
    """
    Gets the session key for a stream
    """
    extra_headers: Dict[str, Optional[str]] = {
        "Authorization": get_auth_cookie_value_login_if_needed(),
        "Referer": get_referer(stream),
    }

    rsp_json: dict = requests.get(
        get_session_key_url(stream.event_id),
        headers={**HEADERS, **extra_headers},
    ).json()

    dump_json_if_debug_enabled(rsp_json)

    _verify_nhltv_request_status_succeeded(rsp_json)
    _verify_game_is_not_blacked_out(rsp_json)

    return _extract_session_key(rsp_json)


def _extract_session_key(session_json: dict) -> str:
    """
    Gets the session key from a session_json
    """
    return str(session_json["session_key"])


def _extract_stream_url(session_json: dict) -> str:
    return session_json["user_verified_event"][0]["user_verified_content"][0][
        "user_verified_media_item"
    ][0]["url"]


def _extract_media_auth(session_json: dict) -> str:
    return (
        str(
            session_json["session_info"]["sessionAttributes"][0][
                "attributeName"
            ]
        )
        + "="
        + str(
            session_json["session_info"]["sessionAttributes"][0][
                "attributeValue"
            ]
        )
    )


def _extract_pretty_game_str(session_json: dict) -> str:
    """
    Gets a pretty string with game date and teams

    Arguments:
        json_source (json): The first parameter.

    Returns:
        str: in the format of 2017-03-06_VAN-ANA
    """
    game_info: str = session_json["user_verified_event"][0][
        "user_verified_content"
    ][0]["name"].replace(":", "|")
    game_time, game_teams, _ = game_info.split(" | ")
    game_teams = game_teams.split()[0] + "-" + game_teams.split()[2]
    return game_time + "_" + game_teams


def _remove_ts_files(game_id: int) -> None:
    for path in iglob(os.path.join(str(game_id), "*.ts")):
        os.remove(path)


def _get_raw_file_name(game_id: int) -> str:
    return f"{game_id}_raw.mkv"


def _get_download_options(game_id: int) -> str:
    return (
        " --load-cookies="
        + f"{game_id}.txt"
        + " --log='"
        + f"{game_id}_dl.log"
        + "' --log-level=notice --quiet=false --retry-wait=10"
        + " --max-tries=0 --header='Accept: */*'"
        + " --header='Accept-Language: en-US,en;q=0.8'"
        + " --header='Origin: https://www.nhl.com' -U='%s'" % UA_PC
        + " --enable-http-pipelining=true --auto-file-renaming=false"
        + " --allow-overwrite=true "
    )


def clean_up_download(game_id: int, delete_cookie: bool = False) -> None:
    log_file: str = f"{game_id}_dl.log"
    if os.path.exists(log_file):
        os.remove(log_file)
    dl_directory: str = f"{game_id}"
    if os.path.isdir(dl_directory):
        rmtree(dl_directory)
    if delete_cookie:
        cookie_file: str = f"{game_id}.txt"
        if os.path.exists(cookie_file):
            os.remove(cookie_file)


def _get_master_file_name(game_id: int) -> str:
    return f"{game_id}/master.m3u8"


def _get_quality_file_name(game_id: int) -> str:
    return f"{game_id}/input.m3u8"


def _download_master_file(download: Download) -> None:
    _download_page_with_aria2(
        download.game_id,
        _get_master_file_name(download.game_id),
        download.stream_url,
    )


def _download_quality_file(game_id: int, quality_url: str) -> None:
    _download_page_with_aria2(
        game_id, _get_quality_file_name(game_id), quality_url
    )


def _download_page_with_aria2(game_id: int, filename: str, url: str):
    download_options = _get_download_options(game_id)
    command = "aria2c -o " + filename + download_options + url
    call_subprocess_and_raise_on_error(command)


def _get_chosen_quality(game_id: int) -> str:
    # Parse the master and get the quality URL
    fh = open(_get_master_file_name(game_id), "r")

    quality: int = get_quality()

    for line in fh:
        if str(quality) + "K" in line:
            return line
        last_line: str = line

    # Otherwise we return the highest value
    return last_line


def _get_quality_url(download: Download) -> str:
    url_root_match: Optional[Match] = re.match(
        "(.*)master_tablet60.m3u8", download.stream_url, re.M | re.I
    )
    if url_root_match:
        url_root: str = url_root_match.group(1)
        quality_url: str = url_root + _get_chosen_quality(download.game_id)
        return quality_url
    else:
        raise ValueError("Missing master_tablet60.m3u8 in _get_quality_url")


def _create_download_folder(game_id: int) -> None:
    # Create the temp and keys directory
    if not os.path.exists(f"{game_id}/keys"):
        os.makedirs(f"{game_id}/keys")


def _parse_quality_file(download: Download) -> Tuple[List, List]:
    quality_url_root_match: Optional[Match] = re.search(
        r"(.*/)(.*)", _get_quality_url(download), re.M | re.I
    )
    if quality_url_root_match is None:
        raise ValueError("Quality url is missing or formatted incorrectly")
    quality_url_root: str = quality_url_root_match.group(1)

    quality_file_lines = read_lines_from_file(
        _get_quality_file_name(download.game_id)
    )
    ts_number: int = 0
    key_number: int = 0
    cur_iv: Union[str, int] = 0
    decode_hashes: list = []
    download_file_contents: list = []

    for line in quality_file_lines:
        if "#EXT-X-KEY" in line:
            # Incremenet key number
            key_number = key_number + 1

            # Pull the key url and iv
            in_line_match = re.search(r'.*"(.*)",IV=0x(.*)', line, re.M | re.I)
            if in_line_match is None:
                raise ValueError("IV or key url did not return a match")
            key_url = in_line_match.group(1)
            cur_iv = in_line_match.group(2)

            # Add file to download list
            download_file_contents.append(key_url + "\n")
            download_file_contents.append(
                " out=%s/keys/%s\n" % (download.game_id, str(key_number))
            )

        elif ".ts\n" in line:
            # Increment ts number
            ts_number = ts_number + 1

            # Add file to download list
            download_file_contents.append(quality_url_root + line)
            download_file_contents.append(
                " out=%s/%s.ts\n" % (download.game_id, str(ts_number))
            )

            # Add to decode_hashes
            decode_hashes.append(
                {
                    "key_number": str(key_number),
                    "ts_number": str(ts_number),
                    "iv": str(cur_iv),
                }
            )
    return download_file_contents, decode_hashes


def _shorten_video(game_id: int) -> None:
    tprint("shorting to 100 files for testing")
    command = "mv %s/download_file.txt %s/download_file_orig.txt;" % (
        game_id,
        game_id,
    )
    command += (
        "head -100 %s/download_file_orig.txt > %s/download_file.txt;"
        % (game_id, game_id)
    )
    command += "rm -f %s/download_file_orig.txt;" % game_id
    call_subprocess_and_raise_on_error(command)


def _download_individual_video_files(
    download: Download, num_of_hashes: int
) -> None:
    tprint(f"Starting download of individual video files", debug_only=True)
    command = "aria2c -i %s/download_file.txt -j 10 %s" % (
        download.game_id,
        _get_download_options(download.game_id),
    )
    proc, plines = call_subprocess_and_get_stdout_iterator(command)

    # Track progress and print progress bar
    progress = 0
    for line in plines:
        if (
            b"Download complete" in line
            and b".ts\n" in line
            and progress < num_of_hashes
        ):
            progress += 1
            print_progress_bar(progress, num_of_hashes, prefix="Downloading:")
    proc.wait()
    if proc.returncode != 0:
        stdout = proc.stdout.readlines()
        dump_pickle_if_debug_enabled(stdout)
        move(
            f"{download.game_id}_dl.log",
            f"{download.game_id}_fail_{datetime.now().isoformat()}.log",
        )
        tprint(f"Downloading game {download.game_id} failed")
        raise DownloadError(stdout)


def _get_concat_file_name(game_id: int) -> str:
    return f"{game_id}/concat.txt"


def _decode_video_and_get_concat_file_content(
    download: Download, decode_hashes: List
) -> List:
    concat_file_content = []

    tprint("Decode video files", debug_only=True)

    progress: int = 0
    for decode_hash in decode_hashes:
        cur_key: str = "blank"
        key_val: bytes = b""

        if progress < len(decode_hashes):
            progress += 1
            print_progress_bar(
                progress, len(decode_hashes), prefix="Decoding:"
            )

        ts_key_num = decode_hash["key_number"]

        # If the cur_key isn't the one from the hash
        # then refresh the key_val
        if cur_key != ts_key_num:
            key_val, cur_key = _hexdump_keys(download, ts_key_num)

        ts_num = decode_hash["ts_number"]

        _decode_ts_file(key_val, decode_hash, ts_num, download.game_id)

        os.replace(
            f"{download.game_id}/{ts_num}.ts.dec",
            f"{download.game_id}/{ts_num}.ts",
        )

        # Add to concat file
        concat_file_content.append("file " + str(ts_num) + ".ts\n")

    return concat_file_content


def _merge_fragments_to_single_video(game_id: int) -> None:
    tprint("Merge to a single video", debug_only=True)
    concat_video(
        _get_concat_file_name(game_id),
        _get_raw_file_name(game_id),
        extra_args="-bsf:a aac_adtstoasc",
    )


def _decode_ts_file(
    key_val: bytes, decode_hash: dict, ts_num: int, game_id: int
) -> None:
    command = (
        'openssl enc -aes-128-cbc -in "'
        + f"{game_id}/{ts_num}.ts"
        + '" -out "'
        + f"{game_id}/{ts_num}.ts.dec"
        + '" -d -K '
        + key_val.decode()
        + " -iv "
        + decode_hash["iv"]
    )

    call_subprocess_and_raise_on_error(command, DecodeError)


def _hexdump_keys(download: Download, ts_key_num: str) -> Tuple[bytes, str]:
    command = "xxd -p %s/keys/%s" % (download.game_id, ts_key_num)
    p, pi = call_subprocess_and_get_stdout_iterator(command)
    for line in pi:
        key_val: bytes = line.strip(b"\n")
        cur_key = ts_key_num
    p.wait()
    if p.returncode != 0:
        raise ExternalProgramError(p.stdout.readlines())
    return key_val, cur_key
