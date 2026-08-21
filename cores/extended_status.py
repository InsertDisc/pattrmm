from dataclasses import dataclass
from datetime import date, datetime, timedelta
import os

from ruamel.yaml import YAML

from modules.cache_handler import load_shows_cache as load_cache
from modules.plex import PlexApi
from modules.tmdb import TmdbApi
from modules.utilities import (
    clean_string,
    current_date,
    get_core_settings,
    path_constructor,
    to_dict,
)

yaml = YAML()
yaml.preserve_quotes = True
today = date.today()
plex = PlexApi()
tmdb = TmdbApi()


@dataclass
class ReturningSoon:
    enabled: bool
    mode: str
    days_ahead: int
    collection_dir: str
    overlay_dir: str
    collection: dict
    overlay: dict

@dataclass
class NewStatus:
    enabled: bool
    mode: str
    considered_new: str
    collection_dir: str
    overlay_dir: str
    collection: dict
    overlay: dict

@dataclass
class GeneralStatus:
    enabled: bool
    mode: str
    collection_dir: str
    overlay_dir: str
    collection: dict
    overlay: dict


def status(message):
    print(f"[Extended Status] {message}")


def run():
    status("Starting Extended Status...")

    default_settings = {
        'returning_soon': {
            'enabled': False,
            'mode': 'all',
            'days_ahead': 45,
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Returning Soon',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'RETURNING {{MM/DD}}',
                'group': 'returning_soon',
                'weight': 35,
                'back_color': '#81007F',
                'color': '#FFFFFF',
            },
        },

        'airing': {
            'enabled': False,
            'mode': 'all',
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Currently Airing',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'AIRING',
                'group': 'airing',
                'weight': 50,
                'back_color': '#343399',
                'color': '#FFFFFF',
            },
        },

        'airing_next': {
            'enabled': False,
            'mode': 'all',
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Airing Next',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'AIRING {{MM}}/{{DD}}',
                'group': 'airing_next',
                'weight': 55,
                'back_color': '#343399',
                'color': '#FFFFFF',
            },
        },

        'new': {
            'enabled': False,
            'mode': 'all',
            'considered_new': 14,
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'New Series',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'N E W  S E R I E S',
                'group': 'new',
                'weight': 60,
                'back_color': '#008001',
                'color': '#FFFFFF',
            },
        },

        'new_airing_next': {
            'enabled': False,
            'mode': 'all',
            'considered_new': 14,
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'New - Airing {{MM}}/{{DD}}',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'NEW · AIRING',
                'group': 'new_next_air',
                'weight': 65,
                'back_color': '#008001',
                'color': '#FFFFFF',
            },
        },

        'upcoming': {
            'enabled': False,
            'mode': 'all',
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Upcoming',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'U P C O M I N G',
                'group': 'upcoming',
                'weight': 90,
                'back_color': '#FC4E03',
                'color': '#FFFFFF',
            },
        },

        'returning': {
            'enabled': False,
            'mode': 'overlay',
            'days': 7,
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Recently Returned',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'R E T U R N I N G',
                'group': 'returning',
                'weight': 30,
                'back_color': '#81007F',
                'color': '#FFFFFF',
            },
        },

        'ended': {
            'enabled': False,
            'mode': 'overlay',
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Ended',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'E N D E D',
                'group': 'ended',
                'weight': 20,
                'back_color': '#000000',
                'color': '#FFFFFF',
            },
        },

        'canceled': {
            'enabled': False,
            'mode': 'overlay',
            'collection_dir': 'collections/',
            'overlay_dir': 'overlays/',
            'collection': {
                'name': 'Canceled',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'C A N C E L E D',
                'group': 'canceled',
                'weight': 20,
                'back_color': '#CF142B',
                'color': '#FFFFFF',
            },
        },
}

    status("Loading Extended Status settings")

    core_settings = get_core_settings('extended_status', 1, default_settings)

    status(f"Found {len(core_settings)} library configuration(s)")

    for library_name, instances in core_settings.items():
        status(f"Processing: {library_name}")

        library = plex.library(library_name)

        if library.type != 'show':
            status(
                f"Skipping {library_name}: "
                "not a Show library"
            )
            continue

        for extended_status in instances:
            settings = extended_status.get(
                'returning_soon',
                {}
            )

            returning_soon = ReturningSoon(**settings)

            if not returning_soon.enabled:
                continue

            library_slug = clean_string(library_name)

            cutoff = (
                today
                + timedelta(days=returning_soon.days_ahead)
            )

            selected = []
            cached = load_cache(library_name)

            for entry in cached.values():
                title = entry.get('title', 'Unknown')

                status_value = entry.get('status')

                if status_value != 'Returning Series':
                    continue

                next_air = (
                    entry.get('next_episode') or {}
                ).get('air_date')

                last_air = (
                    entry.get('last_episode') or {}
                ).get('air_date')

                tmdb_id = (
                    entry.get('ids') or {}
                ).get('tmdb')

                if not tmdb_id:
                    continue

                if not next_air or next_air == 'null':
                    continue

                if next_air <= current_date():
                    continue

                if next_air > cutoff.isoformat():
                    continue

                if (
                    last_air
                    and last_air >= (
                        today - timedelta(days=14)
                    ).isoformat()
                ):
                    continue

                selected.append(entry)

            selected.sort(
                key=lambda item: item['next_episode']['air_date']
            )

            status(
                f"{library_name}: "
                f"{len(selected)} Returning Soon title(s)"
            )

            for item in selected:
                status(
                    f"  {item['title']} "
                    f"({item['next_episode']['air_date']})"
                )

            write_collection = (
                returning_soon.mode in ('all', 'collection')
            )

            write_overlay = (
                returning_soon.mode in ('all', 'overlay')
            )

            if write_collection:
                collection_file = path_constructor(
                    returning_soon.collection_dir,
                    f'{library_slug}-returning-soon.yml'
                )

                text_file = path_constructor(
                    returning_soon.collection_dir,
                    f'{library_slug}-returning-soon-collection.txt'
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
                            f"tmdb:{item['ids']['tmdb']}"
                            for item in selected
                        )
                    )

                    if selected:
                        output.write('\n')

                collection = dict(
                    returning_soon.collection
                )

                collection.pop('name', None)
                collection.pop('trakt_list', None)
                collection.pop('trakt_list_url', None)

                collection['text_file'] = (
                    f"config/{returning_soon.collection_dir}"
                    f"{library_slug}-returning-soon-collection.txt"
                )

                with open(
                    collection_file,
                    'w',
                    encoding='utf-8'
                ) as output:
                    yaml.dump(
                        {
                            'collections': {
                                returning_soon.collection['name']:
                                    collection
                            }
                        },
                        output
                    )

                status(
                    f"Collection files written: "
                    f"{len(selected)} title(s)"
                )

            if write_overlay:
                overlay_file = path_constructor(
                    returning_soon.overlay_dir,
                    f'{library_slug}-returning-soon-overlay.yml'
                )

                os.makedirs(
                    os.path.dirname(overlay_file),
                    exist_ok=True
                )

                overlays = {}

                for item in selected:
                    air_date = item['next_episode']['air_date']

                    date_text = datetime.strptime(
                        air_date,
                        '%Y-%m-%d'
                    ).strftime('%m/%d')

                    overlay_key = (
                        f'{library_slug}_Returning_{air_date}'
                    )

                    if overlay_key not in overlays:
                        overlay = dict(
                            returning_soon.overlay
                        )

                        overlay_text = (
                            overlay.get(
                                'text',
                                'RETURNING {{MM/DD}}'
                            ).replace(
                                '{{MM/DD}}',
                                date_text
                            )
                        )

                        overlay['text'] = (
                            f'text({overlay_text})'
                        )

                        if 'text_color' in overlay:
                            overlay['font_color'] = (
                                overlay.pop('text_color')
                            )

                        if 'background_color' in overlay:
                            overlay['back_color'] = (
                                overlay.pop('background_color')
                            )

                        overlays[overlay_key] = {
                            'tmdb_show': [],
                            'overlay': overlay
                        }

                    overlays[overlay_key]['tmdb_show'].append(
                        item['ids']['tmdb']
                    )

                with open(
                    overlay_file,
                    'w',
                    encoding='utf-8'
                ) as output:
                    yaml.dump(
                        {'overlays': overlays},
                        output
                    )

                status(
                    f"Overlay written: "
                    f"{len(overlays)} group(s)"
                )

            print(
                f"{library_name}: Returning Soon -> "
                f"{len(selected)} titles"
            )

    status("Returning Soon complete")


if __name__ == '__main__':
    run()
