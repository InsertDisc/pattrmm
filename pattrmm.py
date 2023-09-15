#pattrmm-py by insertdisc

# import dependencies
import time
start_time = time.time()
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
# assign YAML variable
yaml = YAML()
yaml.preserve_quotes = True

import xml.etree.ElementTree as ET
import logging
import sys



print("Verifying files.")
# data folder for created files
data = "data"
# If data folder doesn't exist, create it
isData = os.path.exists(data)
if not isData:
    print("Creating data folder...")
    os.makedirs(data)
else:
    print("Data folder present...")


# logs folder
log_path = "data/logs"
# If Logs folder doesn't exist, create it
isLogs = os.path.exists(log_path)
if not isLogs:
    print("Creating logs folder...")
    os.makedirs(log_path)
else:
    print("Logs folder present...")

log_file = "data/logs/pattrmm.log"
isLogFile = os.path.exists(log_file)
if not isLogFile:
    print("Creating log file..")
    writeLogs = open(log_file, "x")
    writeLogs.close()

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")


# preferences folder
pref = "preferences"
# If preferences folder doesn't exist, create it
isPref = os.path.exists(pref)
if not isPref:
    print("Creating preferences folder...")
    os.makedirs(pref)
else:
    print("Preference folder present...")


# settings file for pattrmm
settings = "preferences/settings.yml"
# If settings file doesn't exist, create it
if os.path.isfile(settings) == False:
    print("Creating settings file..")
    writeSettings = open(settings, "x")
    writeSettings.write(
        '''
library_name:
  - TV Shows                         # Plex Libraries to read from. Can enter multiple libraries.
days_ahead: 30
overlay_prefix: "RETURNING"          # Text to display before the dates.
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
''')
    writeSettings.close()
    print("Settings file created. Please configure preferences/settings.yml and rerun PATTRMM.")
    exit()
if os.path.isfile(settings) == True:
    print("Settings file present.")


