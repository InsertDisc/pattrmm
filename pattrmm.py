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


# functions
def verify_or_create_folder(folder_path, folder_name_for_logging):
    """Function verifying if a folder exists and creating the folder if it doesn't."""

    folder_exists = os.path.exists(folder_path)
    if not folder_exists:
        print("Creating " + folder_name_for_logging + " folder...")
        os.makedirs(folder_path)
    else:
        print(folder_name_for_logging.capitalize() + " folder present...")


def verify_or_create_file(file_path, file_name_for_logging):
    """Function verifying if a file exists and creating the file if it doesn't."""

    file_exists = os.path.isfile(file_path)
    if not file_exists:
        print("Creating " + file_name_for_logging + " file...")
        create_file = open(file_path, "x")
        create_file.close()
    else:
        print(file_name_for_logging.capitalize() + " file present...")



print("Verifying files...")

# data folder for created files
verify_or_create_folder("data", "data")

# history folder for timestamps
verify_or_create_folder("./data/history", "stats")

# logs folder
verify_or_create_folder("data/logs", "logs")

# pattrmm log file
log_file = "data/logs/pattrmm.log"
verify_or_create_file(log_file, "log")

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

# preferences folder
verify_or_create_folder("preferences", "preferences")

# settings file for pattrmm
settings_file = "preferences/settings.yml"
# If settings file doesn't exist, create it
if not os.path.isfile(settings_file):
    print("Creating settings file..")
    create_settings_file = open(settings_file, "x")
    create_settings_file.write(
        '''
libraries:
  TV Shows:                          # Plex Libraries to read from. Can enter multiple libraries.
    trakt_list_privacy: private
    save_folder: "metadata/"
    overlay_save_folder: "overlays/"
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
    create_settings_file.close()
    print("Settings file created. Please configure preferences/settings.yml and rerun PATTRMM.")
    exit()
else:
    print("Settings file present.")


# Main variables file
vars_file = 'vars.py'
# Check for vars file and create if not present
vars_file_exists = os.path.exists(vars_file)
if not vars_file_exists:
    print("Creating vars module file..")
    create_vars_file = open(vars_file, "x")
    create_vars_file.write("""
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

class ExtendedLibraryList:
    def __init__(self, ratingKey, title, added, released, size):
        self.ratingKey = ratingKey
        self.title = title
        self.added = added
        self.released = released
        self.size = size

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
    
    @property
    def by_size(self):
        self.context = 'by_size'
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
                poster_url = f'"https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/This%20{self.range.capitalize()}%20in%20History.jpg"'
                self.meta = {}
                self.meta['collections'] = {}
                self.meta['collections'][self.collection_title] = {}
                self.meta['collections'][self.collection_title]['trakt_list'] = trakt_list_meta
                self.meta['collections'][self.collection_title]['visible_home'] = 'true'
                self.meta['collections'][self.collection_title]['visible_shared'] = 'true'
                self.meta['collections'][self.collection_title]['collection_order'] = 'custom'
                self.meta['collections'][self.collection_title]['sync_mode'] = 'sync'
                self.meta['collections'][self.collection_title]['url_poster'] = poster_url
                self.meta['collections'][self.collection_title].update(options)
                
            except Exception as e:
                return f"Error: {str(e)}"
            return self
                
        if self.context == 'by_size':
            settings = settings_path
            with open(settings) as sf:
                pref = yaml.load(sf)
            me = traktApi('me')
            slug = cleanPath(self.extension_library)
            self.slug = slug
            trakt_list_meta = f"https://trakt.tv/users/{me}/lists/sorted-by-size-{slug}"
            try:
                self.trakt_list_privacy = pref['libraries'][self.extension_library]['extensions']['by_size']['trakt_list_privacy']
            except KeyError:
                self.trakt_list_privacy = 'private'
            try:
                minimum = pref['libraries'][self.extension_library]['extensions']['by_size']['minimum']
                self.minimum = minimum
            except KeyError:
                self.minimum = 0

            try:
                maximum = pref['libraries'][self.extension_library]['extensions']['by_size']['maximum']
                self.maximum = maximum
            except KeyError:
                self.maximum = None

            try:
                self.save_folder = pref['libraries'][self.extension_library]['extensions']['by_size']['save_folder']
            except KeyError:
                self.save_folder = ''
            try:
                self.collection_title = pref['libraries'][self.extension_library]['extensions']['by_size']['collection_title']
            except KeyError:
                self.collection_title = 'Sorted by size'
            try:
                default_order_by = 'size.desc'
                order_by = pref['libraries'][self.extension_library]['extensions']['by_size']['order_by']
                possible_filters = ('size.desc', 'size.asc', 'title.desc', 'title.asc', 'added.asc', 'added.desc', 'released.desc', 'released.asc')
                possible_fields = ('size', 'title', 'added', 'released')
                if order_by in possible_filters:
                    self.order_by = order_by
                if order_by not in possible_filters:
                    if order_by in possible_fields:
                        invalid_order_by = order_by
                        if order_by == 'title':
                            order_by = order_by + '.asc'
                        else:
                            order_by = order_by + '.desc'
                    print(f'''Invalid order by setting "{invalid_order_by}".
                          Order by field '{invalid_order_by}' found. Using '{order_by}'.''')
                    logging.warning(f'''Invalid order by setting "{order_by}", falling back to default {default_order_by}''')
                    if order_by not in possible_fields:
                        print(f'''{order_by} is not a valid option. Using default.''')
                        self.order_by = default_order_by
            except KeyError:
                print(f'''No list order setting found. Using default '{default_order_by}'.''')
                logging.info(f'''No list order setting found. Using default '{default_order_by}'.''')
                self.order_by = default_order_by
            
            self.order_by_field, self.order_by_direction = self.order_by.split('.')
            if self.order_by_direction == 'desc':
                self.reverse = True
            if self.order_by_direction == 'asc':
                self.reverse = False

            try:
                try:
                    options = {
                    key: value
                    for key, value in pref['libraries'][self.extension_library]['extensions']['by_size']['meta'].items()
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
                
    def extended_list(self, library):
            try:
                # Replace with the correct section ID and library URL
                section_id = plexGet(library)  # Replace with the correct section ID
                library_url = f"{self.plex_url}/library/sections/{section_id}/all"
                library_url = re.sub("0//", "0/", library_url)
                headers = {"X-Plex-Token": self.plex_token,
                           "accept": "application/json"}
                response = requests.get(library_url, headers=headers)
                extended_library_list = []

                if response.status_code == 200:
                    data = response.json()
                    for item in data['MediaContainer']['Metadata']:
                        try:
                            title = item['title']
                            ratingKey = item['ratingKey']
                            released = item['originallyAvailableAt']
                            added_at_timestamp = item['addedAt']
                            added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
                            added_at = added_dt_object.strftime('%Y-%m-%d')
                            duration_ms = item["Media"][0]["duration"]
                            bitrate_kbps = item["Media"][0]["bitrate"]
                            file_size_gb = (duration_ms * bitrate_kbps) / (8 * 1000 * 1024 * 1024)
                            extended_library_list.append(ExtendedLibraryList(**{
                            'ratingKey': ratingKey,
                            'title': title,
                            'added': added_at,
                            'released': released,
                            'size': file_size_gb
                            }))
                        except KeyError:
                            print(f"{item['title']} has no 'Originally Available At' date. Ommitting title.")
                            continue
                    return extended_library_list
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

    def tmdb_id(self, ratingKey):
        # Attempt to retrieve TMDB ID from Plex
        plex_tmdb_id = self.get_tmdb_id_from_plex(ratingKey)
        
        if plex_tmdb_id is not None:
            return plex_tmdb_id
        
        # If not found in Plex, search TMDB
        if plex_tmdb_id == None:
            show_name = self.get_show_name(ratingKey)
            year = self.year(ratingKey)
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
            


    def get_tmdb_id_from_plex(self, ratingKey):
        try:
            show_details_url = f"{self.plex_url}/library/metadata/{ratingKey}"
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


    def get_show_name(self, ratingKey):
        try:
            show_details_url = f"{self.plex_url}/library/metadata/{ratingKey}"
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
        

    def year(self, ratingKey):
        try:
            # Get the originally available year from Plex
            show_details_url = f"{self.plex_url}/library/metadata/{ratingKey}"
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


    def episodes(self, ratingKey):
        try:
            # Retrieve a list of episodes for a show based on rating key
            episodes_url = f"{self.plex_url}/library/metadata/{ratingKey}/allLeaves"
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

            if value == 'overlay_save_folder':
                try:
                    entry = pref['libraries'][library]['overlay_save_folder']
                except KeyError:
                    entry = 'overlays/'

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
                    entry = 'top'

            if value == 'rs_horizontal_align':
                try:
                    entry = pref['horizontal_align']
                except KeyError:
                    entry = 'center'

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
                    entry = 'center'

            if value == 'ovUpcoming_vertical_align':
                try:
                    entry = pref['extra_overlays']['upcoming']['vertical_align']
                except KeyError:
                    entry = 'top'

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
                    entry = 'center'

            if value == 'ovNew_vertical_align':
                try:
                    entry = pref['extra_overlays']['new']['vertical_align']
                except KeyError:
                    entry = 'top'

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
                    entry = 'center'

            if value == 'ovReturning_vertical_align':
                try:
                    entry = pref['extra_overlays']['returning']['vertical_align']
                except KeyError:
                    entry = 'top'

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
                    entry = 'center'

            if value == 'ovAiring_vertical_align':
                try:
                    entry = pref['extra_overlays']['airing']['vertical_align']
                except KeyError:
                    entry = 'top'

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
                    entry = 'center'

            if value == 'ovEnded_vertical_align':
                try:
                    entry = pref['extra_overlays']['ended']['vertical_align']
                except KeyError:
                    entry = 'top'

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
                    entry = 'center'

            if value == 'ovCanceled_vertical_align':
                try:
                    entry = pref['extra_overlays']['canceled']['vertical_align']
                except KeyError:
                    entry = 'top'

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


""")
    create_vars_file.close()
else:
    print("Vars module file present.")


# Check if this is a Docker Build to format PMM config folder directory
is_docker = os.environ.get('PATTRMM_DOCKER', "False")

if is_docker == "True":
    pmm_config_path_prefix = "./config/"
else:
    pmm_config_path_prefix = "../"


# Plex Meta Manager config file path
pmm_config_folder = pmm_config_path_prefix + 'config.yml'

# Check if PMM config file can be found. If not, inform and exit.
pmm_config_folder_exists = os.path.exists(pmm_config_folder)
if not pmm_config_folder_exists:
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

# overlay folder path
pmm_overlay_folder = pmm_config_path_prefix + 'overlays'

# If PMM overlay folder cannot be found, stop
pmm_overlay_folder_exits = os.path.exists(pmm_overlay_folder)
if not pmm_overlay_folder_exits:
    print("Plex Meta Manager Overlay folder could not be located.")
    print("Please ensure PATTRMM is in a subfolder of the PMM config directory.")
    exit()





##############################################
# Start sequencing through defined Libraries #
read_settings_file = open(settings_file, "r")
loaded_settings_yaml = yaml.load(read_settings_file)
for library in loaded_settings_yaml['libraries']:

    if plex.library.type(library) != 'show':
        print(f"{library} is not compatible with the 'Returning Soon' method. Skipping.")
        continue
    
    if vars.librarySetting(library, 'returning-soon') is False:
        print(f"'Returning Soon' disabled for {library}. Skipping.")
        continue

    library_clean_path = vars.cleanPath(library)
    
    # check for days_ahead assignment
    days_ahead = vars.librarySetting(library, 'days')

    # Set stats file
    stats_file = "./data/history/" + library_clean_path + "-history.json"
    stats_file_exists = os.path.exists(stats_file)
    if not stats_file_exists:
        create_stats_file = open(stats_file, "x")
        create_stats_file.write(f'''
{{
    "lastRefresh": "{today}"
}}''')
        create_stats_file.close()

    read_stats_file = open(stats_file, "r")
    loaded_stats_json = json.load(read_stats_file)
    read_stats_file.close()


    # Check for last run of this library
    refresh_days = vars.librarySetting(library, 'refresh')
    refresh_history = vars.history(library_clean_path, 'lastFull')
    refresh_history = datetime.strptime(refresh_history, "%Y-%m-%d")
    delay = refresh_history + timedelta(days=refresh_days)
    if today >= delay.date():
        should_be_refreshed = True
    else:    
        should_be_refreshed = False

    # keys file for ratingKey and tmdb pairs
    keys_file = "./data/" + library_clean_path + "-keys.json"

    # cache file for tmdb details
    cache_file = "./data/" + library_clean_path + "-tmdb-cache.json"

    # returning soon metadata save folder
    rs_metadata_folder = vars.librarySetting(library, 'save_folder')
    pmm_rs_metadata_folder = pmm_config_path_prefix + rs_metadata_folder
    if pmm_rs_metadata_folder != '':
        pmm_rs_metadata_folder_exists = os.path.exists(pmm_rs_metadata_folder)
        if not pmm_rs_metadata_folder_exists:
            rs_metadata_subfolder_path = f"config/{rs_metadata_folder}"
            print(f"Sub-folder {rs_metadata_subfolder_path} not found.")
            print(f"Attempting to create.")
            logging.info(f"Sub-folder {rs_metadata_subfolder_path} not found.")
            logging.info(f"Attempting to create.")
            try:
                os.makedirs(pmm_rs_metadata_folder)
                print(f"{rs_metadata_subfolder_path} created successfully.")
                logging.info(f"{rs_metadata_subfolder_path} created successfully.")
            except Exception as sf:
                print(f"Exception: {str(sf)}")
                logging.warning(f"Exception: {str(sf)}")

    # returning-soon metadata file for collection
    rs_metadata_file = pmm_rs_metadata_folder + library_clean_path + "-returning-soon-metadata.yml"

    # returning soon overlay save folder
    rs_overlay_folder = vars.librarySetting(library, 'overlay_save_folder')
    pmm_rs_overlay_folder = pmm_config_path_prefix + rs_overlay_folder
    if pmm_rs_overlay_folder != '':
        pmm_rs_overlay_folder_exists = os.path.exists(pmm_rs_overlay_folder)
        if not pmm_rs_overlay_folder_exists:
            rs_overlay_subfolder_path = f"config/{rs_overlay_folder}"
            print(f"Sub-folder {rs_overlay_subfolder_path} not found.")
            print(f"Attempting to create.")
            logging.info(f"Sub-folder {rs_overlay_subfolder_path} not found.")
            logging.info(f"Attempting to create.")
            try:
                os.makedirs(rs_overlay_subfolder_path)
                print(f"{rs_overlay_subfolder_path} created successfully.")
                logging.info(f"{rs_overlay_subfolder_path} created successfully.")
            except Exception as sf:
                print(f"Exception: {str(sf)}")
                logging.warning(f"Exception: {str(sf)}")
    
    # generated overlay file path
    rs_overlay_file = pmm_rs_overlay_folder + library_clean_path + "-returning-soon-overlay.yml"
    
    # overlay template path
    rs_overlay_template_file = "./preferences/" + library_clean_path + "-returning-soon-template.yml"
    

    # Just some information
    print("Checking folder structure for " + library + ".")
    logging.info('Checking folder structure for ' + library + '.')

    print("Checking " + library + " files...")
    logging.info("Checking " + library + " files...")


    # If keys file doesn't exist, create it
    keys_file_exists = os.path.exists(keys_file)
    if not keys_file_exists:
        print("Creating " + library + " keys file..")
        logging.info("Creating " + library + " keys file..")
        create_keys_file = open(keys_file, "x")
        create_keys_file.close()
        is_first_run = True
    else:
        print(library + " keys file found.")
        logging.info(library + " keys file found.")
        print("Checking " + library + " data...")
        logging.info("Checking " + library + " data...")
        if os.stat(keys_file).st_size == 0:
            is_first_run = True
            print(library + " keys file is empty. Initiating first run.")
            logging.info(library + " keys file is empty. Initiating first run.")
        if os.stat(keys_file).st_size != 0:

            ## Has the refresh status delay passed for this library ##
            if should_be_refreshed:
                is_first_run = True
                print("Keys data has expired. Rebuilding...")
            else:
                print("Keys data refresh delay for " + library + " not yet met.")
                logging.info("Keys data refresh delay for " + library + " not yet met. Skipping status renewal.")
                is_first_run = False
            

    # If cache file doesn't exist, create it
    cache_file_exists = os.path.exists(cache_file)
    if not cache_file_exists:
        print("Creating " + library + " cache file..")
        logging.info("Creating " + library + " cache file..")
        creata_cache_file = open(cache_file, "x")
        creata_cache_file.write('tmdbDataCache')
        creata_cache_file.close()
    else:
        print(library + " cache file present.")
        logging.info(library + " cache file present.")

    # If returning-soon metadata file doesn't exist, create it
    rs_metadata_file_exists = os.path.exists(rs_metadata_file)
    if not rs_metadata_file_exists:
        print("Creating " + library + " metadata collection file..")
        logging.info("Creating " + library + " metadata collection file..")
        create_rs_metadata_file = open(rs_metadata_file, "x")
        trakt_user_name = vars.traktApi('me')
        create_rs_metadata_file.write(
            f'''
collections:
  Returning Soon:
    trakt_list: https://trakt.tv/users/{trakt_user_name}/lists/returning-soon-{library_clean_path}
    url_poster: https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/Returning%20Soon.jpg
    collection_order: custom
    visible_home: true
    visible_shared: true
    sync_mode: sync
    '''
        )
        create_rs_metadata_file.close()
    else:
        print(library + " metadata file present.")
        logging.info(library + " metadata file present.")

    
    # If overlay template doesn't exist, create it
    rs_overlay_template_file_exists = os.path.exists(rs_overlay_template_file)
    if not rs_overlay_template_file_exists:
        print("Generating " + library + " template file..")
        logging.info("Generating " + library + " template file..")
        create_rs_overlay_template_file = open(rs_overlay_template_file, "x")
        create_rs_overlay_template_file.write(
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
        create_rs_overlay_template_file.close()
    else:
        print(library + " template file found.")
        logging.info(library + " template file found.")

    
    # If overlay file doesn't exist, create it
    rs_overlay_file_exists = os.path.exists(rs_overlay_file)
    if not rs_overlay_file_exists:
        print("Creating empty " + library + " Overlay file..")
        logging.info("Creating empty " + library + " Overlay file..")
        create_rs_overlay_file = open(rs_overlay_file, "x")
        create_rs_overlay_file.write('')
        create_rs_overlay_file.close()
    else:
        print(library + " overlay file present.")
        logging.info(library + " overlay file present.")

    # define classes and definitions
    def sorted_list(list, field):
        return sorted(list, key=lambda k: k[field], reverse=False)

    def pretty_json(value):
        return json.dumps(value, indent=4, sort_keys=False)

    def dict_to_json(value):
        return json.dumps([ob.__dict__ for ob in value], indent=4, sort_keys=False)

    # function to count a list #
    def get_count(list):
        count = 0
        for element in list:
            count += 1
        return str(count)

    # strip date to just year #
    def get_year(date):
        return datetime.strptime(date, '%Y-%m-%d').year

    # strip (words) and url format plex title #
    class PlexItem:
        def __init__(self, title, year, ratingKey):
            self.title = re.sub("\s\(.*?\)","", title)
            if year != "null":
                self.year = datetime.strptime(year, '%Y-%m-%d').year
            else:
                self.year = year
            self.ratingKey = ratingKey

    class TMDBSearch:
        def __init__(self, title, ratingKey, tmdb_id, status):
            self.title = title
            self.ratingKey = ratingKey
            self.tmdb_id = tmdb_id
            self.status = status

    class TMDBDetails:
        def __init__(self, id, title, first_air_date, last_air_date, next_air_date, status, popularity):
            self.id = id
            self.title = title
            self.first_air_date = first_air_date
            self.last_air_date = last_air_date
            self.next_air_date = next_air_date
            self.status = status
            self.popularity = popularity

    # declare lists
    search_list = []
    key_pairs_list = []
    status_key_pairs_list = []
    tmdb_details_list = []



    # create access variables 
    #library = vars.setting('library')
    plex_call = vars.plexApi('url') + '/library/sections/' + vars.plexGet(library) + '/all'
    plex_url = re.sub("//lib", "/lib", plex_call)
    plex_headers = {
        "accept": "application/json"
    }
    plex_token = {'X-Plex-Token': '' + vars.plexApi('token') + ''}


    # gather list of entries in plex
    print("Gathering Plex entries...")
    logging.info("Gathering Plex entries...")
    

    loaded_plex_series_json = json.loads(pretty_json(requests.get(plex_url, headers=plex_headers, params=plex_token).json()))
    plex_number_of_series = get_count(loaded_plex_series_json['MediaContainer']['Metadata'])
    missing_data_counter = 1
    for plex_series_entry in loaded_plex_series_json['MediaContainer']['Metadata']:
        try:
            search_list.append(PlexItem(plex_series_entry['title'],plex_series_entry['originallyAvailableAt'], plex_series_entry['ratingKey']))
        except KeyError:
            print("")
            print("Caution " + plex_series_entry['title'] + " does not have an originally available at date. May not be able to match.")
            logging.warning("Caution " + plex_series_entry['title'] + " does not have an originally available at date. May not be able to match.")
            search_list.append(PlexItem(plex_series_entry['title'],"null", plex_series_entry['ratingKey']))
        missing_data_counter += 1
        
    print("Found " + get_count(loaded_plex_series_json['MediaContainer']['Metadata']) + " entries...")

    # search for tmdb id of each entry, will update to use stored keys to reduce unnecessary searches
    refresh_search_list = search_list
    search_list = json.loads(dict_to_json(search_list))

    
    # No need to run a full lookup on subsequent runs
    if not is_first_run:
        read_keys_file = open(keys_file, "r")
        loaded_keys_json = json.load(read_keys_file)
        read_keys_file.close()

        cleaned_keys_list = []
        compare_search_json = dict_to_json(refresh_search_list)

        # Find if any entries were removed from Plex and remove from Key data
        for existing_key in loaded_keys_json[:]:
            if (existing_key['ratingKey'] not in compare_search_json):
                loaded_keys_json.remove(existing_key)
                print("")
                print(existing_key['title'] + " was no longer found in Plex. Removing from Keys.")
                time.sleep(.6)
        for cleaned_key in loaded_keys_json:
            cleaned_keys_list.append(TMDBSearch(cleaned_key['title'], cleaned_key['ratingKey'], cleaned_key['tmdb_id'], cleaned_key['status']))

        updated_keys_json = dict_to_json(cleaned_keys_list)


        # Check for existing data for remaining Plex entries.
        refresh_search_counter = 0
        new_search_list = search_list
        print("")
        for plex_item in new_search_list[:]:
            if (plex_item['ratingKey'] in updated_keys_json):
                new_search_list.remove(plex_item)
                #print("Key data exists for " + plex_item['title'] + ". Removed from search list")
                refresh_search_counter += 1
                
        # Output how many entries have existing data                   
        print("Found existing data for " + str(refresh_search_counter) + " titles. Removing from search list.")
        logging.info("Found existing data for " + str(refresh_search_counter) + " titles. Removing from search list.")
        print("")

        # Search for new and missing data
        for remaining_plex_item in new_search_list:
            print("No key entry found for " + remaining_plex_item['title'] + ". Adding to search queue...")
            logging.info("No key entry found for " + remaining_plex_item['title'] + ". Adding to search queue...")
        if len(new_search_list) > 0:
            found_series_to_update = True
            search_list = new_search_list
        else:
            found_series_to_update = False
            print("Nothing new to search for. Proceeding...")
            logging.info("Nothing new to search for. Proceeding...")

        # Hold list to append searches
        status_key_pairs_list = cleaned_keys_list



    # Start searching for missing data. Look for TMDB ID first.
    missing_data_counter = 1
    for query_plex_item in search_list:
        # display search progress
        print("\rSearching... " + "(" + str(missing_data_counter) + "/" + get_count(search_list) + ")", end="")
        ratingKey = query_plex_item['ratingKey']
        search_year = True
        if query_plex_item['year'] == "null":
            search_year = False
        id = plex.show.tmdb_id(ratingKey)
        if id != "null" and search_year:
            key_pairs_list.append(TMDBSearch(query_plex_item['title'], query_plex_item['ratingKey'], id, "null"))
                    # info for found match
            print(" Found ID ==> " + str(id) + " for " + '"' + query_plex_item['title'] + '"')
            logging.info(" Found ID ==> " + str(id) + " for " + '"' + query_plex_item['title'] + '"')
            # end adding to the list after the first match is found, else duplicate entries occur
                
        # increment progress after a successful match
        missing_data_counter += 1
    
    # Get details using the TMDB IDs.
    for key_pair_item in json.loads(dict_to_json(key_pairs_list)):

        tmdb_url = "https://api.themoviedb.org/3/tv/" + str(key_pair_item['tmdb_id'])
        tmdb_headers = {
        "accept": "application/json"
        }
        tmdb_parameters = {
            "language": "en-US", "api_key": vars.tmdbApi('token')
        }

        tmdb_request = requests.get(tmdb_url, headers=tmdb_headers, params=tmdb_parameters)
        
        # If the page does not return successful
        if tmdb_request.status_code != 200:
            print("There was a problem accessing the resource for TMDB ID " + str(key_pair_item['tmdb_id']))


            if tmdb_request.status_code == 34:
                print("This ID has been removed from TMDB, or is no longer accessible.")
                print("Try refreshing the metadata for " + key_pair_item['title'])
            
            continue

        # If the page returns successful, get details.    
        tmdb_series_entry = json.loads(pretty_json(tmdb_request.json()))

        print("Found details for " + tmdb_series_entry['name'] + " ( " + str(tmdb_series_entry['id']) + " )")
        logging.info("Found details for " + tmdb_series_entry['name'] + " ( " + str(tmdb_series_entry['id']) + " )")

        if tmdb_series_entry['last_air_date'] is not None and tmdb_series_entry['last_air_date'] != "" :
            last_air_date = tmdb_series_entry['last_air_date']
        else:
            last_air_date = "null"

        if tmdb_series_entry['next_episode_to_air'] is not None and tmdb_series_entry['next_episode_to_air']['air_date'] is not None:
            next_air_date = tmdb_series_entry['next_episode_to_air']['air_date']
        else:
            next_air_date = "null"

        if tmdb_series_entry['first_air_date'] is not None and tmdb_series_entry['first_air_date'] != "":
            first_air_date = tmdb_series_entry['first_air_date']
        else:
            first_air_date = "null"

        status_key_pairs_list.append(
            TMDBSearch(
                key_pair_item['title'],
                key_pair_item['ratingKey'],
                key_pair_item['tmdb_id'],
                tmdb_series_entry['status']
            )
        )

        if is_first_run:
            if tmdb_series_entry['status'] == "Returning Series":
                tmdb_details_list.append(
                    TMDBDetails(
                        tmdb_series_entry['id'],
                        tmdb_series_entry['name'],
                        first_air_date,
                        last_air_date,
                        next_air_date,
                        tmdb_series_entry['status'],
                        tmdb_series_entry['popularity']
                    )
                )


    new_keys_file_content = dict_to_json(status_key_pairs_list)
    write_keys_file = open(keys_file, "w")
    write_keys_file.write(new_keys_file_content)
    write_keys_file.close()
    if is_first_run:
        print(library + " Keys updated...")
        logging.info(library + " Keys updated...")
    else:
        if found_series_to_update:
            print(library + " Keys updated...")
            logging.info(library + " Keys updated...")
            print("Updating data for Returning " + library + ".")
            logging.info("Updating data for Returning " + library + ".")

        series_to_update_list = []
        read_keys_file = open(keys_file, "r")
        loaded_keys_json = json.load(read_keys_file)
        
        for update_key in loaded_keys_json:

            if update_key['status'] != "Returning Series":
                series_to_update_list.append(TMDBSearch(update_key['title'], update_key['ratingKey'], update_key['tmdb_id'], update_key['status']))
            else:
                tmdb_url = "https://api.themoviedb.org/3/tv/" + str(update_key['tmdb_id'])
                tmdb_headers = {
                    "accept": "application/json"
                }
                tmdb_parameters = {
                    "language": "en-US", "api_key": vars.tmdbApi('token')
                }

                tmdb_sub_request = requests.get(tmdb_url,headers=tmdb_headers, params=tmdb_parameters)
                if tmdb_sub_request.status_code != 200:
                    print("There was a problem accessing the resource for TMDB ID " + str(update_key['tmdb_id']))
                    print(update_key['title'] + '( ' + str(update_key['tmdb_id']) + ' ) may have been removed.')
                    continue
                if tmdb_sub_request.status_code == 34:
                    print("This ID has been removed from TMDB, or is no longer accessible.")
                    print("Try refreshing the metadata for " + update_key['title'])
                    continue
                
                tmdb_series_entry = json.loads(pretty_json(tmdb_sub_request.json()))

                print("Refreshing data for " + tmdb_series_entry['name'] + " ( " + str(tmdb_series_entry['id']) + " )")

                if tmdb_series_entry['last_air_date'] is not None and tmdb_series_entry['last_air_date'] != "" :
                    last_air_date = tmdb_series_entry['last_air_date']
                else:
                    last_air_date = "null"

                if tmdb_series_entry['next_episode_to_air'] is not None and tmdb_series_entry['next_episode_to_air']['air_date'] != None:
                    next_air_date = tmdb_series_entry['next_episode_to_air']['air_date']
                else:
                    next_air_date = "null"

                if tmdb_series_entry['first_air_date'] is not None and tmdb_series_entry['first_air_date'] != "":
                    first_air_date = tmdb_series_entry['first_air_date']
                else:
                    first_air_date = "null"
                
                series_to_update_list.append(TMDBSearch(update_key['title'], update_key['ratingKey'], update_key['tmdb_id'], tmdb_series_entry['status']))
                if tmdb_series_entry['status'] == "Returning Series":
                    tmdb_details_list.append(
                        TMDBDetails(
                            tmdb_series_entry['id'],
                            tmdb_series_entry['name'],
                            first_air_date,
                            last_air_date,
                            next_air_date,
                            tmdb_series_entry['status'],
                            tmdb_series_entry['popularity']
                        )
                    )

        updated_keys_file_content = dict_to_json(series_to_update_list)
        write_updates_to_keys_file = open(keys_file, "w")
        write_updates_to_keys_file.write(updated_keys_file_content)
        write_updates_to_keys_file.close()

    # update history timestamp
    if should_be_refreshed:
        try:
            # Read the JSON file
            with open(stats_file, 'r') as read_stats_file_to_update:
                loaded_stats_json = json.load(read_stats_file_to_update)

            # Update the 'lastRefresh' field with the current date
            now = date.today().strftime("%Y-%m-%d")
            loaded_stats_json['lastRefresh'] = now

            # Write the updated data back to the JSON file
            with open(stats_file, 'w') as write_updated_data_to_stats_file:
                json.dump(loaded_stats_json, write_updated_data_to_stats_file, indent=4)

            print("Timestamp updated successfully.")

        except Exception as e:
            print(f"An error occurred updating the timestamp: {str(e)}")


    next_air_dates_list = pretty_json(sorted_list(json.loads(dict_to_json(tmdb_details_list)), 'next_air_date'))


    ## write tmdb details to file ##
    write_tmdb_details_to_cache_file = open(cache_file, "w")
    write_tmdb_details_to_cache_file.write(next_air_dates_list)
    write_tmdb_details_to_cache_file.close()
    print("\033[K" + library + " TMDB data updated...")
    logging.info(library + " TMDB data updated...")


    # write Template to Overlay file
    print("Writing " + library + " Overlay Template to Returning Soon " + library + " overlay file.")
    logging.info("Writing " + library + " Overlay Template to Returning Soon " + library + " overlay file.")

    with open(rs_overlay_template_file) as read_rs_overlay_template_file:
        loaded_rs_overlay_template_yaml = yaml.load(read_rs_overlay_template_file)
        write_rs_overlay_file = open(rs_overlay_file, "w")
        yaml.dump(loaded_rs_overlay_template_yaml, write_rs_overlay_file)
        print(library + " template applied.")


    # Generate Overlay body
    # define date ranges
    day_counter = 1
    last_air_date = date.today() - timedelta(days=45)
    last_episode_aired = last_air_date.strftime("%m/%d/%Y")
    next_air_date = date.today() + timedelta(days=int(days_ahead))
    this_day_temporary = date.today() + timedelta(days=int(day_counter))
    this_day = this_day_temporary.strftime("%m/%d/%Y")

    try:
        date_style = vars.setting('dateStyle')
    except:
        date_style = 1

    try:
        date_delimiter = vars.setting('delimiter')
        allowed_delimiter_symbols = ['/', '-', '.', '_']
        if date_delimiter not in allowed_delimiter_symbols:
            date_delimiter = "/"
    except:
        date_delimiter = "/"

    
    if vars.setting('zeros'):
        day_format_code = "%d"
        month_format_code = "%m"
    else:
        if platform.system() == "Windows":
            month_format_code = "%#m"
            day_format_code = "%#d"
            
        if platform.system() == "Linux" or platform.system() == "Darwin":
            month_format_code = "%-m"
            day_format_code = "%-d"

    if date_style == 1:
        month_day_format = "%m/%d"
        month_day_format_for_text = month_format_code + date_delimiter + day_format_code
        
    if date_style == 2:
        month_day_format = "%d/%m"
        month_day_format_for_text = day_format_code + date_delimiter + month_format_code
        

    if vars.setting('year'):
        year_format_code = "%Y"
        date_format = month_day_format + "/" + year_format_code
        date_format_for_text = month_day_format_for_text + date_delimiter + year_format_code
    else:
        date_format = month_day_format + "/%Y"
        date_format_for_text = month_day_format_for_text
    
    this_day_display = this_day_temporary.strftime(date_format)
    this_day_display_for_text = this_day_temporary.strftime(date_format_for_text)
            

    prefix_text = vars.setting('prefix')

    print("Generating " + library + " overlay body.")
    logging.info("Generating " + library + " overlay body.")

    overlay_body = '''

overlays:
    '''


    if vars.setting('ovUpcoming'):
        logging.info('"Upcoming" Overlay enabled, generating body...')
        upcoming_text = vars.setting('ovUpcomingText')
        upcoming_font_color = vars.setting('ovUpcomingFontColor')
        upcoming_color = vars.setting('ovUpcomingColor')
        upcoming_horizontal_align = vars.setting('ovUpcoming_horizontal_align')
        upcoming_vertical_align = vars.setting('ovUpcoming_vertical_align')
        upcoming_horizontal_offset = vars.setting('ovUpcoming_horizontal_offset')
        upcoming_vertical_offset = vars.setting('ovUpcoming_vertical_offset')

        overlay_upcoming = f'''
  # Upcoming
  TV_Top_TextCenter_Upcoming:
    template:
      - name: TV_Top_TextCenter
        weight: 90
        text: "{upcoming_text}"
        color: "{upcoming_font_color}"
        back_color: "{upcoming_color}"
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
        overlay_body = overlay_body + overlay_upcoming



    if vars.setting('ovNew'):
        logging.info('"New" Overlay enabled, generating body...')
        new_text = vars.setting('ovNewText')
        new_font_color = vars.setting('ovNewFontColor')
        new_color = vars.setting('ovNewColor')
        new_horizontal_align = vars.setting('ovNew_horizontal_align')
        new_vertical_align = vars.setting('ovNew_vertical_align')
        new_horizontal_offset = vars.setting('ovNew_horizontal_offset')
        new_vertical_offset = vars.setting('ovNew_vertical_offset')

        overlay_new = f'''
  # New
  TV_Top_TextCenter_New:
    template:
      - name: TV_Top_TextCenter
        weight: 60
        text: "{new_text}"
        color: "{new_font_color}"
        back_color: "{new_color}"
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
        overlay_body = overlay_body + overlay_new



    if vars.setting('ovAiring'):
        airing_today = date.today()
        airing_today_formatted = airing_today.strftime("%m/%d/%Y")
        considered_airing = date.today() - timedelta(days=15)
        considered_airing_formatted = considered_airing.strftime("%m/%d/%Y")

        logging.info('"Airing" Overlay enabled, generating...')
        airing_text = vars.setting('ovAiringText')
        airing_font_color = vars.setting('ovAiringFontColor')
        airing_color = vars.setting('ovAiringColor')
        airing_horizontal_align = vars.setting('ovAiring_horizontal_align')
        airing_vertical_align = vars.setting('ovAiring_vertical_align')
        airing_horizontal_offset = vars.setting('ovAiring_horizontal_offset')
        airing_vertical_offset = vars.setting('ovAiring_vertical_offset')

        overlay_airing = f'''
  # Airing
  TV_Top_TextCenter_Airing:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "{airing_text}"
        color: "{airing_font_color}"
        back_color: "{airing_color}"
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
      last_episode_aired.after: {considered_airing_formatted}

  # Airing Today
  TV_Top_TextCenter_Airing_Today:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "{airing_text}"
        color: "{airing_font_color}"
        back_color: "{airing_color}"
        horizontal_align: {airing_horizontal_align}
        vertical_align: {airing_vertical_align}
        horizontal_offset: {airing_horizontal_offset}
        vertical_offset: {airing_vertical_offset}
    tmdb_discover:
      air_date.gte: {airing_today_formatted}
      air_date.lte: {airing_today_formatted}
      with_status: 0
      limit: 500
'''
        overlay_body = overlay_body + overlay_airing


    if vars.setting('ovEnded'):
        logging.info('"Ended" Overlay enabled, generating body...')
        ended_text = vars.setting('ovEndedText')
        ended_font_color = vars.setting('ovEndedFontColor')
        ended_color = vars.setting('ovEndedColor')
        ended_horizontal_align = vars.setting('ovEnded_horizontal_align')
        ended_vertical_align = vars.setting('ovEnded_vertical_align')
        ended_horizontal_offset = vars.setting('ovEnded_horizontal_offset')
        ended_vertical_offset = vars.setting('ovEnded_vertical_offset')
        
        overlay_ended = f'''
  # Ended
  TV_Top_TextCenter_Ended:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{ended_text}"
        color: "{ended_font_color}"
        back_color: "{ended_color}"
        horizontal_align: {ended_horizontal_align}
        vertical_align: {ended_vertical_align}
        horizontal_offset: {ended_horizontal_offset}
        vertical_offset: {ended_vertical_offset}
    plex_all: true
    filters:
      tmdb_status:
        - ended
'''
        overlay_body = overlay_body + overlay_ended


    if vars.setting('ovCanceled'):
        logging.info('"Canceled" Overlay enabled, generating body...')
        canceled_text = vars.setting('ovCanceledText')
        canceled_font_color = vars.setting('ovCanceledFontColor')
        canceled_color = vars.setting('ovCanceledColor')
        canceled_horizontal_align = vars.setting('ovCanceled_horizontal_align')
        canceled_vertical_align = vars.setting('ovCanceled_vertical_align')
        canceled_horizontal_offset = vars.setting('ovCanceled_horizontal_offset')
        canceled_vertical_offset = vars.setting('ovCanceled_vertical_offset')
        
        overlay_canceled = f'''
  # Canceled
  TV_Top_TextCenter_Canceled:
    template:
      - name: TV_Top_TextCenter
        weight: 20
        text: "{canceled_text}"
        color: "{canceled_font_color}"
        back_color: "{canceled_color}"
        horizontal_align: {canceled_horizontal_align}
        vertical_align: {canceled_vertical_align}
        horizontal_offset: {canceled_horizontal_offset}
        vertical_offset: {canceled_vertical_offset}
    plex_all: true
    filters:
      tmdb_status:
        - canceled
'''
        overlay_body = overlay_body + overlay_canceled


    if vars.setting('ovReturning'):
        logging.info('"Returning" Overlay enabled, generating body...')
        returning_text = vars.setting('ovReturningText')
        returning_font_color = vars.setting('ovReturningFontColor')
        returning_color = vars.setting('ovReturningColor')
        returning_horizontal_align = vars.setting('ovReturning_horizontal_align')
        returning_vertical_align = vars.setting('ovReturning_vertical_align')
        returning_horizontal_offset = vars.setting('ovReturning_horizontal_offset')
        returning_vertical_offset = vars.setting('ovReturning_vertical_offset')

        overlay_returning = f'''
  # Returning
  TV_Top_TextCenter_Returning:
    template:
      - name: TV_Top_TextCenter
        weight: 30
        text: "{returning_text}"
        color: "{returning_font_color}"
        back_color: "{returning_color}"
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
        overlay_body = overlay_body + overlay_returning


    rs_font_color = vars.setting('rsfont_color')
    rs_color = vars.setting('rsback_color')
    rs_horizontal_align = vars.setting('rs_horizontal_align')
    rs_vertical_align = vars.setting('rs_vertical_align')
    rs_horizontal_offset = vars.setting('rs_horizontal_offset')
    rs_vertical_offset = vars.setting('rs_vertical_offset')

    while this_day_temporary < next_air_date:
        overlay_rs_temporary = f'''
# RETURNING {this_day_display}
  TV_Top_TextCenter_Returning_{this_day_display}:
    template:
      - name: TV_Top_TextCenter
        weight: 35
        text: "{prefix_text} {this_day_display_for_text}"
        color: "{rs_font_color}"
        back_color: "{rs_color}"
        horizontal_align: {rs_horizontal_align}
        vertical_align: {rs_vertical_align}
        horizontal_offset: {rs_horizontal_offset}
        vertical_offset: {rs_vertical_offset}
    tmdb_discover:
      air_date.gte: {this_day}
      air_date.lte: {this_day}
      with_status: 0
      limit: 500
    filters:
      last_episode_aired.before: {last_episode_aired}
'''
        day_counter += 1
        this_day_temporary = date.today() + timedelta(days=int(day_counter))
        this_day = this_day_temporary.strftime("%m/%d/%Y")

        this_day_display = this_day_temporary.strftime(date_format)
        this_day_display_for_text = this_day_temporary.strftime(date_format_for_text)
        
        overlay_body = overlay_body + overlay_rs_temporary


    
    print(library + " overlay body generated. Writing to file.")
    logging.info(library + " overlay body generated. Writing to file.")

    # Write the rest of the overlay
    write_body_to_overlay_file = open(rs_overlay_file, "a")
    yaml.dump(yaml.load(overlay_body), write_body_to_overlay_file)
    write_body_to_overlay_file.close()
    print("Overlay body appended to " + library + "-returning-soon-overlay.")
    logging.info("Overlay body appended to " + library + "-returning-soon-overlay.")

    # use keys file to gather show details
    print("Reading " + library + " cache file...")
    logging.info("Reading " + library + " cache file...")
    read_cache_file = open(cache_file, "r")
    loaded_cache_json = json.load(read_cache_file)
    read_cache_file.close()

    # this is for the trakt list
    print("Filtering " + library + " data...")
    logging.info("Filtering " + library + " data...")
    series_rs_list = filter(
        lambda x: (
            x['status'] == "Returning Series" and
            x['next_air_date'] != "null" and
            x['next_air_date'] < str(next_air_date) and
            x['next_air_date'] > str(today) and
            x['last_air_date'] < str(last_air_date)),
            loaded_cache_json)
    print("Sorting " + library + "...")
    logging.info("Sorting " + library + "...")
    series_rs_sorted_list = sorted_list(series_rs_list, 'next_air_date')

    trakt_access = vars.traktApi('token')
    trakt_api = vars.traktApi('client')
    trakt_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + trakt_access + '',
                    'trakt-api-version': '2',
                    'trakt-api-key': '' + trakt_api + ''
                    }
    trakt_list_url = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists"
    trakt_list_url_post = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + library_clean_path + ""
    trakt_list_url_post_show = "https://api.trakt.tv/users/" + vars.traktApi('me') + "/lists/returning-soon-" + library_clean_path + "/items"
    trakt_list_privacy = vars.librarySetting(library, 'trakt_list_privacy')
    trakt_list_data = f'''
{{
    "name": "Returning Soon {library}",
    "description": "Season premiers and returns within the next {days_ahead} days.",
    "privacy": "{trakt_list_privacy}",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''

    print("Clearing " + library + " trakt list...")
    logging.info("Clearing " + library + " trakt list...")
    trakt_delete_list = requests.delete(trakt_list_url_post, headers=trakt_headers)
    time.sleep(1.25)
    logging.info("Initializing " + library + " trakt list...")
    trakt_make_list = requests.post(trakt_list_url, headers=trakt_headers, data=trakt_list_data)
    time.sleep(1.25)
    trakt_list_show = '''
{
    "shows": [
        '''
    for series_item in series_rs_sorted_list:
        print("Adding " + series_item['title'] + " | TMDB ID: " + str(series_item['id']) + ", to Returning Soon " + library + ".")
        logging.info("Adding " + series_item['title'] + " | TMDB ID: " + str(series_item['id']) + ", to Returning Soon " + library + ".")

        trakt_list_show += f'''
    {{
    "ids": {{
        "tmdb": "{str(series_item['id'])}"
            }}
    }},'''
        
        
    trakt_list_show = trakt_list_show.rstrip(",")
    trakt_list_show += '''
]
}
'''
    
    post_show = requests.post(trakt_list_url_post_show, headers=trakt_headers, data=trakt_list_show)
    if post_show.status_code == 201:
        print("Success")
        print("Added " + str(get_count(series_rs_sorted_list)) + " entries to Trakt.")
        logging.info('Success: Added ' + str(get_count(series_rs_sorted_list)) + ' entries to Trakt.')
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

with open(settings_file, "r") as read_extensions_from_settings_file:
    extension_settings = yaml.load(read_extensions_from_settings_file)

print(f'''
==================================================
Checking Extensions''')
logging.info("Checking Extensions")

for this_library in extension_settings['libraries']:

    try:
        extensions = extension_settings['libraries'][this_library]['extensions']

        for extension_item in extensions:
            
            if extension_item == 'in-history':
                print(f'''
