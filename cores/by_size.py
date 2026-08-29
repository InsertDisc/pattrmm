from dataclasses import dataclass

from modules.plex import PlexApi
from modules.utilities import (
    clean_string,
    get_core_settings,
    write_collection_files
)

plex = PlexApi()


@dataclass
class BySize:
    enabled: bool
    order_by: str
    minimum: float
    maximum: float | None
    limit: int
    collection_dir: str
    collection: dict


## Just formatting some info
def status(library_name, message):
    print(
        f"[{library_name}][By Size] "
        f"{message}"
    )
## formatting function end


def run():
    default_settings = {
        'enabled': True,
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

    core_settings = get_core_settings(
        'by_size',
        1,
        default_settings
    )

    for library_name, instances in core_settings.items():
        library = plex.library(library_name)

        if library.type not in ('movie', 'show'):
            continue

        media_items = library.contents()

        for settings in instances:
            by_size = BySize(**settings)

            status(
                library_name,
                "checking"
            )

            if not by_size.enabled:
                status(library_name, "Skipping: By Size disabled for this instance")
                continue

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

            if library.type == 'show':
                status(
                    library_name,
                    "calculating show sizes"
                )

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

            selected = [
                item
                for item, size in items
            ]

            status(
                library_name,
                f"{len(selected)} title(s)"
            )

            library_slug = clean_string(library_name)

            count = write_collection_files(
                selected_list=selected,
                library_slug=library_slug,
                description='by-size',
                collection_dir=by_size.collection_dir,
                collection=by_size.collection
            )

            status(
                library_name,
                f"Collection files written: {count} title(s)"
            )


if __name__ == '__main__':
    run()