# Main variables file
var_path = 'vars.py'
# Check for vars file and create if not present
isVars = os.path.exists(var_path)
if not isVars:
    print("Creating vars module file..")
    writeVars = open(var_path, "x")
    writeVars.write(
        '''
from ruamel.yaml import YAML
yaml = YAML()
import xml.etree.ElementTree as ET
import requests
import json
import re
import os
library = ""

is_docker = os.environ.get('PATTRMM_DOCKER', "False")

if is_docker == "True":
    configPathPrefix = "./config/"
    

if is_docker == "False":
    configPathPrefix = "../"

import logging
log_file = "data/logs/pattrmm.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")


config_path = configPathPrefix + 'config.yml'
settings_path = 'preferences/settings.yml'

class Plex:
    def __init__(self, plex_url, plex_token, tmdb_api_key):
        self.plex_url = plex_url
        self.plex_token = plex_token
        self.tmdb_api_key = tmdb_api_key
        self.context = None

    @property
    def show(self):
        self.context = 'show'
        return self  # Return self to allow method chaining

    def id(self, show_name):
        if self.context == 'show':
            try:
                # Replace with the correct section ID and library URL
                section_id = plexGet(library)  # Replace with the correct section ID
                library_url = f"{self.plex_url}/library/sections/{section_id}/all"
                library_url = re.sub("0//", "0/", library_url)
                headers = {"X-Plex-Token": self.plex_token}
                response = requests.get(library_url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    for item in data['MediaContainer']['Metadata']:
                        if item['type'] == 'show' and item['title'] == show_name:
                            return f"ID for show '{show_name}': {item['ratingKey']}"
                    return f"Show '{show_name}' not found"
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error: {str(e)}"

    def tmdb_id(self, rating_key):
        # Attempt to retrieve TMDB ID from Plex
        plex_tmdb_id = self.get_tmdb_id_from_plex(rating_key)
        
        if plex_tmdb_id is not None:
            return plex_tmdb_id
        
        # If not found in Plex, search TMDB
        if plex_tmdb_id == None:
            show_name = self.get_show_name(rating_key)
            year = self.year(rating_key)
            if year != None:
                print("")
                print("No TMDB ID found locally: Searching for " + show_name + " with year " + str(year))
                logging.info("No TMDB ID found locally: Searching for " + show_name + " with year " + str(year))
                search =  self.search_tmdb_id(show_name, year)
                if search == None:
                    year = int(year)
                    year += 1
                    print("No results, searching again with year " + str(year))
                    logging.info("No results, searching again with year " + str(year))
                    search = self.search_tmdb_id(show_name, str(year))
                    if search == None:              
                         year -= 2
                         print("No results, searching again with year " + str(year))
                         logging.info("No results, searching again with year " + str(year))
                         search = self.search_tmdb_id(show_name, str(year))
                         if search == None:
                              print(show_name + " could not be matched.")
                              logging.info(show_name + " could not be matched.")
                              search = "null"
                              
                return search
                
            if year == None:
                print("")
                print("No originally availabe year for " + show_name + ", cannot search for title reliably.")
                logging.warning("No originally availabe year for " + show_name + ", cannot search for title reliably.")
                search = "null"
                return search
            


    def get_tmdb_id_from_plex(self, rating_key):
        try:
            show_details_url = f"{self.plex_url}/library/metadata/{rating_key}"
            show_details_url = re.sub("0//", "0/", show_details_url)
            headers = {"X-Plex-Token": self.plex_token}
            response = requests.get(show_details_url, headers=headers)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                guid_elements = root.findall('.//Guid')
                for guid_element in guid_elements:
                    if guid_element.get('id', '').startswith('tmdb://'):
                        tmdb_id = guid_element.get('id')[7:]
                        #tmdb_id = guid.split('tmdb://')[1]
                        return tmdb_id
                return None
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"


    def get_show_name(self, rating_key):
        try:
            show_details_url = f"{self.plex_url}/library/metadata/{rating_key}"
            show_details_url = re.sub("0//", "0/", show_details_url)
            headers = {"X-Plex-Token": self.plex_token,
                       "accept": "application/json"
            }
            
            # Make a request to get show details
            response = requests.get(show_details_url, headers=headers)
            
            if response.status_code == 200:
               data = json.loads(json.dumps(response.json()))
               values = data['MediaContainer']['Metadata']
               for result in values:
                   title = result['title']
                   title = re.sub("\s\(.*?\)","", title)
               return title
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"

    def retry_search_with_adjusted_years(self, title, year):
        for i in range(2):
            if i == 0:
                year += 1
            elif i == 1:
                year -= 2

        tmdb_search_result = self.search_tmdb_id(title, year)
        if tmdb_search_result is not None:
            return tmdb_search_result

        return "null"
        

    def year(self, rating_key):
        try:
            # Get the originally available year from Plex
            show_details_url = f"{self.plex_url}/library/metadata/{rating_key}"
            show_details_url = re.sub("0//", "0/", show_details_url)
            headers = {"X-Plex-Token": self.plex_token,
                       "accept": "application/json"}
            
            response = requests.get(show_details_url, headers=headers)
            
            if response.status_code == 200:
                data = json.loads(json.dumps(response.json()))
                for result in data['MediaContainer']['Metadata']:
                    try:
                        year = result['originallyAvailableAt'][:4]
                    except KeyError:
                        year = None
                return year
            else:
                return None
        except Exception as e:
            return None

    def search_tmdb_id(self, title, year):
        try:
            # Query TMDB to search for a show based on title and year
            tmdb_api_url = "https://api.themoviedb.org/3/search/tv"
            tmdb_api_key = self.tmdb_api_key
            tmdb_headers = {
            'accept': 'application/json'
            }
            tmdb_params = {
                "api_key": tmdb_api_key,
                "query": title,
                "first_air_date_year": year
            }
            tmdb_response = requests.get(tmdb_api_url, headers=tmdb_headers, params=tmdb_params)

            if tmdb_response.status_code == 200:
                tmdb_data = json.loads(json.dumps(tmdb_response.json()))
                if tmdb_data['total_results'] > 0:
                    for item in tmdb_data['results']:
                        if item['first_air_date'][:4] == year:
                            id = item['id']
                            
                            return id
                if tmdb_data['total_results'] == 0:
                    return None

        except Exception as e:
            return e


    def episodes(self, rating_key):
        try:
            # Retrieve a list of episodes for a show based on rating key
            episodes_url = f"{self.plex_url}/library/metadata/{rating_key}/allLeaves"
            episodes_url = re.sub("0//", "0/", episodes_url)
            headers = {"X-Plex-Token": self.plex_token,
                       "accept": "application/json"}
            response = requests.get(episodes_url, headers=headers)

            if response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(response.text))
                root = tree.getroot()
                episodes = []
                for video in root.iter('Video'):
                    if video.get('type') == 'episode':
                        episodes.append(video.get('title'))
                return episodes
            else:
                return None
        except Exception as e:
            return None

def read_config():
    config_file = config_path
    with open(config_file, "r") as yaml_file:
        config = yaml.load(yaml_file)
        plex_url = config['plex']['url']
        plex_token = config['plex']['token']
        tmdb_api_key = config['tmdb']['apikey']
    return plex_url, plex_token, tmdb_api_key

if __name__ == "__main__":
    plex_url, plex_token, tmdb_api_key = read_config()
    if plex_url and plex_token and tmdb_api_key:
        plex = Plex(plex_url, plex_token, tmdb_api_key)

def setting(value):
        yaml = YAML()
        settings = settings_path
        with open(settings) as sf:
            pref = yaml.load(sf)
            if value == 'library':
                entry = pref['library_name']
            if value == 'days':
                 entry = pref['days_ahead']
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
''')