==================================================''')
                print(f'''
Extension setting found. Running 'In History' on {this_library}
''')
                logging.info(f"Extension setting found. Running 'In History' on {this_library}")
                in_history_settings = vars.Extensions(this_library).in_history.settings()
                pmm_in_history_folder = pmm_config_path_prefix + in_history_settings.save_folder
                if pmm_in_history_folder != '':
                    pmm_in_history_folder_exists = os.path.exists(pmm_in_history_folder)
                    if not pmm_in_history_folder_exists:
                        in_history_subfolder_path = f"config/{in_history_settings.save_folder}"
                        print(f"Sub-folder {in_history_subfolder_path} not found.")
                        print(f"Attempting to create.")
                        logging.info(f"Sub-folder {in_history_subfolder_path} not found.")
                        logging.info(f"Attempting to create.")
                        try:
                            os.makedirs(pmm_in_history_folder)
                            print(f"{in_history_subfolder_path} created successfully.")
                            logging.info(f"{in_history_subfolder_path} created successfully.")
                        except Exception as sf:
                            print(f"Exception: {str(sf)}")
                            logging.warning(f"Exception: {str(sf)}")
                in_history_range = in_history_settings.range
                trakt_user_name = vars.traktApi('me')
                library_clean_path = vars.cleanPath(in_history_settings.slug)
                collection_title = in_history_settings.collection_title
                in_history_meta = in_history_settings.meta
                try:
                    output_stream = StringIO()
                    yaml.dump(in_history_meta, output_stream)
                    in_history_meta_str = output_stream.getvalue()
                    output_stream.close()
                    in_history_meta_str = in_history_meta_str.replace("'","")
                    in_history_meta_str = in_history_meta_str.replace('{{range}}', in_history_range)
                    in_history_meta_str = in_history_meta_str.replace('{{Range}}', in_history_range.capitalize())
                except Exception as e:
                    print(f"An error occurred: {e}")


                in_history_file = f"{pmm_config_path_prefix}{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                in_history_file_exists = os.path.exists(in_history_file)

                if not in_history_file_exists:
                    try:
                        print(f"Creating {this_library} 'In History' metadata file..")
                        logging.info(f"Creating {this_library} 'In History' metadata file..")
                        create_in_history_file = open(in_history_file, "x")
                        create_in_history_file.write(in_history_meta_str)
                        create_in_history_file.close()
                        print(f"File created")
                        logging.info(f"File created")
                        in_history_file_location = f"config/{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                        print(f"{in_history_file_location}")
                        logging.info(f"{in_history_file_location}")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                else:
                    print(f"Updating {this_library} 'In History' metadata file..")
                    logging.info(f"Updating {this_library} 'In History' metadata file..")
                    in_history_file_location = f"config/{in_history_settings.save_folder}{library_clean_path}-in-history.yml"
                    print(f"{in_history_file_location}")
                    logging.info(f"{in_history_file_location}")

                    with open(in_history_file, "r") as read_in_history_file:
                        loaded_in_history_yaml = yaml.load(read_in_history_file)

                        for key, value in loaded_in_history_yaml['collections'].items():
                            if key != collection_title:
                                print(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                logging.info(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                library_id = vars.plexGet(this_library)
                                old_collection_id = plex.collection.id(key, library_id)
                                delete_old_collection = plex.collection.delete(old_collection_id)
                                if delete_old_collection:
                                    print(f"Successfully removed old '{key}' collection.")
                                    logging.info(f"Successfully removed old '{key}' collection.")
                                else:
                                    print(f"Could not remove deprecated '{key}' collection.")
                                    logging.warning(f"Could not remove deprecated '{key}' collection.")

                    with open(in_history_file, "w") as write_in_history_file:
                        write_in_history_file.write(in_history_meta_str)
                        print('')
                        print(f'''{in_history_meta_str}''')
                        logging.info('')
                        logging.info(f'''{in_history_meta_str}''')


                month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
                
                
                if in_history_range == 'day':
                    today = datetime.now()
                    start_date = today
                    end_date = today

                if in_history_range == 'week':
                    today = datetime.now()
                    weekday_number = today.weekday()
                    first_weekday = today - timedelta(days=weekday_number)
                    days_till_last_weekday = 6 - weekday_number
                    last_weekday = today + timedelta(days=days_till_last_weekday)
                    start_date = first_weekday
                    end_date = last_weekday

                if in_history_range == 'month':
                    today = datetime.now()
                    first_day_of_month = today.replace(day=1)
                    if first_day_of_month.month == 12:
                        last_day_of_month = first_day_of_month.replace(day=31)
                    elif first_day_of_month.month < 12:
                        last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month + 1) - timedelta(days=1)
                    start_date = first_day_of_month
                    end_date = last_day_of_month
                
                description_identifier = plex.library.type(this_library)
                if description_identifier == 'show':
                    description_type = 'Shows'
                    trakt_type = 'shows'
                if description_identifier == 'movie':
                    description_type = 'Movies'
                    trakt_type = 'movies'
                trakt_access = vars.traktApi('token')
                trakt_api = vars.traktApi('client')
                trakt_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + trakt_access + '',
                    'trakt-api-version': '2',
                    'trakt-api-key': '' + trakt_api + ''
                    }
                trakt_list_url = f"https://api.trakt.tv/users/{trakt_user_name}/lists"
                trakt_list_url_post = f"https://api.trakt.tv/users/{trakt_user_name}/lists/in-history-{library_clean_path}"
                trakt_list_url_post_items = f"https://api.trakt.tv/users/{trakt_user_name}/lists/in-history-{library_clean_path}/items"
                trakt_list_data = f'''
{{
    "name": "In History {this_library}",
    "description": "{description_type} released this {in_history_range} in history.",
    "privacy": "{in_history_settings.trakt_list_privacy}",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''
                print("Clearing " + this_library + " trakt list...")
                logging.info("Clearing " + this_library + " trakt list...")
                trakt_delete_list = requests.delete(trakt_list_url_post, headers=trakt_headers)
                if trakt_delete_list.status_code == 201 or 200 or 204:
                    print("List cleared")
                time.sleep(1.25)
                trakt_make_list = requests.post(trakt_list_url, headers=trakt_headers, data=trakt_list_data)
                if trakt_make_list.status_code == 201 or 200 or 204:
                    print("Initialization successful.")
                time.sleep(1.25)
                trakt_list_items = '''
{'''
                trakt_list_items += f'''
    "{trakt_type}": [
        '''
                print(f"Filtering ==> This '{in_history_range}' in history")
                logging.info(f'Filtering ==> This {in_history_range} in history')
                if in_history_settings.starting != 0:
                    print(f"From {in_history_settings.starting} to {in_history_settings.ending}")
                    logging.info(f"From {in_history_settings.starting} to {in_history_settings.ending}")
                if in_history_settings.starting == 0:
                    print(f"From earliest to {in_history_settings.ending}")
                    logging.info(f"From earliest to {in_history_settings.ending}")
                if in_history_settings.increment != 1:
                    print(f"{in_history_settings.increment} year increment")
                    logging.info(f"{in_history_settings.increment} year increment")
                if in_history_settings.increment == 1:
                    print(f"Using all years")
                    logging.info(f"Using all years")
                print(f'''
''')
                library_list = plex.library.list(this_library)
                library_list = sorted(library_list, key=lambda item: item.date)
                library_list_in_range = [item for item in library_list if date_within_range(item.date, start_date, end_date)]
                for entry in library_list_in_range:
                    title_in_range = plex.item.info(entry.ratingKey)
                    title_in_range_month = month_names[title_in_range.date.month - 1]

                    if title_in_range.details.tmdb and title_in_range.details.imdb and title_in_range.details.tvdb == 'Null':
                        continue
                    
                    if (in_history_settings.starting <= title_in_range.date.year <= in_history_settings.ending 
                        and (in_history_settings.ending - title_in_range.date.year) % in_history_settings.increment == 0
                        and title_in_range.date.year != today.year):
                        print(f"Adding {title_in_range.title} ({title_in_range_month} {title_in_range.date.day}, {title_in_range.date.year})")
                        logging.info(f"Adding {title_in_range.title} ({title_in_range_month} {title_in_range.date.day}, {title_in_range.date.year})")
                        trakt_list_items += f'''
    {{
    "ids": {{'''
                
                        if title_in_range.details.tmdb != 'Null':
                            trakt_list_items += f'''
        "tmdb": "{title_in_range.details.tmdb}",'''
                        if title_in_range.details.tvdb != 'Null':
                            trakt_list_items += f'''
        "tvdb": "{title_in_range.details.tvdb}",'''
                        if title_in_range.details.imdb != 'Null':
                            trakt_list_items += f'''
        "imdb": "{title_in_range.details.imdb}",'''
                        
                        trakt_list_items = trakt_list_items.rstrip(",")
                    
                        trakt_list_items += f'''
            }}
    }},'''
        
        
                trakt_list_items = trakt_list_items.rstrip(",")
                trakt_list_items += '''
]
}
'''
                
                post_items = requests.post(trakt_list_url_post_items, headers=trakt_headers, data=trakt_list_items)
                if post_items.status_code == 201:
                    print(f"Successfully posted This {in_history_range} In History items for {this_library}")
                    logging.info(f"Successfully posted This {in_history_range} In History items for {this_library}")




            if extension_item == 'by_size' and plex.library.type(this_library) == 'movie':
                print(f'''
==================================================''')
                print(f'''
Extension setting found. Running 'Sort by size' on {this_library}
''')
                logging.info(f"Extension setting found. Running 'Sort by size' on {this_library}")


                by_size_settings = vars.Extensions(this_library).by_size.settings()
                pmm_by_size_folder = pmm_config_path_prefix + by_size_settings.save_folder
                if pmm_by_size_folder != '':
                    pmm_by_size_folder_exists = os.path.exists(pmm_by_size_folder)
                    if not pmm_by_size_folder_exists:
                        by_size_subfolder_path = f"config/{by_size_settings.save_folder}"
                        print(f"Sub-folder {by_size_subfolder_path} not found.")
                        print(f"Attempting to create.")
                        logging.info(f"Sub-folder {by_size_subfolder_path} not found.")
                        logging.info(f"Attempting to create.")
                        try:
                            os.makedirs(pmm_by_size_folder)
                            print(f"{by_size_subfolder_path} created successfully.")
                            logging.info(f"{by_size_subfolder_path} created successfully.")
                        except Exception as sf:
                            print(f"Exception: {str(sf)}")
                            logging.warning(f"Exception: {str(sf)}")
                trakt_user_name = vars.traktApi('me')
                library_clean_path = vars.cleanPath(by_size_settings.slug)
                collection_title = by_size_settings.collection_title
                by_size_meta = by_size_settings.meta
                try:
                    output_stream = StringIO()
                    yaml.dump(by_size_meta, output_stream)
                    by_size_meta_str = output_stream.getvalue()
                    output_stream.close()
                    by_size_meta_str = by_size_meta_str.replace("'","")
                except Exception as e:
                    print(f"An error occurred: {e}")
                by_size_file = f"{pmm_config_path_prefix}{by_size_settings.save_folder}{library_clean_path}-by-size.yml"
                by_size_file_exists = os.path.exists(by_size_file)

                if not by_size_file_exists:
                    try:
                        print(f"Creating {this_library} 'By Size' metadata file..")
                        logging.info(f"Creating {this_library} 'By Size' metadata file..")
                        creata_by_size_file = open(by_size_file, "x")
                        creata_by_size_file.write(by_size_meta_str)
                        creata_by_size_file.close()
                        print(f"File created")
                        logging.info(f"File created")
                        by_size_file_location = f"config/{by_size_settings.save_folder}{library_clean_path}-by-size.yml"
                        print(f"{by_size_file_location}")
                        logging.info(f"{by_size_file_location}")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                else:
                    print(f"Updating {this_library} 'By Size' metadata file..")
                    logging.info(f"Updating {this_library} 'By Size' metadata file..")
                    by_size_file_location = f"config/{by_size_settings.save_folder}{library_clean_path}-by-size.yml"
                    print(f"{by_size_file_location}")
                    logging.info(f"{by_size_file_location}")
    
                    with open(by_size_file, "r") as read_by_size_file:
                        check_BySize_Title = yaml.load(read_by_size_file)
                        
                        
                        
                        for key, value in check_BySize_Title['collections'].items():
                            if key != collection_title:
                                print(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                logging.info(f'''Collection for {this_library} has been changed from {key} ==> {collection_title}
Attempting to remove unused collection.''')
                                library_id = vars.plexGet(this_library)
                                old_collection_id = plex.collection.id(key, library_id)
                                delete_old_collection = plex.collection.delete(old_collection_id)
                                if delete_old_collection == True:
                                    print(f"Successfully removed old '{key}' collection.")
                                    logging.info(f"Successfully removed old '{key}' collection.")
                                if delete_old_collection == False:
                                    print(f"Could not remove deprecated '{key}' collection.")
                                    logging.warning(f"Could not remove deprecated '{key}' collection.")

                    with open(by_size_file, "w") as write_by_size_file:
                        write_by_size_file.write(by_size_meta_str)
                        print('')
                        print(f'''{by_size_meta_str}''')
                        logging.info('')
                        logging.info(f'''{by_size_meta_str}''')

                movies_list = plex.library.extended_list(this_library)
                sort_key = by_size_settings.order_by_field
                reverse_value = by_size_settings.reverse
                minimum = by_size_settings.minimum
                maximum =  by_size_settings.maximum
                movies_list = sorted(movies_list, key=lambda x: getattr(x, sort_key), reverse=reverse_value)
                movies_list = [
                    movie for movie in movies_list
                    if (
                        minimum <= movie.size and
                        (maximum is None or movie.size <= maximum)
                    )
                ]

                print(f'''Sorting {this_library} by '{by_size_settings.order_by_field}.{by_size_settings.order_by_direction}'.''')

                library_clean_path = vars.cleanPath(this_library)
                trakt_user_name = vars.traktApi('me')
                trakt_access = vars.traktApi('token')
                trakt_api = vars.traktApi('client')
                trakt_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + trakt_access + '',
    'trakt-api-version': '2',
    'trakt-api-key': '' + trakt_api + ''
    }
                trakt_list_url = f"https://api.trakt.tv/users/{trakt_user_name}/lists"
                trakt_list_url_post = f"https://api.trakt.tv/users/{trakt_user_name}/lists/sorted-by-size-{library_clean_path}"
                trakt_list_url_post_items = f"https://api.trakt.tv/users/{trakt_user_name}/lists/sorted-by-size-{library_clean_path}/items"
                trakt_list_data = f'''
{{
    "name": "Sorted by size {this_library}",
    "description": "{this_library}, sorted by size.",
    "privacy": "private",
    "display_numbers": true,
    "allow_comments": true,
    "sort_by": "rank",
    "sort_how": "asc"
}}
    '''
                print("Clearing " + this_library + " trakt list...")
                logging.info("Clearing " + this_library + " trakt list...")
                trakt_delete_list = requests.delete(trakt_list_url_post, headers=trakt_headers)
                if trakt_delete_list.status_code == 201 or 200 or 204:
                    print("List cleared")
                    time.sleep(1.25)
                trakt_make_list = requests.post(trakt_list_url, headers=trakt_headers, data=trakt_list_data)
                if trakt_make_list.status_code == 201 or 200 or 204:
                    print("Initialization successful.")
                    time.sleep(1.25)

                description_identifier = plex.library.type(this_library)
                if description_identifier == 'show':
                    description_type = 'Shows'
                    trakt_type = 'shows'
                if description_identifier == 'movie':
                    description_type = 'Movies'
                    trakt_type = 'movies'

                trakt_list_items = '''
{'''
                trakt_list_items += f'''
    "{trakt_type}": [
        '''

                for movie_info in movies_list:

    
                    print(f'''Adding '{movie_info.title}'.''')

                    movie_by_size = plex.item.info(movie_info.ratingKey)
                    trakt_list_items += f'''
    {{
    "ids": {{'''
                
                    if movie_by_size.details.tmdb != 'Null':
                        trakt_list_items += f'''
    "tmdb": "{movie_by_size.details.tmdb}",'''
                    if movie_by_size.details.tvdb != 'Null':
                        trakt_list_items += f'''
    "tvdb": "{movie_by_size.details.tvdb}",'''
                    if movie_by_size.details.imdb != 'Null':
                        trakt_list_items += f'''
    "imdb": "{movie_by_size.details.imdb}",'''
                        
                    trakt_list_items = trakt_list_items.rstrip(",")
                                    
                    trakt_list_items += f'''
            }}
    }},'''
        
        
                trakt_list_items = trakt_list_items.rstrip(",")
                trakt_list_items += '''
]
}
'''

                post_items = requests.post(trakt_list_url_post_items, headers=trakt_headers, data=trakt_list_items)
                if post_items.status_code == 201:
                    print(f"Successfully posted Sorted by size items for {this_library}")
                    logging.info(f"Successfully Sorted by size items for {this_library}")

            if extension_item == 'by_size' and plex.library.type(this_library) != 'movie':
                print(f'''The 'By Size' extension is only valid for Movie libraries. {this_library} is not compatible and will be skipped.''')

                    
    except KeyError:
        print(f"No extensions set for {this_library}.")
        logging.info(f"No extensions set for {this_library}.")
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
