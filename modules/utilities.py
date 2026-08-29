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
        self.kometa_config = None

        self.settings_name = os.getenv(
            'PATTRMM_SETTINGS',
            'settings.yml'
        )

        self.settings_slug = clean_string(
            os.path.splitext(self.settings_name)[0]
        )

        self.load_configs()

    def load_configs(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        settings_file = os.path.join(
            script_dir,
            '..',
            'settings',
            self.settings_name
        )

        with open(settings_file, 'r', encoding='utf-8') as file:
            self.settings = yaml.load(file) or {}

        self.settings.setdefault('settings', {})
        self.settings['settings'].setdefault(
            'cache_expiry',
            30
        )

        kometa_config_file = self.settings.get(
            'settings',
            {}
        ).get(
            'kometa_config',
            'config.yml'
        )

        config_file = os.path.join(
            kometa_base_path(),
            kometa_config_file
        )

        with open(config_file, 'r', encoding='utf-8') as file:
            config_data = yaml.load(file) or {}

        filtered_config = {}

        for name, dataclass_type in ConfigData.__annotations__.items():
            values = config_data.get(name, {}) or {}

            values = {
                key: value
                for key, value in values.items()
                if key in dataclass_type.__dataclass_fields__
            }

            filtered_config[name] = dataclass_type(**values)

        self.kometa_config = ConfigData(**filtered_config)

    @property
    def settings_data(self):
        return self.settings

    @property
    def kometa_config_data(self):
        return self.kometa_config


def get_core_settings(
    core_name: str,
    allowed_instances: int = 1,
    default_settings: dict | None = None
):
    default_settings = default_settings or {}
    settings = ConfigLoader().settings or {}
    result = {}

    for library, configured_cores in settings.get('libraries', {}).items():
        instances = []

        for core in configured_cores or []:
            if core_name not in core:
                continue

            value = core[core_name] or {}

            if isinstance(value, list):
                instances.extend(value)
            else:
                instances.append(value)
        # Check if there are more instances of a core configured for a library than the core is made to handle. 
        # Inform and truncate if true.
        if allowed_instances and len(instances) > allowed_instances:
            print(
                f"[Config] {library}: {core_name} has "
                f"{len(instances)} instances configured, "
                f"but only {allowed_instances} allowed. "
                f"Ignoring {len(instances) - allowed_instances}."
            )
            instances = instances[:allowed_instances]

        merged_instances = []

        for instance in instances:

            def merge(defaults, values):
                merged = {}

                for key, default in defaults.items():
                    value = values.get(key, default)

                    if isinstance(default, dict) and isinstance(value, dict):
                        if key in ('collection', 'overlay'):
                            merged[key] = {
                                **default,
                                **value
                            }
                        else:
                            merged[key] = merge(default, value)
                    else:
                        merged[key] = value

                return merged

            merged_instances.append(
                merge(default_settings, instance)
            )

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

def kometa_base_path():
    if os.environ.get('PATTRMM_DOCKER') == 'True':
        kometa_base_path = 'config'
    else:
        utilities_file_path = os.path.abspath(__file__)
        kometa_base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(utilities_file_path)))))
    return kometa_base_path

def pattrmm_base_path():
    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

def path_constructor(save_folder, file_name):
    absolute_file_path = os.path.join(kometa_base_path(), save_folder, file_name)
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

def format_date_text(text, date_value):
    date_object = datetime.strptime(
        date_value,
        '%Y-%m-%d'
    )

    return (
        text
        .replace('{{MMMM}}', date_object.strftime('%B'))
        .replace('{{DDDD}}', date_object.strftime('%A'))
        .replace('{{YYYY}}', date_object.strftime('%Y'))
        .replace('{{YYYY}}', date_object.strftime('%Y'))
        .replace('{{MM}}', date_object.strftime('%m'))
        .replace('{{M}}', str(date_object.month))
        .replace('{{DD}}', date_object.strftime('%d'))
        .replace('{{D}}', str(date_object.day))
        .replace('{{YY}}', date_object.strftime('%y'))
    )

def write_collection_files(
    selected_list: list,      # List of selected Plex show objects
    library_slug: str,        # Cleaned library name used in file names
    description: str,         # Description name used in collection/file names
    collection_dir: str,      # Directory where collection files are written
    collection: dict,         # Collection settings
) -> int:
    collection_file = path_constructor(
        collection_dir,
        f'{library_slug}-{description}-collection.yml'
    )

    text_file = path_constructor(
        collection_dir,
        f'{library_slug}-{description}-collection.txt'
    )

    os.makedirs(
        os.path.dirname(collection_file),
        exist_ok=True
    )

    with open(
        text_file,
        'w',
        encoding='utf-8'
    ) as output:
        output.write(
            '\n'.join(
                f'{item.id.guid}'
                for item in selected_list
            )
        )

        if selected_list:
            output.write('\n')

    collection_data = dict(collection)

    collection_data.pop('name', None)
    collection_data.pop('trakt_list', None)
    collection_data.pop('trakt_list_url', None)

    collection_data['text_file'] = (
        f'config/{collection_dir}'
        f'{library_slug}-{description}-collection.txt'
    )

    with open(
        collection_file,
        'w',
        encoding='utf-8'
    ) as output:
        yaml.dump(
            {
                'collections': {
                    collection['name']: collection_data
                }
            },
            output
        )

    return len(selected_list)
## end collection file write function


def write_overlay_file(
    overlay_data: dict,         # Complete overlay document including 'overlays'
    library_slug: str,          # Cleaned library name used in the file name
    description: str,           # Description used in the file name
    overlay_dir: str,           # Directory where the overlay file is written
) -> int:
    overlay_file = path_constructor(
        overlay_dir,
        f'{library_slug}-{description}-overlay.yml'
    )

    os.makedirs(
        os.path.dirname(overlay_file),
        exist_ok=True
    )

    with open(
        overlay_file,
        'w',
        encoding='utf-8'
    ) as output:
        yaml.dump(
            overlay_data,
            output
        )

    return len(overlay_data.get('overlays', {}))
## end overlay file write function
