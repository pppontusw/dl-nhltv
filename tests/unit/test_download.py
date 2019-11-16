import requests_mock
import pytest
from nhltv_lib.common import debug_dump_json
from nhltv_lib.download import (
    _get_download_from_stream,
    _decode_ts_file,
    _write_concat_file,
    _get_quality_url,
    _write_download_file,
    _verify_game_is_not_blacked_out,
    _verify_nhltv_request_status_succeeded,
    _extract_session_key,
    Download,
    _merge_fragments_to_single_video,
    _get_alt_quality_url_root,
    _decode_video_and_get_concat_file_content,
    _get_session_key,
    _get_raw_file_name,
    _get_master_file_name,
    _get_quality_file_name,
    _shorten_video,
    _get_chosen_quality,
    _download_page_with_aria2,
    _download_master_file,
    _download_quality_file,
    _clean_up_download,
    _read_quality_file,
    _create_download_folder,
    _parse_quality_file,
    download_game,
)
from nhltv_lib.stream import Stream
from nhltv_lib.exceptions import (
    BlackoutRestriction,
    AuthenticationFailed,
    DecodeError,
)


def test_parse_quality_file(
    mocker,
    fake_quality_file,
    fake_download,
    fake_download_file,
    fake_decode_hashes,
):
    mocker.patch(
        "nhltv_lib.download._read_quality_file", return_value=fake_quality_file
    )
    dlc, dch = _parse_quality_file(fake_download)
    assert dlc == fake_download_file
    assert dch == fake_decode_hashes


def test_get_download_from_stream(mocker, fake_stream_json):
    mocker.patch("requests.cookies")
    mocker.patch("nhltv_lib.download.save_cookie_to_txt")
    mocker.patch("nhltv_lib.download._get_session_key", return_value="raboof")
    mocker.patch(
        "nhltv_lib.download._verify_game_is_not_blacked_out", return_value=None
    )
    mocker.patch(
        "nhltv_lib.download._verify_nhltv_request_status_succeeded",
        return_value=None,
    )
    stream_url = "http://foo"
    mocker.patch("nhltv_lib.download.get_stream_url", return_value=stream_url)
    # TODO: fix this up with a real object
    stream = Stream(1, 2, 3)

    with requests_mock.Mocker() as rm:
        rm.get(stream_url, json=fake_stream_json)
        assert _get_download_from_stream(stream) == Download(
            1,
            "2019-10-18_NSH-ARI",
            "https://vod-l3c-na1.med.nhl.com/ps01/nhl/2019/10/18/NHL_GAME_VIDEO_NSHARI_M2_VISIT_20191018_1570700310035/master_tablet60.m3u8",  # noqa: E501
            "raboof",
        )


def test_get_quality_url(mocker, fake_download):
    mocker.patch(
        "nhltv_lib.download._get_chosen_quality",
        return_value="5600K/5600_complete-trimmed.m3u8",
    )
    assert (
        _get_quality_url(fake_download)
        == "https://vod-l3c-na1.med.nhl.com/ps01/nhl/2019/10/18/NHL_GAME_VIDEO_NSHARI_M2_VISIT_20191018_1570700310035/5600K/5600_complete-trimmed.m3u8"  # noqa: E501
    )


def test_decode_ts_file(mocker):
    m = mocker.patch("nhltv_lib.download.call_subprocess_and_raise_on_error")
    _decode_ts_file("abc".encode(), {"iv": "baabaa"}, 5, 8)
    m.assert_called_once_with(
        'openssl enc -aes-128-cbc -in "8/5.ts" -out "8/5.ts.dec" -d -K abc -iv baabaa',  # noqa: E501
        DecodeError,
    )


def test_read_quality_file(mocker):
    mo = mocker.mock_open(read_data="coo\nloo")
    mocker.patch("builtins.open", mo)
    assert _read_quality_file(1) == ["coo\n", "loo"]


def test_get_raw_file_name():
    assert _get_raw_file_name(30) == "30_raw.mkv"


def test_get_master_file_name():
    assert _get_master_file_name(30) == "30/master.m3u8"


def test_get_quality_file_name():
    assert _get_quality_file_name(30) == "30/input.m3u8"


def test_extract_session_key(mocker):
    retjson = {"session_key": 3000}
    assert _extract_session_key(retjson) == "3000"


