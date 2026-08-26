from dataclasses import dataclass
from datetime import datetime, timedelta
import os

from ruamel.yaml import YAML

from modules.plex import PlexApi
from modules.utilities import (
    clean_string,
    date_within_range,
    get_core_settings,
    path_constructor
)

yaml = YAML()
yaml.preserve_quotes = True
plex = PlexApi()


@dataclass
class InHistory:
    range: str
    starting: int
    ending: int | None
    increment: int
    collection_dir: str
    collection: dict


def status(library_name, message):
    print(f"[{library_name}] [In History] {message}")


def run():
    default_settings = {
        'range': 'month',
        'starting': 0,
        'ending': None,
        'increment': 1,
        'collection_dir': 'collections/',
        'collection': {
            'name': 'This {{range}} in history',
            'collection_order': 'custom',
            'sync_mode': 'sync'
        }
    }

    core_settings = get_core_settings(
        'in_history',
        3,
        default_settings
    )

    for library_name, instances in core_settings.items():
        status(
            library_name,
            "Processing library"
        )

        library = plex.library(
            library_name
        )

        media_items = library.contents()
        today = datetime.now()

        status(
            library_name,
            f"{len(media_items)} item(s) found in Plex"
        )

        if not media_items:
            status(
                library_name,
                "Skipping: library is empty"
            )
            continue

        for settings in instances:
            history = InHistory(**settings)
            library_slug = clean_string(
                library_name
            )

            status(
                library_name,
                f"Processing: {history.range} "
                f"({history.starting} -> "
                f"{history.ending or today.year}, "
                f"increment {history.increment})"
            )

            if history.range == 'day':
                start_date = today
                end_date = today

            elif history.range == 'week':
                start_date = (
                    today
                    - timedelta(
                        days=today.weekday()
                    )
                )
                end_date = (
                    start_date
                    + timedelta(days=6)
                )

            elif history.range == 'month':
                start_date = today.replace(
                    day=1
                )

                if start_date.month == 12:
                    end_date = start_date.replace(
                        day=31
                    )
                else:
                    end_date = (
                        start_date.replace(
                            month=start_date.month + 1
                        )
                        - timedelta(days=1)
                    )

            else:
                raise ValueError(
                    f"Unsupported In History range: "
                    f"{history.range}"
                )

            ending_year = (
                history.ending
                or today.year
            )

            selected = []

            for item in media_items:
                available = (
                    item.date.available_date
                )

                if not available:
                    continue

                try:
                    release_date = (
                        datetime.strptime(
                            available,
                            '%Y-%m-%d'
                        )
                    )
                except ValueError:
                    continue

                if release_date.year == today.year:
                    continue

                if not (
                    history.starting
                    <= release_date.year
                    <= ending_year
                ):
                    continue

                if (
                    ending_year
                    - release_date.year
                ) % history.increment:
                    continue

                if not date_within_range(
                    release_date,
                    start_date,
                    end_date
                ):
                    continue

                status(
                    library_name,
                    f"Checking: {item.title}"
                )

                detail = (
                    plex.show(
                        item.id.rating_key
                    )
                    if library.type == 'show'
                    else plex.movie(
                        item.id.rating_key
                    )
                )

                ids = detail.id

                if (
                    ids.tmdb
                    and ids.tmdb != 'null'
                ):
                    selected.append(
                        f'tmdb:{ids.tmdb}'
                    )

                elif (
                    ids.tvdb
                    and ids.tvdb != 'null'
                ):
                    selected.append(
                        f'tvdb:{ids.tvdb}'
                    )

                elif (
                    ids.imdb
                    and ids.imdb != 'null'
                ):
                    selected.append(
                        f'imdb:{ids.imdb}'
                    )

                else:
                    status(
                        library_name,
                        f"No usable ID: "
                        f"{item.title}"
                    )

            selected = list(
                dict.fromkeys(selected)
            )

            status(
                library_name,
                f"Selected {len(selected)} "
                f"title(s)"
            )

            text_file = path_constructor(
                history.collection_dir,
                f'{library_slug}-'
                f'{history.range}-in-history.txt'
            )

            collection_file = path_constructor(
                history.collection_dir,
                f'{library_slug}-'
                f'{history.range}-in-history.yml'
            )

            os.makedirs(
                os.path.dirname(text_file),
                exist_ok=True
            )

            status(
                library_name,
                f"Writing text file: "
                f"{text_file}"
            )

            with open(
                text_file,
                'w',
                encoding='utf-8'
            ) as output:
                output.write(
                    '\n'.join(selected)
                )

                if selected:
                    output.write('\n')

            title = (
                history.collection['name']
                .replace(
                    '{{range}}',
                    history.range
                )
                .replace(
                    '{{Range}}',
                    history.range.capitalize()
                )
            )

            collection = dict(
                history.collection
            )

            collection.pop(
                'name',
                None
            )

            collection.pop(
                'trakt_list',
                None
            )

            collection.pop(
                'trakt_list_url',
                None
            )

            collection['text_file'] = (
                f'config/'
                f'{history.collection_dir}'
                f'{library_slug}-'
                f'{history.range}-in-history.txt'
            )

            status(
                library_name,
                f"Writing collection file: "
                f"{collection_file}"
            )

            with open(
                collection_file,
                'w',
                encoding='utf-8'
            ) as output:
                yaml.dump(
                    {
                        'collections': {
                            title: collection
                        }
                    },
                    output
                )

            status(
                library_name,
                f"Complete: "
                f"{len(selected)} title(s)"
            )


if __name__ == '__main__':
    run()
