#pattrmm-py v0.85 by insertdisc

# import dependencies
from datetime import date
from datetime import timedelta
from datetime import datetime
import platform
import json
import re
import time
import requests
import os.path
import os
from ruamel.yaml import YAML
import xml.etree.ElementTree as ET

# check for needed folders and files

# Main variables file
var_path = 'vars.py'
# Plex Meta Manager config file path
config_path = '../config.yml'
# overlay folder path
overlay_path = '../overlays'
# data folder for created files
data = "data"
# preferences folder
pref = "preferences"
# keys file for ratingKey and tmdb pairs
keys = "data/keys.json"
# cache file for tmdb details
cache = "data/tmdb_cache.json"
# settings file for pattrmm
settings = "preferences/settings.yml"
# returning-soon metadata file for collection
meta = "../returning-soon.yml"
# generated overlay file path
rso = "../overlays/returning-soon-overlay.yml"
# overlay template path
overlay_temp = "preferences/returning-soon-template.yml"
# assign YAML variable
yaml = YAML()
yaml.preserve_quotes = True


# define date ranges
today = str(date.today())
lastAirDate = str(date.today() - timedelta(days=45))
nextAirDate = str(date.today() + timedelta(days=30))

# Info display
print("Checking folder structure")

# Check if PMM config file can be found. If not, inform and exit.
isConfig = os.path.exists(config_path)
if not isConfig:
    print("Plex Meta Manager Config file could not be located.")
    print("Please ensure PATTRMM is in a subfolder of the Plex Meta Manager config directory.")
    exit()
else:
    print("PMM config file found.")

# Check for vars file and create if not present
# If overlay file doesn't exist, create it
isVars = os.path.exists(var_path)
if not isVars:
    print("Creating vars module file..")
    writeVars = open(var_path, "x")
    writeVars.write(
        '''
from ruamel.yaml import YAML
import xml.etree.ElementTree as ET
import requests
import json
import re

config_path = '../config.yml'
settings_path = 'preferences/settings.yml'

def setting(value):
        yaml = YAML()
        settings = settings_path
        with open(settings) as sf:
            pref = yaml.load(sf)
            if value == 'library':
                entry = pref['library_name']
            if value == 'rsback_color':
                entry = pref['returning_soon_bgcolor']
            if value == 'rsfont_color':
                entry = pref['returning_soon_fontcolor']
            if value == 'prefix':
                entry = pref['overlay_prefix']
            if value == 'zeros':
                entry = pref['leading_zeros']
            if value == 'ovNew':
                 entry = pref['extra_overlays']['new']['use']
            if value == 'ovNewColor':
                 entry = pref['extra_overlays']['new']['bgcolor']
            if value == 'ovNewFontColor':
                 entry = pref['extra_overlays']['new']['font_color']
            if value == 'ovNewText':
                 entry = pref['extra_overlays']['new']['text']
            if value == 'ovReturning':
                 entry = pref['extra_overlays']['returning']['use']
            if value == 'ovReturningColor':
                 entry = pref['extra_overlays']['returning']['bgcolor']
            if value == 'ovReturningFontColor':
                 entry = pref['extra_overlays']['returning']['font_color']
            if value == 'ovReturningText':
                 entry = pref['extra_overlays']['returning']['text']
            if value == 'ovAiring':
                 entry = pref['extra_overlays']['airing']['use']
            if value == 'ovAiringColor':
                 entry = pref['extra_overlays']['airing']['bgcolor']
            if value == 'ovAiringFontColor':
                 entry = pref['extra_overlays']['airing']['font_color']
            if value == 'ovAiringText':
                 entry = pref['extra_overlays']['airing']['text']
            if value == 'ovEnded':
                 entry = pref['extra_overlays']['ended']['use']
            if value == 'ovEndedColor':
                 entry = pref['extra_overlays']['ended']['bgcolor']
            if value == 'ovEndedFontColor':
                 entry = pref['extra_overlays']['ended']['font_color']
            if value == 'ovEndedText':
                 entry = pref['extra_overlays']['ended']['text']
            if value == 'ovCanceled':
                 entry = pref['extra_overlays']['canceled']['use']
            if value == 'ovCanceledColor':
                 entry = pref['extra_overlays']['canceled']['bgcolor']
            if value == 'ovCanceledFontColor':
                 entry = pref['extra_overlays']['canceled']['font_color']
            if value == 'ovCanceledText':
                 entry = pref['extra_overlays']['canceled']['text']   
        return entry

def traktApi(type):
        yaml = YAML()
        config = config_path
        with open(config) as fp:
            trakt = yaml.load(fp)
            if type == 'token':
                key = trakt['trakt']['authorization']['access_token']
            if type == 'client':
                key = trakt['trakt']['client_id']
            if type == 'secret':
                key = trakt['trakt']['client_secret']
            if type == 'me':
                api = traktApi('client')
                access = traktApi('token')
                headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access + '',
                'trakt-api-version': '2',
                'trakt-api-key': '' + api + ''
                }
                key = json.loads(json.dumps(requests.get('https://api.trakt.tv/users/me', headers=headers).json()))['username']
        return key

def tmdbApi(var):
        yaml = YAML()
        config = config_path
        with open(config) as fp:
            tmdb = yaml.load(fp)
            if var == 'token':
                key = tmdb['tmdb']['apikey']
        return key

def plexApi(vix):
        yaml = YAML()
        config = config_path
        with open(config) as fp:
            plex = yaml.load(fp)
            if vix == 'url':
                key = plex['plex']['url']
            if vix == 'token':
                 key = plex['plex']['token']
        return key


def plexGet(identifier):
        URL =  plexApi('url') + '/library/sections/?X-Plex-Token=' + plexApi('token')
        libraries = re.sub("0//", "0/", URL)
        libSearch = ET.fromstring(requests.get(libraries).text)
        for directory in libSearch.findall('Directory'):
            if directory.get('title') == identifier:
                key = directory.get('key')
                title = directory.get('title')
        return key

'''
    )
    writeVars.close()