def test_get_session_key(mocker, fake_session_json):
    mocker.patch(
        "nhltv_lib.download.get_auth_cookie_value", return_value="bar"
    )
    mocker.patch("nhltv_lib.download.get_referer", return_value="foo")
    mocker.patch(
        "nhltv_lib.download.get_session_key_url", return_value="http://nhl"
    )
    with requests_mock.Mocker() as m:
        m.get("http://nhl", json=fake_session_json)
        assert _get_session_key(Stream(1, 2, 3)) == "foo="


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


def test_download_page_with_aria2(mocker):
    mock_subp = mocker.patch(
        "nhltv_lib.download.call_subprocess_and_raise_on_error"
    )

    _download_page_with_aria2(1, "file", "url")
    mock_subp.assert_called_once_with(
        "aria2c -o file --load-cookies=1.txt --log='1_dl.log' --log-level=notice --quiet=false --retry-wait=1 --max-file-not-found=5 --max-tries=5 --header='Accept: */*' --header='Accept-Language: en-US,en;q=0.8' --header='Origin: https://www.nhl.com' -U='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36' --enable-http-pipelining=true --auto-file-renaming=false --allow-overwrite=true url"  # noqa: E501
    )


def test_get_chosen_quality(mocker, fake_master_file):
    mo = mocker.mock_open(read_data=fake_master_file)
    mocker.patch("builtins.open", mo)
    assert _get_chosen_quality(1) == "5600K/5600_complete-trimmed.m3u8\n"

    mocker.patch("nhltv_lib.download.get_quality", return_value=3500)
    assert _get_chosen_quality(1) == "3500K/3500_complete-trimmed.m3u8\n"


def test_write_download_file(mocker):
    call = mocker.call
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    _write_download_file(1, ["foo", "bar"])
    mo.assert_called_with("1/download_file.txt", "w")
    calls = [call(["foo", "bar"])]
    mo().writelines.assert_has_calls(calls)


def test_write_concat_file(mocker):
    call = mocker.call
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    _write_concat_file(1, ["foo", "bar"])
    mo.assert_called_with("1/concat.txt", "w")
    calls = [call(["foo", "bar"])]
    mo().writelines.assert_has_calls(calls)


def test_download_master_file(mocker, fake_download):
    m = mocker.patch("nhltv_lib.download._download_page_with_aria2")
    _download_master_file(fake_download)
    m.assert_called_once_with(
        2019020104,
        "2019020104/master.m3u8",
        "https://vod-l3c-na1.med.nhl.com/ps01/nhl/2019/10/18/NHL_GAME_VIDEO_NSHARI_M2_VISIT_20191018_1570700310035/master_tablet60.m3u8",  # noqa: E501
    )


def test_download_quality_file(mocker):
    m = mocker.patch("nhltv_lib.download._download_page_with_aria2")
    _download_quality_file(1, "http://nhl")
    m.assert_called_once_with(1, "1/input.m3u8", "http://nhl")


def test_clean_up_before_dl(mocker):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.isdir", return_value=True)
    rm = mocker.patch("os.remove")
    rmt = mocker.patch("nhltv_lib.download.rmtree")
    _clean_up_download(1)
    rm.assert_called_once_with("1_dl.log")
    rmt.assert_called_once_with("1")


def test_create_dl_folder(mocker):
    mocker.patch("os.path.exists", return_value=False)
    rm = mocker.patch("os.makedirs")
    _create_download_folder(1)
    rm.assert_called_once_with("1/keys")


def test_get_alt_quality_root():
    assert (
        _get_alt_quality_url_root("https://media-l3c.nhl.com.svc/bar")
        == "https://media-akc.nhl.com.svc/bar"
    )
    assert (
        _get_alt_quality_url_root("https://media-akc.nhl.com.svc/bar")
        == "https://media-l3c.nhl.com.svc/bar"
    )


def test_shorten_video(mocker):
    mp = mocker.patch("nhltv_lib.download.call_subprocess_and_raise_on_error")
    _shorten_video(1)
    mp.assert_called_once_with(
        "mv 1/download_file.txt 1/download_file_orig.txt;head -100 "
        + "1/download_file_orig.txt > 1/download_file.txt;rm -f "
        + "1/download_file_orig.txt;"
    )


def test_decode_video_get_concat_file_content(
    mocker, fake_download, fake_decode_hashes, fake_concat_file
):
    mocker.patch("nhltv_lib.download.print_progress_bar")
    mocker.patch("nhltv_lib.download._decode_ts_file")
    mocker.patch("nhltv_lib.download._hexdump_keys", return_value=(1, 2))
    mocker.patch("os.replace")

    assert (
        _decode_video_and_get_concat_file_content(
            fake_download, fake_decode_hashes
        )
        == fake_concat_file
    )

