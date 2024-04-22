# dl-nhltv

Download NHL.tv Streams with up to 720p60, remove the commercial breaks and obfuscate the ending time of
the video.

## Requirements:

- _You need A offical NHL.tv account to run this script! This is not for free!_
- Either Docker (recommended) - or a Mac/Linux machine with python >3.11, openssl, ffmpeg

## Installation

### Docker (recommended)

Using Docker is the easiest way to run dl-nhltv as you do not have to deal with dependencies yourself.

[Install Docker](https://docs.docker.com/install/)

#### Run interactively

1. `docker run -v /your/media/folder/:/home/nhltv/media -it ghcr.io/pppontusw/dl-nhltv:latest nhltv --team NSH -u *username* -p *password* -d media`

For information about which parameters are available, check the Usage section below.

If you prefer to build yourself you can run `docker build . -t nhltv:latest` in this folder and replace the image name above like `docker run -v ... -it nhltv:latest nhltv --team ...`

#### Run as a background service

1. Copy the docker-compose.example file to docker-compose.yml and edit the command and volume accordingly (see interactive example above) 

2. Run with `docker-compose up -d` and the service will stay in the background and download new games as they become available.

### Install nhltv manually

1. Install ffmpeg
2. Download the .whl (or the repository) and install with pip
3. Run with `nhltv --team NSH -u *username* -p *password*` and any optional arguments you want (see Usage)

## Usage

```bash
usage: main.py [-h] -t TEAM [TEAM ...] -u USERNAME -p PASSWORD [-d DOWNLOAD_FOLDER] [-i CHECKINTERVAL] [-k RETENTIONDAYS] [-b DAYS_BACK_TO_SEARCH] [--short-debug] [--debug]

main.py: Download NHL TV

options:
  -h, --help            show this help message and exit
  -t TEAM [TEAM ...], --team TEAM [TEAM ...]
                        Team name or ID - example: 'Nashville Predators', NSH or 18 (Multiple teams separated by spaces)
  -u USERNAME, --username USERNAME
                        Username of your NHLTV account
  -p PASSWORD, --password PASSWORD
                        Password of your NHLTV account
  -d DOWNLOAD_FOLDER, --download_folder DOWNLOAD_FOLDER
                        Final video destination e.g. $HOME/Desktop/NHL/
  -i CHECKINTERVAL, --checkinterval CHECKINTERVAL
                        Interval in minutes to look for new games (default: 10)
  -k RETENTIONDAYS, --keep RETENTIONDAYS
                        How many days video and logs are kept (default: forever)
  -b DAYS_BACK_TO_SEARCH, --days-back DAYS_BACK_TO_SEARCH
                        How many days back to search (default: 3)
  --short-debug         Shorten video length to 15 minutes for faster debugging
  --debug, --debug-dumps
                        Enable debugging -- adds extra logging and debug dumps in the ./dumps folder (NOTE: dumps may contain secrets, do not share)
```

### How dl-nhltv works

When it runs it will check the nhl.tv servers for a new game for your team and if it finds it then it will
download it. Then after it downloads it will do a loop and start looking for the next game.

Information about downloaded games are stored in a sqlite database in your target download folder (default:
folder where you run the program) called `nhltv_database`. If you need to reset the info about already downloaded
games you can remove this file and it will be recreated the next time the program runs.
If you know some sql you can of course maintain it manually with e.g. sqlite3, the data is stored in a single table `games`.

#### Files and folders

dl-nhltv downloads temporary files into a subdirectory for each game, relative to the location you run the program.
It will also save some settings in that same folder.
