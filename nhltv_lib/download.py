import logging
import os
import re
import time
from collections import namedtuple
from glob import iglob
from shutil import rmtree

import requests

from nhltv_lib.auth import get_auth_cookie_value
from nhltv_lib.constants import HEADERS, UA_NHL, UA_PC
from nhltv_lib.cookies import save_cookie_to_txt
from nhltv_lib.common import print_progress_bar, dump_json_if_debug_enabled
from nhltv_lib.exceptions import (
    AuthenticationFailed,
    BlackoutRestriction,
    DownloadError,
    ExternalProgramError,
    DecodeError,
)
from nhltv_lib.process import (
    call_subprocess_and_raise_on_error,
    call_subprocess,
)
from nhltv_lib.stream import get_quality, get_shorten_video
from nhltv_lib.urls import get_referer, get_session_key_url, get_stream_url

logger = logging.getLogger("nhltv")

Download = namedtuple(
    "Download", ["game_id", "game_info", "stream_url", "session_key"]
)


def download_game(stream):
    download = _get_download_from_stream(stream)

    _clean_up_download(download.game_id)

    logging.debug("Starting Download: " + download.stream_url)

    _download_master_file(download)

    _download_quality_file(download.game_id, _get_quality_url(download))

    download_file_contents, decode_hashes = _parse_quality_file(download)
    _write_download_file(download.game_id, download_file_contents)

    #  for testing only shorten it to 100
    if get_shorten_video():
        _shorten_video(download.game_id)
        decode_hashes = decode_hashes[:45]

    _download_individual_video_files(download, len(decode_hashes))

    concat_file_content = _decode_video_and_get_concat_file_content(
        download, decode_hashes
    )
    _write_concat_file(download.game_id, concat_file_content)

    # TODO: Add retry

    _merge_fragments_to_single_video(download.game_id)

    _remove_ts_files(download.game_id)

    return download


def _get_download_from_stream(stream):
    authorization = get_auth_cookie_value()

    extra_headers = {"Authorization": authorization, "User-Agent": UA_NHL}

    session_key = _get_session_key(stream)

    stream_json = requests.get(
        get_stream_url(stream.content_id, session_key),
        headers={**HEADERS, **extra_headers},
    ).json()

    dump_json_if_debug_enabled(stream_json)

    _verify_nhltv_request_status_succeeded(stream_json)
    _verify_game_is_not_blacked_out(stream_json)

    stream_url = _extract_stream_url(stream_json)
    media_auth = _extract_media_auth(stream_json)
    pretty_game_str = _extract_pretty_game_str(stream_json)

    media_auth_cookie = requests.cookies.create_cookie(
        "mediaAuth",
        "" + media_auth.replace("mediaAuth=", "") + "",
        port=None,
        domain=".nhl.com",
        path="/",
        secure=False,
        expires=(int(time.time()) + 7500),
        discard=False,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )
    save_cookie_to_txt(media_auth_cookie, f"{stream.game_id}.txt")

    return Download(stream.game_id, pretty_game_str, stream_url, session_key)


def _verify_nhltv_request_status_succeeded(nhltv_json):
    """
    Takes a response from the session key URL and raises
    AuthenticationFailed if authentication failed
    """
    # Expecting negative values to always be bad i.e.:
    # -3500 is Sign-on restriction:
    # Too many usage attempts
    if nhltv_json["status_code"] < 0:
        logger.error(nhltv_json["status_message"])
        raise AuthenticationFailed(nhltv_json["status_message"])


def _verify_game_is_not_blacked_out(nhltv_json):
    """
    Takes a response from the session key URL and raises
    BlackoutRestriction if the game is blacked out
    """
    if nhltv_json["status_code"] == 1:
        if (
            nhltv_json["user_verified_event"][0]["user_verified_content"][0][
                "user_verified_media_item"
            ][0]["blackout_status"]["status"]
            == "BlackedOutStatus"
        ):
            msg = "This game is affected by blackout restrictions."
            logger.warning(msg)
            raise BlackoutRestriction(msg)


