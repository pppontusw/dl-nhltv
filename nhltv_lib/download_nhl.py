import os
from glob import iglob
from shutil import rmtree, move
import re
import subprocess
from datetime import timedelta
from datetime import datetime
import time
import json
from urllib.parse import quote_plus
import requests
from nhltv_lib.common import (
    tprint,
    save_cookies_to_txt,
    set_setting,
    get_setting,
)
from nhltv_lib.common import wait, save_cookie, load_cookie, print_progress_bar
from nhltv_lib.common import call_subprocess
from nhltv_lib.exceptions import (
    CredentialsError,
    BlackoutRestriction,
    NoGameFound,
)
from nhltv_lib.exceptions import (
    DownloadError,
    ExternalProgramError,
    DecodeError,
)
from nhltv_lib.constants import UA_NHL, UA_PC


class DownloadNHL:
    def __init__(self, teamID=0):
        self.teamID = teamID

        self.session = requests.session()
        self.session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-encoding": "gzip, deflate, sdch",
            "Accept-language": "en-US,en;q=0.8",
            "User-agent": UA_PC,
            "Origin": "https://www.nhl.com",
        }

        # These are initialized when a game is found
        self.game_id = None
        self.content_id = None
        self.event_id = None
        self.cookie_txt = None  # game_id.txt
        self.temp_folder = None  # ./game_id

        # These will be initialized when a stream is fetched
        self.stream_url = None
        self.game_info = None

    def remove_lines_without_errors(self, errors):
        # Open download file
        download_file = open(self.temp_folder + "/download_file.txt", "r+")
        download_file_lines = download_file.readlines()

        download_file.seek(0)
        writeNext = False
        for line in download_file_lines:
            for error in errors:
                # For each error check to see if it is in the line
                # If it is then write that line and the next one
                if error in line:
                    download_file.write(line)
                    writeNext = True
                if writeNext and "out=" + self.temp_folder in line:
                    download_file.write(line)
                    writeNext = False
        download_file.truncate()
        download_file.close()

    def redo_broken_downloads(self, outFile):
        DOWNLOAD_OPTIONS = (
            " --load-cookies="
            + self.cookie_txt
            + " --log='"
            + outFile
            + "_dl.log' --log-level=notice --quiet=true --retry-wait=1 --max-file-not-found=5"
            + " --max-tries=5 --header='Accept: */*' --header='Accept-Language: en-US,en;q=0.8'"
            + " --header='Origin: https://www.nhl.com' -U='%s'" % UA_PC
            + " --enable-http-pipelining=true --auto-file-renaming=false --allow-overwrite=true "
        )

        logFileName = outFile + "_dl.log"

        # Set counters
        lastErrorCount = 0
        lastLineNumber = 0

        while True:
            # Loop through log file looking for errors
            logFile = open(logFileName, "r")
            log_file_lines = logFile.readlines()
            log_file_lines_str = str(log_file_lines)
            errors = []
            curLineNumber = 0
            download_file = open(self.temp_folder + "/download_file.txt", "r+")
            download_file_lines = download_file.readlines()
            download_file.close()

            for line in log_file_lines:
                curLineNumber = curLineNumber + 1
                if curLineNumber > lastLineNumber:
                    # Is line an error?
                    if "[ERROR]" in line:
                        error_match = re.search(
                            r"/.*K/(.*)", line, re.M | re.I
                        ).group(1)
                        failed_url = line.split("URI=")[1]
                        if "-l3c" in failed_url:
                            l3c_url = failed_url.replace("\n", "")
                            akc_url = failed_url.replace("\n", "").replace(
                                "-l3c", "-akc"
                            )

                        elif "-akc" in failed_url:
                            akc_url = failed_url.replace("\n", "")
                            l3c_url = failed_url.replace("\n", "").replace(
                                "-akc", "-l3c"
                            )
                        else:
                            errors.append(error_match)
                            break
                        try:
                            index_in_download_file = download_file_lines.index(
                                f"{l3c_url}\t{akc_url}\n"
                            )
                        except ValueError:
                            index_in_download_file = download_file_lines.index(
                                f"{akc_url}\t{l3c_url}\n"
                            )
                        download_output_file = download_file_lines[
                            index_in_download_file + 1
                        ].replace("out=", "")
                        download_output_file = download_output_file.strip()
                        if download_output_file not in log_file_lines_str:
                            # no download completed exists for this file
                            errors.append(error_match)

            lastLineNumber = curLineNumber
            logFile.close()

            if errors:
                tprint("Found " + str(len(errors)) + " download errors.")
                if lastErrorCount == len(errors):
                    wait(
                        reason="Same number of errrors as last time so waiting 10 minutes",
                        minutes=10,
                    )
                self.remove_lines_without_errors(errors)

                tprint("Trying to download the erroneous files again...")

                # Use aria2 to download the list
                command = "aria2c -i %s/download_file.txt -j 20 %s" % (
                    self.temp_folder,
                    DOWNLOAD_OPTIONS,
                )
                _ = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                ).wait()

                lastErrorCount = len(errors)
            else:
                break

    def get_quality_url(self, masterFile):
        # Parse the master and get the quality URL
        fh = open(masterFile, "r")

        quality = get_setting("QUALITY", "GLOBAL")

        for line in fh:
            if quality + "K" in line:
                return line
            last_line = line

        # Otherwise we return the highest value
        return last_line

    def download_web_page(self, url, outputFile, logFile):
        DOWNLOAD_OPTIONS = (
            " --load-cookies="
            + self.cookie_txt
            + " --log='"
            + logFile
            + "' --log-level=notice --quiet=true --retry-wait=1 --max-file-not-found=5"
            + " --max-tries=5 --header='Accept: */*' --header='Accept-Language: en-US,en;q=0.8'"
            + " --header='Origin: https://www.nhl.com'"
            + " -U='%s'" % UA_PC
            + " --enable-http-pipelining=true --auto-file-renaming=false --allow-overwrite=true "
        )
        command = "aria2c -o " + outputFile + DOWNLOAD_OPTIONS + url
        subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        ).wait()

    def create_download_file(self, inputFile, download_file, quality_url):
        download_file = open(download_file, "w")
        quality_url_root = re.search(
            r"(.*/)(.*)", quality_url, re.M | re.I
        ).group(1)

        fh = open(inputFile, "r")
        ts_number = 0
        key_number = 0
        cur_iv = 0
        decode_hashes = []

        for line in fh:
            if "#EXT-X-KEY" in line:
                # Incremenet key number
                key_number = key_number + 1

                # Pull the key url and iv
                in_line_match = re.search(
                    r'.*"(.*)",IV=0x(.*)', line, re.M | re.I
                )
                key_url = in_line_match.group(1)
                cur_iv = in_line_match.group(2)

                # Add file to download list
                download_file.write(key_url + "\n")
                download_file.write(
                    " out=%s/keys/%s\n" % (self.temp_folder, str(key_number))
                )

            elif ".ts\n" in line:
                # Increment ts number
                ts_number = ts_number + 1

                # Make alternate uri
                alt_quality_url_root = quality_url_root
                if "-l3c." in alt_quality_url_root:
                    alt_quality_url_root = alt_quality_url_root.replace(
                        "-l3c.", "-akc."
                    )
                else:
                    alt_quality_url_root = alt_quality_url_root.replace(
                        "-akc.", "-l3c."
                    )

                # Add file to download list
                download_file.write(
                    quality_url_root
                    + line.strip("\n")
                    + "\t"
                    + alt_quality_url_root
                    + line
                )
                download_file.write(
                    " out=%s/%s.ts\n" % (self.temp_folder, str(ts_number))
                )

                # Add to decode_hashes
                decode_hashes.append(
                    {
                        "key_number": str(key_number),
                        "ts_number": str(ts_number),
                        "iv": str(cur_iv),
                    }
                )
        download_file.close()
        return decode_hashes

    def download_nhl(self, url, outFile):
        logFile = outFile + "_dl.log"
        if os.path.exists(logFile):
            os.remove(logFile)
        DOWNLOAD_OPTIONS = (
            " --load-cookies="
            + self.cookie_txt
            + " --log='"
            + logFile
            + "' --log-level=notice --quiet=false --retry-wait=1 --max-file-not-found=5"
            + " --max-tries=5 --header='Accept: */*' --header='Accept-Language: en-US,en;q=0.8'"
            + " --header='Origin: https://www.nhl.com' -U='%s'" % UA_PC
            + " --enable-http-pipelining=true --auto-file-renaming=false --allow-overwrite=true "
        )
        tprint("Starting Download: " + url)
        # Pull url_root
        url_root = re.match(
            "(.*)master_tablet60.m3u8", url, re.M | re.I
        ).group(1)

        # Create the temp and keys directory
        if not os.path.exists("%s/keys" % self.temp_folder):
            os.makedirs("%s/keys" % self.temp_folder)

        # Get the master m3u8
        masterFile = "%s/master.m3u8" % self.temp_folder
        self.download_web_page(url, masterFile, logFile)
        quality_url = url_root + self.get_quality_url(masterFile)

        # Get the m3u8 for the quality
        inputFile = "%s/input.m3u8" % self.temp_folder
        self.download_web_page(quality_url, inputFile, logFile)

        # Parse m3u8
        # Create files
        download_file = "%s/download_file.txt" % self.temp_folder
        decode_hashes = self.create_download_file(
            inputFile, download_file, quality_url
        )

        #  for testing only shorten it to 100
        if get_setting("DEBUG", "GLOBAL"):
            tprint("shorting to 100 files for testing")
            command = "mv %s/download_file.txt %s/download_file_orig.txt;" % (
                self.temp_folder,
                self.temp_folder,
            )
            command += (
                "head -100 %s/download_file_orig.txt > %s/download_file.txt;"
                % (self.temp_folder, self.temp_folder)
            )
            command += "rm -f %s/download_file_orig.txt;" % self.temp_folder
            decode_hashes = decode_hashes[:45]
            p = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
            p.wait()

        retry_errored_downloads = get_setting(
            "RETRY_ERRORED_DOWNLOADS", "GLOBAL"
        )

        # User aria2 to download the list
        tprint("starting download of individual video files")
        command = "aria2c -i %s/download_file.txt -j 20 %s" % (
            self.temp_folder,
            DOWNLOAD_OPTIONS,
        )
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )

        # Track progress and print progress bar
        progress = 0
        for line in iter(p.stdout.readline, b""):
            if b"Download complete" in line and b".ts\n" in line:
                if progress < len(decode_hashes):
                    progress += 1
                    print_progress_bar(
                        progress,
                        len(decode_hashes),
                        prefix="Downloading:",
                        suffix="Complete",
                        length=50,
                    )
        p.wait()
        if p.returncode != 0 and not retry_errored_downloads:
            raise DownloadError("Download failed, see logs: %s" % logFile)

        # Repair broken downloads if necessary
        if retry_errored_downloads is True:
            tprint("Checking download log for errors..")
            self.redo_broken_downloads(outFile)

        # Create the concat file
        concat_file = open(self.temp_folder + "/concat.txt", "w")

        # Iterate through the decode_hashes and run the decoder function
        tprint("Decode video files")
        progress = 0
        for dH in decode_hashes:
            cur_key = "blank"
            key_val = ""

            if progress < len(decode_hashes):
                progress += 1
                print_progress_bar(
                    progress,
                    len(decode_hashes),
                    prefix="Decoding:",
                    suffix="Complete",
                    length=50,
                )

            # If the cur_key isn't the one from the has then refresh the key_val
            if cur_key != dH["key_number"]:
                # Extract the key value
                command = "xxd -p %s/keys/%s" % (
                    self.temp_folder,
                    dH["key_number"],
                )
                p = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                pi = iter(p.stdout.readline, b"")
                for line in pi:
                    key_val = line.strip(b"\n")
                    cur_key = dH["key_number"]
                p.wait()
                if p.returncode != 0:
                    raise ExternalProgramError(p.stdout.readlines())

            # Decode TS
            command = (
                'openssl enc -aes-128-cbc -in "'
                + self.temp_folder
                + "/"
                + dH["ts_number"]
                + '.ts" -out "'
                + self.temp_folder
                + "/"
                + dH["ts_number"]
                + '.ts.dec" -d -K '
                + key_val.decode()
                + " -iv "
                + dH["iv"]
            )
            p = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
            p.wait()
            if p.returncode != 0:
                raise DecodeError(p.stdout.readlines())

            # Move decoded files over old files
            command = (
                "mv "
                + self.temp_folder
                + "/"
                + dH["ts_number"]
                + ".ts.dec "
                + self.temp_folder
                + "/"
                + dH["ts_number"]
                + ".ts"
            )
            call_subprocess(command)

            # Add to concat file
            concat_file.write("file " + dH["ts_number"] + ".ts\n")

        # close concat file
        concat_file.close()

        tprint("Merge to a single video")
        # merge to single
        command = (
            "ffmpeg -y -nostats -loglevel 0 -f concat -i "
            + self.temp_folder
            + "/concat.txt -c copy -bsf:a aac_adtstoasc "
            + self.temp_folder
            + "/"
            + outFile
        )
        call_subprocess(command)
        for path in iglob(os.path.join(self.temp_folder, "*.ts")):
            os.remove(path)

    def get_auth_cookie(self):
        authorization = ""
        cj = load_cookie()

        # If authorization cookie is missing or stale, perform login
        for cookie in cj:
            if cookie.name == "Authorization" and not cookie.is_expired():
                authorization = cookie.value

        return authorization

    def fetch_stream(self):
        stream_url = ""

        authorization = self.get_auth_cookie()

        if authorization == "":
            self.login()
            authorization = self.get_auth_cookie()
            if authorization == "":
                return stream_url, ""

        self.session.cookies = load_cookie()

        tprint("Fetching session_key")
        session_key = self.get_session_key(authorization)

        tprint("Checking session key")
        if session_key == "":
            return stream_url, ""

        # Org
        url = "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId="
        url += (
            str(self.content_id)
            + "&playbackScenario=HTTP_CLOUD_TABLET_60&platform=IPAD&sessionKey="
        )
        url += quote_plus(session_key)

        extra_headers = {"Authorization": authorization, "User-Agent": UA_NHL}

        json_source = self.session.get(
            url, headers={**self.session.headers, **extra_headers}
        ).json()

        # Pulling out game_info in formated like "2017-03-06_VAN-ANA" for file name prefix
        game_info = self.get_game_info(json_source)
        tprint("game info=" + game_info)

        # Expecting - values to always be bad i.e.:
        #  -3500 is Sign-on restriction:
        # Too many usage attempts
        if json_source["status_code"] < 0:
            raise CredentialsError(json_source["status_message"])

        if json_source["status_code"] == 1:
            if (
                json_source["user_verified_event"][0]["user_verified_content"][
                    0
                ]["user_verified_media_item"][0]["blackout_status"]["status"]
                == "BlackedOutStatus"
            ):
                msg = "This game is affected by blackout restrictions."
                tprint(msg)
                raise BlackoutRestriction

        stream_url = json_source["user_verified_event"][0][
            "user_verified_content"
        ][0]["user_verified_media_item"][0]["url"]
        media_auth = (
            str(
                json_source["session_info"]["sessionAttributes"][0][
                    "attributeName"
                ]
            )
            + "="
            + str(
                json_source["session_info"]["sessionAttributes"][0][
                    "attributeValue"
                ]
            )
        )
        session_key = json_source["session_key"]
        set_setting(sid="media_auth", value=media_auth, tid=self.teamID)

        # Update Session Key
        set_setting(sid="session_key", value=session_key, tid=self.teamID)

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
        self.session.cookies.set_cookie(media_auth_cookie)
        save_cookies_to_txt(self.session.cookies, self.cookie_txt)

        self.stream_url, self.game_info = stream_url, game_info
        return stream_url, game_info

    def get_game_info(self, json_source=json):
        """
        ==================================================
        Game info for file prefix like 2017-03-06_VAN-ANA
        ==================================================

        Arguments:
            json_source (json): The first parameter.

        Returns:
            str: game info string like 2017-03-06_VAN-ANA
        """
        if json_source["status_code"] == -3500:
            tprint(json_source["status_message"])
            raise CredentialsError
        game_info = json_source["user_verified_event"][0][
            "user_verified_content"
        ][0]["name"].replace(":", "|")
        game_time, game_teams, _ = game_info.split(" | ")
        game_teams = game_teams.split()[0] + "-" + game_teams.split()[2]
        return game_time + "_" + game_teams

    def get_session_key(self, authorization):
        session_key = str(get_setting(sid="session_key", tid=self.teamID))

        if session_key == "":
            tprint("Need to fetch new session key")
            epoch_time_now = str(int(round(time.time() * 1000)))

            url = "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId="
            url += (
                self.event_id
                + "&format=json&platform=WEB_MEDIAPLAYER&subject=NHLTV&_="
            )
            url += epoch_time_now

            referer = "https://www.nhl.com/tv/%s/%s/%s" % (
                self.game_id,
                self.event_id,
                self.content_id,
            )

            extra_headers = {
                "Authorization": authorization,
                "Referer": referer,
            }

            json_source = self.session.get(
                url, headers={**self.session.headers, **extra_headers}
            ).json()

            tprint("status_code" + str(json_source["status_code"]))
            # Expecting - values to always be bad i.e.:
            # -3500 is Sign-on restriction:
            # Too many usage attempts
            if json_source["status_code"] < 0:
                tprint(json_source["status_message"])
                raise CredentialsError

            tprint("REQUESTED SESSION KEY")

            if json_source["status_code"] == 1:
                if (
                    json_source["user_verified_event"][0][
                        "user_verified_content"
                    ][0]["user_verified_media_item"][0]["blackout_status"][
                        "status"
                    ]
                    == "BlackedOutStatus"
                ):
                    msg = "This game is affected by blackout restrictions."
                    tprint(msg)
                    return "blackout"
            session_key = str(json_source["session_key"])
            set_setting(sid="session_key", value=session_key, tid=self.teamID)

        return session_key

    def login(self):
        username = get_setting("USERNAME", "GLOBAL")
        password = get_setting("PASSWORD", "GLOBAL")

        tprint("Need to login to NHL Gamecenter")

        # Check if username and password are provided
        if (username == "") or (password == ""):
            raise CredentialsError("Please provide a username or password!")

        # Get Token
        get_token_url = "https://user.svc.nhl.com/oauth/token?grant_type=client_credentials"
        # from https:/www.nhl.com/tv?affiliated=NHLTVLOGIN

        auth_token = "Basic d2ViX25obC12MS4wLjA6MmQxZDg0NmVhM2IxOTRhMThlZjQwYWM5ZmJjZTk3ZTM="
        get_token_auth_header = {"Authorization": auth_token}
        json_source = self.session.post(
            get_token_url,
            headers={**self.session.headers, **get_token_auth_header},
        ).json()

        authorization = self.get_auth_cookie()
        if authorization == "":
            authorization = json_source["access_token"]

        url = "https://gateway.web.nhl.com/ws/subscription/flow/nhlPurchase.login"
        login_data = (
            '{"nhlCredentials":{"email":"'
            + username
            + '","password":"'
            + password
            + '"}}'
        )

        self.session.headers["Authorization"] = authorization
        # self.session.headers['Accept'] = '*/*'
        req = self.session.post(url, data=login_data)
        if req.status_code != 200:
            tprint("There was an error with the login request")
            if req.status_code == 401:
                tprint("Your username and password is likely incorrect")
        save_cookie(self.session.cookies)

    def check_for_new_game(self, startDate="YYYY-MM-DD", endDate="YYYY-MM-DD"):
        """
        Fetches game schedule between two dates and returns it as a json source
        """
        tprint(
            "Checking for new game between " + startDate + " and " + endDate
        )

        url = (
            "http://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.teams,schedule"
            + ".linescore,schedule.scoringplays,schedule.game.content.media.epg&startDate="
        )
        url += (
            startDate
            + "&endDate="
            + endDate
            + "&site=en_nhl&platform=playstation"
        )
        tprint("Looking up games @ " + url)

        response = self.session.get(url).json()
        return response

    def look_for_the_next_game_to_get(self, json_source):
        """
        Get NHL TV Team names
        Class parses all teams so that you can pull from it.

        Arguments:
            json_source (json): json object form schelude.gamecontent.media.epg

        Returns:
            game (json): Json object of next game
            favTeamHomeAway (string): String if the teams a "AWAY" or "HOME" feed

        """
        favTeamHomeAway = "HOME"
        lastGame = get_setting("lastGameID", self.teamID)

        for jd in json_source["dates"]:
            for jg in jd["games"]:
                homeTeamId = int(jg["teams"]["home"]["team"]["id"])
                awayTeamId = int(jg["teams"]["away"]["team"]["id"])
                game_id = jg["gamePk"]

                if (
                    homeTeamId == self.teamID or awayTeamId == self.teamID
                ) and game_id > lastGame:
                    if awayTeamId == self.teamID:
                        favTeamHomeAway = "AWAY"
                    return (jg, favTeamHomeAway)
        raise NoGameFound

    def get_next_game(self):
        """
        Gets the next game info and returns it
        """
        current_time = datetime.now()
        days_back = get_setting("DAYSBACK", "GLOBAL")
        startDate = (
            current_time.date() - timedelta(days=days_back)
        ).isoformat()
        endDate = current_time.date().isoformat()
        json_source = self.check_for_new_game(startDate, endDate)

        # Go through all games in the file and look for the next game
        gameToGet, favTeamHomeAway = self.look_for_the_next_game_to_get(
            json_source
        )

        bestScore = -1
        bestEpg = None
        for epg in gameToGet["content"]["media"]["epg"][0]["items"]:
            score = 0
            if epg["language"] == "eng":
                score = score + 100
            if epg["mediaFeedType"] == favTeamHomeAway:
                score = score + 50
            if score > bestScore:
                bestScore = score
                bestEpg = epg

        # If there isn't a bestEpg then treat it like an archive case
        if bestEpg is None:
            bestEpg = {}
            bestEpg["mediaState"] = ""

        # If the feed is good to go then return the info
        if bestEpg["mediaState"] == "MEDIA_ARCHIVE":
            game_id = gameToGet["gamePk"]
            content_id = str(bestEpg["mediaPlaybackId"])
            event_id = str(bestEpg["eventId"])
            tprint("Found a game: " + str(game_id))
            self.game_id, self.content_id, self.event_id = (
                game_id,
                content_id,
                event_id,
            )
            self.cookie_txt = "%s.txt" % str(self.game_id)
            self.temp_folder = "./%s" % str(self.game_id)
            return game_id, content_id, event_id

        # If it is not then figure out how long to wait and wait
        # If the game hasn't started then wait until 3 hours after the game has started
        startDateTime = datetime.strptime(
            gameToGet["gameDate"], "%Y-%m-%dT%H:%M:%SZ"
        )
        if startDateTime > datetime.utcnow():
            waitUntil = startDateTime + timedelta(minutes=180)
            if datetime.utcnow() > waitUntil:
                wait(15)
                return self.get_next_game()
            waitTimeInMin = (
                (waitUntil - datetime.utcnow()).total_seconds()
            ) / 60
            tprint(
                "Game scheduled for "
                + gameToGet["gameDate"]
                + " hasn't started yet"
            )
            wait(waitTimeInMin)
            return self.get_next_game()

        raise NoGameFound

    def skip_silence(self, inputFile):
        """
        Analyzes the video for silent parts and removes them
        """
        inputFile = self.temp_folder + "/" + inputFile
        tprint("Analyzing " + inputFile + " for silence.")
        command = (
            "ffmpeg -y -nostats -i "
            + inputFile
            + " -af silencedetect=n=-50dB:d=10 -c:v copy -c:a libmp3lame -f mp4 /dev/null"
        )
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        pi = iter(p.stdout.readline, b"")
        marks = []
        marks.append("0")
        for line in pi:
            line = line.decode()
            if "silencedetect" in line:
                start_match = re.search(
                    r".*silence_start: (.*)", line, re.M | re.I
                )
                end_match = re.search(
                    r".*silence_end: (.*) \|.*", line, re.M | re.I
                )
                if (start_match is not None) and (start_match.lastindex == 1):
                    marks.append(start_match.group(1))

                    # tprint("Start: " + start_match.group(1))
                if (end_match is not None) and end_match.lastindex == 1:
                    marks.append(end_match.group(1))
                # tprint("End: " + end_match.group(1))
        # If it is not an even number of segments then add the end point. If the last silence goes
        # to the endpoint then it will be an even number.
        if len(marks) % 2 == 1:
            marks.append("end")

        tprint("Creating segments.")
        seg = 0
        # Create segments
        for i, mark in enumerate(marks):
            if i % 2 == 0:
                if marks[i + 1] != "end":
                    seg = seg + 1
                    length = float(marks[i + 1]) - float(mark)
                    command = (
                        "ffmpeg -y -nostats -i "
                        + inputFile
                        + " -ss "
                        + str(mark)
                        + " -t "
                        + str(length)
                        + " -c:v copy -c:a copy "
                        + self.temp_folder
                        + "/cut"
                        + str(seg)
                        + ".mp4"
                    )
                else:
                    seg = seg + 1
                    command = (
                        "ffmpeg -y -nostats -i "
                        + inputFile
                        + " -ss "
                        + str(mark)
                        + " -c:v copy -c:a copy "
                        + self.temp_folder
                        + "/cut"
                        + str(seg)
                        + ".mp4"
                    )
                call_subprocess(command)
                print_progress_bar(
                    seg,
                    len(marks),
                    prefix="Creating segments:",
                    suffix="Complete",
                    length=50,
                )

        # Create file list
        fh = open("%s/concat_list.txt" % self.temp_folder, "w")
        for i in range(1, seg + 1):
            # if some cut doesn't contain a video stream,
            # it will break the output file
            command = (
                "ffprobe -i %s/cut%s.mp4 -show_streams -select_streams v -loglevel error"
                % (self.temp_folder, str(i))
            )
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            p.wait()
            if p.returncode != 0:
                raise ExternalProgramError(p.stdout.readlines())
            if p.stdout.readlines() != []:
                fh.write("file\t" + "cut" + str(i) + ".mp4\n")
        fh.close()

        command = (
            "ffmpeg -y -nostats -f concat -i %s/concat_list.txt -c copy %s"
            % (self.temp_folder, inputFile)
        )
        tprint(
            "Merging segments back to single video and saving: " + inputFile
        )
        call_subprocess(command)
        for path in iglob(os.path.join(self.temp_folder, "cut*.mp4")):
            os.remove(path)

    def clean_up(self):
        """
        Removes cookies and temp folder
        """
        os.remove(self.cookie_txt)

        # Erase temp
        rmtree(self.temp_folder)

    def move_file(self, inputFile, outputFile):
        """
        Moves the final product to the DOWNLOAD_FOLDER
        """
        inputFile = self.temp_folder + "/" + inputFile
        # Create the download directory if required
        command = "mkdir -p $(dirname " + outputFile + ")"
        call_subprocess(command)
        move(inputFile, outputFile)

    def obfuscate(self, inputFile, outputFile):
        """
        Pads the end of the video with 100 minutes of black
        """
        outputFile = self.temp_folder + "/" + outputFile
        black = os.path.join(os.path.dirname(__file__), "extras/black.mkv")
        fh = open("%s/obfuscate_concat_list.txt" % self.temp_folder, "w")
        fh.write("file\t" + inputFile + "\n")
        for _ in range(100):
            fh.write("file\t" + black + "\n")
        fh.close()
        command = (
            "ffmpeg -y -nostats -f concat -safe 0 -i %s/%s.txt -c copy %s"
            % (self.temp_folder, "obfuscate_concat_list", outputFile)
        )
        call_subprocess(command)
        os.remove(os.path.join(self.temp_folder, inputFile))

    def cut_to_closest_hour(self, inputFile, outputFile):
        """
        Cuts video to the closest hour, rounding down, minimum 1
        """
        inputFile = self.temp_folder + "/" + inputFile
        outputFile = self.temp_folder + "/" + outputFile
        command = (
            "ffprobe -v error -show_entries format=duration -of \
                    default=noprint_wrappers=1:nokey=1 %s"
            % inputFile
        )
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        p.wait()
        if p.returncode != 0:
            raise ExternalProgramError(p.stdout.readlines())
        length = p.stdout.readlines()[0]
        length = int(length.split(b".")[0])
        len_in_hours = length / 3600
        desired_len_in_seconds = (
            int(len_in_hours) * 3600 if int(len_in_hours) > 0 else 3600
        )
        command = "ffmpeg -ss 0 -i %s -t %d -c copy %s" % (
            inputFile,
            desired_len_in_seconds,
            outputFile,
        )
        call_subprocess(command)
        os.remove(inputFile)
