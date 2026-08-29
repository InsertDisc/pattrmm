from dataclasses import dataclass
from datetime import datetime, timedelta

from modules.plex import PlexApi
from modules.utilities import (
    clean_string,
    date_within_range,
    get_core_settings,
    to_dict,
    write_collection_files
)


plex = PlexApi()


@dataclass
class InHistory:
    enabled: bool
    range: str
    starting: int
    ending: int | None
    increment: int
    collection_dir: str
    collection: dict


def status(library_name, message):
    print(
        f"[{library_name}] [In History] {message}"
    )


def run():
    default_settings = {
        'enabled': False,
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
        None,
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

        instance_counts = {}

        for settings in instances:
            history = InHistory(**settings)

            if not history.enabled:
                status(
                    library_name,
                    "Skipping: In History disabled "
                    f"in instance"
                )
                continue

            instance_int = instance_counts.get(
                history.range,
                0
            )

            description = (
                f'{history.range}-in-history'
                f'{f"-{instance_int}" if instance_int else ""}'
            )

            instance_counts[history.range] = (
                instance_int + 1
            )

            status(
                library_name,
                f"Processing: This {history.range} in history: "
                f"From ({history.starting} -> "
                f"To {history.ending or today.year}, "
                f"Increment of {history.increment} year/s)"
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

                selected.append(
                    item
                )

            status(
                library_name,
                f"Selected {len(selected)} title(s)"
            )

            for item in selected:
                print(
                    f"  {item.title} "
                    f"({item.date.available_date})"
                )

            collection = dict(
                history.collection
            )

            collection['name'] = (
                collection['name']
                .replace(
                    '{{range}}',
                    history.range
                )
                .replace(
                    '{{Range}}',
                    history.range.capitalize()
                )
            )

            count = write_collection_files(
                selected_list=selected,
                library_slug=clean_string(
                    library_name
                ),
                description=description,
                collection_dir=history.collection_dir,
                collection=collection
            )

            status(
                library_name,
                f"Complete: {count} title(s)"
            )


if __name__ == '__main__':
    run()
