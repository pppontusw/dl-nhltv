import json
from datetime import datetime
import os
import subprocess
import time
import pickle

try:
    from http.cookiejar import MozillaCookieJar
except ImportError:
    from cookielib import MozillaCookieJar

from nhltv_lib.constants import SETTINGS_FILE, COOKIES_LWP_FILE


def tprint(outString):
    outString = datetime.now().strftime('%m/%d/%y %H:%M:%S - ') + outString
    print(outString)


def find(source, start_str, end_str):
    start = source.find(start_str)
    end = source.find(end_str, start + len(start_str))

    if start != -1:
        return source[start + len(start_str):end]
    return ''


def get_setting(sid, tid):
    TEAMSETTINGS_FILE = SETTINGS_FILE + "." + str(tid)
    # Ensure file exists
    if not os.path.isfile(TEAMSETTINGS_FILE):
        create_settings_file(TEAMSETTINGS_FILE)

    # Load the settings file
    with open(TEAMSETTINGS_FILE, "r") as settingsFile:
        j = json.load(settingsFile)
    settingsFile.close()
    if sid in j:
        return j[sid]
    return ''


def set_setting(sid, value, tid):
    TEAMSETTINGS_FILE = SETTINGS_FILE + "." + str(tid)
    # Ensure file exists
    if not os.path.isfile(TEAMSETTINGS_FILE):
        create_settings_file(TEAMSETTINGS_FILE)

    # Write to settings file
    with open(TEAMSETTINGS_FILE, "r") as settingsFile:
        j = json.load(settingsFile)

    settingsFile.close()
    j[sid] = value

    with open(TEAMSETTINGS_FILE, "w") as settingsFile:
        json.dump(j, settingsFile, indent=4)

    settingsFile.close()


def save_cookies_to_txt(cookies, file):
    # Ensure the cookie file exists
    if not os.path.isfile(file):
        touch(file)

    cjT = MozillaCookieJar(file)
    for cookie in cookies:
        cjT.set_cookie(cookie)
    cjT.save(ignore_discard=False)


def load_cookie():
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIES_LWP_FILE):
        touch(COOKIES_LWP_FILE)

    with open(COOKIES_LWP_FILE, 'rb') as f:
        try:
            return pickle.load(f)
        except EOFError:
            return []


def save_cookie(cookies):
    # Ensure the cookie file exists
    if not os.path.isfile(COOKIES_LWP_FILE):
        touch(COOKIES_LWP_FILE)

    with open(COOKIES_LWP_FILE, 'wb') as f:
        return pickle.dump(cookies, f)


def touch(fname):
    with open(fname, 'w'):
        pass


def create_settings_file(fname):
    with open(fname, "w") as settingsFile:
        jstring = """{
    "session_key": "000",
    "media_auth": "mediaAuth=000",
    "lastGameID": 2015030166
}"""
        j = json.loads(jstring)
        json.dump(j, settingsFile, indent=4)


def which(program):
    command = 'which ' + program
    returnCode = subprocess.Popen(
        command, stdout=subprocess.PIPE, shell=True).wait()
    if returnCode == 0:
        return True
    return False


def format_wait_time_string(minutes):
    """
    Formats  minutes in int to a human readable string
    """
    minutes = float(int(minutes))
    if minutes >= 60 * 24:
        unit = "day"
        if minutes > 60 * 24:
            unit += "s"
        waitTime = minutes / 60 / 24
    elif minutes >= 60:
        unit = "hour"
        if minutes >= 120:
            unit += "s"
        waitTime = minutes / 60
    else:
        unit = "minute"
        if minutes >= 2:
            unit += "s"
        waitTime = minutes
    return str(int(waitTime)) + " " + unit


def wait(minutes=0, reason=""):
    """
    Wait for minutes by comparing elapsed epoch time instead of sleep.
    So if the computer wakes up from sleep or suspend we don't wait longer.
    We also let the user know that we noticed the time jump.
    """

    tprint(reason + " Waiting for " + format_wait_time_string(minutes))

    # Find out destination time
    epochTo = time.time() + minutes * 60.0

    # Time to sleep in between checking
    sleepTime = 10.0

    # Storing current time so that we can figure out if there was a time jump
    epochBeforeSleep = time.time()

    while epochTo > epochBeforeSleep:
        time.sleep(sleepTime)

        # Check if we had a time jump
        epochNow = time.time()
        timeDelta = epochNow - epochBeforeSleep - sleepTime

        # When a time jump is bigger than the sleep time
        # we know we where sleeping and need to re-evaluate the situation.
        if timeDelta > sleepTime:
            # if we where sleeping longer then we had to wait
            if epochNow > epochTo:
                return

            # still time left to wait
            remainingMin = (epochTo - epochNow) / 60
            tprint("Remaining waiting time " +
                   format_wait_time_string(remainingMin))
        epochBeforeSleep = time.time()


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Prints an updatable terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filled = int(length * iteration // total)
    bar_ = fill * filled + '-' * (length - filled)
    print('\r%s |%s| %s%% %s' % (prefix, bar_, percent, suffix), end='\r')

    if iteration == total:
        print()
