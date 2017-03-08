# coding=utf-8
import json
import cookielib
from datetime import datetime

#Settings
USERNAME = ""
PASSWORD = ""
QUALITY = "5000"
#QUALITY = "192" # Just for testing
DOWNLOAD_FOLDER = "./" # Folder for downloaded files i.e.: /home/username/NHL_TV/
RETRY_ERRORED_DOWNLOADS=False # usually works fine if you want it perfect set to True

TEAMID = "24" # Washington = 15 # Philly = 4 # Rangers = 3 # Pens = 5 # Detroit = 17 # STL =  19# ANH = 24
#TEAMID = "12" # Just for testing
MASTER_FILE_TYPE = 'master_tablet60.m3u8'
SETTINGS_FILE = 'settings.json'

#User Agents
UA_GCL = 'NHL1415/5.0925 CFNetwork/711.4.6 Darwin/14.0.0'
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 iphone nhl 5.0925'
UA_IPAD = 'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 ipad nhl 5.0925'
UA_NHL = 'NHL/2542 CFNetwork/758.2.8 Darwin/15.0.0'
UA_PC = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
UA_PS4 = 'PS4Application libhttp/1.000 (PS4) libhttp/3.15 (PlayStation 4)'

def tprint(outString):
    outString = datetime.now().strftime('%m/%d/%y %H:%M:%S - ') + outString
    print(outString) 

def find(source,start_str,end_str):    
    start = source.find(start_str)
    end = source.find(end_str,start+len(start_str))

    if start != -1:        
        return source[start+len(start_str):end]
    return ''

def getSetting(sid):
    # Load the settings file
    with open(SETTINGS_FILE, "r") as settingsFile:
        j = json.load(settingsFile)
    settingsFile.close()
    if sid in j:
        return(j[sid])
    return('')

def setSetting(sid, value):
    # Write to settings file
    with open(SETTINGS_FILE, "r") as settingsFile:
        j = json.load(settingsFile)
    
    settingsFile.close()
    j[sid] = value
    
    with open(SETTINGS_FILE, "w") as settingsFile:
        json.dump(j, settingsFile, indent=4)
    
    settingsFile.close()

def saveCookiesAsText():
    cjT = cookielib.MozillaCookieJar('cookies.txt')

    cj = cookielib.LWPCookieJar('cookies.lwp')
    cj.load('cookies.lwp',ignore_discard=False)
    for cookie in cj: 
        cjT.set_cookie(cookie)
    cjT.save(ignore_discard=False)