# Check if this is a Docker Build to format PMM config folder directory
is_docker = os.environ.get('PATTRMM_DOCKER', "False")

if is_docker == "True":
    configPathPrefix = "./config/"

if is_docker == "False":
    configPathPrefix = "../"

# Plex Meta Manager config file path
config_path = configPathPrefix + 'config.yml'
# overlay folder path
overlay_path = configPathPrefix + 'overlays'



# Check if PMM config file can be found. If not, inform and exit.
isConfig = os.path.exists(config_path)
if not isConfig:
    print("Plex Meta Manager Config file could not be located.")
    print("Please ensure config directory is bound to the Plex Meta Manager config directory.")
    sys.exit()
else:
    print("PMM config file found.")


# Import the vars module
import vars
from vars import Plex
plex_method_url = vars.plexApi('url')
plex_method_token = vars.plexApi('token')
tmdb_method_api_key = vars.tmdbApi('token')
plex = Plex(plex_method_url, plex_method_token, tmdb_method_api_key)


# If PMM overlay folder cannot be found, stop
isOvPath = os.path.exists(overlay_path)
if not isOvPath:
    print("Plex Meta Manager Overlay folder could not be located.")
    print("Please ensure PATTRMM is in a subfolder of the PMM config directory.")
    exit()


#check for days_ahead assignment
try:
    days_ahead = vars.setting('days')
    if days_ahead > 90:
        days_ahead = 90
except KeyError:
    days_ahead = 30

