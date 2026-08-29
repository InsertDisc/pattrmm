from dataclasses import dataclass
from datetime import datetime, timedelta

from modules.plex import PlexApi
from modules.utilities import (
    clean_string,
    get_core_settings,
    to_dict,
    write_collection_files
)


plex = PlexApi()


@dataclass
class NewShows:
    enabled: bool
    first_episode_aired: int
    collection_dir: str
    collection: dict


def status(library_name, message):
    print(
        f"[{library_name}] [New Shows] {message}"
    )


def run():
    default_settings = {
        'enabled': False,
        'first_episode_aired': 45,
        'collection_dir': 'collections/',
        'collection': {
            'name': 'New Shows',
            'collection_order': 'custom',
            'sync_mode': 'sync'
        }
    }

    core_settings = get_core_settings(
        'new_shows',
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

        if library.type != 'show':
            print(f'Invalid library type: --> {library.type} <-- for this core')
            print(f'Skipping: {library_name}')
            continue

        media_items = library.contents()

        status(
            library_name,
            f"{len(media_items)} show(s) found in Plex"
        )

        if not media_items:
            status(
                library_name,
                "Skipping: library is empty"
            )
            continue

        for settings in instances:

            new_shows = NewShows(**settings)

            if not new_shows.enabled:
                status(
                    library_name,
                    "Skipping: New Shows disabled "
                    "in instance"
                )
                continue

            status(
                library_name,
                f"Processing: First episode aired "
                f"within {new_shows.first_episode_aired} day(s)"
            )

            today = datetime.now()

            cutoff = (
                today
                - timedelta(
                    days=new_shows.first_episode_aired
                )
            )

            selected = []

            for item in media_items:

                plex_id = item.id.guid

                if not plex_id:
                    continue

                available = (
                    item.date.available_date
                )

                if not available:
                    continue

                try:
                    first_episode_aired = (
                        datetime.strptime(
                            available,
                            '%Y-%m-%d'
                        )
                    )

                except ValueError:
                    continue

                if first_episode_aired < cutoff:
                    continue

                if first_episode_aired > today:
                    continue

                selected.append(
                    item
                )

            selected.sort(
                key=lambda item: item.date.available_date,
                reverse=True
            )

            status(
                library_name,
                f"Selected {len(selected)} title(s)"
            )

            for item in selected:
                status(
                    library_name,
                    f"  {item.title} "
                    f"({item.date.available_date})"
                )

            count = write_collection_files(
                selected_list=selected,
                library_slug=clean_string(
                    library_name
                ),
                description='new_shows',
                collection_dir=new_shows.collection_dir,
                collection=new_shows.collection
            )

            status(
                library_name,
                f"Complete: {count} title(s)"
            )


if __name__ == '__main__':
    run()
