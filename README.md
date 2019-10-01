# dl-nhltv

Download NHL.tv Streams with up to 720p60 and remove the commercial breaks

## Requirements:

- _You need A offical NHL.tv account to run this script! This is not for free!_
- Either Docker (recommended) - or a Mac/Linux machine with python 3, aria2c, openssl, ffmpeg

## Usage:

```
usage: nhltv [-h] -t TEAMID [-u USERNAME] [-p PASSWORD] [-q QUALITY]
             [-d DOWNLOAD_FOLDER] [-i CHECKINTERVAL] [-r] [-m]
             [-k RETENTIONDAYS] [-b DAYSBACK] [-o] [--debug]

nhltv: Download NHL TV

optional arguments:
  -h, --help            show this help message and exit

  -t TEAMID, --team TEAMID, --append-action TEAMID
                        Team ID i.e. 17 or DET or Detroit, can be used
                        multiple times

  -u USERNAME, --username USERNAME
                        User name of your NHLTV account

  -p PASSWORD, --password PASSWORD
                        Password of your NHL TV account

  -q QUALITY, --quality QUALITY
                        is highest by default you can set it to 5000, 3500,
                        1500, 900

  -d DOWNLOAD_FOLDER, --download_folder DOWNLOAD_FOLDER
                        Output folder where you want to store your final file
                        like $HOME/Desktop/NHL/

  -i CHECKINTERVAL, --checkinterval CHECKINTERVAL
                        Specify checkinterval in hours to look for new games,
                        default is 4

  -r, --retry           Usually works fine without, Use this flag if you want
                        it perfect

  -m, --mobile_video    Set this to also encode video for mobile devices

  -k RETENTIONDAYS, --keep RETENTIONDAYS
                        Specify how many days video and download logs are
                        kept, default is forever

  -b DAYSBACK, --days-back DAYSBACK
                        Specify how many days to go back when looking for a
                        game, default is 3

  -o, --obfuscate       Obfuscate the ending time of the video (pads the video
                        end with black video)

  --debug               Debug (shorten video)
```

# How to install nhltv

## Docker (recommended)

Using Docker is the easiest way to run dl-nhltv as you do not have to deal with dependencies yourself.

1. Install Docker (from https://docs.docker.com/install/)

2. Copy the docker-compose example file to docker-compose.yml (and edit the volume to point to where you want to save your output video)

3. Run with `docker-compose up` or run as a background service with `docker-compose up -d`


## Install nhltv script manually

1. Install aria2 and ffmpeg

2. Clone or download the repository to a folder, navigate to it in your terminal and run `sudo pip install .` or `sudo pip3 install .` depending on your Python installation.


## Run dl-nhltv

BEWARE ! This early version stores settings.json and temporary files in the folder you run it from!
Temporary files can exceed 5GB on your drive you want at least 10GB free space!
Best is to have a folder per team line to run the command in like $HOME/NHL/Detroit /$HOME/NHL/Capitals etc..

- Press Command+Space and type Terminal and press enter/return key.
- Run in Terminal app

```
nhltv -t Detroit
```

# How dl-nhltv works

When it runs it will check the nhl.tv servers for a new game for your team and if it finds it then it will download it. Then after it downloads it will do a loop and start looking for the next game. It saves the id of the last game in settings.json in the folder you ran it from so if you aren't getting the results you expect then take a look at the settings.json file and set the game id manually to be lower than the gameid you want to download. It also saves the username and password in the settings.json file when you pass it in via -u -p. Otherwise it will ask when the cookies run old.

# Files and folders

dl-nhltv downloads the parts of a stream into a temporary subfolder below the folder you started from.
Per game you have a different log file for the download.
You can watch the progress of the download by looking into the temp folder.
