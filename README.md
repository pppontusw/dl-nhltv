# dl-nhltv

Download NHL.tv Streams with up to 720p60 and remove the commercial breaks

## Requirements:

- _You need A offical NHL.tv account to run this script! This is not for free!_
- Either Docker (recommended) - or a Mac/Linux machine with python 3, aria2c, openssl, ffmpeg

# How to install nhltv

## Docker (recommended)

Using Docker is the easiest way to run dl-nhltv as you do not have to deal with dependencies yourself.


1. Install Docker (from https://docs.docker.com/install/)

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

### How dl-nhltv works

When it runs it will check the nhl.tv servers for a new game for your team and if it finds it then it will download it. Then after it downloads it will do a loop and start looking for the next game. It saves the id of the last game in settings.json in the folder you ran it from so if you aren't getting the results you expect then take a look at the settings.json file and set the game id manually to be lower than the gameid you want to download. It also saves the username and password in the settings.json file when you pass it in via -u -p. Otherwise it will ask when the cookies run old.

#### Files and folders

dl-nhltv downloads temporary files into a subdirectory for each game, relative to the location you run the program.
It will also save some settings in that same folder. 
If you run the program interactively, you will also get a progress bar to indicate download progress. This does not work when running as a background service however.