else:
    print("Vars module found.")

import vars
# If data folder doesn't exist, create it
isData = os.path.exists(data)
if not isData:
    print("Creating data folder...")
    os.makedirs(data)
else:
    print("data folder present...")

# If data folder doesn't exist, create it
isOvPath = os.path.exists(overlay_path)
if not isOvPath:
    print("Plex Meta Manager Overlay folder could not be located.")
    print("Please ensure PATTRMM is in a subfolder of the PMM config directory.")
    exit()

# If preferences folder doesn't exist, create it
isPref = os.path.exists(pref)
if not isPref:
    print("Creating preferences folder...")
    os.makedirs(pref)
else:
    print("Preference folder present...")



# If settings file doesn't exist, create it
isSettings = os.path.exists(settings)
if not isSettings:
    print("Creating settings file..")
    writeSettings = open(settings, "x")
    writeSettings.write(
        '''
library_name: "TV Shows"             # Plex Library to read from.
overlay_prefix: "RETURNING"     # Text to display before the dates.
leading_zeros: True                  # 01/14 vs 1/14 for dates. True or False
returning_soon_bgcolor: "#81007F"
returning_soon_fontcolor: "#FFFFFF"
extra_overlays:
  new:
    use: True
    bgcolor: "#008001"
    font_color: "#FFFFFF"
    text: "N E W  S E R I E S"
  airing:
    use: True
    bgcolor: "#343399"
    font_color: "#FFFFFF"
    text: "A I R I N G"
  returning:
    use: True
    bgcolor: "#81007F"
    font_color: "#FFFFFF"
    text: "R E T U R N I N G"
  ended:
    use: True
    bgcolor: "#000000"
    font_color: "#FFFFFF"
    text: "E N D E D"
  canceled:
    use: True
    bgcolor: "#CF142B"
    font_color: "#FFFFFF"
    text: "C A N C E L E D"
'''
    )
    writeSettings.close()
    print("Settings file created. Please configure preferences/settings.yml and rerun PATTRMM.")
    exit()
else:
    print("Settings file present.")


print("Checking files...")

# If keys file doesn't exist, create it
isKeys = os.path.exists(keys)
if not isKeys:
    print("Creating keys file..")
    writeKeys = open(keys, "x")
    writeKeys.close()
    firstRun = True
else:
    print("Keys file found.")
    print("Checking data...")
    if os.stat(keys).st_size == 0:
        firstRun = True
        print("Keys file is empty. Initiating first run.")
    if os.stat(keys).st_size != 0:
        print("Keys file found.")
        firstRun = False

