import os
import pytest
from nhltv_lib.obfuscate import (
    _create_obfuscation_concat_content,
    _get_desired_length_after_obfuscation,
    cut_to_closest_hour,
    obfuscate,
)


@pytest.fixture(scope="function", autouse=True)
def mock_game_tracking(mocker):
    return mocker.patch("nhltv_lib.obfuscate.game_tracking")


def test_cut_to_closest_hour(mocker):
    mocker.patch("nhltv_lib.obfuscate.get_video_length", return_value=12080)

    mock_remove = mocker.patch("os.remove")
    mock_cut_vid = mocker.patch("nhltv_lib.obfuscate.cut_video")

    cut_to_closest_hour(1)

    mock_cut_vid.assert_called_once_with(
        "1_obfuscated.mkv", "1_ready.mkv", 10800
    )
    mock_remove.assert_called_once_with("1_obfuscated.mkv")


def test_obfuscate(mocker, fake_download):
    mocker.patch("nhltv_lib.obfuscate.cut_to_closest_hour")
    mocker.patch(
        "nhltv_lib.obfuscate._create_obfuscation_concat_content",
        return_value=["foo\n", "bar\n"],
    )

    mock_writelines = mocker.patch("nhltv_lib.obfuscate.write_lines_to_file")
    mock_move = mocker.patch(
        "nhltv_lib.obfuscate.move_file_to_download_folder"
    )
    mock_remove = mocker.patch("os.remove")
    mock_concat_vid = mocker.patch("nhltv_lib.obfuscate.concat_video")

    obfuscate(fake_download)

    mock_writelines.assert_called_once_with(
        ["foo\n", "bar\n"],
        f"{fake_download.game_id}/obfuscate_concat_list.txt",
    )
    mock_concat_vid.assert_called_once_with(
        f"{fake_download.game_id}/obfuscate_concat_list.txt",
        f"{fake_download.game_id}_obfuscated.mkv",
    )
    mock_remove.assert_called_once_with(f"{fake_download.game_id}_silent.mkv")
    mock_move.assert_called_once_with(fake_download)


def test_obfuscation_content(mocker):
    mocker.patch("os.path.dirname", return_value="./bar")
    black = os.path.join("./bar", "extras/black.mkv")

    expected = []
    expected.append("file\t" + "../FOO" + "\n")
    for _ in range(100):
        expected.append("file\t" + black + "\n")

    assert _create_obfuscation_concat_content("FOO") == expected


def test_get_desire_length_after_obfuscation():
    assert _get_desired_length_after_obfuscation(12000) == 10800
    assert _get_desired_length_after_obfuscation(9999) == 7200
    assert _get_desired_length_after_obfuscation(16000) == 14400

    assert _get_desired_length_after_obfuscation(7201) == 7200
    assert _get_desired_length_after_obfuscation(7200) == 7200
    assert _get_desired_length_after_obfuscation(7199) == 3600

    assert _get_desired_length_after_obfuscation(10801) == 10800
    assert _get_desired_length_after_obfuscation(10800) == 10800
    assert _get_desired_length_after_obfuscation(10799) == 7200

    assert _get_desired_length_after_obfuscation(14401) == 14400
    assert _get_desired_length_after_obfuscation(14400) == 14400
    assert _get_desired_length_after_obfuscation(14399) == 10800