def _get_session_key(stream):
    """
    Gets the session key for a stream
    """
    # TODO: Reuse session key?
    extra_headers = {
        "Authorization": get_auth_cookie_value(),
        "Referer": get_referer(stream),
    }

    rsp_json = requests.get(
        get_session_key_url(stream.event_id),
        headers={**HEADERS, **extra_headers},
    ).json()

    dump_json_if_debug_enabled(rsp_json)

    _verify_nhltv_request_status_succeeded(rsp_json)
    _verify_game_is_not_blacked_out(rsp_json)

    return _extract_session_key(rsp_json)


def _extract_session_key(session_json):
    """
    Gets the session key from a session_json
    """
    return str(session_json["session_key"])


def _extract_stream_url(session_json):
    return session_json["user_verified_event"][0]["user_verified_content"][0][
        "user_verified_media_item"
    ][0]["url"]


def _extract_media_auth(session_json):
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


def _extract_pretty_game_str(session_json):
    """
    Gets a pretty string with game date and teams

    Arguments:
        json_source (json): The first parameter.

    Returns:
        str: in the format of 2017-03-06_VAN-ANA
    """
    game_info = session_json["user_verified_event"][0][
        "user_verified_content"
    ][0]["name"].replace(":", "|")
    game_time, game_teams, _ = game_info.split(" | ")
    game_teams = game_teams.split()[0] + "-" + game_teams.split()[2]
    return game_time + "_" + game_teams


def _write_concat_file(game_id, concat_file_content):
    with open(_get_concat_file_name(game_id), "w") as f:
        f.writelines(concat_file_content)


def _remove_ts_files(game_id):
    for path in iglob(os.path.join(str(game_id), "*.ts")):
        os.remove(path)


def _get_raw_file_name(game_id):
    return f"{game_id}_raw.mkv"


def _get_download_options(game_id):
    return (
        " --load-cookies="
        + f"{game_id}.txt"
        + " --log='"
        + f"{game_id}_dl.log"
        + "' --log-level=notice --quiet=false --retry-wait=1"
        + " --max-file-not-found=5"
        + " --max-tries=5 --header='Accept: */*'"
        + " --header='Accept-Language: en-US,en;q=0.8'"
        + " --header='Origin: https://www.nhl.com' -U='%s'" % UA_PC
        + " --enable-http-pipelining=true --auto-file-renaming=false"
        + " --allow-overwrite=true "
    )


def _clean_up_download(game_id):
    logFile = f"{game_id}_dl.log"
    if os.path.exists(logFile):
        os.remove(logFile)
    if os.path.isdir(game_id):
        rmtree(str(game_id))


def _get_master_file_name(game_id):
    return f"{game_id}/master.m3u8"


def _get_quality_file_name(game_id):
    return f"{game_id}/input.m3u8"


def _download_master_file(download):
    _download_page_with_aria2(
        download.game_id,
        _get_master_file_name(download.game_id),
        download.stream_url,
    )


def _download_quality_file(game_id, quality_url):
    _download_page_with_aria2(
        game_id, _get_quality_file_name(game_id), quality_url
    )


def _download_page_with_aria2(game_id, filename, url):
    download_options = _get_download_options(game_id)
    command = "aria2c -o " + filename + download_options + url
    call_subprocess_and_raise_on_error(command)


def _get_chosen_quality(game_id):
    # Parse the master and get the quality URL
    fh = open(_get_master_file_name(game_id), "r")

    quality = get_quality()

    for line in fh:
        if str(quality) + "K" in line:
            return line
        last_line = line

    # Otherwise we return the highest value
    return last_line


def _get_quality_url(download):
    url_root = re.match(
        "(.*)master_tablet60.m3u8", download.stream_url, re.M | re.I
    ).group(1)
    quality_url = url_root + _get_chosen_quality(download.game_id)
    return quality_url


def _create_download_folder(game_id):
    # Create the temp and keys directory
    if not os.path.exists(f"{game_id}/keys"):
        os.makedirs(f"{game_id}/keys")


def _write_download_file(game_id, download_file_contents):
    with open(f"{game_id}/download_file.txt", "w") as f:
        f.writelines(download_file_contents)


def _read_quality_file(game_id):
    with open(_get_quality_file_name(game_id), "r") as f:
        return f.readlines()


