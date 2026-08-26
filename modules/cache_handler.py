import json
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime

from modules.plex import PlexApi
from modules.tmdb import TmdbApi
from modules.utilities import (
    ConfigLoader,
    clean_string,
    current_date,
    to_dict,
)

plex = PlexApi()
tmdb = TmdbApi()
config = ConfigLoader()

cache_expiry = config.settings_data['settings']['cache_expiry']

# Cached show data is returned as dataclasses.
# Access show data via attributes:
# show.ids.guid, show.title, show.dates.added,
# show.status, show.next_episode.air_date,
# show.next_episode.episode_number

@dataclass
class Episode:
    id: int | None = None
    name: str | None = None
    air_date: str | None = None
    episode_number: int | None = None
    season_number: int | None = None
    episode_type: str | None = None


@dataclass
class ShowIds:
    guid: str | None = None
    tmdb: str | None = None
    tvdb: str | None = None
    imdb: str | None = None


@dataclass
class ShowDates:
    year: int | None = None
    added: str | None = None
    first_air_date: str | None = None
    last_air_date: str | None = None


@dataclass
class Show:
    title: str
    status: str
    ids: ShowIds
    dates: ShowDates
    next_episode: Episode
    last_episode: Episode


def status(message):
    print(f"[Cache] {message}")


def load_shows_cache(library_name):
    status(f"Loading {library_name} cache...")

    status(f"Gathering Plex data for {library_name}")
    library = plex.library(library_name)
    library_slug = clean_string(library_name)
    cache_path = f'data/cache/{library_slug}_cache.json'

    media_items = library.contents()

    status(f"{len(media_items)} show(s) found in Plex")

    cache_data = {
        'full_sync': None,
        'shows': {}
    }

    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as cache_file:
            try:
                cache_data = json.load(cache_file) or cache_data
            except json.JSONDecodeError:
                status("Invalid cache found. Full sync required.")
    else:
        status("No existing cache found. Full sync required.")

    cached = {}

    for key, entry in cache_data.get('shows', {}).items():
        cached[key] = Show(
            title=entry.get('title', 'Unknown'),
            status=entry.get('status', 'Unknown'),
            ids=ShowIds(**entry.get('ids', {})),
            dates=ShowDates(**entry.get('dates', {})),
            next_episode=Episode(**(entry.get('next_episode') or {})),
            last_episode=Episode(**(entry.get('last_episode') or {}))
        )

    status(f"{len(cached)} show(s) in cache")

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
        cache_data['last_run'] = current_date()

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

        cached[str(item.id.rating_key)] = Show(
            title=details.name,
            status=details.status,
            ids=ShowIds(
                guid=show.id.guid,
                tmdb=str(details.show_id),
                tvdb=show.id.tvdb,
                imdb=show.id.imdb
            ),
            dates=ShowDates(
                year=item.date.year,
                added=item.date.added_date,
                first_air_date=(
                    details.first_air_date
                    or item.date.available_date
                ),
                last_air_date=details.last_air_date
            ),
            next_episode=Episode(
                **to_dict(details.next_episode_to_air)
            ),
            last_episode=Episode(
                **to_dict(details.last_episode_to_air)
            )
        )

        status(
            f"Lookup: {details.name} "
            f"({lookup_source}, TMDB {details.show_id})"
        )

    if cache_data.get('last_run') != current_date():
        refreshed = 0
        unchanged = 0

        for key, entry in cached.items():
            if entry.status != 'Returning Series':
                continue

            next_air = entry.next_episode.air_date

            if (
                next_air
                and next_air != 'null'
                and next_air >= current_date()
            ):
                continue

            tmdb_id = entry.ids.tmdb

            if not tmdb_id:
                continue

            details = tmdb.show(tmdb_id).details()

            if not details:
                status(
                    f"Refresh failed: "
                    f"{entry.title}"
                )
                continue

            new_status = details.status
            new_next_episode = Episode(
                **to_dict(details.next_episode_to_air)
            )
            new_last_episode = Episode(
                **to_dict(details.last_episode_to_air)
            )

            changed = (
                entry.status != new_status
                or entry.next_episode != new_next_episode
                or entry.last_episode != new_last_episode
            )

            if changed:
                entry.status = new_status
                entry.next_episode = new_next_episode
                entry.last_episode = new_last_episode

                refreshed += 1

                status(
                    f"Updated: {entry.title}"
                )
            else:
                unchanged += 1

        cache_data['last_run'] = current_date()

        status(
            f"Daily refresh complete: "
            f"{refreshed} show(s) updated, "
            f"{unchanged} unchanged"
        )

    else:
        status("Daily refresh skipped: already ran today")
    cache_data['shows'] = {
        key: asdict(value)
        for key, value in cached.items()
    }

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    with open(cache_path, 'w', encoding='utf-8') as cache_file:
        json.dump(cache_data, cache_file, indent=2)

    status(
        f"Cache operation complete."
    )

    return cached