# If cache file doesn't exist, create it
isCache = os.path.exists(cache)
if not isCache:
    print("Creating cache file..")
    writeCache = open(cache, "x")
    writeCache.write('tmdbDataCache')
    writeCache.close()
else:
    print("Cache file present.")




# If returning-soon metadata file doesn't exist, create it
isMeta = os.path.exists(meta)
if not isMeta:
    print("Creating metadata collection file..")
    writeMeta = open(meta, "x")
    me = vars.traktApi('me')
    writeMeta.write(
        f'''
collections:
  Returning Soon:
    trakt_list: https://trakt.tv/users/{me}/lists/returning-soon
    collection_order: custom
    visible_home: true
    visible_shared: true
    sync_mode: sync
'''
    )
    writeMeta.close()
else:
    print("Metadata file present.")

# If overlay template doesn't exist, create it
isTemplate = os.path.exists(overlay_temp)
if not isTemplate:
    print("Generating Template file..")
    writeTemp = open(overlay_temp, "x")
    writeTemp.write(
        '''
templates:
  # TEXT CENTER
  TV_Top_TextCenter:
    sync_mode: sync
    builder_level: show
    overlay:
      name: text(<<text>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 0
      vertical_align: top
      font: config/fonts/Juventus-Fans-Bold.ttf
      font_size: 70
      font_color: <<color>>
      group: TV_Top_TextCenter
      weight: <<weight>>
      back_color: <<back_color>>
      back_width: 1920
      back_height: 90
'''
)
    writeTemp.close()
else:
    print("Template file found.")

# If overlay file doesn't exist, create it
isOverlay = os.path.exists(rso)
if not isOverlay:
    print("Creating empty Overlay file..")
    writeRSO = open(rso, "x")
    writeRSO.write('')
    writeRSO.close()
else:
    print("Overlay file present.")




# declare date formats
date_format = '%Y-%m-%d'

# define classes and definitions
def sortedList(list, field):
    return sorted(list, key=lambda k: k[field], reverse=False)

def prettyJson(value):
    return json.dumps(value, indent=4, sort_keys=False)

def dict_ToJson(value):
    return json.dumps([ob.__dict__ for ob in value], indent=4, sort_keys=False)

# function to count a list #
def get_count(list):
    count = 0
    for element in list:
        count += 1
    return str(count)

# strip date to just year #
def get_year(date):
    return datetime.strptime(date, date_format).year

# strip (words) and url format plex title #
class Plex_Item:
    def __init__(self, title, year, ratingKey):
        self.title = re.sub("\s\(.*?\)","", title)
        self.year = datetime.strptime(year, date_format).year
        self.ratingKey = ratingKey

class tmdb_search:
    def __init__(self, title, ratingKey, tmdb_id, status):
        self.title = title
        self.ratingKey = ratingKey
        self.tmdb_id = tmdb_id
        self.status = status

class tmdbDetails:
    def __init__(self, id, title, firstAir, lastAir, nextAir, status, pop):
        self.id = id
        self.title = title
        self.firstAir = firstAir
        self.lastAir = lastAir
        self.nextAir = nextAir
        self.status = status
        self.pop = pop

# declare lists
Search = []
key_pairs = []
status_key_pairs = []
tmdb_details = []

# create access variables 
library = vars.setting('library')
plexCall = vars.plexApi('url') + '/library/sections/' + vars.plexGet(library) + '/all'
plex_url = re.sub("//lib", "/lib", plexCall)
plex_headers = {
    "accept": "application/json"
}
plex_token = {'X-Plex-Token': '' + vars.plexApi('token') + ''}


# gather list of entries in plex
print("Gathering Plex entries...")
time.sleep(.01)

series = json.loads(prettyJson(requests.get(plex_url, headers=plex_headers, params=plex_token).json()))
titlesInPlex = get_count(series['MediaContainer']['Metadata'])
count = 1
for this in series['MediaContainer']['Metadata']:
    print("\rAdding to list " + "(" + str(count) + "/" + get_count(series['MediaContainer']['Metadata']) + ")", end="")
    try:
        Search.append(Plex_Item(this['title'],this['originallyAvailableAt'], this['ratingKey']))
    except KeyError:
        print(this['title'] + " does not have an originally available at - date. Skipping")
        continue 
    count += 1
    time.sleep(.004)