def _parse_quality_file(download):
    quality_url_root = re.search(
        r"(.*/)(.*)", _get_quality_url(download), re.M | re.I
    ).group(1)

    quality_file_lines = _read_quality_file(download.game_id)
    ts_number = 0
    key_number = 0
    cur_iv = 0
    decode_hashes = []
    download_file_contents = []

    for line in quality_file_lines:
        if "#EXT-X-KEY" in line:
            # Incremenet key number
            key_number = key_number + 1

            # Pull the key url and iv
            in_line_match = re.search(r'.*"(.*)",IV=0x(.*)', line, re.M | re.I)
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

            # Make alternate uri
            alt_quality_url_root = _get_alt_quality_url_root(quality_url_root)

            # Add file to download list
            download_file_contents.append(
                quality_url_root
                + line.strip("\n")
                + "\t"
                + alt_quality_url_root
                + line
            )
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


def _shorten_video(game_id):
    logger.debug("shorting to 100 files for testing")
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


def _download_individual_video_files(download, num_of_hashes):
    logger.debug("starting download of individual video files")
    command = "aria2c -i %s/download_file.txt -j 20 %s" % (
        download.game_id,
        _get_download_options(download.game_id),
    )
    p = call_subprocess(command)
    # Track progress and print progress bar
    progress = 0
    for line in iter(p.stdout.readline, b""):
        if b"Download complete" in line and b".ts\n" in line:
            if progress < num_of_hashes:
                progress += 1
                print_progress_bar(
                    progress, num_of_hashes, prefix="Downloading:"
                )
    p.wait()
    if p.returncode != 0:
        logger.error("Downloading game %s failed", download.game_id)
        raise DownloadError("Download failed")


def _get_concat_file_name(game_id):
    return f"{game_id}/concat.txt"


def _decode_video_and_get_concat_file_content(download, decode_hashes):
    concat_file_content = []

    logger.debug("Decode video files")

    progress = 0
    for dH in decode_hashes:
        cur_key = "blank"
        key_val = ""

        if progress < len(decode_hashes):
            progress += 1
            print_progress_bar(
                progress, len(decode_hashes), prefix="Decoding:"
            )

        ts_key_num = dH["key_number"]

        # If the cur_key isn't the one from the hash
        # then refresh the key_val
        if cur_key != ts_key_num:
            key_val, cur_key = _hexdump_keys(download, ts_key_num)

        ts_num = dH["ts_number"]

        _decode_ts_file(key_val, dH, ts_num, download.game_id)

        os.replace(
            f"{download.game_id}/{ts_num}.ts.dec",
            f"{download.game_id}/{ts_num}.ts",
        )

        # Add to concat file
        concat_file_content.append("file " + str(ts_num) + ".ts\n")

    return concat_file_content


def _get_alt_quality_url_root(quality_url_root):
    if "-l3c." in quality_url_root:
        alt_quality_url_root = quality_url_root.replace("-l3c.", "-akc.")
    else:
        alt_quality_url_root = quality_url_root.replace("-akc.", "-l3c.")
    return alt_quality_url_root


def _merge_fragments_to_single_video(game_id):
    logger.debug("Merge to a single video")
    # merge to single
    command = (
        "ffmpeg -y -nostats -loglevel 0 -f concat -i "
        + _get_concat_file_name(game_id)
        + " -c copy -bsf:a aac_adtstoasc "
        + _get_raw_file_name(game_id)
    )
    call_subprocess_and_raise_on_error(command)


def _decode_ts_file(key_val, dH, ts_num, game_id):
    command = (
        'openssl enc -aes-128-cbc -in "'
        + f"{game_id}/{ts_num}.ts"
        + '" -out "'
        + f"{game_id}/{ts_num}.ts.dec"
        + '" -d -K '
        + key_val.decode()
        + " -iv "
        + dH["iv"]
    )

    call_subprocess_and_raise_on_error(command, DecodeError)


def _hexdump_keys(download, ts_key_num):
    command = "xxd -p %s/keys/%s" % (download.game_id, ts_key_num)
    p = call_subprocess(command)
    pi = iter(p.stdout.readline, b"")
    for line in pi:
        key_val = line.strip(b"\n")
        cur_key = ts_key_num
    p.wait()
    if p.returncode != 0:
        raise ExternalProgramError(p.stdout.readlines())
    return key_val, cur_key
