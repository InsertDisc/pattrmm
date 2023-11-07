#pattrmm-py by insertdisc

# import dependencies
import time
start_time = time.time()
from datetime import date
from datetime import timedelta
from datetime import datetime
today = date.today()
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
from io import StringIO
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

# history folder for timestamps
statsDir = "./data/history"
isStatsDir = os.path.exists(statsDir)
if not isStatsDir:
    os.makedirs(statsDir)


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
libraries:
  TV Shows:                          # Plex Libraries to read from. Can enter multiple libraries.
    trakt_list_privacy: private
    save_folder: "metadata/"
    refresh: 30                      # Full-refresh delay for library          
    days_ahead: 30                   # How far ahead to consider 'Returning Soon'
    extensions:
      in-history:
        range: month
        trakt_list_privacy: private
        save_folder: "collections/"
date_style: 1                        # 1 for mm/dd, 2 for dd/mm
overlay_prefix: "RETURNING"          # Text to display before the dates.
horizontal_align: center
vertical_align: top
vertical_offset: 0
horizontal_offset: 0
leading_zeros: True                  # 01/14 vs 1/14 for dates. True or False
date_delimiter: "/"                  # Delimiter for dates. Can be "/", "-", "." or "_", e.g. 01/14, 01-14, 01.14, 01_14
year_in_dates: False                 # Show year in dates: 01/14/22 vs 01/14. True or False
returning_soon_bgcolor: "#81007F"
returning_soon_fontcolor: "#FFFFFF"

extra_overlays:
  new:
    use: True
    bgcolor: "#008001"
    font_color: "#FFFFFF"
    text: "N E W  S E R I E S"
    horizontal_align: center
    vertical_align: top
  upcoming:
    use: True
    bgcolor: "#fc4e03"
    font_color: "#FFFFFF"
    text: "U P C O M I N G"
    horizontal_align: center
    vertical_align: top
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
yaml.preserve_quotes = True
import xml.etree.ElementTree as ET
import requests
import json
import re
import datetime
today = datetime.datetime.today()
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

def date_within_range(item_date, start_date, end_date):
    if (start_date.month, start_date.day) <= (end_date.month, end_date.day):
        return (
            (start_date.month, start_date.day) <= 
            (item_date.month, item_date.day) <= 
            (end_date.month, end_date.day)
        )
    else:
        return (
            (item_date.month, item_date.day) >= 
            (start_date.month, start_date.day) 
            or 
            (item_date.month, item_date.day) <= 
            (end_date.month, end_date.day)
        )

class LibraryList:
    def __init__(self, title, date, ratingKey):
        self.title = title
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        self.ratingKey = ratingKey

class itemBase:
    def __init__(self, title, date, details):
        self.title = re.sub("\s\(.*?\)","", title)
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        self.details = details
        

class itemDetails:
    def __init__(self, ratingKey, imdb, tmdb, tvdb):
        self.ratingKey = ratingKey
        self.imdb = imdb
        self.tmdb = tmdb
        self.tvdb = tvdb

class Extensions:
    def __init__(self, extension_library):
        self.extension_library = extension_library

    @property
    def in_history(self):
        self.context = 'in_history'
        return self

    def settings(self):
        if self.context == 'in_history':
            settings = settings_path
            with open(settings) as sf:
                pref = yaml.load(sf)
            me = traktApi('me')
            slug = cleanPath(self.extension_library)
            self.slug = slug
            trakt_list_meta = f"https://trakt.tv/users/{me}/lists/in-history-{slug}"
            try:
                self.trakt_list_privacy = pref['libraries'][self.extension_library]['extensions']['in-history']['trakt_list_privacy']
            except KeyError:
                self.trakt_list_privacy = 'private'
            try:
                range = pref['libraries'][self.extension_library]['extensions']['in-history']['range']
                range_lower = range.lower()
                self.range = range_lower
            except KeyError:
                self.range = 'day'        
            try:
                self.save_folder = pref['libraries'][self.extension_library]['extensions']['in-history']['save_folder']
            except KeyError:
                self.save_folder = ''
            try:
                self.collection_title = pref['libraries'][self.extension_library]['extensions']['in-history']['collection_title']
            except KeyError:
                self.collection_title = 'This {{range}} in history'
            if "{{range}}" in self.collection_title:
                self.collection_title = self.collection_title.replace("{{range}}", self.range)
            if "{{Range}}" in self.collection_title:
                self.collection_title = self.collection_title.replace("{{Range}}", self.range.capitalize())
            try:
                self.starting = pref['libraries'][self.extension_library]['extensions']['in-history']['starting']
            except KeyError:
                self.starting = 0
            try:
                self.ending = pref['libraries'][self.extension_library]['extensions']['in-history']['ending']
            except KeyError:
                self.ending = today.year
            try:
                self.increment = pref['libraries'][self.extension_library]['extensions']['in-history']['increment']
            except KeyError:
                self.increment = 1
            try:
                try:
                    options = {
                    key: value
                    for key, value in pref['libraries'][self.extension_library]['extensions']['in-history']['meta'].items()
                        }
                    if "sort_title" in options:
                        options['sort_title'] = '"' + options['sort_title'] + '"'
                except KeyError:
                    options = {}
                self.meta = {}
                self.meta['collections'] = {}
                self.meta['collections'][self.collection_title] = {}
                self.meta['collections'][self.collection_title]['trakt_list'] = trakt_list_meta
                self.meta['collections'][self.collection_title]['visible_home'] = 'true'
                self.meta['collections'][self.collection_title]['visible_shared'] = 'true'
                self.meta['collections'][self.collection_title]['collection_order'] = 'custom'
                self.meta['collections'][self.collection_title]['sync_mode'] = 'sync'
                self.meta['collections'][self.collection_title].update(options)
                
            except Exception as e:
                return f"Error: {str(e)}"
        return self
                