# search for tmdb id of each entry, will update to use stored keys to reduce unnecessary searches
refreshSearch = Search
Search = json.loads(dict_ToJson(Search))

if firstRun == False:
    keyFile = open(keys, "r")
    keyData = json.load(keyFile)
    keyFile.close()

    cleanedKeysList = []
    compareSearch = dict_ToJson(refreshSearch)

    # Find if any entries were removed from Plex and remove from Key data
    for existingKey in keyData[:]:
        if (existingKey['ratingKey'] not in compareSearch):
            keyData.remove(existingKey)
            print("")
            print(existingKey['title'] + " was no longer found in Plex. Removing from Keys.")
            time.sleep(.6)
    for cleanedKey in keyData:
        cleanedKeysList.append(tmdb_search(cleanedKey['title'], cleanedKey['ratingKey'], cleanedKey['tmdb_id'], cleanedKey['status']))

    updatedKeys = dict_ToJson(cleanedKeysList)

    rfSearch = 0
    newSearch = Search
    print("")
    for eachItem in newSearch[:]:
        if (eachItem['ratingKey'] in updatedKeys):
            newSearch.remove(eachItem)
            #print("Key data exists for " + eachItem['title'] + ". Removed from search list")
            rfSearch += 1
            print("\rFound existing data for " + str(rfSearch) + " titles. Removing from search list.", end="")
            time.sleep(.004)       
    time.sleep(2.5)
    print("")
    for remainingItem in newSearch:
        print("No key entry found for " + remainingItem['title'] + ". Searching for details...")
    if len(newSearch) < 1:
        message = False
        print("Nothing new to search for. Proceeding...")
    if len(newSearch) > 0:
        message = True
        Search = newSearch

    # Hold list to append searches
    status_key_pairs = cleanedKeysList








count = 1
for query in Search:
    # display search progress
    print("\rSearching... " + "(" + str(count) + "/" + get_count(Search) + ")", end="")
    
    # define search parameters
    tmdb_url = "https://api.themoviedb.org/3/search/tv"
    tmdb_params = {"query": query['title'], "first_air_date_year": query['year'], "api_key": vars.tmdbApi('token')}
    tmdb_headers = {
        'accept': 'application/json'
    }

    # store search result
    tmdb_response = requests.get(tmdb_url, headers=tmdb_headers, params=tmdb_params)
    tmdb_response_json = json.loads(prettyJson(tmdb_response.json()))

    # check if a match was found given parameters
    if tmdb_response_json['total_results'] < 1:
        # if no match, increase search year to try and allow for variances and search again
        query['year'] += 1
        tmdb_params = {"query": query['title'], "first_air_date_year": query['year'], "api_key": vars.tmdbApi('token')}
        tmdb_response = requests.get(tmdb_url, headers=tmdb_headers, params=tmdb_params)
        tmdb_response_json = json.loads(prettyJson(tmdb_response.json()))
        #check secondary search results
        if tmdb_response_json['total_results'] < 1:
            # if nothing was found, try again using an earlier year
            query['year'] -= 2
            tmdb_params = {"query": query['title'], "first_air_date_year": query['year'], "api_key": vars.tmdbApi('token')}
            tmdb_response = requests.get(tmdb_url, headers=tmdb_headers, params=tmdb_params)
            tmdb_response_json = json.loads(prettyJson(tmdb_response.json()))
            # if nothing was found on this attempt, skip entry
            if tmdb_response_json['total_results'] < 1:
                print(" Could not find an ID for " + query['title'] + " ...skipping.")
                time.sleep(.6)
                # increment progress count to include skipped entries
                count += 1
                # continue after the failed search attempt
                continue

    # if a match was found, try and get the correct entry based of the year used
    if tmdb_response_json['total_results'] >=1:
        for item in tmdb_response_json['results']:
            # if the year matches, add it to the key pairs list
            if str(query['year']) in str(get_year(item['first_air_date'])):
                key_pairs.append(tmdb_search(query['title'], query['ratingKey'], str(item['id']), "null"))
                # info for found match
                print(" Found ID ==> " + str(item['id']) + " for " + '"' + query['title'] + '"')
                # end adding to the list after the first match is found, else duplicate entries occur
                break
    # increment progress after a successful match 
    count += 1
 










