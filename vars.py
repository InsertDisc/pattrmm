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