class Plex:
    def __init__(self, plex_url, plex_token, tmdb_api_key):
        self.plex_url = plex_url
        self.plex_token = plex_token
        self.tmdb_api_key = tmdb_api_key
        self.context = None

    @property
    def library(self):
        self.context = 'library'
        return self  # Return self to allow method chaining
    
    @property
    def collection(self):
        self.context = 'collection'
        return self  # Return self to allow method chaining
    
    @property
    def item(self):
        self.context = 'item'
        return self  # Return self to allow method chaining

    @property
    def show(self):
        self.context = 'show'
        return self  # Return self to allow method chaining
    
    @property
    def shows(self):
        self.context = 'shows'
        return self  # Return self to allow method chaining
    
    @property
    def movie(self):
        self.context = 'movie'
        return self  # Return self to allow method chaining
    
    @property
    def movies(self):
        self.context = 'movies'
        return self  # Return self to allow method chaining
        
    
    def type(self, library):
        library_details_url = f"{self.plex_url}/library/sections"
        library_details_url = re.sub("0//", "0/", library_details_url)
        headers = {"X-Plex-Token": self.plex_token,
                "accept": "application/json"}
        response = requests.get(library_details_url, headers=headers)
        data = response.json()
        for section in data['MediaContainer']['Directory']:
            if section["title"] == library:
                library_type = section["type"]

        return library_type


    
    def info(self, ratingKey):
        
        if self.context == 'item':
            movie_details_url = f"{self.plex_url}/library/metadata/{ratingKey}"
            movie_details_url = re.sub("0//", "0/", movie_details_url)
            headers = {"X-Plex-Token": self.plex_token,
                "accept": "application/json"}
            response = requests.get(movie_details_url, headers=headers)
            if response.status_code == 200:
                imdbID = "Null"
                tmdbID = "Null"
                tvdbID = "Null"
                
                data = response.json()
                extendedDetails = response.json()
                try:
                    data = data['MediaContainer']['Metadata']
                    for item in data:
                        title = item.get('title')
                        if item.get('originallyAvailableAt'):
                            date = item.get('originallyAvailableAt')
                        else:
                            date = "Null"
                        key = item.get('ratingKey')
                except:
                    None
                try:
                    dataDetails = extendedDetails['MediaContainer']['Metadata'][0]['Guid']
                    for guid_item in dataDetails:
                        guid_id = guid_item.get('id')
                        if guid_id.startswith("tmdb://"):
                            tmdbID = guid_item.get('id')[7:]
                        if guid_id.startswith("imdb://"):
                            imdbID = guid_item.get('id')[7:]
                        if guid_id.startswith("tvdb://"):
                            tvdbID = guid_item.get('id')[7:]
                except KeyError:
                    return itemBase(title=title, date=date, details=itemDetails(key, imdbID, tmdbID, tvdbID))
                return itemBase(title=title, date=date, details=itemDetails(key, imdbID, tmdbID, tvdbID))
                    
    
    def list(self, library):
            try:
                # Replace with the correct section ID and library URL
                section_id = plexGet(library)  # Replace with the correct section ID
                library_url = f"{self.plex_url}/library/sections/{section_id}/all"
                library_url = re.sub("0//", "0/", library_url)
                headers = {"X-Plex-Token": self.plex_token,
                           "accept": "application/json"}
                response = requests.get(library_url, headers=headers)
                library_list = []

                if response.status_code == 200:
                    data = response.json()
                    for item in data['MediaContainer']['Metadata']:
                        try:
                            check_if_has_date = item['originallyAvailableAt']

                            library_list.append(LibraryList(title=item['title'],ratingKey=item['ratingKey'], date=item['originallyAvailableAt']))
                        except KeyError:
                            print(f"{item['title']} has no 'Originally Available At' date. Ommitting title.")
                            continue
                    return library_list
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error: {str(e)}"
            

    def id(self, name, library_id=None):
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
                        if item['type'] == 'show' and item['title'] == name:
                            return f"ID for show '{name}': {item['ratingKey']}"
                    return f"Show '{name}' not found"
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error: {str(e)}"
            
        if self.context == 'movie':
            try:
                num = 1 + 1 # get movie id here

            except Exception as e:
                return f"Error: {str(e)}"
            
        if self.context == 'collection':
            try:
                section_id = library_id
                collection_name = name
                collection_url = f"{self.plex_url}/library/sections/{section_id}/collections"
                collection_url = re.sub("0//", "0/", collection_url)
                headers = {"X-Plex-Token": self.plex_token,
                           "accept": "application/json"}
                response = requests.get(collection_url, headers=headers)
                if response.status_code == 200:
                    collections_data = response.json()
                for collection in collections_data['MediaContainer']['Metadata']:
                    if collection['title'] == collection_name:
                        collection_id = collection['ratingKey']
                return collection_id
            except Exception as e:
                return f"Error: {str(e)}"

    def delete(self, key):
        if self.context == 'collection':
            try:
                collection_id = key
                collection_delete_url = f"{self.plex_url}/library/collections/{collection_id}"
                collection_delete_url = re.sub("0//", "0/", collection_delete_url)
                headers = {"X-Plex-Token": self.plex_token,
                           "accept": "application/json"}
                response = requests.delete(collection_delete_url, headers=headers)
                if response.status_code == 200:
                    return True
                elif response.status_code != 200:
                    return False
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