for d in json.loads(dict_ToJson(key_pairs)):

    tmdbUrl = "https://api.themoviedb.org/3/tv/" + d['tmdb_id']
    tmdbHeaders = {
    "accept": "application/json"
    }
    tmdbParams = {
        "language": "en-US", "api_key": vars.tmdbApi('token')
    }
    
    tmdb = json.loads(prettyJson(requests.get(tmdbUrl, headers=tmdbHeaders, params=tmdbParams).json()))

    print("Found details for " + tmdb['name'] + " ( " + str(tmdb['id']) + " )")

    if tmdb['last_air_date'] != None and tmdb['last_air_date'] != "" :
        lastAir = tmdb['last_air_date']
    if tmdb['last_air_date'] == None or tmdb['last_air_date'] == "":
        lastAir = "null"

    if tmdb['next_episode_to_air'] != None and tmdb['next_episode_to_air']['air_date'] != None:
        nextAir = tmdb['next_episode_to_air']['air_date']
    if tmdb['next_episode_to_air'] == None or tmdb['next_episode_to_air'] == "":
        nextAir = "null"

    if tmdb['first_air_date'] != None and tmdb['first_air_date'] != "":
        firstAir = tmdb['first_air_date']
    if tmdb['first_air_date'] == None or tmdb['first_air_date'] == "":
        firstAir = "null"

    status_key_pairs.append(
        tmdb_search(
            d['title'],
            d['ratingKey'],
            d['tmdb_id'],
            tmdb['status']
            )
            )




    if firstRun == True:
        if tmdb['status'] == "Returning Series":
            tmdb_details.append(
                tmdbDetails(
                    tmdb['id'],
                    tmdb['name'],
                    firstAir,
                    lastAir,
                    nextAir,
                    tmdb['status'],
                    tmdb['popularity']
                    )
                    )
            

key_string = dict_ToJson(status_key_pairs)
writeKeys = open(keys, "w")
writeKeys.write(key_string)
writeKeys.close()
if firstRun == True:
    print("Keys updated...")
if firstRun == False:
    if message == True:
        print("Keys updated...")
        print("Updating data for Returning Series.")

if firstRun == False:
    updateMe = []
    keyFile = open(keys, "r")
    keyData = json.load(keyFile)
    
    for u in keyData:

        if u['status'] != "Returning Series":
            updateMe.append(tmdb_search(u['title'], u['ratingKey'], u['tmdb_id'], u['status']))
        if u['status'] == "Returning Series":
            tmdbUrl = "https://api.themoviedb.org/3/tv/" + u['tmdb_id']
            tmdbHeaders = {
            "accept": "application/json"
            }
            tmdbParams = {
            "language": "en-US", "api_key": vars.tmdbApi('token')
            }
    
            tmdb = json.loads(prettyJson(requests.get(tmdbUrl, headers=tmdbHeaders, params=tmdbParams).json()))

            print("Refreshing data for " + tmdb['name'] + " ( " + str(tmdb['id']) + " )")

            if tmdb['last_air_date'] != None and tmdb['last_air_date'] != "" :
                lastAir = tmdb['last_air_date']
            if tmdb['last_air_date'] == None or tmdb['last_air_date'] == "":
                lastAir = "null"

            if tmdb['next_episode_to_air'] != None and tmdb['next_episode_to_air']['air_date'] != None:
                nextAir = tmdb['next_episode_to_air']['air_date']
            if tmdb['next_episode_to_air'] == None or tmdb['next_episode_to_air'] == "":
                nextAir = "null"

            if tmdb['first_air_date'] != None and tmdb['first_air_date'] != "":
                firstAir = tmdb['first_air_date']
            if tmdb['first_air_date'] == None or tmdb['first_air_date'] == "":
                firstAir = "null"
            updateMe.append(tmdb_search(u['title'], u['ratingKey'], u['tmdb_id'], tmdb['status']))
            if tmdb['status'] == "Returning Series":
                tmdb_details.append(
                        tmdbDetails(
                            tmdb['id'],
                            tmdb['name'],
                            firstAir,
                            lastAir,
                            nextAir,
                            tmdb['status'],
                            tmdb['popularity']
                            )
                            )
    updated_key_string = dict_ToJson(updateMe)
    updatedwriteKeys = open(keys, "w")
    updatedwriteKeys.write(updated_key_string)
    updatedwriteKeys.close()


