import os
from datetime import date, datetime

from ruamel.yaml import YAML

from modules.plex import PlexApi
from modules.tmdb import TmdbApi
from modules.utilities import (
    ConfigLoader,
    clean_string,
    current_date,
    to_dict,
)

yaml = YAML()
yaml.preserve_quotes = True

plex = PlexApi()
tmdb = TmdbApi()
config = ConfigLoader()

cache_expiry = config.settings_data['settings']['cache_expiry']


def status(message):
    print(f"[Cache] {message}")


def load_shows_cache(library_name):
    status(f"Loading {library_name} cache...")

    library = plex.library(library_name)
    library_slug = clean_string(library_name)
    cache_path = f'data/cache/{library_slug}_cache.yaml'

    media_items = library.contents()

    status(f"{len(media_items)} show(s) found in Plex")

    cache_data = {
        'full_sync': current_date(),
        'shows': []
    }

    if os.path.exists(cache_path):
        with open(
            cache_path,
            'r',
            encoding='utf-8'
        ) as cache_file:
            cache_data = yaml.load(cache_file) or cache_data
    else:
        status("No existing cache found. Full sync required.")

    cached = {}

    for entry in cache_data.get('shows', []):
        if isinstance(entry, dict):
            cached.update(entry)

    plex_keys = {
        str(item.id.rating_key)
        for item in media_items
    }

    removed_cache_entries = 0

    for key in list(cached):
        if key not in plex_keys:
            del cached[key]
            removed_cache_entries += 1

    if removed_cache_entries:
        status(
            f"Removed {removed_cache_entries} "
            f"show(s) no longer in Plex"
        )

    full_sync = True

    if cache_data.get('full_sync'):
        try:
            days_since_sync = (
                date.today()
                - datetime.strptime(
                    str(cache_data['full_sync']),
                    '%Y-%m-%d'
                ).date()
            ).days

            full_sync = days_since_sync >= cache_expiry

        except (TypeError, ValueError):
            status(
                "Invalid full sync date. "
                "Forcing full sync."
            )
            full_sync = True

    items_to_lookup = (
        media_items
        if full_sync
        else [
            item
            for item in media_items
            if str(item.id.rating_key) not in cached
        ]
    )

    if full_sync:
        cached = {}
        cache_data['full_sync'] = current_date()

        status(
            f"Performing full TMDB refresh "
            f"({len(items_to_lookup)} show(s))"
        )

    elif items_to_lookup:
        status(
            f"{len(items_to_lookup)} new show(s) "
            f"require TMDB lookup"
        )

    for item in items_to_lookup:
        show = plex.show(item.id.rating_key)
        tmdb_id = show.id.tmdb
        lookup_source = "Plex"

        if not tmdb_id and show.id.imdb:
            tmdb_id = tmdb.external_source(
                show.id.imdb,
                'imdb_id',
                'show'
            )
            lookup_source = "IMDb"

        if not tmdb_id and show.id.tvdb:
            tmdb_id = tmdb.external_source(
                show.id.tvdb,
                'tvdb_id',
                'show'
            )
            lookup_source = "TVDB"

        if not tmdb_id:
            status(
                f"Lookup failed: {show.title} "
                f"(no TMDB ID)"
            )
            continue

        details = tmdb.show(tmdb_id).details()

        if not details:
            status(
                f"Lookup failed: {show.title} "
                f"(no TMDB details)"
            )
            continue

        cached[str(item.id.rating_key)] = {
            'title': details.name,
            'status': details.status,
            'ids': {
                'guid': show.id.guid,
                'tmdb': str(details.show_id),
                'tvdb': show.id.tvdb,
                'imdb': show.id.imdb
            },
            'dates': {
                'year': item.date.year,
                'added': item.date.added_date,
                'available': item.date.available_date or details.first_air_date
            },
            'next_episode': to_dict(
                details.next_episode_to_air
            ),
            'last_episode': to_dict(
                details.last_episode_to_air
            )
        }

        status(
            f"Lookup: {details.name} "
            f"(TMDB {details.show_id}, {lookup_source})"
        )

    if cache_data.get('last_run') != current_date():
        refreshed = 0

        for key, entry in cached.items():
            if entry.get('status') != 'Returning Series':
                continue

            next_air = (
                entry.get('next_episode') or {}
            ).get('air_date')

            if (
                next_air
                and next_air != 'null'
                and next_air >= current_date()
            ):
                continue

            tmdb_id = (
                entry.get('ids') or {}
            ).get('tmdb')

            if not tmdb_id:
                continue

            details = tmdb.show(tmdb_id).details()

            if not details:
                status(
                    f"Refresh failed: "
                    f"{entry.get('title', 'Unknown')}"
                )
                continue

            entry['status'] = details.status
            entry['next_episode'] = to_dict(
                details.next_episode_to_air
            )
            entry['last_episode'] = to_dict(
                details.last_episode_to_air
            )

            refreshed += 1

            status(
                f"Updated: {entry.get('title', 'Unknown')}"
            )

        cache_data['last_run'] = current_date()

        if refreshed:
            status(
                f"Daily refresh complete: "
                f"{refreshed} show(s) updated"
            )

    cache_data['full_sync'] = cache_data.get(
        'full_sync',
        current_date()
    )

    cache_data['shows'] = [
        {key: value}
        for key, value in cached.items()
    ]

    os.makedirs(
        os.path.dirname(cache_path),
        exist_ok=True
    )

    with open(
        cache_path,
        'w',
        encoding='utf-8'
    ) as cache_file:
        yaml.dump(
            cache_data,
            cache_file
        )

    status(
        f"Cache complete: {len(cached)} show(s) "
        f"→ {cache_path}"
    )

    return cached
