import requests_mock
import pytest
from nhltv_lib.download import (
    get_download_from_stream,
    _verify_game_is_not_blacked_out,
    _verify_nhltv_request_status_succeeded,
    _extract_session_key,
    Download,
    _merge_fragments_to_single_video,
    _get_alt_quality_url_root,
    _decode_video_and_get_concat_file_content,
)
from nhltv_lib.stream import Stream
from nhltv_lib.exceptions import BlackoutRestriction, AuthenticationFailed


def test_get_stream(mocker):
    mocker.patch(
        "nhltv_lib.download._verify_game_is_not_blacked_out", return_value=None
    )
    mocker.patch(
        "nhltv_lib.download._verify_nhltv_request_status_succeeded",
        return_value=None,
    )
    session_key_url = "http://foo"
    mocker.patch(
        "nhltv_lib.download.get_session_key_url", return_value=session_key_url
    )

    stream = Stream(1, 2, 3)


def test_get_session_key(mocker):
    retjson = {"session_key": 3000}
    assert _extract_session_key(retjson) == "3000"


def test_verify_req_stat_succeeded():
    dict_ = {"status_code": 1}
    assert _verify_nhltv_request_status_succeeded(dict_) is None


def test_verify_req_stat_succeeded_raises():
    dict_ = {"status_code": -3500, "status_message": "foo"}
    with pytest.raises(AuthenticationFailed) as e:
        _verify_nhltv_request_status_succeeded(dict_)
    assert str(e.value) == "foo"


def test_verify_game_not_blacked_out():
    dict_ = {
        "status_code": 1,
        "user_verified_event": [
            {
                "user_verified_content": [
                    {
                        "user_verified_media_item": [
                            {"blackout_status": {"status": "BlackedOutStatus"}}
                        ]
                    }
                ]
            }
        ],
    }
    with pytest.raises(BlackoutRestriction) as e:
        _verify_game_is_not_blacked_out(dict_)
    assert str(e.value) == "This game is affected by blackout restrictions."


def test_merge_frags_to_single(mocker):
    mock_subp = mocker.patch(
        "nhltv_lib.download.call_subprocess_and_raise_on_error"
    )

    _merge_fragments_to_single_video(30)
    mock_subp.assert_called_once_with(
        "ffmpeg -y -nostats -loglevel 0 -f concat -i 30/concat.txt -c"
        + " copy -bsf:a aac_adtstoasc 30_raw.mkv"
    )


def test_get_alt_quality_root():
    assert (
        _get_alt_quality_url_root("https://media-l3c.nhl.com.svc/bar")
        == "https://media-akc.nhl.com.svc/bar"
    )
    assert (
        _get_alt_quality_url_root("https://media-akc.nhl.com.svc/bar")
        == "https://media-l3c.nhl.com.svc/bar"
    )


def test_decode_video_get_concat_file_content(mocker):
    mocker.patch("nhltv_lib.download.print_progress_bar")
    mocker.patch("nhltv_lib.download._decode_ts_file")
    mock_subp = mocker.patch("nhltv_lib.download.call_subprocess")
    mocker.patch("os.replace")
    mock_subp.return_value.stdout.return_value.readline.return_value = [b"1\n"]

    decode_hashes = [{"key_number": 0, "ts_number": 0}]

    assert _decode_video_and_get_concat_file_content(
        Download(0, 0, 0, 0), decode_hashes
    ) == ["file 0.ts\n"]
