from modules.utilities import ConfigLoader
import requests
import datetime

loader = ConfigLoader()
config = loader.meta_config


class ItemDetails:
    def __init__(self, id=None, title=None, size=None, date=None, season_num=None, episode_num=None):
        self.id = id
        self.title = title
        self.size = size
        self.date = date
        self.season_num = season_num
        self.episode_num = episode_num


class ItemID:
    def __init__(self, rating_key=None, guid=None, tmdb=None, imdb=None, tvdb=None):
        self.rating_key = rating_key
        self.guid = guid
        self.tmdb = tmdb
        self.imdb = imdb
        self.tvdb = tvdb


class ItemDate:
    def __init__(self, available_date=None, added_date=None, year=None):
        self.available_date = available_date
        self.added_date = added_date
        self.year = year


class EpisodeList(list):
    @property
    def size(self):
        return sum(episode.size for episode in self)


class PlexApi:
    def __init__(self):
        self.plex_url = config.plex.url
        self.plex_token = config.plex.token
        self.rating_key = None
        self.context = None
        self.id = None
        self.title = None
        self.date = None
        self.size = None

    def test_connection(self):
        try:
            headers = {
                "X-Plex-Token": self.plex_token,
                "accept": "application/json"
            }

            response = requests.get(self.plex_url, headers=headers)

            if response.status_code == 200:
                print("Plex connection successful.")
            else:
                print("Plex connection failed. Status code:", response.status_code)
        except requests.RequestException as e:
            print("Error connecting to Plex:", e)

    def library(self, library_name):
        self.library_name = library_name
        self.context = 'library'
        self.section_id = None

        library_details_url = f"{self.plex_url}/library/sections"
        headers = {
            "X-Plex-Token": self.plex_token,
            "accept": "application/json"
        }

        response = requests.get(library_details_url, headers=headers)

        if response.status_code == 200:
            print(f"Connection to {library_name} successful.")
            sections = response.json()

            for section in sections['MediaContainer']['Directory']:
                if section['title'] == library_name:
                    self.section_id = section['key']
                    self.type = section['type']

        return self

    def contents(self):
        if self.context == 'library' and self.section_id:
            try:
                library_url = f"{self.plex_url}/library/sections/{self.section_id}/all"
                headers = {
                    "X-Plex-Token": self.plex_token,
                    "accept": "application/json"
                }

                response = requests.get(library_url, headers=headers)
                library_list = []

                if response.status_code == 200:
                    data = response.json()
                    media_items = data['MediaContainer']['Metadata']
                    total_num_items = len(media_items)
                    total_digit_length = len(str(total_num_items))
                    current_item_num = 1

                    for media_item in media_items:

                        if self.type == 'movie':
                            try:
                                size_str = media_item['Media'][0]['Part'][0]['size']
                                size_bytes = int(size_str)
                                size_GB = size_bytes / 1073741824

                                library_list.append(
                                    ItemDetails(
                                        title=media_item['title'],
                                        id=ItemID(
                                            rating_key=media_item['ratingKey'], 
                                            guid=media_item['guid']
                                        ),
                                        date=ItemDate(
                                            available_date=media_item.get('originallyAvailableAt'),
                                            added_date=media_item['addedAt'],
                                            year=media_item['year']
                                        ),
                                        size=round(size_GB, 2)
                                    )
                                )

                            except KeyError:
                                print(f"Unable to process {media_item['title']}. Ommitting title.")
                                continue

                        if self.type == 'show':
                            try:
                                added_at_str = media_item.get('addedAt', '0')
                                added_at_timestamp = abs(int(added_at_str))
                                added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
                                added_date = added_dt_object.strftime('%Y-%m-%d')

                                library_list.append(
                                    ItemDetails(
                                        title=media_item['title'],
                                        id=ItemID(
                                            rating_key=media_item['ratingKey'],
                                            guid=media_item['guid']
                                        ),
                                        date=ItemDate(
                                            available_date=media_item.get('originallyAvailableAt'),
                                            added_date=added_date,
                                            year=media_item['year']
                                        )
                                    )
                                )

                            except KeyError:
                                print(f"Unable to process {media_item['title']}. Ommitting title.")
                                continue

                        info_title = media_item['title'][:30] + '...' if len(media_item['title']) > 30 else media_item['title']
                        print(f"{str(current_item_num).zfill(total_digit_length)}/{total_num_items} | {self.type.capitalize()} | {info_title.ljust(33)}")
                        current_item_num += 1

                    return library_list

                else:
                    return f"Error: {response.status_code} - {response.text}"

            except Exception as e:
                return f"Error: {str(e)}"

    def show(self, rating_key):
        self.rating_key = rating_key
        self.context = 'show'

        try:
            show_details_url = f"{self.plex_url}/library/metadata/{rating_key}"
            headers = {
                "X-Plex-Token": self.plex_token,
                "accept": "application/json"
            }

            response = requests.get(show_details_url, headers=headers)

            if response.status_code == 200:
                show_data = response.json()['MediaContainer']['Metadata'][0]

                show_title = show_data.get('title', 'Unknown Show Title')
                rating_key = show_data.get('ratingKey', 'Unknown rating key')
                guid = show_data.get('guid', 'Unknown Plex GUID')
                
                available_date = show_data.get('originallyAvailableAt')
                show_year = show_data.get('year')

                added_at_str = show_data.get('addedAt', '0')
                added_at_timestamp = abs(int(added_at_str))
                added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
                added_date = added_dt_object.strftime('%Y-%m-%d')

                guids = show_data.get('Guid', [])

                tvdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("tvdb://")), 'null')[7:]
                tmdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("tmdb://")), 'null')[7:]
                imdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("imdb://")), 'null')[7:]

                self.title = show_title
                self.id = ItemID(
                    rating_key=rating_key,
                    guid=guid,
                    tmdb=tmdb_id,
                    imdb=imdb_id,
                    tvdb=tvdb_id
                )
                self.date = ItemDate(
                    available_date=available_date,
                    added_date=added_date,
                    year=show_year
                )

                return self

        except Exception as e:
            print(f"Error fetching show details: {e}")
            return self

    def movie(self, rating_key):
        headers = {
            "X-Plex-Token": self.plex_token,
            "accept": "application/json"
        }

        try:
            movie_response = requests.get(
                f"{self.plex_url}/library/metadata/{rating_key}",
                headers=headers
            )

            movie_data = movie_response.json()['MediaContainer']['Metadata'][0]

            movie_title = movie_data.get('title', 'Unknown Movie Title')
            rating_key = movie_data.get('ratingKey', 'Unknown rating key')
            guid = movie_data.get('guid', 'Unknown Plex GUID')
            
            available_date = movie_data.get('originallyAvailableAt')
            movie_year = movie_data.get('year')

            added_at_str = movie_data.get('addedAt', '0')
            added_at_timestamp = abs(int(added_at_str))
            added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
            added_date = added_dt_object.strftime('%Y-%m-%d')

            size_GB = int(movie_data.get("Media", [{}])[0].get("Part", [{}])[0].get("size", "0")) / 1073741824

            guids = movie_data.get('Guid', [])

            tvdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("tvdb://")), 'null')[7:]
            tmdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("tmdb://")), 'null')[7:]
            imdb_id = next((guid['id'] for guid in guids if guid['id'].startswith("imdb://")), 'null')[7:]

            self.title = movie_title
            self.id = ItemID(
                rating_key=rating_key,
                guid=guid,
                tmdb=tmdb_id,
                imdb=imdb_id,
                tvdb=tvdb_id
            )
            self.date = ItemDate(
                available_date=available_date,
                added_date=added_date,
                year=movie_year
            )
            self.size = round(size_GB, 2)

            return self

        except Exception as e:
            print(f"Error fetching movie details: {e}")
            return self

    def episode(self, rating_key):
        try:
            episode_url = f"{self.plex_url}/library/metadata/{rating_key}"
            headers = {
                "X-Plex-Token": self.plex_token,
                "accept": "application/json"
            }

            response = requests.get(episode_url, headers=headers)

            if response.status_code == 200:
                episode = response.json()['MediaContainer']['Metadata'][0]

                title = episode['title']
                season_num = str(episode['parentIndex']).zfill(2)
                episode_num = str(episode['index']).zfill(2)
                rating_key = episode['ratingKey']
                guid = episode.get('guid', 'Unknown Plex GUID')
                available_date = episode.get('originallyAvailableAt')

                added_at_str = episode['addedAt']
                added_at_timestamp = abs(int(added_at_str))
                added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
                added_date = added_dt_object.strftime('%Y-%m-%d')

                year = episode['year']
                size_str = episode['Media'][0]['Part'][0]['size']
                size_bytes = int(size_str)
                size_GB = round(size_bytes / 1073741824, 2)

                return ItemDetails(
                    title=title,
                    id=ItemID(
                        rating_key=rating_key,
                        guid=guid
                    ),
                    date=ItemDate(
                        available_date=available_date,
                        added_date=added_date,
                        year=year
                    ),
                    size=size_GB,
                    season_num=season_num,
                    episode_num=episode_num
                )

        except Exception as e:
            print(f"Error fetching episode: {e}")
            return None

    def episodes(self):
        episodes_list = EpisodeList()

        if self.context == 'show':
            try:
                episodes_url = f"{self.plex_url}/library/metadata/{self.rating_key}/allLeaves"
                headers = {
                    "X-Plex-Token": self.plex_token,
                    "accept": "application/json"
                }

                response = requests.get(episodes_url, headers=headers)

                if response.status_code == 200:
                    episodes_data = response.json()

                    for episode in episodes_data['MediaContainer']['Metadata']:
                        title = episode['title']
                        season_num = str(episode['parentIndex']).zfill(2)
                        episode_num = str(episode['index']).zfill(2)
                        rating_key = episode['ratingKey']
                        guid = episode.get('guid', 'Unknown Plex GUID')
                        available_date = episode.get('originallyAvailableAt')

                        added_at_str = episode['addedAt']
                        added_at_timestamp = abs(int(added_at_str))
                        added_dt_object = datetime.datetime.utcfromtimestamp(added_at_timestamp)
                        added_date = added_dt_object.strftime('%Y-%m-%d')

                        year = episode['year']
                        size_str = episode['Media'][0]['Part'][0]['size']
                        size_bytes = int(size_str)
                        size_GB = round(size_bytes / 1073741824, 2)

                        episodes_list.append(
                            ItemDetails(
                                title=title,
                                id=ItemID(
                                    rating_key=rating_key,
                                    guid=guid
                                ),
                                date=ItemDate(
                                    available_date=available_date,
                                    added_date=added_date,
                                    year=year
                                ),
                                size=size_GB,
                                season_num=season_num,
                                episode_num=episode_num
                            )
                        )

                    return episodes_list

            except Exception as e:
                print(f"Error fetching episodes: {e}")
                return episodes_list

        else:
            print("Context not set to 'show'. Please call 'show(rating_key)' before fetching episodes.")
            return episodes_list
