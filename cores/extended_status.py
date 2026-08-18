from dataclasses import dataclass
from datetime import date, datetime, timedelta
import os

from ruamel.yaml import YAML

from modules.plex import PlexApi
from modules.tmdb import TmdbApi
from modules.utilities import ConfigLoader, clean_string, current_date, get_core_settings, path_constructor, to_dict

yaml = YAML()
yaml.preserve_quotes = True

plex = PlexApi()
tmdb = TmdbApi()


@dataclass
class ReturningSoon:
    days_ahead: int
    refresh: int
    collection_name: str
    collection_save_folder: str
    overlay_save_folder: str
    text: str
    collection: dict
    overlay: dict


def run():
    default_settings = {
        'days_ahead': 45,
        'refresh': 7,
        'collection_name': 'Returning Soon',
        'collection_save_folder': 'collections/',
        'overlay_save_folder': 'overlays/',
        'text': 'RETURNING',
        'collection': {
            'collection_order': 'custom',
            'sync_mode': 'sync'
        },
        'overlay': {
            'weight': 35,
            'group': 'returning_soon',
            'horizontal_align': 'center',
            'vertical_align': 'top',
            'horizontal_offset': 0,
            'vertical_offset': 0,
            'font_color': '#FFFFFF',
            'back_color': '#81007F'
        }
    }

    core_settings = get_core_settings('returning_soon', 1, default_settings)

    for library_name, instances in core_settings.items():
        library = plex.library(library_name)
        if library.type != 'show':
            print(f"'{library_name}' is not a Show library. Skipping Returning Soon.")
            continue

        for settings in instances:
            returning_soon = ReturningSoon(**settings)
            library_slug = clean_string(library_name)
            cache_path = path_constructor('data/cache/', f'{library_slug}_cache.yaml')

            media_items = library.contents()
            cache_data = {'full_sync': current_date(), 'shows': []}

            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as cache_file:
                    cache_data = yaml.load(cache_file) or cache_data

            cached = {}
            for entry in cache_data.get('shows', []):
                if isinstance(entry, dict):
                    cached.update(entry)

            plex_keys = {str(item.id.rating_key) for item in media_items}
            for key in list(cached):
                if key not in plex_keys:
                    del cached[key]

            full_sync = True
            if cache_data.get('full_sync'):
                try:
                    full_sync = (date.today() - datetime.strptime(str(cache_data['full_sync']), '%Y-%m-%d').date()).days >= returning_soon.refresh
                except (TypeError, ValueError):
                    full_sync = True

            items_to_lookup = media_items if full_sync else [
                item for item in media_items if str(item.id.rating_key) not in cached
            ]

            if full_sync:
                cached = {}
                cache_data['full_sync'] = current_date()
                print(f"{library_name}: refreshing TMDB cache")

            for item in items_to_lookup:
                show = plex.show(item.id.rating_key)
                tmdb_id = show.id.tmdb

                if not tmdb_id and show.id.imdb:
                    tmdb_id = tmdb.external_source(show.id.imdb, 'imdb_id', 'show')
                if not tmdb_id and show.id.tvdb:
                    tmdb_id = tmdb.external_source(show.id.tvdb, 'tvdb_id', 'show')
                if not tmdb_id:
                    print(f"{show.title}: no TMDB ID found. Skipping cache entry.")
                    continue

                details = tmdb.show(tmdb_id).details()
                if details:
                    cached[str(item.id.rating_key)] = {
                        'title': details.name,
                        'status': details.status,
                        'ids': {
                            'tmdb': str(details.show_id),
                            'tvdb': show.id.tvdb,
                            'imdb': show.id.imdb
                        },
                        'dates': {
                            'year': item.date.year,
                            'added': item.date.added_date,
                            'available': item.date.available_date
                        },
                        'next_episode': to_dict(details.next_episode_to_air),
                        'last_episode': to_dict(details.last_episode_to_air)
                    }

            today = date.today()
            if cache_data.get('last_run') != current_date():
                for key, entry in cached.items():
                    if entry.get('status') != 'Returning Series':
                        continue

                    next_air = (entry.get('next_episode') or {}).get('air_date')
                    if next_air and next_air != 'null' and next_air > current_date():
                        continue

                    tmdb_id = (entry.get('ids') or {}).get('tmdb')
                    if not tmdb_id:
                        continue

                    details = tmdb.show(tmdb_id).details()
                    if details:
                        entry['status'] = details.status
                        entry['next_episode'] = to_dict(details.next_episode_to_air)
                        entry['last_episode'] = to_dict(details.last_episode_to_air)

                cache_data['last_run'] = current_date()

            cache_data['full_sync'] = cache_data.get('full_sync', current_date())
            cache_data['shows'] = [{key: value} for key, value in cached.items()]
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as cache_file:
                yaml.dump(cache_data, cache_file)

            cutoff = today + timedelta(days=returning_soon.days_ahead)
            selected = []
            for entry in cached.values():
                if entry.get('status') != 'Returning Series':
                    continue

                next_air = (entry.get('next_episode') or {}).get('air_date')
                last_air = (entry.get('last_episode') or {}).get('air_date')
                tmdb_id = (entry.get('ids') or {}).get('tmdb')

                if not tmdb_id or not next_air or next_air == 'null':
                    continue
                if next_air <= current_date() or next_air > cutoff.isoformat():
                    continue
                if last_air and last_air >= (today - timedelta(days=14)).isoformat():
                    continue

                selected.append(entry)

            selected.sort(key=lambda item: item['next_episode']['air_date'])

            collection_file = path_constructor(
                returning_soon.collection_save_folder,
                f'{library_slug}-returning-soon.yml'
            )
            text_file = path_constructor(
                returning_soon.collection_save_folder,
                f'{library_slug}-returning-soon.txt'
            )
            overlay_file = path_constructor(
                returning_soon.overlay_save_folder,
                f'{library_slug}-returning-soon-overlay.yml'
            )

            os.makedirs(os.path.dirname(collection_file), exist_ok=True)
            os.makedirs(os.path.dirname(overlay_file), exist_ok=True)

            with open(text_file, 'w', encoding='utf-8') as output:
                output.write('\n'.join(f"tmdb:{item['ids']['tmdb']}" for item in selected))
                if selected:
                    output.write('\n')

            collection = dict(returning_soon.collection)
            collection.pop('trakt_list', None)
            collection.pop('trakt_list_url', None)
            collection['text_file'] = f"config/{returning_soon.collection_save_folder}{library_slug}-returning-soon.txt"

            with open(collection_file, 'w', encoding='utf-8') as output:
                yaml.dump({'collections': {returning_soon.collection_name: collection}}, output)

            overlays = {}
            for item in selected:
                air_date = item['next_episode']['air_date']
                date_text = datetime.strptime(air_date, '%Y-%m-%d').strftime('%m/%d')
                overlay_key = f'{library_slug}_Returning_{air_date}'

                if overlay_key not in overlays:
                    overlay = dict(returning_soon.overlay)
                    overlay['name'] = f"text({returning_soon.text} {date_text})"
                    overlays[overlay_key] = {
                        'tmdb_show': [],
                        'overlay': overlay
                    }

                overlays[overlay_key]['tmdb_show'].append(item['ids']['tmdb'])

            with open(overlay_file, 'w', encoding='utf-8') as output:
                yaml.dump({'overlays': overlays}, output)

            print(f"{library_name}: Returning Soon -> {len(selected)} titles")


if __name__ == '__main__':
    run()