##############################################
# Start sequencing through defined Libraries #
openSettings = open(settings, "r")
loadSettings = yaml.load(openSettings)
for library in loadSettings['library_name']:
    

    # keys file for ratingKey and tmdb pairs
    keys = "./data/" + library + "-keys.json"
    keys = re.sub(" ", "-", keys)

    # cache file for tmdb details
    cache = "./data/" + library + "-tmdb-cache.json"
    cache = re.sub(" ", "-", cache)
    
    # returning-soon metadata file for collection
    meta = "./config/" + library + "-returning-soon.yml"
    meta = re.sub(" ", "-", meta)
    # generated overlay file path
    rso = "./config/overlays/" + library + "-returning-soon-overlay.yml"
    rso = re.sub(" ", "-", rso)
    # overlay template path
    overlay_temp = "./preferences/" + library + "-returning-soon-template.yml"
    overlay_temp = re.sub(" ", "-", overlay_temp)
    

    # Just some information
    print("Checking folder structure for " + library + ".")
    logging.info('Checking folder structure for ' + library + '.')

    print("Checking " + library + " files...")
    logging.info("Checking " + library + " files...")


    # If keys file doesn't exist, create it
    isKeys = os.path.exists(keys)
    if not isKeys:
        print("Creating " + library + " keys file..")
        logging.info("Creating " + library + " keys file..")
        writeKeys = open(keys, "x")
        writeKeys.close()
        firstRun = True
    else:
        print(library + " keys file found.")
        logging.info(library + " keys file found.")
        print("Checking " + library + " data...")
        logging.info("Checking " + library + " data...")
        if os.stat(keys).st_size == 0:
            firstRun = True
            print(library + " keys file is empty. Initiating first run.")
            logging.info(library + " keys file is empty. Initiating first run.")
        if os.stat(keys).st_size != 0:
            firstRun = False

    # If cache file doesn't exist, create it
    isCache = os.path.exists(cache)
    if not isCache:
        print("Creating " + library + " cache file..")
        logging.info("Creating " + library + " cache file..")
        writeCache = open(cache, "x")
        writeCache.write('tmdbDataCache')
        writeCache.close()
    else:
        print(library + " cache file present.")
        logging.info(library + " cache file present.")

    # If returning-soon metadata file doesn't exist, create it
    isMeta = os.path.exists(meta)
    if not isMeta:
        print("Creating " + library + " metadata collection file..")
        logging.info("Creating " + library + " metadata collection file..")
        writeMeta = open(meta, "x")
        me = vars.traktApi('me')
        slug = re.sub(" ", "-", library)
        writeMeta.write(
            f'''
collections:
  Returning Soon:
    trakt_list: https://trakt.tv/users/{me}/lists/returning-soon-{slug}
    collection_order: custom
    visible_home: true
    visible_shared: true
    sync_mode: sync
    '''
        )
        writeMeta.close()
    else:
        print(library + " metadata file present.")
        logging.info(library + " metadata file present.")

    
    # If overlay template doesn't exist, create it
    isTemplate = os.path.exists(overlay_temp)
    if not isTemplate:
        print("Generating " + library + " template file..")
        logging.info("Generating " + library + " template file..")
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
        print(library + " template file found.")
        logging.info(library + " template file found.")

    
    # If overlay file doesn't exist, create it
    isOverlay = os.path.exists(rso)
    if not isOverlay:
        print("Creating empty " + library + " Overlay file..")
        logging.info("Creating empty " + library + " Overlay file..")
        writeRSO = open(rso, "x")
        writeRSO.write('')
        writeRSO.close()
    else:
        print(library + " overlay file present.")
        logging.info(library + " overlay file present.")

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
            if year != "null":
                self.year = datetime.strptime(year, date_format).year
            else:
                self.year = year
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
    #library = vars.setting('library')
    plexCall = vars.plexApi('url') + '/library/sections/' + vars.plexGet(library) + '/all'
    plex_url = re.sub("//lib", "/lib", plexCall)
    plex_headers = {
        "accept": "application/json"
    }
    plex_token = {'X-Plex-Token': '' + vars.plexApi('token') + ''}


    # gather list of entries in plex
    print("Gathering Plex entries...")
    logging.info("Gathering Plex entries...")
    

    series = json.loads(prettyJson(requests.get(plex_url, headers=plex_headers, params=plex_token).json()))
    titlesInPlex = get_count(series['MediaContainer']['Metadata'])
    count = 1
    for this in series['MediaContainer']['Metadata']:
        
        try:
            Search.append(Plex_Item(this['title'],this['originallyAvailableAt'], this['ratingKey']))
        except KeyError:
            print("")
            print("Caution " + this['title'] + " does not have an originally available at date. May not be able to match.")
            logging.warning("Caution " + this['title'] + " does not have an originally available at date. May not be able to match.")
            Search.append(Plex_Item(this['title'],"null", this['ratingKey']))
        count += 1
        
    print("Found " + get_count(series['MediaContainer']['Metadata']) + " entries...")

    # search for tmdb id of each entry, will update to use stored keys to reduce unnecessary searches
    refreshSearch = Search
    Search = json.loads(dict_ToJson(Search))

    
    # No need to run a full lookup on subsequent runs
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


        # Check for existing data for remaining Plex entries.
        rfSearch = 0
        newSearch = Search
        print("")
        for eachItem in newSearch[:]:
            if (eachItem['ratingKey'] in updatedKeys):
                newSearch.remove(eachItem)
                #print("Key data exists for " + eachItem['title'] + ". Removed from search list")
                rfSearch += 1
                
        # Output how many entries have existing data                   
        print("Found existing data for " + str(rfSearch) + " titles. Removing from search list.")
        logging.info("Found existing data for " + str(rfSearch) + " titles. Removing from search list.")
        print("")

        # Search for new and missing data
        for remainingItem in newSearch:
            print("No key entry found for " + remainingItem['title'] + ". Searching for details...")
            logging.info("No key entry found for " + remainingItem['title'] + ". Searching for details...")
        if len(newSearch) < 1:
            message = False
            print("Nothing new to search for. Proceeding...")
            logging.info("Nothing new to search for. Proceeding...")
        if len(newSearch) > 0:
            message = True
            Search = newSearch

        # Hold list to append searches
        status_key_pairs = cleanedKeysList







    # Start searching for missing data. Look for TMDB ID first.
    count = 1
    for query in Search:
        # display search progress
        print("\rSearching... " + "(" + str(count) + "/" + get_count(Search) + ")", end="")
        ratingKey = query['ratingKey']
        searchYear = True
        if query['year'] == "null":
            searchYear = False
        id = plex.show.tmdb_id(ratingKey)
        if id != "null" and searchYear != False:
            key_pairs.append(tmdb_search(query['title'], query['ratingKey'], id, "null"))
                    # info for found match
            print(" Found ID ==> " + str(id) + " for " + '"' + query['title'] + '"')
            logging.info(" Found ID ==> " + str(id) + " for " + '"' + query['title'] + '"')
            # end adding to the list after the first match is found, else duplicate entries occur
                
        # increment progress after a successful match 
        count += 1
    
    # Get details using the TMDB IDs.
    for d in json.loads(dict_ToJson(key_pairs)):

        tmdbUrl = "https://api.themoviedb.org/3/tv/" + str(d['tmdb_id'])
        tmdbHeaders = {
        "accept": "application/json"
        }
        tmdbParams = {
            "language": "en-US", "api_key": vars.tmdbApi('token')
        }

        tmdb_request = requests.get(tmdbUrl, headers=tmdbHeaders, params=tmdbParams)
        
        # If the page does not return successful
        if tmdb_request.status_code != 200:
            print("There was a problem accessing the resource for TMDB ID " + str(d['tmdb_id']))
            if tmdb_request.status_code == 34:
                print("This ID has been removed from TMDB, or is no longer accessible.")
                print("Try refreshing the metadata for " + d['title'])
            
            continue

        # If the page returns successful, get details.    
        tmdb = json.loads(prettyJson(tmdb_request.json()))

        print("Found details for " + tmdb['name'] + " ( " + str(tmdb['id']) + " )")
        logging.info("Found details for " + tmdb['name'] + " ( " + str(tmdb['id']) + " )")

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
        print(library + " Keys updated...")
        logging.info(library + " Keys updated...")
    if firstRun == False:
        if message == True:
            print(library + " Keys updated...")
            logging.info(library + " Keys updated...")
            print("Updating data for Returning " + library + ".")
            logging.info("Updating data for Returning " + library + ".")

    if firstRun == False:
        updateMe = []
        keyFile = open(keys, "r")
        keyData = json.load(keyFile)
        
        for u in keyData:

            if u['status'] != "Returning Series":
                updateMe.append(tmdb_search(u['title'], u['ratingKey'], u['tmdb_id'], u['status']))
            if u['status'] == "Returning Series":
                tmdbUrl = "https://api.themoviedb.org/3/tv/" + str(u['tmdb_id'])
                tmdbHeaders = {
                "accept": "application/json"
                }
                tmdbParams = {
                "language": "en-US", "api_key": vars.tmdbApi('token')
                }

                tmdbSubRequest = requests.get(tmdbUrl,headers=tmdbHeaders, params=tmdbParams)
                if tmdbSubRequest.status_code != 200:
                    print("There was a problem accessing the resource for TMDB ID " + str(u['tmdb_id']))
                if tmdbSubRequest.status_code == 34:
                    print("This ID has been removed from TMDB, or is no longer accessible.")
                    print("Try refreshing the metadata for " + u['title'])
                    continue
                
                tmdb = json.loads(prettyJson(tmdbSubRequest.json()))

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
    print("\033[K" + library + " TMDB data updated...")
    logging.info(library + " TMDB data updated...")


    # write Template to Overlay file
    print("Writing " + library + " Overlay Template to Returning Soon " + library + " overlay file.")
    logging.info("Writing " + library + " Overlay Template to Returning Soon " + library + " overlay file.")
    with open(overlay_temp) as ot:
        ovrTemp = yaml.load(ot)
        rsoWrite = open(rso, "w")
        yaml.dump(ovrTemp, rsoWrite)
        print(library + " template applied.")


    # Generate Overlay body
    # define date ranges
    dayCounter = 1
    today = date.today()
    lastAirDate = date.today() - timedelta(days=45)
    last_episode_aired = lastAirDate.strftime("%m/%d/%Y")
    nextAirDate = date.today() + timedelta(days=int(days_ahead))
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

    print("Generating " + library + " overlay body.")
    logging.info("Generating " + library + " overlay body.")

    overlay_base = '''

overlays:
    '''




    if vars.setting('ovNew') == True:
        logging.info('"New" Overlay enabled, generating body...')
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
        logging.info('"Airing" Overlay enabled, generating...')
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
        logging.info('"Ended" Overlay enabled, generating body...')
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
        logging.info('"Canceled" Overlay enabled, generating body...')
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
        logging.info('"Returning" Overlay enabled, generating body...')
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
    
    print(library + " overlay body generated. Writing to file.")
    logging.info(library + " overlay body generated. Writing to file.")

    # Write the rest of the overlay
    writeBody = open(rso, "a")
    yaml.dump(yaml.load(overlay_base), writeBody)
    writeBody.close()
    print("Overlay body appended to " + library + "-returning-soon-overlay.")
    logging.info("Overlay body appended to " + library + "-returning-soon-overlay.")

    # use keys file to gather show details
    print("Reading " + library + " cache file...")
    logging.info("Reading " + library + " cache file...")
    cacheFile = open(cache, "r")
    cacheData = json.load(cacheFile)
    cacheFile.close()

    # this is for the trakt list
    print("Filtering " + library + " data...")
    logging.info("Filtering " + library + " data...")
    returningSoon = filter(
        lambda x: (
            x['status'] == "Returning Series" and 
            x['nextAir'] != "null" and 
            x['nextAir'] < str(nextAirDate) and 
            x['nextAir'] > str(today) and 
            x['lastAir'] < str(lastAirDate)),
            cacheData)
    print("Sorting " + library + "...")
    logging.info("Sorting " + library + "...")
    returningSorted = sortedList(returningSoon, 'nextAir')

    traktaccess = vars.traktApi('token')
    traktapi = vars.traktApi('client')
    traktHeaders = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + traktaccess + '',
                    'trakt-api-version': '2',
                    'trakt-api-key': '' + traktapi + ''
                    }
    slug = re.sub(" ", "-", library)
    traktListUrl = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists"
    traktListUrlPost = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + slug + ""
    traktListUrlPostShow = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + slug + "/items"
    traktListData = f'''
{{
    "name": "Returning Soon {library}",
    "description": "Season premiers and returns within the next 30 days.",
    "privacy": "private",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''

    print("Clearing " + library + " trakt list...")
    logging.info("Clearing " + library + " trakt list...")
    traktDeleteList = requests.delete(traktListUrlPost, headers=traktHeaders)
    time.sleep(1.25)
    traktMakeList = requests.post(traktListUrl, headers=traktHeaders, data=traktListData)
    time.sleep(1.25)
    traktListShow = '''
{
    "shows": [
        '''
    for item in returningSorted:
        print("Adding " + item['title'] + " | TMDB ID: " + str(item['id']) + ", to Returning Soon " + library + ".")
        logging.info("Adding " + item['title'] + " | TMDB ID: " + str(item['id']) + ", to Returning Soon " + library + ".")

        traktListShow += f'''
    {{
    "ids": {{
        "tmdb": "{str(item['id'])}"
            }}
    }},'''
        
        
    traktListShow = traktListShow.rstrip(",")
    traktListShow += '''
]
}
'''
    
    postShow = requests.post(traktListUrlPostShow, headers=traktHeaders, data=traktListShow)
    if postShow.status_code == 201:
        print("Success")
        print("Added " + str(get_count(returningSorted)) + " entries to Trakt.")
        logging.info('Success: Added ' + str(get_count(returningSorted)) + ' entries to Trakt.')
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"All operations complete. Run time {minutes:02}:{seconds:02}")
logging.info(f"All operations complete. Run time {minutes:02}:{seconds:02}")
