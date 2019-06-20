import unittest
import os
import time
import sys
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from nhltv_lib.common import format_wait_time_string, which, tprint, wait

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


class TestCommon(unittest.TestCase):

    def test_whichIsTrueOnExistingCommand(self):
        self.assertTrue(which("ls"))

    def test_whichIsFalseOnMissingCommand(self):
        self.assertFalse(which("lsasdkfld"))

    @unittest.skip("Real test is taking to long")
    def test_wait(self):
        wait(minutes=1.1, reason="For some reason.")
        tprint("Was this a minute?")

    @unittest.skip("Real test is taking to long")
    def test_wait5min(self):
        wait(minutes=5, reason="For some reason.")
        tprint("Was this 5 minutes?")

    def test_format_wait_time_string_minute(self):
        self.assertEqual(format_wait_time_string(1), "1 minute")

    def test_format_wait_time_string_minutes(self):
        self.assertEqual(format_wait_time_string(2), "2 minutes")

    def test_format_wait_time_string_hour(self):
        self.assertEqual(format_wait_time_string(1.0 * 60), "1 hour")

    def test_format_wait_time_string_hours(self):
        self.assertEqual(format_wait_time_string(2 * 60), "2 hours")

    def test_format_wait_time_string_day(self):
        self.assertEqual(format_wait_time_string(24 * 60), "1 day")

    @unittest.skip("Real test is taking to long")
    @patch.object(time, "time")
    def test_waitCanContinue(self, mock_time_time):
        startTime = 1000.0
        midTime = startTime + 23 * 60 * 60
        endTime = startTime + 24 * 60 * 60
        mock_time_time.side_effect = [startTime, startTime + 10, startTime + 20, startTime + 30, midTime,
                                      midTime + 10, midTime + 60 * 40, midTime + 60 * 40, midTime + 60 * 40, endTime, endTime, endTime]
        wait(minutes=24 * 60, reason="For testing.")
        tprint("done waiting")


if __name__ == "__main__":
    unittest.main()
