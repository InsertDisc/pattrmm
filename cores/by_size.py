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
    collection_dir: str
    collection: dict


def run():
    default_settings = {
        'order_by': 'size.desc',
        'minimum': 0,
        'maximum': None,
        'limit': 500,
        'collection_dir': 'collections/',
        'collection': {
            'name': 'By Size',
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

            if field not in (
                'size',
                'title',
                'added',
                'released',
                'release_date'
            ):
                raise ValueError(
                    f"Unsupported By Size sort field: {field}"
                )

            items = []

            for item in media_items:
                if library.type == 'show':
                    size = plex.show(
                        item.id.rating_key
                    ).episodes().size
                else:
                    size = item.size

                if size is None:
                    continue

                if size < by_size.minimum:
                    continue

                if (
                    by_size.maximum is not None
                    and size > by_size.maximum
                ):
                    continue

                items.append(
                    (item, size)
                )

            if field == 'size':
                items.sort(
                    key=lambda item: item[1],
                    reverse=reverse
                )

            elif field == 'title':
                items.sort(
                    key=lambda item: item[0].title or '',
                    reverse=reverse
                )

            elif field == 'added':
                items.sort(
                    key=lambda item: item[0].date.added_date or '',
                    reverse=reverse
                )

            else:
                items.sort(
                    key=lambda item: item[0].date.available_date or '',
                    reverse=reverse
                )

            items = items[:by_size.limit]

            ids = []

            for item, size in items:
                if item.id.guid and item.id.guid != 'null':
                    ids.append(
                        item.id.guid
                    )

            library_slug = clean_string(library_name)

            text_file = path_constructor(
                by_size.collection_dir,
                f'{library_slug}-by-size.txt'
            )

            collection_file = path_constructor(
                by_size.collection_dir,
                f'{library_slug}-by-size.yml'
            )

            os.makedirs(
                os.path.dirname(text_file),
                exist_ok=True
            )

            with open(
                text_file,
                'w',
                encoding='utf-8'
            ) as output:
                output.write(
                    '\n'.join(ids)
                )

                if ids:
                    output.write('\n')

            collection = dict(
                by_size.collection
            )

            collection.pop('trakt_list', None)
            collection.pop('trakt_list_url', None)
            collection.pop('name')

            collection['text_file'] = (
                f'config/{by_size.collection_dir}'
                f'{library_slug}-by-size.txt'
            )

            with open(
                collection_file,
                'w',
                encoding='utf-8'
            ) as output:
                yaml.dump(
                    {
                        'collections': {
                            by_size.collection['name']: collection
                        }
                    },
                    output
                )

            print(
                f"{library_name}: By Size -> "
                f"{len(ids)} titles"
            )


if __name__ == '__main__':
    run()
