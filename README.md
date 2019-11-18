# dl-nhltv

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
- Added CI and automated Docker image builds

New features:
- Added obfuscation of the video length, so that the final minutes in the 3rd period stay interesting even if you pause or otherwise glance at the remaining time of the video
- Added progress bars to a number of long running tasks such as downloading and decoding

Major fixes:
- Added error handling for a lot of cases that previously would pass silently and result in broken or no video
- Fixed a few bugs responsible for a lot of intermittent download failures eliminating the need for retry functionality
- Fixed a video corruption bug when there were streams with only audio, corrupting the entire video

Removed features:
- Retry functionality is removed in favour of retrying with aria2, after removing alternate urls due to issues they caused - this seems to solve most issues
- Mobile video recoding was removed, I'm not planning to add it back as I don't see much of a use for it but PRs are of course welcome

Features not implemented yet (but that I plan to still implement):
- Housekeeping
- Run with multiple teams

## Requirements:

- _You need A offical NHL.tv account to run this script! This is not for free!_
- Either Docker (recommended) - or a Mac/Linux machine with python >3.7, aria2c, openssl, ffmpeg

# How to install nhltv

## Docker (recommended)

Using Docker is the easiest way to run dl-nhltv as you do not have to deal with dependencies yourself.


1. [Install Docker](from https://docs.docker.com/install/)

### Run interactively 

1. `docker run -v /your/media/folder/:/home/nhltv/media -it pontusw/nhltv:latest nhltv --team NSH -u *username* -p *password* -d media -o`

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

  -k RETENTIONDAYS, --keep RETENTIONDAYS
                        How many days video and logs are kept (default: forever)

  -b DAYS_BACK_TO_SEARCH, --days-back DAYS_BACK_TO_SEARCH
                        How many days back to search (default: 3)

debug arguments:
  --short-debug         Shorten video length to just a few minutes for debugging

  --debug-dumps         Enable debug dumps -- be careful - it will dump session keys
```

### How dl-nhltv works

When it runs it will check the nhl.tv servers for a new game for your team and if it finds it then it will 
download it. Then after it downloads it will do a loop and start looking for the next game. 

It saves the id of the last game in downloaded_games.json in the folder you ran it from so if you aren't 
getting the results you expect then take a look at the settings.json file and set the game id manually to be lower than the gameid you want to download.

#### Files and folders

dl-nhltv downloads temporary files into a subdirectory for each game, relative to the location you run the program.
It will also save some settings in that same folder. 

If you run the program interactively, you will also get a progress bar to indicate download progress. 
This does not work when running as a background service however.
