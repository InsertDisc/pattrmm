from modules.utilities import ConfigLoader
from modules.utilities import log_title
from dataclasses import dataclass, fields
from typing import List, Optional
config = ConfigLoader().meta_config
import requests
import datetime
import re

apikey = config.tmdb.apikey
language = config.tmdb.language
region = config.tmdb.region

@dataclass
class LastEpisode:
    id: Optional[int]
    name: Optional[str]
    air_date: Optional[str]
    episode_number: Optional[int]
    season_number: Optional[int]
    episode_type: Optional[str]


@dataclass
class NextEpisode:
    id: Optional[int]
    name: Optional[str]
    air_date: Optional[str]
    episode_number: Optional[int]
    season_number: Optional[int]
    episode_type: Optional[str]


@dataclass
class SpokenLanguages:
    english_name: Optional[str]
    iso_639_1: Optional[str]
    name: Optional[str]


@dataclass
class ShowDetails:
    show_id: Optional[int]
    name: Optional[str]
    first_air_date: Optional[str]
    last_air_date: Optional[str]
    last_episode_to_air: LastEpisode
    next_episode_to_air: NextEpisode
    original_language: Optional[str]
    popularity: Optional[float]
    status: Optional[str]
    spoken_languages: List[SpokenLanguages]


@dataclass
class MovieDetails:
    id: Optional[int]
    imdb_id: Optional[str]
    original_language: Optional[str]
    original_title: Optional[str]
    popularity: Optional[float]
    release_date: Optional[str]
    spoken_languages: List[SpokenLanguages]
    status: Optional[str]
    title: Optional[str]



class TmdbApi:
    def __init__(self):
        self.headers = {
            'accept': 'application/json'
        }
        self.apikey = apikey
        self.language = language
        self.region = region
        self.search_tv = "https://api.themoviedb.org/3/search/tv"
        self.discover_tv = "https://api.themoviedb.org/3/discover/tv"
        self.details_tv = "https://api.themoviedb.org/3/tv"
        self.search_external_id = "https://api.themoviedb.org/3/find"
        self.details_movie = "https://api.themoviedb.org/3/movie"
        self.auth = "https://api.themoviedb.org/3/authentication"

    def movie(self, id):
        self.context = 'movie'
        self.id = id
        return self

    def show(self, id):
        self.context = 'show'
        self.id = id
        return self

    def test_connection(self):
        self.params = {
            'api_key': self.apikey
        }
        try:
            response = requests.get(self.auth, headers=self.headers, params=self.params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()
            if response_data['success'] == True:
                print("Connection to TMDB Api successful.")
        except requests.RequestException as e:
            print(f'An error occurred during TMDB authorization: {e}')

    def details(self):
        self.params = {
            'api_key': self.apikey
        }
        if self.context == 'show':
            try:
                self.url = f'{self.details_tv}/{self.id}'
                response = requests.get(self.url, headers=self.headers, params=self.params)
                if response.status_code == 200:
                    data = response.json()
                    last_episode_details = data.get("last_episode_to_air")
                    if last_episode_details:
                        last_episode = LastEpisode(
                            id=last_episode_details.get("id", None),
                            name=last_episode_details.get("name", None),
                            air_date=last_episode_details.get("air_date", None),
                            episode_number=last_episode_details.get("episode_number", None),
                            season_number=last_episode_details.get("season_number", None),
                            episode_type=last_episode_details.get("episode_type", None)
                        )
                    else:
                        last_episode = LastEpisode(id = None,
                                                    name= None,
                                                    air_date = None,
                                                    episode_number = None,
                                                    season_number = None,
                                                    episode_type = None)

                    next_episode_details = data.get("next_episode_to_air", None)
                    if next_episode_details:
                        next_episode = NextEpisode(
                            id=next_episode_details.get("id", None),
                            name=next_episode_details.get("name", None),
                            air_date=next_episode_details.get("air_date", None),
                            episode_number=next_episode_details.get("episode_number", None),
                            season_number=next_episode_details.get("season_number", None),
                            episode_type=next_episode_details.get("episode_type", None)
                        )
                    else:
                        next_episode = NextEpisode(id = None,
                                                   name = None,
                                                   air_date = None,
                                                   episode_number = None,
                                                   season_number = None,
                                                   episode_type = None)

                    spoken_languages_details = data.get("spoken_languages")
                    if spoken_languages_details:
                        spoken_languages = [SpokenLanguages(**lang) for lang in spoken_languages_details]
                    else:
                        spoken_languages = SpokenLanguages(english_name = None, iso_639_1 = None, name = None)

                    show_details = ShowDetails(
                        show_id=data.get("id", None),
                        name=data.get("name", None),
                        first_air_date=data.get("first_air_date", None),
                        last_air_date=data.get("last_air_date", None),
                        last_episode_to_air=last_episode,
                        next_episode_to_air=next_episode,
                        original_language=data.get("original_language", None),
                        popularity=data.get("popularity", None),
                        status=data.get("status", None),
                        spoken_languages=spoken_languages
                        )
                    return show_details
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return None
            except KeyError as e:
                print(f"Missing key in API response: {e}")
                return None
        
        if self.context == "movie":
            try:
                self.url = f'{self.details_movie}/{self.id}'
                response = requests.get(self.url, headers=self.headers, params=self.params)
                if response.status_code == 200:
                    data = response.json()

                    spoken_languages_details = data.get("spoken_languages")
                    if spoken_languages_details:
                        spoken_languages = [SpokenLanguages(**lang) for lang in spoken_languages_details]
                    else:
                        spoken_languages = None

                    movie_details = MovieDetails(
                        id = data.get("id", None),
                        imdb_id = data.get("imdb_id", None),
                        original_language = data.get("original_language", None),
                        original_title = data.get("original_title", None),
                        popularity =  data.get("popularity", None),
                        release_date = data.get("release_date", None),
                        spoken_languages = spoken_languages,
                        status = data.get("status", None),
                        title = data.get("title", None)
                        )
                    return movie_details
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return None
            except KeyError as e:
                print(f"Missing key in API response: {e}")
                return None
            
    def external_source(self, external_id, source, media_type):
        self.external_id = external_id
        self.source = source
        self.media_type = media_type
        self.params = {
            'api_key': self.apikey,
            'external_source': self.source
        }
        try:
            self.url = f'{self.search_external_id}/{self.external_id}'
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                data = response.json()
                if self.media_type == 'show':
                    tmdb_id = data['tv_results']['id']
                if self.media_type == 'movie':
                    tmdb_id = data['movie_results']['id']
                return tmdb_id
        except:
            return False
