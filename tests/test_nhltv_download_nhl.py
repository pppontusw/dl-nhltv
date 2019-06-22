import unittest
import os
import sys
import json
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch
import requests
import nhltv_lib
from nhltv_lib.common import get_setting
from nhltv_lib.exceptions import NoGameFound
from nhltv_lib.download_nhl import DownloadNHL
#############
# Expanding PYTHONPATH hack start
# A bit of a hack to make it easier to use cross without project file:

fullCurrentPath = os.path.realpath(__file__)
global currentPath
currentPath = os.path.dirname(fullCurrentPath)
relativePath = os.path.join(currentPath, "..")
classPath = os.path.realpath(relativePath)
sys.path.insert(0, classPath)

#
#############


class Test_nhltv_lib_download_nhl(unittest.TestCase):
    """
    To run this do the following from anywhere in the project:
    python -m unittest discover -v
    """
    teamID = 17
    dl = DownloadNHL(teamID)
    sampleDataFolder = os.path.join(currentPath, "data")
    download_file = os.path.join(sampleDataFolder, "test_download_file.txt")
    sample_schedule_epg_file = os.path.join(
        sampleDataFolder, "schedule.gamecontent.media.epg")
    with open(sample_schedule_epg_file) as data_file:
        json_source = json.load(data_file)

    sample_masterFile = os.path.join(sampleDataFolder, "master.m3u8")
    sample_inputFile = os.path.join(sampleDataFolder, "input.m3u8")

    def tearDown(self):
        if os.path.isfile(self.download_file):
            os.remove(self.download_file)

    def test01_check_for_new_game(self):
        json_source = self.dl.check_for_new_game('2017-03-14', '2017-03-17')
        self.assertTrue(isinstance(json_source, dict))

    @patch.object(requests, "get")
    def test02_check_for_new_game_returns_json(self, mock_requests):
        mock_requests.return_value = open(self.sample_schedule_epg_file)
        json_source = self.dl.check_for_new_game('2017-03-14', '2017-03-17')
        self.assertTrue(isinstance(json_source, dict),
                        "Expected json_source to be of type dict")

    @patch("nhltv_lib.download_nhl.get_setting", return_value=123)
    def test03_look_for_the_next_game_to_get(self, mock_patch):
        game, favTeamHomeAway = self.dl.look_for_the_next_game_to_get(
            self.json_source)
        self.assertEqual(game["teams"]["away"]["team"]
                         ['abbreviation'], "DET")
        self.assertEqual(favTeamHomeAway, "AWAY")

    @patch("nhltv_lib.download_nhl.get_setting", return_value=3016021040)
    def test_look_for_the_next_game_to_get_raises_NoGameFound(self, mock_patch):
        with self.assertRaises(NoGameFound):
            self.dl.look_for_the_next_game_to_get(self.json_source)

    @patch.object(nhltv_lib.download_nhl, "get_setting")
    @patch.object(requests, "get")
    @patch.object(nhltv_lib.download_nhl.DownloadNHL, "check_for_new_game")
    def test04_getGameId(self, mock_check_for_new_game, mock_requests, mock_get_setting):
        mock_check_for_new_game.return_value = self.json_source
        mock_requests.return_value = self.sample_schedule_epg_file
        mock_get_setting.return_value = 123
        gameID, contentID, eventID = self.dl.get_next_game()
        self.assertTrue(isinstance(gameID, int),
                        "Expected gameID to be of type int")
        self.assertTrue(isinstance(contentID, str),
                        "Expected contentID to be of type str")
        self.assertTrue(isinstance(eventID, str),
                        "Expected contentID to be of type str")

    def test05_getQualityUrlFromMasterDropToNextBest_m3u8(self):
        quality_url = self.dl.get_quality_url(
            self.sample_masterFile)
        self.assertTrue("3500K" in quality_url)

    def test06_createDownloadFile(self):
        quality_url = "http://hlslive-akc.med2.med.nhl.com/hdnts=exp=1489918789~acl=/*~id=nhlGatewayId:3821533~data=50068103~hmac=8004dc987fb52ff4b2aff47edbf6845a686755bdd2f34d66e9da312a265cb97f/5fa5a38415b1e0787f24aa9005f8377a/ls04/nhl/2017/03/17/NHL_GAME_VIDEO_BOSEDM_M2_HOME_20170317_1488820214854/3500K/3500_complete-trimmed.m3u8"
        self.dl.create_download_file(
            self.sample_inputFile, self.download_file, quality_url)


if __name__ == '__main__':
    unittest.main()