listResults = prettyJson(sortedList(json.loads(dict_ToJson(tmdb_details)), 'nextAir'))



## write tmdb details to file ##
writeTmdb = open(cache, "w")
writeTmdb.write(listResults)
writeTmdb.close()
print("TMDB data updated...")


# write Template to Overlay file
print("Writing user Overlay Template to Returning Soon overlay file.")
with open(overlay_temp) as ot:
    ovrTemp = yaml.load(ot)
    rsoWrite = open(rso, "w")
    yaml.dump(ovrTemp, rsoWrite)
    print("Template applied.")


# Generate Overlay body
# define date ranges
dayCounter = 1
today = date.today()
lastAirDate = date.today() - timedelta(days=45)
last_episode_aired = lastAirDate.strftime("%m/%d/%Y")
nextAirDate = date.today() + timedelta(days=31)
thisDayTemp = date.today() + timedelta(days=int(dayCounter))
thisDay = thisDayTemp.strftime("%m/%d/%Y")
thisDayDisplay = thisDayTemp.strftime("%m/%d/%Y")
if vars.setting('zeros') == True or vars.setting('zeros') != False:
    thisDayDisplayText = thisDayTemp.strftime("%m/%d")
if vars.setting('zeros') == False:
    if platform.system() == "Windows":
        thisDayDisplayText = thisDayTemp.strftime("%#m/%d")
    if platform.system() == "Linux" or platform.system() == "Darwin":
        thisDayDisplayText = thisDayTemp.strftime("%-m/%d")
prefix = vars.setting('prefix')

print("Generating overlay body.")

overlay_base = '''

overlays:
'''




if vars.setting('ovNew') == True:
    newText = vars.setting('ovNewText')
    newFontColor = vars.setting('ovNewFontColor')
    newColor = vars.setting('ovNewColor')
    ovNew = f'''
  # New
  TV_Top_TextCenter_New:
    template:
      - name: TV_Top_TextCenter
        weight: 60
        text: "{newText}"
        color: "{newFontColor}"
        back_color: "{newColor}"
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      first_episode_aired: 45
      '''
    overlay_base = overlay_base + ovNew



if vars.setting('ovAiring') == True:
    airTodayTemp = date.today()
    airToday = airTodayTemp.strftime("%m/%d/%Y")
    considered_airingTemp = date.today() - timedelta(days=15)
    considered_airing = considered_airingTemp.strftime("%m/%d/%Y")
    airingText = vars.setting('ovAiringText')
    airingFontColor = vars.setting('ovAiringFontColor')
    airingColor = vars.setting('ovAiringColor')
    ovAiring = f'''
  # Airing
  TV_Top_TextCenter_Airing:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "{airingText}"
        color: "{airingFontColor}"
        back_color: "{airingColor}"
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      last_episode_aired.after: {considered_airing}

  # Airing Today
  TV_Top_TextCenter_Airing_Today:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "{airingText}"
        color: "{airingFontColor}"
        back_color: "{airingColor}"
    tmdb_discover:
      air_date.gte: {airToday}
      air_date.lte: {airToday}
      with_status: 0
      limit: 500
'''
    overlay_base = overlay_base + ovAiring


if vars.setting('ovEnded') == True:
    endedText = vars.setting('ovEndedText')
    endedFontColor = vars.setting('ovEndedFontColor')
    endedColor = vars.setting('ovEndedColor')
    ovEnded = f'''
  # Ended
  TV_Top_TextCenter_Ended:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{endedText}"
        color: "{endedFontColor}"
        back_color: "{endedColor}"
    plex_all: true
    filters:
      tmdb_status:
        - ended
'''
    overlay_base = overlay_base + ovEnded


if vars.setting('ovCanceled') == True:
    canceledText = vars.setting('ovCanceledText')
    canceledFontColor = vars.setting('ovCanceledFontColor')
    canceledColor = vars.setting('ovCanceledColor')
    ovCanceled = f'''
  # Canceled
  TV_Top_TextCenter_Canceled:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{canceledText}"
        color: "{canceledFontColor}"
        back_color: "{canceledColor}"
    plex_all: true
    filters:
      tmdb_status:
        - canceled
'''
    overlay_base = overlay_base + ovCanceled


