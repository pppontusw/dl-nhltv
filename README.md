# dl-nhltv
[![Build Status](https://github.com/pppontusw/dl-nhltv/workflows/Python%20package/badge.svg)](https://github.com/pppontusw/dl-nhltv/actions)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/pontusw/nhltv)
![Codecov](https://img.shields.io/codecov/c/github/pppontusw/dl-nhltv)


![Sonar Tech Debt](https://img.shields.io/sonar/tech_debt/pppontusw_dl-nhltv?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/pppontusw_dl-nhltv?server=https%3A%2F%2Fsonarcloud.io)


![Docker Pulls](https://img.shields.io/docker/pulls/pontusw/nhltv)


Download NHL.tv Streams with up to 720p60, remove the commercial breaks and obfuscate the ending time of
the video.

## About the fork

This is an near complete rewrite of the original dl-nhltv project by [cmaxwe](https://github.com/cmaxwe/dl-nhltv) with 
the main goal being improving maintainability, stability and fixing a number of bugs. 

I found myself debugging a lot of issues in the original project but even after a few refactoring sessions the codebase was difficult to test
and maintain so I decided to do this rewrite reusing only some of the core logic.

Biggest differences are:
- Upgraded to python 3, where the original was python 2
- Unit test code coverage >90% compared to the previous ~30%
- Added a linter (flake8) that now reports no issues
- Added strict type checking with mypy
- Added static code analysis with sonarcloud
- Added CI to automate all of the above
- Added CD with automated Docker image builds to Docker Hub

New features:
- Added obfuscation of the video length, so that the final minutes in the 3rd period stay interesting even if you pause or otherwise glance at the remaining time of the video
- Added progress bars to a number of long running tasks such as downloading and decoding
- Added the ability to choose which stream to prefer (not forcing the local stream for the team, however that is still the default)

Major fixes:
- Added error handling for a lot of cases that previously would pass silently and result in broken or no video
- Fixed a few bugs responsible for a lot of intermittent download failures eliminating the need for retry functionality
- Fixed a video corruption bug when there were streams with only audio, corrupting the entire video

Removed features:
- Retry functionality is removed in favour of retrying with aria2, after removing alternate urls due to issues they caused - this seems to solve most issues
- Mobile video recoding was removed, I'm not planning to add it back as I don't see much of a use for it but PRs are of course welcome

Features not implemented yet (that I will eventually still want to implement):
- Housekeeping
- Run with multiple teams

Also PRs are open and welcome, Github Actions is set up to run the same test and lint suite as is defined
in the Makefile - so you can use make locally to ensure your changes can be accepted.

## Requirements:

- _You need A offical NHL.tv account to run this script! This is not for free!_
- Either Docker (recommended) - or a Mac/Linux machine with python >3.7, aria2c, openssl, ffmpeg

# How to install nhltv

## Docker (recommended)

Using Docker is the easiest way to run dl-nhltv as you do not have to deal with dependencies yourself.


1. [Install Docker](from https://docs.docker.com/install/)

### Run interactively 

1. `docker run -v /your/media/folder/:/home/nhltv/media -it pontusw/nhltv:latest nhltv --team NSH -u *username* -p *password* -d media`

For information about which parameters are available, check the Usage section below.

If you prefer to build yourself you can run `docker build . -t nhltv:latest` in this folder and replace the image name above like `docker run -v ... -it nhltv:latest nhltv --team ...`

### Run as a background service

1. Copy the docker-compose.example file to docker-compose.yml and edit the command and volume accordingly (see interactive example above) 

2. Run with `docker-compose up -d` and the service will stay in the background and download new games as they become available.


### Install nhltv manually

1. Install aria2 and ffmpeg

2. Clone or download the repository to a folder, navigate to it in your terminal and run `sudo pip install .` or `sudo pip3 install .` depending on your Python installation.

3. Run with `nhltv --team NSH -u *username* -p *password*` and any optional arguments you want (see Usage)


## Usage:

```
usage: nhltv [-h] -t TEAM -u USERNAME -p PASSWORD [-q QUALITY] [-d DOWNLOAD_FOLDER] [-i CHECKINTERVAL]
               [-k RETENTIONDAYS] [-b DAYS_BACK_TO_SEARCH] [--short-debug] [--debug-dumps]

nhltv: Download NHL TV

required arguments:
  -t TEAM, --team TEAM  Team name or ID - example: Nashville Predators, NSH or 18

  -u USERNAME, --username USERNAME
                        Username of your NHLTV account

  -p PASSWORD, --password PASSWORD
                        Password of your NHLTV account

optional arguments:
  -h, --help            show this help message and exit

  -q QUALITY, --quality QUALITY
                        5000, 3500, 1500, 900 (default: 5000)

  -d DOWNLOAD_FOLDER, --download_folder DOWNLOAD_FOLDER
                        Final video destination e.g. $HOME/Desktop/NHL/

  -i CHECKINTERVAL, --checkinterval CHECKINTERVAL
                        Interval in minutes to look for new games (default: 60)

  -b DAYS_BACK_TO_SEARCH, --days-back DAYS_BACK_TO_SEARCH
                        How many days back to search (default: 3)

  -s PREFERRED_STREAM, --prefer-stream PREFERRED_STREAM
                        Abbreviation of your preferred provided for example FS-TN. Can be used multiple times
                        like -s FS-TN -s TSN2 but there is no internal ordering between preferred streams.

debug arguments:
  --short-debug         Shorten video length to just a few minutes for debugging

  --debug, --debug-dumps
                        Enable debugging -- WARNING: will dump session keys to disk
```

### Streams to choose from

When using `--prefer-stream` these are the providers I'm aware of that can be chosen:

```
{'NBCSN', 'MSG+ 2', None, 'WRHU', 'NBCS-CH+', 'FS-W', 'ATT-RM', 'KLAA', 'TSN4', 'WJFK', 'WGN', 'WXYT', 'FSW'
, 'RDS', 'WPEN', 'FSMW', 'SN', 'WCMC', 'RDS2', 'NBCS-CA', 'ATT-PT', 'SN960', 'SNW', 'WPRT', '101ESPN', 'FS-N', '
TSN5', 'FSSW', 'SN360', 'CBC', 'CHED', 'SN1', 'NBCS-PH', 'SN590', 'KTCK', 'SNF', 'KRLV', 'MSG+', 'WBZ', 'TVAS', 
'WBNS', 'FS-D+', 'WQAM', 'FS-TN', 'TSN2', 'NBCS-WA', 'NBCS-PH+', 'TSN1290', 'WEPN', 'FSAZ', 'FOX910', 'FSAZ+', '
KCOP-13', 'NESN', 'TSN1200', 'TVAS2', 'FS-F', 'MSG', 'CHMP', 'WXDX', 'CITY', 'KFOX', 'FS-D', 'WFLA', 'SUN', 'TSN
3', 'SN650', 'MSG-B', 'ALT', 'FS-CR', 'CJFO', 'FSOH', 'KFAN', 'TSN690', 'NHL.com', 'SNP', 'PRIME', 'WGR', 'MSG2'
, 'NBCS-CH', 'KKSE'}
```

The default when not using the prefer provider is to use whichever stream is matches your selected team.
That selection will also be used if your preferred provider is not listed as streaming the current game.


### How dl-nhltv works

When it runs it will check the nhl.tv servers for a new game for your team and if it finds it then it will 
download it. Then after it downloads it will do a loop and start looking for the next game. 

It saves the id of the games you have downloaded in downloaded_games.json in the folder you ran it from so if you aren't 
getting the results you expect then take a look at that file.


#### Files and folders

dl-nhltv downloads temporary files into a subdirectory for each game, relative to the location you run the program.
It will also save some settings in that same folder. 

If you run the program interactively, you will also get a progress bar to indicate download progress. 
This does not work when running as a background service however.
