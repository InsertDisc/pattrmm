import os
from ruamel.yaml import YAML
from dataclasses import dataclass, fields
from typing import Optional
import re
from datetime import datetime

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
    tmdb: Tmdb
    tvdb: Tvdb
    sonarr: Sonarr
    radarr: Radarr
    # Add other attributes for the remaining keys...

class ConfigLoader:
    def __init__(self):
        self.settings = None
        self.meta_config = None
        self.load_configs()

    def load_configs(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_file = os.path.join(script_dir, '..', 'preferences', 'settings.yml')

        with open(settings_file, 'r', encoding='utf-8') as file:
            self.settings = yaml.load(file) or {}

        meta_config_file = self.settings.get('settings', {}).get('kometa_config', 'config.yml')
        config_file = os.path.join(base_path(), meta_config_file)

        with open(config_file, 'r', encoding='utf-8') as file:
            config_data = yaml.load(file) or {}

        filtered_config = {}
        for name, dataclass_type in ConfigData.__annotations__.items():
            values = config_data.get(name, {}) or {}
            values = {key: value for key, value in values.items() if key in dataclass_type.__dataclass_fields__}
            filtered_config[name] = dataclass_type(**values)

        self.meta_config = ConfigData(**filtered_config)

    @property
    def settings_data(self):
        return self.settings

    @property
    def meta_config_data(self):
        return self.meta_config


def get_core_settings(core_name: str, allowed_instances: int = 1, default_settings: dict | None = None):
    default_settings = default_settings or {}
    settings = ConfigLoader().settings or {}
    result = {}

    for library, configured_cores in settings.get('libraries', {}).items():
        instances = []
        for core in configured_cores or []:
            if core_name not in core:
                continue

            value = core[core_name]
            if value is None:
                value = {}
            if isinstance(value, list):
                instances.extend(value)
            else:
                instances.append(value)

        if allowed_instances and len(instances) > allowed_instances:
            raise ValueError(f"'{core_name}' can only be configured {allowed_instances} time(s) in {library}.")

        merged_instances = []
        for instance in instances:
            merged = {**default_settings, **instance}
            for key in ('collection', 'overlay'):
                if key in default_settings:
                    merged[key] = {**default_settings[key], **instance.get(key, {})}
            merged_instances.append(merged)

        if merged_instances:
            result[library] = merged_instances

    return result


def clean_string(string):
    cleaned_string = re.sub(r'[^\w]+', '-', string)
    cleaned_string = re.sub(r'-+', '-', cleaned_string)
    return cleaned_string.rstrip('-')


def to_dict(obj):
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        obj_dict = obj.__dict__.copy()
        for key, value in obj_dict.items():
            obj_dict[key] = to_dict(value)
        return obj_dict
    else:
        return obj

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

def log_title(item):
    display_title = item[:30] + '...' if len(item) > 30 else item
    return display_title

def current_date():
    return datetime.now().strftime("%Y-%m-%d")

def file_exists(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        print(f"Creating directory {directory}")
        try:
            os.makedirs(directory)
            print(f"Successfully created directory {directory}")
        except OSError as e:
            print(f"Failed to create directory {directory}: {e}")
            return False
    
    if not os.path.exists(path):
        print(f"Creating file {path}")
        try:
            with open(path, 'w') as file:
                file.write('')
            print(f"Successfully created file {path}")
        except IOError as e:
            print(f"Failed to create file {path}: {e}")
            return False
    
    return True