if vars.setting('ovReturning') == True:
    returningText = vars.setting('ovReturningText')
    returningFontColor = vars.setting('ovReturningFontColor')
    returningColor = vars.setting('ovReturningColor')
    ovReturning = f'''
  # Returning
  TV_Top_TextCenter_Returning:
    template:
      - name: TV_Top_TextCenter
        weight: 30
        text: "{returningText}"
        color: "{returningFontColor}"
        back_color: "{returningColor}"
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
'''
    overlay_base = overlay_base + ovReturning












while thisDayTemp < nextAirDate:
    rsback_color = vars.setting('rsback_color')
    rsfont_color = vars.setting('rsfont_color')
    overlay_gen = f'''
# RETURNING {thisDayDisplay}
  TV_Top_TextCenter_Returning_{thisDayDisplay}:
    template:
      - name: TV_Top_TextCenter
        weight: 35
        text: "{prefix} {thisDayDisplayText}"
        color: "{rsfont_color}"
        back_color: "{rsback_color}"
    tmdb_discover:
      air_date.gte: {thisDay}
      air_date.lte: {thisDay}
      with_status: 0
      limit: 500
    filters:
      last_episode_aired.before: {last_episode_aired}
'''
    dayCounter += 1
    thisDayTemp = date.today() + timedelta(days=int(dayCounter))
    thisDay = thisDayTemp.strftime("%m/%d/%Y")
    thisDayDisplay = thisDayTemp.strftime("%m/%d/%Y")
    if vars.setting('zeros') == True or vars.setting('zeros') != False:
        thisDayDisplayText = thisDayTemp.strftime("%m/%d")
    if vars.setting('zeros') == False:
        if platform.system() == "Windows":
            thisDayDisplayText = thisDayTemp.strftime("%#m/%d")
        if platform.system() == "Linux" or platform.system() == "Darwin":
            thisDayDisplayText = thisDayTemp.strftime("%-m/%d")
    overlay_base = overlay_base + overlay_gen
  
print("Overlay body generated. Writing to file.")

# Write the rest of the overlay
writeBody = open(rso, "a")
yaml.dump(yaml.load(overlay_base), writeBody)
writeBody.close()
print("Overlay body appened to returning-soon-overlay.")

# use keys file to gather show details
print("Reading cache file...")
cacheFile = open(cache, "r")
cacheData = json.load(cacheFile)
cacheFile.close()

# this is for the trakt list
print("Filtering data...")
returningSoon = filter(
    lambda x: (
        x['status'] == "Returning Series" and 
        x['nextAir'] != "null" and 
        x['nextAir'] < str(nextAirDate) and 
        x['nextAir'] > str(today) and 
        x['lastAir'] < str(lastAirDate)),
        cacheData)
print("Sorting...")
returningSorted = sortedList(returningSoon, 'nextAir')

traktaccess = vars.traktApi('token')
traktapi = vars.traktApi('client')
traktHeaders = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + traktaccess + '',
                'trakt-api-version': '2',
                'trakt-api-key': '' + traktapi + ''
                }

traktListUrl = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists"
traktListUrlPost = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon"
traktListUrlPostShow = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon/items"
traktListData = """
{
    "name": "Returning Soon",
    "description": "Season premiers within the next 30 days.",
    "privacy": "private",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}
"""

print("Clearing trakt list...")
traktDeleteList = requests.delete(traktListUrlPost, headers=traktHeaders)
time.sleep(1.25)
traktMakeList = requests.post(traktListUrl, headers=traktHeaders, data=traktListData)
time.sleep(1.25)

for item in returningSorted:
    print("Adding " + item['title'] + " | TMDB ID: " + str(item['id']) + ", to Returning Soon.")

    traktListShow = f'''
{{
"shows": [
    {{
      "ids": {{
        "tmdb": "{str(item['id'])}"
               }}
    }}
  ]
}}
'''
    postShow = requests.post(traktListUrlPostShow, headers=traktHeaders, data=traktListShow)
    time.sleep(1.25)

print("Added " + str(get_count(returningSorted)) + " entries to Trakt.")
print("All operations complete.")
