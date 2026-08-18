from dataclasses import dataclass
import os

from ruamel.yaml import YAML

from modules.plex import PlexApi
from modules.utilities import clean_string, get_core_settings, path_constructor

yaml = YAML()
yaml.preserve_quotes = True
plex = PlexApi()


@dataclass
class BySize:
    order_by: str
    minimum: float
    maximum: float | None
    limit: int
    collection_title: str
    collection_save_folder: str
    collection: dict


def run():
    default_settings = {
        'order_by': 'size.desc',
        'minimum': 0,
        'maximum': None,
        'limit': 500,
        'collection_title': 'Sorted by size',
        'collection_save_folder': 'collections/',
        'collection': {
            'collection_order': 'custom',
            'sync_mode': 'sync'
        }
    }

    core_settings = get_core_settings('by_size', 1, default_settings)
    for library_name, instances in core_settings.items():
        library = plex.library(library_name)
        if library.type not in ('movie', 'show'):
            continue

        media_items = library.contents()
        for settings in instances:
            by_size = BySize(**settings)
            field, direction = by_size.order_by.split('.', 1)
            reverse = direction == 'desc'

            if field == 'size':
                sortable = media_items
            elif field == 'title':
                sortable = media_items
            elif field == 'added':
                sortable = media_items
            elif field in ('released', 'release_date'):
                sortable = media_items
                field = 'available'
            else:
                raise ValueError(f"Unsupported By Size sort field: {field}")

            filtered = [item for item in sortable if item.size is not None and by_size.minimum <= item.size and (by_size.maximum is None or item.size <= by_size.maximum)]
            filtered.sort(key=lambda item: getattr(item, 'size') if field == 'size' else getattr(item.date, field if field != 'available' else 'available_date') or '', reverse=reverse)
            filtered = filtered[:by_size.limit]

            ids = []
            for item in filtered:
                detail = plex.show(item.id.rating_key) if library.type == 'show' else plex.movie(item.id.rating_key)
                if detail.id.tmdb and detail.id.tmdb != 'null':
                    ids.append(f'tmdb:{detail.id.tmdb}')
                elif detail.id.tvdb and detail.id.tvdb != 'null':
                    ids.append(f'tvdb:{detail.id.tvdb}')
                elif detail.id.imdb and detail.id.imdb != 'null':
                    ids.append(f'imdb:{detail.id.imdb}')

            library_slug = clean_string(library_name)
            text_file = path_constructor(by_size.collection_save_folder, f'{library_slug}-by-size.txt')
            collection_file = path_constructor(by_size.collection_save_folder, f'{library_slug}-by-size.yml')
            os.makedirs(os.path.dirname(text_file), exist_ok=True)

            with open(text_file, 'w', encoding='utf-8') as output:
                output.write('\n'.join(ids))
                if ids:
                    output.write('\n')

            collection = dict(by_size.collection)
            collection.pop('trakt_list', None)
            collection.pop('trakt_list_url', None)
            collection['text_file'] = f'config/{by_size.collection_save_folder}{library_slug}-by-size.txt'

            with open(collection_file, 'w', encoding='utf-8') as output:
                yaml.dump({'collections': {by_size.collection_title: collection}}, output)

            print(f"{library_name}: By Size -> {len(ids)} titles")


if __name__ == '__main__':
    run()