def history(libraryCleanPath, stat):
        stats = "./data/history/" + libraryCleanPath + "-history.json"
        statsFile = open(stats, "r")
        try:
            statsData = json.load(statsFile)
            statsFile.close()
            if stat == "lastFull":
                lastRefresh = statsData['lastRefresh']
        except:
            lastRefresh = today
        return lastRefresh

def librarySetting(library, value):

        yaml = YAML()
        settings = settings_path
        with open(settings) as sf:
            pref = yaml.load(sf)
            if value == 'returning-soon':
                try:
                    entry = pref['libraries'][library]['returning-soon']
                except KeyError:
                    entry = True
                if entry not in (True, False):
                    print(f"Invalid setting returning-soon: '{entry}' for {library}, defaulting to True")
                    entry = True
            if value == 'refresh':
                try:
                    entry = pref['libraries'][library]['refresh']
                except KeyError:
                    entry = 15
            if value == 'days':
                try:
                    entry = pref['libraries'][library]['days_ahead']
                    if entry > 90:
                        entry = 90
                except:
                    entry = 30

            if value == 'save_folder':
                try:
                    entry = pref['libraries'][library]['save_folder']
                except KeyError:
                    entry = ''

            if value == 'trakt_list_privacy':
                try:
                    entry = pref['libraries'][library]['trakt_list_privacy']
                except KeyError:
                    entry = 'private'

        return entry

