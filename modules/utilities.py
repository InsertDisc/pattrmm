import os
from ruamel.yaml import YAML
from dataclasses import dataclass, fields
from typing import Optional
import requests
import re

yaml = YAML()
yaml.preserve_quotes = True


@dataclass
class Plex:
    url: str
    token: str
    def __post_init__(self):
        if self.url.endswith('/'):
            self.url = self.url[:-1]

@dataclass
class Trakt:
    client_id: str
    client_secret: str
    authorization: dict
    pin: Optional[str] = None
    def __post_init__(self):
        client_id = self.client_id
        access_token = self.authorization['access_token']
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token + '',
        'trakt-api-version': '2',
        'trakt-api-key': client_id
        }
        self.username = requests.get('https://api.trakt.tv/users/me', headers=headers).json()['username']
        

@dataclass
class Tmdb:
    apikey: str
    language: str
    region: str

@dataclass
class Tvdb:
    apikey: Optional[str] = None

@dataclass
class Sonarr:
    url: str
    token: str
    root_folder_path: str
    monitor: bool
    language_profile: str
    series_type: str

@dataclass
class Radarr:
    url: str
    token: str
    root_folder_path: str
    monitor: bool

@dataclass
class ConfigData:
    plex: Plex
    trakt: Trakt
    tmdb: Tmdb
    tvdb: Tvdb
    sonarr: Sonarr
    radarr: Radarr
    # Add other attributes for the remaining keys...

class ConfigLoader:
    def __init__(self):
        self.settings = None
        self.pmm_config = None
        self.pmm_config_loaded = False
        self.settings_loaded = False
        self.load_configs()

    @property
    def settings_data(self):
        return self.settings

    @property
    def pmm_config_data(self):
        return self.pmm_config

    def load_configs(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_file_path = os.path.join(script_dir, '..', 'Preferences', 'settings.yml') 

        with open(settings_file_path, 'r') as file:
            self.settings = yaml.load(file)
        
        if os.environ.get('PATTRMM_DOCKER') == 'True':
            config_file_path = os.path.join(script_dir, 'config', 'config.yml')
        else:
            config_file_path = os.path.join(script_dir, '..', '..', 'config.yml')

        with open(config_file_path, 'r') as file:
            config_data_dict = yaml.load(file)
            self.pmm_config_loaded = True

        filtered_config_data = {}

        for dataclass_key_name, dataclass_key_type in ConfigData.__annotations__.items():
            dataclass_attribute_data = config_data_dict.get(dataclass_key_name, {})
            valid_keys = {data_attribute.name for data_attribute in fields(dataclass_key_type)}
            filtered_attribute_data = {key: value for key, value in dataclass_attribute_data.items() if key in valid_keys}
            filtered_config_data[dataclass_key_name] = dataclass_key_type(**filtered_attribute_data)

        self.pmm_config = ConfigData(**filtered_config_data)

def get_core_settings(core_name: str, allowed_instances: int, default_settings: dict) -> list:
    processed_settings = {}

    data = ConfigLoader().settings

    for library_name, cores in data['libraries'].items():
        core_count = sum(
            isinstance(core, dict) and core_name in core for core in cores
        )
        if core_count > allowed_instances:
            print(f"The '{core_name}' constructor is instanced in {library_name} {core_count} times, allowed ({allowed_instances}), skipping {core_name} for {library_name}")
            continue
        library_settings = []

        has_core = False
        core_values = []

        for core in cores:
            if isinstance(core, dict) and core_name in core:
                has_core = True
                if core[core_name] is None:  # Check if core settings are empty
                    library_settings.append(default_settings)
                    continue
                core_values.append(core[core_name])

        if has_core:
            for core in core_values:
                merged_settings = {**default_settings, **core}
                filtered_settings = {
                    key: value for key, value in merged_settings.items() if key in default_settings
                }

                for key, value in default_settings.items():
                    if key not in filtered_settings:
                        if isinstance(value, dict):
                            filtered_settings[key] = {
                                k: v for k, v in value.items() if k in merged_settings.get(key, {})
                            }
                        else:
                            filtered_settings[key] = value

                    elif isinstance(value, dict) and isinstance(filtered_settings[key], dict):
                        default_subsettings = value
                        filtered_settings[key].update({
                            k: v for k, v in default_subsettings.items() if k not in filtered_settings[key]
                        })

                library_settings.append(filtered_settings)

            processed_settings[library_name] = library_settings

    return processed_settings

def clean_string(string):
        cleaned_string = re.sub(r'[^\w]+', '-', string).rstrip('-')
        return cleaned_string

def base_path():
    if os.environ.get('PATTRMM_DOCKER') == 'True':
        base_path = 'config'
    else:
        utilities_file_path = os.path.abspath(__file__)
        base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(utilities_file_path)))))
    return base_path

def path_constructor(save_folder, file_name):
    absolute_file_path = os.path.join(base_path(), save_folder, file_name)
    if os.name == 'posix':
        absolute_file_path = absolute_file_path.replace('\\', '/')
    elif os.name == 'nt':
        absolute_file_path = absolute_file_path.replace('/', '\\')
    return absolute_file_path

def date_within_range(item_date, start_date, end_date): #Returns True or False
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