def setting(value):
        yaml = YAML()
        settings = settings_path
        with open(settings) as sf:
            pref = yaml.load(sf)

            if value == 'rsback_color':
                entry = pref['returning_soon_bgcolor']
            if value == 'rsfont_color':
                entry = pref['returning_soon_fontcolor']

            if value == 'rs_vertical_align':
                try:
                    entry = pref['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'rs_horizontal_align':
                try:
                    entry = pref['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'rs_horizontal_offset':
                try:
                    entry = pref['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'rs_vertical_offset':
                try:
                    entry = pref['vertical_offset']
                except KeyError:
                    entry = '0'

            if value == 'prefix':
                entry = pref['overlay_prefix']
            if value == 'dateStyle':
                entry = pref['date_style']
            if value == 'zeros':
                try:
                    entry = pref['leading_zeros']
                except:
                    entry = True
            if value == 'delimiter':
                try:
                    entry = pref['date_delimiter']
                except:
                    entry = "/"
            if value == 'year':
                try:
                    entry = pref['year_in_dates']
                except:
                    entry = False


            if value == 'ovUpcoming':
                try:
                    entry = pref['extra_overlays']['upcoming']['use']
                except:
                    entry = False
            if value == 'ovUpcomingColor':
                try:
                    entry = pref['extra_overlays']['upcoming']['bgcolor']
                except KeyError:
                    entry = "#fc4e03"
            if value == 'ovUpcomingFontColor':
                try:
                    entry = pref['extra_overlays']['upcoming']['font_color']
                except KeyError:
                    entry = "#FFFFFF"
            if value == 'ovUpcomingText':
                try:
                    entry = pref['extra_overlays']['upcoming']['text']
                except KeyError:
                    entry = "U P C O M I N G"

            if value == 'ovUpcoming_horizontal_align':
                try:
                    entry = pref['extra_overlays']['upcoming']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovUpcoming_vertical_align':
                try:
                    entry = pref['extra_overlays']['upcoming']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovUpcoming_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['upcoming']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovUpcoming_vertical_offset':
                try:
                    entry = pref['extra_overlays']['upcoming']['vertical_offset']
                except KeyError:
                    entry = '0'



            if value == 'ovNew':
                try:
                    entry = pref['extra_overlays']['new']['use']
                except:
                    entry = False
            if value == 'ovNewColor':
                 entry = pref['extra_overlays']['new']['bgcolor']
            if value == 'ovNewFontColor':
                 entry = pref['extra_overlays']['new']['font_color']
            if value == 'ovNewText':
                 entry = pref['extra_overlays']['new']['text']

            if value == 'ovNew_horizontal_align':
                try:
                    entry = pref['extra_overlays']['new']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovNew_vertical_align':
                try:
                    entry = pref['extra_overlays']['new']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovNew_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['new']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovNew_vertical_offset':
                try:
                    entry = pref['extra_overlays']['new']['vertical_offset']
                except KeyError:
                    entry = '0'



                 
            
            if value == 'ovReturning':
                try:
                    entry = pref['extra_overlays']['returning']['use']
                except:
                    entry = False
            if value == 'ovReturningColor':
                 entry = pref['extra_overlays']['returning']['bgcolor']
            if value == 'ovReturningFontColor':
                 entry = pref['extra_overlays']['returning']['font_color']
            if value == 'ovReturningText':
                 entry = pref['extra_overlays']['returning']['text']

            if value == 'ovReturning_horizontal_align':
                try:
                    entry = pref['extra_overlays']['returning']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovReturning_vertical_align':
                try:
                    entry = pref['extra_overlays']['returning']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovReturning_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['returning']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovReturning_vertical_offset':
                try:
                    entry = pref['extra_overlays']['returning']['vertical_offset']
                except KeyError:
                    entry = '0'




            if value == 'ovAiring':
                try:
                    entry = pref['extra_overlays']['airing']['use']
                except:
                    entry = False
            if value == 'ovAiringColor':
                 entry = pref['extra_overlays']['airing']['bgcolor']
            if value == 'ovAiringFontColor':
                 entry = pref['extra_overlays']['airing']['font_color']
            if value == 'ovAiringText':
                 entry = pref['extra_overlays']['airing']['text']

            if value == 'ovAiring_horizontal_align':
                try:
                    entry = pref['extra_overlays']['airing']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovAiring_vertical_align':
                try:
                    entry = pref['extra_overlays']['airing']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovAiring_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['airing']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovAiring_vertical_offset':
                try:
                    entry = pref['extra_overlays']['airing']['vertical_offset']
                except KeyError:
                    entry = '0'




            if value == 'ovEnded':
                try:
                    entry = pref['extra_overlays']['ended']['use']
                except:
                    entry = False
            if value == 'ovEndedColor':
                 entry = pref['extra_overlays']['ended']['bgcolor']
            if value == 'ovEndedFontColor':
                 entry = pref['extra_overlays']['ended']['font_color']
            if value == 'ovEndedText':
                 entry = pref['extra_overlays']['ended']['text']

            if value == 'ovEnded_horizontal_align':
                try:
                    entry = pref['extra_overlays']['ended']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovEnded_vertical_align':
                try:
                    entry = pref['extra_overlays']['ended']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovEnded_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['ended']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovEnded_vertical_offset':
                try:
                    entry = pref['extra_overlays']['ended']['vertical_offset']
                except KeyError:
                    entry = '0'




            if value == 'ovCanceled':
                try:
                    entry = pref['extra_overlays']['canceled']['use']
                except:
                    entry = False
            if value == 'ovCanceledColor':
                 entry = pref['extra_overlays']['canceled']['bgcolor']
            if value == 'ovCanceledFontColor':
                 entry = pref['extra_overlays']['canceled']['font_color']
            if value == 'ovCanceledText':
                 entry = pref['extra_overlays']['canceled']['text']

            if value == 'ovCanceled_horizontal_align':
                try:
                    entry = pref['extra_overlays']['canceled']['horizontal_align']
                except KeyError:
                    entry = 'Center'

            if value == 'ovCanceled_vertical_align':
                try:
                    entry = pref['extra_overlays']['canceled']['vertical_align']
                except KeyError:
                    entry = 'Top'

            if value == 'ovCanceled_horizontal_offset':
                try:
                    entry = pref['extra_overlays']['canceled']['horizontal_offset']
                except KeyError:
                    entry = '0'

            if value == 'ovCanceled_vertical_offset':
                try:
                    entry = pref['extra_overlays']['canceled']['vertical_offset']
                except KeyError:
                    entry = '0'

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

def cleanPath(string):
        cleanedPath = re.sub(r'[^\w]+', '-', string)
        return cleanedPath


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
from vars import date_within_range
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





##############################################
# Start sequencing through defined Libraries #
openSettings = open(settings, "r")
loadSettings = yaml.load(openSettings)
for library in loadSettings['libraries']:

    if plex.library.type(library) != 'show':
        print(f"{library} is not compatible with the 'Returning Soon' method. Skipping.")
        continue
    
    if vars.librarySetting(library, 'returning-soon') is False:
        print(f"'Returning Soon' disabled for {library}. Skipping.")
        continue

    libraryCleanPath = vars.cleanPath(library)
    
    # check for days_ahead assignment
    days_ahead = vars.librarySetting(library, 'days')

    # Set stats file
    stats = "./data/history/" + libraryCleanPath + "-history.json"
    isStats = os.path.exists(stats)
    if not isStats:
        writeStats = open(stats, "x")
        writeStats.write(f'''
{{
    "lastRefresh": "{today}"
}}''')
        writeStats.close()

    statsFile = open(stats, "r")
    statsData = json.load(statsFile)
    statsFile.close()


    # Check for last run of this library
    refreshDays = vars.librarySetting(library, 'refresh')
    refreshHist = vars.history(libraryCleanPath, 'lastFull')
    refreshHist = datetime.strptime(refreshHist, "%Y-%m-%d")
    delay = refreshHist + timedelta(days=refreshDays)
    if today >= delay.date():
        refresh = True
    if today < delay.date():    
        refresh = False

    # keys file for ratingKey and tmdb pairs
    keys = "./data/" + libraryCleanPath + "-keys.json"

    # cache file for tmdb details
    cache = "./data/" + libraryCleanPath + "-tmdb-cache.json"

    # returning soon metadata save folder
    metadata_save_folder = vars.librarySetting(library, 'save_folder')
    save_folder = configPathPrefix + metadata_save_folder
    if save_folder != '':
        is_save_folder = os.path.exists(save_folder)
        if not is_save_folder:
            subfolder_display_path = f"config/{metadata_save_folder}"
            print(f"Sub-folder {subfolder_display_path} not found.")
            print(f"Attempting to create.")
            logging.info(f"Sub-folder {subfolder_display_path} not found.")
            logging.info(f"Attempting to create.")
            try:
                os.makedirs(save_folder)
                print(f"{subfolder_display_path} created successfully.")
                logging.info(f"{subfolder_display_path} created successfully.")
            except Exception as sf:
                print(f"Exception: {str(sf)}")
                logging.warning(f"Exception: {str(sf)}")
    
    # returning-soon metadata file for collection
    meta = save_folder + libraryCleanPath + "-returning-soon-metadata.yml"
    # generated overlay file path
    rso = configPathPrefix + "overlays/" + libraryCleanPath + "-returning-soon-overlay.yml"
    # overlay template path
    overlay_temp = "./preferences/" + libraryCleanPath + "-returning-soon-template.yml"
    

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

            ## Has the refresh status delay passed for this library ##
            if refresh == False:
                print("Keys data refresh delay for " + library + " not yet met.")
                logging.info("Keys data refresh delay for " + library + " not yet met. Skipping status renewal.")
                firstRun = False
            if refresh == True:
                firstRun = True
                print("Keys data has expired. Rebuilding...")

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
        slug = libraryCleanPath
        writeMeta.write(
            f'''
collections:
  Returning Soon:
    trakt_list: https://trakt.tv/users/{me}/lists/returning-soon-{slug}
    url_poster: https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/Returning%20Soon.jpg
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
      horizontal_offset: <<horizontal_offset>>
      horizontal_align: <<horizontal_align>>
      vertical_offset: <<vertical_offset>>
      vertical_align: <<vertical_align>>
      font: config/fonts/Juventus-Fans-Bold.ttf
      font_size: 70
      font_color: <<color>>
      group: TV_Top_TextCenter
      weight: <<weight>>
      back_color: <<back_color>>
      back_width: 1920
      back_height: 90

    default:
      horizontal_align: center
      vertical_align: top
      horizontal_offset: 0
      vertical_offset: 0
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
                    print(u['title'] + '( ' + str(u['tmdb_id']) + ' ) may have been removed.')
                    continue
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

    # update history timestamp
    if refresh == True:
        try:
            # Read the JSON file
            with open(stats, 'r') as sh:
                statsData = json.load(sh)

            # Update the 'lastRefresh' field with the current date
            now = date.today().strftime("%Y-%m-%d")
            statsData['lastRefresh'] = now

            # Write the updated data back to the JSON file
            with open(stats, 'w') as sh:
                json.dump(statsData, sh, indent=4)

            print("Timestamp updated successfully.")

        except Exception as e:
            print(f"An error occurred updating the timestamp: {str(e)}")



    


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
    lastAirDate = date.today() - timedelta(days=45)
    last_episode_aired = lastAirDate.strftime("%m/%d/%Y")
    nextAirDate = date.today() + timedelta(days=int(days_ahead))
    thisDayTemp = date.today() + timedelta(days=int(dayCounter))
    thisDay = thisDayTemp.strftime("%m/%d/%Y")

    try:
        dateStyle = vars.setting('dateStyle')
    except:
        dateStyle = 1

    try:
        delimiter = vars.setting('delimiter')
        allowedDelimiterTypes = ['/', '-', '.', '_']
        if delimiter not in allowedDelimiterTypes:
            delimiter = "/"
    except:
        delimiter = "/"

    
    if vars.setting('zeros') == True or vars.setting('zeros') != False:
        dayFormatCode = "%d"
        monthFormatCode = "%m"
        
    if vars.setting('zeros') == False:
        if platform.system() == "Windows":
            monthFormatCode = "%#m"
            dayFormatCode = "%#d"
            
        if platform.system() == "Linux" or platform.system() == "Darwin":
            monthFormatCode = "%-m"
            dayFormatCode = "%-d"

    if dateStyle == 1:
        monthDayFormat = "%m/%d"
        monthDayFormatText = monthFormatCode + delimiter + dayFormatCode
        
    if dateStyle == 2:
        monthDayFormat = "%d/%m"
        monthDayFormatText = dayFormatCode + delimiter + monthFormatCode
        

    if vars.setting('year') == True or vars.setting('year') != False:
        yearFormatCode = "%Y"
        dateFormat = monthDayFormat + "/" + yearFormatCode
        dateFormatText = monthDayFormatText + delimiter + yearFormatCode
        
    if vars.setting('year') == False:
        dateFormat = monthDayFormat + "/%Y"
        dateFormatText = monthDayFormatText
    
    thisDayDisplay = thisDayTemp.strftime(dateFormat)
    thisDayDisplayText = thisDayTemp.strftime(dateFormatText)
            

    prefix = vars.setting('prefix')

    print("Generating " + library + " overlay body.")
    logging.info("Generating " + library + " overlay body.")

    overlay_base = '''

overlays:
    '''

    
    if vars.setting('ovUpcoming') == True:
        logging.info('"Upcoming" Overlay enabled, generating body...')
        upcoming_Text = vars.setting('ovUpcomingText')
        upcoming_FontColor = vars.setting('ovUpcomingFontColor')
        upcoming_Color = vars.setting('ovUpcomingColor')
        upcoming_horizontal_align = vars.setting('ovUpcoming_horizontal_align')
        upcoming_vertical_align = vars.setting('ovUpcoming_vertical_align')
        upcoming_horizontal_offset = vars.setting('ovUpcoming_horizontal_offset')
        upcoming_vertical_offset = vars.setting('ovUpcoming_vertical_offset')
        ovUpcoming = f'''
  # Upcoming
  TV_Top_TextCenter_Upcoming:
    template:
      - name: TV_Top_TextCenter
        weight: 90
        text: "{upcoming_Text}"
        color: "{upcoming_FontColor}"
        back_color: "{upcoming_Color}"
        horizontal_align: {upcoming_horizontal_align}
        vertical_align: {upcoming_vertical_align}
        horizontal_offset: {upcoming_horizontal_offset}
        vertical_offset: {upcoming_vertical_offset}
    plex_all: true
    filters:
      tmdb_status:
      - returning
      - planned
      - production
      release.after: today
      '''
        overlay_base = overlay_base + ovUpcoming
    
    
    
    if vars.setting('ovNew') == True:
        logging.info('"New" Overlay enabled, generating body...')
        newText = vars.setting('ovNewText')
        newFontColor = vars.setting('ovNewFontColor')
        newColor = vars.setting('ovNewColor')
        new_horizontal_align = vars.setting('ovNew_horizontal_align')
        new_vertical_align = vars.setting('ovNew_vertical_align')
        new_horizontal_offset = vars.setting('ovNew_horizontal_offset')
        new_vertical_offset = vars.setting('ovNew_vertical_offset')
        ovNew = f'''
  # New
  TV_Top_TextCenter_New:
    template:
      - name: TV_Top_TextCenter
        weight: 60
        text: "{newText}"
        color: "{newFontColor}"
        back_color: "{newColor}"
        horizontal_align: {new_horizontal_align}
        vertical_align: {new_vertical_align}
        horizontal_offset: {new_horizontal_offset}
        vertical_offset: {new_vertical_offset}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
        - ended
        - canceled
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
        airing_horizontal_align = vars.setting('ovAiring_horizontal_align')
        airing_vertical_align = vars.setting('ovAiring_vertical_align')
        airing_horizontal_offset = vars.setting('ovAiring_horizontal_offset')
        airing_vertical_offset = vars.setting('ovAiring_vertical_offset')
        ovAiring = f'''
  # Airing
  TV_Top_TextCenter_Airing:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "{airingText}"
        color: "{airingFontColor}"
        back_color: "{airingColor}"
        horizontal_align: {airing_horizontal_align}
        vertical_align: {airing_vertical_align}
        horizontal_offset: {airing_horizontal_offset}
        vertical_offset: {airing_vertical_offset}
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
        horizontal_align: {airing_horizontal_align}
        vertical_align: {airing_vertical_align}
        horizontal_offset: {airing_horizontal_offset}
        vertical_offset: {airing_vertical_offset}
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
        ended_horizontal_align = vars.setting('ovEnded_horizontal_align')
        ended_vertical_align = vars.setting('ovEnded_vertical_align')
        ended_horizontal_offset = vars.setting('ovEnded_horizontal_offset')
        ended_vertical_offset = vars.setting('ovEnded_vertical_offset')
        ovEnded = f'''
  # Ended
  TV_Top_TextCenter_Ended:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{endedText}"
        color: "{endedFontColor}"
        back_color: "{endedColor}"
        horizontal_align: {ended_horizontal_align}
        vertical_align: {ended_vertical_align}
        horizontal_offset: {ended_horizontal_offset}
        vertical_offset: {ended_vertical_offset}
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
        canceled_horizontal_align = vars.setting('ovCanceled_horizontal_align')
        canceled_vertical_align = vars.setting('ovCanceled_vertical_align')
        canceled_horizontal_offset = vars.setting('ovCanceled_horizontal_offset')
        canceled_vertical_offset = vars.setting('ovCanceled_vertical_offset')
        ovCanceled = f'''
  # Canceled
  TV_Top_TextCenter_Canceled:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{canceledText}"
        color: "{canceledFontColor}"
        back_color: "{canceledColor}"
        horizontal_align: {canceled_horizontal_align}
        vertical_align: {canceled_vertical_align}
        horizontal_offset: {canceled_horizontal_offset}
        vertical_offset: {canceled_vertical_offset}
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
        returning_horizontal_align = vars.setting('ovReturning_horizontal_align')
        returning_vertical_align = vars.setting('ovReturning_vertical_align')
        returning_horizontal_offset = vars.setting('ovReturning_horizontal_offset')
        returning_vertical_offset = vars.setting('ovReturning_vertical_offset')
        ovReturning = f'''
  # Returning
  TV_Top_TextCenter_Returning:
    template:
      - name: TV_Top_TextCenter
        weight: 30
        text: "{returningText}"
        color: "{returningFontColor}"
        back_color: "{returningColor}"
        horizontal_align: {returning_horizontal_align}
        vertical_align: {returning_vertical_align}
        horizontal_offset: {returning_horizontal_offset}
        vertical_offset: {returning_vertical_offset}
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
        rs_horizontal_align = vars.setting('rs_horizontal_align')
        rs_vertical_align = vars.setting('rs_vertical_align')
        rs_horizontal_offset = vars.setting('rs_horizontal_offset')
        rs_vertical_offset = vars.setting('rs_vertical_offset')
        overlay_gen = f'''
# RETURNING {thisDayDisplay}
  TV_Top_TextCenter_Returning_{thisDayDisplay}:
    template:
      - name: TV_Top_TextCenter
        weight: 35
        text: "{prefix} {thisDayDisplayText}"
        color: "{rsfont_color}"
        back_color: "{rsback_color}"
        horizontal_align: {rs_horizontal_align}
        vertical_align: {rs_vertical_align}
        horizontal_offset: {rs_horizontal_offset}
        vertical_offset: {rs_vertical_offset}
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

        thisDayDisplay = thisDayTemp.strftime(dateFormat)
        thisDayDisplayText = thisDayTemp.strftime(dateFormatText)
        
        
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
    slug = libraryCleanPath
    traktListUrl = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists"
    traktListUrlPost = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + slug + ""
    traktListUrlPostShow = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + slug + "/items"
    trakt_list_privacy = vars.librarySetting(library, 'trakt_list_privacy')
    traktListData = f'''
{{
    "name": "Returning Soon {library}",
    "description": "Season premiers and returns within the next 30 days.",
    "privacy": "{trakt_list_privacy}",
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
    logging.info("Initializing " + library + " trakt list...")
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
print(f"Returning Soon operations complete. Run time {minutes:02}:{seconds:02}")
logging.info(f"Returning Soon operations complete. Run time {minutes:02}:{seconds:02}")

##########################
####    Extensions    ####
##########################
extension_start_time = time.time()

with open(settings, "r") as openSettings:
    extensionSettings = yaml.load(openSettings)

print(f'''
==================================================
Checking Extensions''')
logging.info("Checking Extensions")

for thisLibrary in extensionSettings['libraries']:

    try:
        extensions = extensionSettings['libraries'][thisLibrary]['extensions']

        for extension_item in extensions:
            
            if extension_item == 'in-history':
                print(f'''
==================================================''')
                print(f'''
Extension setting found. Running 'In History' on {thisLibrary}
''')
                logging.info(f"Extension setting found. Running 'In History' on {thisLibrary}")
                extension = vars.Extensions(thisLibrary).in_history.settings()
                save_folder = configPathPrefix + extension.save_folder
                if save_folder != '':
                    is_save_folder = os.path.exists(save_folder)
                    if not is_save_folder:
                        subfolder_display_path = f"config/{extension.save_folder}"
                        print(f"Sub-folder {subfolder_display_path} not found.")
                        print(f"Attempting to create.")
                        logging.info(f"Sub-folder {subfolder_display_path} not found.")
                        logging.info(f"Attempting to create.")
                        try:
                            os.makedirs(save_folder)
                            print(f"{subfolder_display_path} created successfully.")
                            logging.info(f"{subfolder_display_path} created successfully.")
                        except Exception as sf:
                            print(f"Exception: {str(sf)}")
                            logging.warning(f"Exception: {str(sf)}")
                range = extension.range
                me = vars.traktApi('me')
                slug = vars.cleanPath(extension.slug)
                collection_title = extension.collection_title
                in_history_meta = extension.meta
                try:
                    output_stream = StringIO()
                    yaml.dump(in_history_meta, output_stream)
                    in_history_meta_str = output_stream.getvalue()
                    output_stream.close()
                    in_history_meta_str = in_history_meta_str.replace("'","")
                    in_history_meta_str = in_history_meta_str.replace('{{range}}', range)
                    in_history_meta_str = in_history_meta_str.replace('{{Range}}', range.capitalize())
                except Exception as e:
                    print(f"An error occurred: {e}")


                inHistory = f"{configPathPrefix}{extension.save_folder}{slug}-in-history.yml"
                isInHistory = os.path.exists(inHistory)

                if not isInHistory:
                    try:
                        print(f"Creating {thisLibrary} 'In History' metadata file..")
                        logging.info(f"Creating {thisLibrary} 'In History' metadata file..")
                        writeInHistory = open(inHistory, "x")
                        writeInHistory.write(in_history_meta_str)
                        writeInHistory.close()
                        print(f"File created")
                        logging.info(f"File created")
                        file_location = f"config/{extension.save_folder}{slug}-in-history.yml"
                        print(f"{file_location}")
                        logging.info(f"{file_location}")
                    except Exception as e:
                        print(f"An error occurred: {e}")


                if isInHistory:
                    print(f"Updating {thisLibrary} 'In History' metadata file..")
                    logging.info(f"Updating {thisLibrary} 'In History' metadata file..")
                    file_location = f"config/{extension.save_folder}{slug}-in-history.yml"
                    print(f"{file_location}")
                    logging.info(f"{file_location}")
    
                    with open(inHistory, "r") as inHistory_file:
                        check_InHistory_Title = yaml.load(inHistory_file)
                        
                        
                        
                        for key, value in check_InHistory_Title['collections'].items():
                            if key != collection_title:
                                print(f'''Collection for {thisLibrary} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                logging.info(f'''Collection for {thisLibrary} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                library_id = vars.plexGet(thisLibrary)
                                old_collection_id = plex.collection.id(key, library_id)
                                delete_old_collection = plex.collection.delete(old_collection_id)
                                if delete_old_collection == True:
                                    print(f"Successfully removed old '{key}' collection.")
                                    logging.info(f"Successfully removed old '{key}' collection.")
                                if delete_old_collection == False:
                                    print(f"Could not remove deprecated '{key}' collection.")
                                    logging.warning(f"Could not remove deprecated '{key}' collection.")

                    with open(inHistory, "w") as write_inHistory:
                        write_inHistory.write(in_history_meta_str)
                        print('')
                        print(f'''{in_history_meta_str}''')
                        logging.info('')
                        logging.info(f'''{in_history_meta_str}''')


                month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
                
                
                if range == 'day':
                    today = datetime.now()
                    start_date = today
                    end_date = today

                if range == 'week':
                    today = datetime.now()
                    weekday_number = today.weekday()
                    first_weekday = today - timedelta(days=weekday_number)
                    days_till_last_weekday = 6 - weekday_number
                    last_weekday = today + timedelta(days=days_till_last_weekday)
                    start_date = first_weekday
                    end_date = last_weekday

                if range == 'month':
                    today = datetime.now()
                    first_day_of_month = today.replace(day=1)
                    if first_day_of_month.month == 12:
                        last_day_of_month = first_day_of_month.replace(day=31)
                    elif first_day_of_month.month < 12:
                        last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month + 1) - timedelta(days=1)
                    start_date = first_day_of_month
                    end_date = last_day_of_month
                
                description_identifier = plex.library.type(thisLibrary)
                if description_identifier == 'show':
                    description_type = 'Shows'
                    trakt_type = 'shows'
                if description_identifier == 'movie':
                    description_type = 'Movies'
                    trakt_type = 'movies'
                traktaccess = vars.traktApi('token')
                traktapi = vars.traktApi('client')
                traktHeaders = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + traktaccess + '',
                    'trakt-api-version': '2',
                    'trakt-api-key': '' + traktapi + ''
                    }
                traktListUrl = f"https://api.trakt.tv/users/{me}/lists"
                traktListUrlPost = f"https://api.trakt.tv/users/{me}/lists/in-history-{slug}"
                traktListUrlPostItems = f"https://api.trakt.tv/users/{me}/lists/in-history-{slug}/items"
                traktListData = f'''
{{
    "name": "In History {thisLibrary}",
    "description": "{description_type} released this {range} in history.",
    "privacy": "{extension.trakt_list_privacy}",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''
                print("Clearing " + thisLibrary + " trakt list...")
                logging.info("Clearing " + thisLibrary + " trakt list...")
                traktDeleteList = requests.delete(traktListUrlPost, headers=traktHeaders)
                if traktDeleteList.status_code == 201 or 200 or 204:
                    print("List cleared")
                time.sleep(1.25)
                traktMakeList = requests.post(traktListUrl, headers=traktHeaders, data=traktListData)
                if traktMakeList.status_code == 201 or 200 or 204:
                    print("Initialization successful.")
                time.sleep(1.25)
                traktListItems = '''
{'''
                traktListItems += f'''
    "{trakt_type}": [
        '''
                print(f"Filtering ==> This '{range}' in history")
                logging.info(f'Filtering ==> This {range} in history')
                if extension.starting != 0:
                    print(f"From {extension.starting} to {extension.ending}")
                    logging.info(f"From {extension.starting} to {extension.ending}")
                if extension.starting == 0:
                    print(f"From earliest to {extension.ending}")
                    logging.info(f"From earliest to {extension.ending}")
                if extension.increment != 1:
                    print(f"{extension.increment} year increment")
                    logging.info(f"{extension.increment} year increment")
                if extension.increment == 1:
                    print(f"Using all years")
                    logging.info(f"Using all years")
                print(f'''
''')
                library_List = plex.library.list(thisLibrary)
                library_List = sorted(library_List, key=lambda item: item.date)
                library_List_inRange = [item for item in library_List 
                if date_within_range(item.date, start_date, end_date)]
                for entry in library_List_inRange:
                    title_inRange = plex.item.info(entry.ratingKey)
                    title_inRange_month = month_names[title_inRange.date.month - 1]

                    if title_inRange.details.tmdb and title_inRange.details.imdb and title_inRange.details.tvdb == 'Null':
                        continue
                    
                    if (extension.starting <= title_inRange.date.year <= extension.ending 
                        and (extension.ending - title_inRange.date.year) % extension.increment == 0
                        and title_inRange.date.year != today.year):
                        print(f"Adding {title_inRange.title} ({title_inRange_month} {title_inRange.date.day}, {title_inRange.date.year})")
                        logging.info(f"Adding {title_inRange.title} ({title_inRange_month} {title_inRange.date.day}, {title_inRange.date.year})")
                        traktListItems += f'''
    {{
    "ids": {{'''
                
                        if title_inRange.details.tmdb != 'Null':
                            traktListItems += f'''
        "tmdb": "{title_inRange.details.tmdb}",'''
                        if title_inRange.details.tvdb != 'Null':
                            traktListItems += f'''
        "tvdb": "{title_inRange.details.tvdb}",'''
                        if title_inRange.details.imdb != 'Null':
                            traktListItems += f'''
        "imdb": "{title_inRange.details.imdb}",'''
                        
                        traktListItems = traktListItems.rstrip(",")
                    
                        traktListItems += f'''
            }}
    }},'''
        
        
                traktListItems = traktListItems.rstrip(",")
                traktListItems += '''
]
}
'''
                
                postItems = requests.post(traktListUrlPostItems, headers=traktHeaders, data=traktListItems)
                if postItems.status_code == 201:
                    print(f"Successfully posted This {range} In History items for {thisLibrary}")
                    logging.info(f"Successfully posted This {range} In History items for {thisLibrary}")

                    
    except KeyError:
        print(f"No extensions set for {thisLibrary}.")
        logging.info(f"No extensions set for {thisLibrary}.")
        continue
    except Exception as e:
        print(f"Exception Error: {str(e)}")


extension_end_time = time.time()
extension_elapsed_time = extension_end_time - extension_start_time
ext_minutes = int(extension_elapsed_time // 60)
ext_seconds = int(extension_elapsed_time % 60)
print(f"Extensions operations complete. Run time {ext_minutes:02}:{ext_seconds:02}")
logging.info(f"Extensions operations complete. Run time {ext_minutes:02}:{ext_seconds:02}")
total_elapsed_time = extension_end_time - start_time
total_minutes = int(total_elapsed_time // 60)
total_seconds = int(total_elapsed_time % 60)
print(f"All operations complete. Run time {total_minutes:02}:{total_seconds:02}")
logging.info(f"All operations complete. Run time {total_minutes:02}:{total_seconds:02}")
