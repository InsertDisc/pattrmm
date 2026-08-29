from dataclasses import dataclass
from datetime import date, timedelta
import os

from ruamel.yaml import YAML

from modules.cache_handler import load_shows_cache as load_cache
from modules.plex import PlexApi
from modules.tmdb import TmdbApi
from modules.utilities import (
    ConfigLoader,
    clean_string,
    current_date,
    get_core_settings,
    write_collection_files,
    write_overlay_file,
    format_date_text,
    pattrmm_base_path
)

yaml = YAML()
yaml.preserve_quotes = True
plex = PlexApi()
tmdb = TmdbApi()
config = ConfigLoader()


@dataclass
class ReturningSoon:
    enabled: bool
    mode: str
    days_ahead: int
    collection_dir: str
    collection: dict
    overlay: dict


@dataclass
class NewStatus:
    enabled: bool
    mode: str
    considered_new: int
    collection_dir: str
    collection: dict
    overlay: dict


@dataclass
class Airing:
    enabled: bool
    mode: str
    days_ahead: int
    days_behind: int
    collection_dir: str
    collection: dict
    overlay: dict


@dataclass
class GeneralStatus:
    enabled: bool
    mode: str
    collection_dir: str
    collection: dict
    overlay: dict


## Copy and format template file for each library
def ensure_overlay_template(
    library_name: str,
    template_file: str,
    source_file: str
):
    if os.path.exists(template_file):
        return

    os.makedirs(
        os.path.dirname(template_file),
        exist_ok=True
    )

    with open(
        source_file,
        'r',
        encoding='utf-8'
    ) as source:
        template = source.read()

    template = template.replace(
        '{library}',
        clean_string(library_name)
    )

    with open(
        template_file,
        'w',
        encoding='utf-8'
    ) as output:
        output.write(template)
## end template copy


## Universal status function to build and format all 'dated' overlays.
def build_date_overlays(
    selected,
    library_slug,
    status_name,
    overlay
):
    overlays = {}

    for item in selected:
        air_date = item.next_episode.air_date

        banner_key = (
            f'{library_slug}_{status_name}_{air_date}_Banner'
        )

        status_key = (
            f'{library_slug}_{status_name}_{air_date}'
        )

        if banner_key not in overlays:
            status_settings = {}
            banner_settings = {}

            for key, value in overlay.items():

                # status_* targets the status overlay.
                # banner_* targets the banner overlay.
                # Unprefixed settings target both.
                # The prefix is removed before passing into the overlay.

                if key == 'status_text':
                    continue
                elif key.startswith('status_'):
                    status_settings[key.removeprefix('status_')] = value
                elif key.startswith('banner_'):
                    banner_settings[key.removeprefix('banner_')] = value
                else:
                    status_settings[key] = value
                    banner_settings[key] = value

            status_settings['text'] = format_date_text(
                overlay['status_text'],
                air_date
            )

            overlays[banner_key] = {
                'template': {
                    'name': f'{library_slug}_Status_Banner',
                    **banner_settings,
                },
                'plex_id': []
            }

            overlays[status_key] = {
                'template': {
                    'name': f'{library_slug}_Status',
                    **status_settings,
                },
                'plex_id': []
            }

        overlays[banner_key]['plex_id'].append(
            item.id.guid
        )

        overlays[status_key]['plex_id'].append(
            item.id.guid
        )

    return overlays
## end of dated overlay builder


## build non dated overlay list ##
def build_overlays(
    selected,
    library_slug,
    status_name,
    overlay
):
    overlays = {}

    status_settings = {}
    banner_settings = {}

    for key, value in overlay.items():

        if key == 'status_text':
            status_settings['text'] = value
        elif key.startswith('status_'):
            status_settings[key.removeprefix('status_')] = value
        elif key.startswith('banner_'):
            banner_settings[key.removeprefix('banner_')] = value
        else:
            status_settings[key] = value
            banner_settings[key] = value

    banner_key = (
        f'{library_slug}_{status_name}_Banner'
    )

    status_key = (
        f'{library_slug}_{status_name}'
    )

    overlays[banner_key] = {
        'template': {
            'name': f'{library_slug}_Status_Banner',
            **banner_settings,
        },
        'plex_id': []
    }

    overlays[status_key] = {
        'template': {
            'name': f'{library_slug}_Status',
            **status_settings,
        },
        'plex_id': []
    }

    for item in selected:
        overlays[banner_key]['plex_id'].append(
            item.id.guid
        )

        overlays[status_key]['plex_id'].append(
            item.id.guid
        )

    return overlays


## Get shows that are considered newly airing
def get_new_shows(cached, today, considered_new):
    cutoff = (
        today - timedelta(days=considered_new)
    ).isoformat()

    selected = []

    for show in cached.values():

        first_air = show.dates.first_air_date
        plex_id = show.id.guid

        if not plex_id:
            continue

        if not first_air or first_air == 'null':
            continue

        if first_air < cutoff:
            continue

        if first_air > today.isoformat():
            continue

        selected.append(show)

    selected.sort(
        key=lambda item: item.dates.first_air_date
    )

    return selected


## Get shows that are currently airing.
def get_airing_shows(
    cached,
    today,
    days_ahead,
    days_behind
):
    last_cutoff = (
        today - timedelta(days=days_behind)
    ).isoformat()

    next_cutoff = (
        today + timedelta(days=days_ahead)
    ).isoformat()

    selected = []

    for show in cached.values():

        next_air = show.next_episode.air_date
        last_air = show.last_episode.air_date
        plex_id = show.id.guid

        if not plex_id:
            continue

        if not next_air or next_air == 'null':
            continue

        if not last_air or last_air == 'null':
            continue

        ## Last episode must have aired within
        ## the previous N days, including today.
        if last_air < last_cutoff:
            continue

        ## Next episode must air within the next
        ## N days, including today.
        if next_air < current_date():
            continue

        if next_air > next_cutoff:
            continue

        selected.append(show)

    selected.sort(
        key=lambda item: item.next_episode.air_date
    )

    return selected
## end airing filter

## General status filter.
def get_shows_by_status(
    cached,
    status
):
    selected = []

    for show in cached.values():

        plex_id = show.id.guid

        if not plex_id:
            continue

        if show.status != status:
            continue

        selected.append(show)

    return selected
## end general status filter


## Just formatting some info
def info(section, message):
    print(
        f"[Extended Status][{section}] "
        f"{message}"
    )


def library_info(library_name, section, message):
    print(
        f"[{library_name}][Extended Status][{section}] "
        f"{message}"
    )
## formatting function end


## Main logic
def run():
    today = date.today()

    info(
        "Core",
        "Starting Extended Status..."
    )

    ## Define default settings for each status
    ## Dated overlays can use {{MM}} -> 04, {{M}} -> 4, {{MMMM}} -> April
    ## {{DD}} -> 09, {{D}} -> 9, {{DDDD}} -> Tuesday
    ## {{YYYY}} -> 2026, {{YY}} -> 26
    ## If built with the build_date_overlay function

    default_settings = {
        'overlay_dir': 'overlays/',

        'returning_soon': {
            'enabled': False,
            'mode': 'all',
            'days_ahead': 45,
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Returning Soon',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'RETURNING {{MM}}/{{DD}}',
                'weight': 35,
                'banner_back_color': '#81007F',
                'status_font_color': '#FFFFFF',
            },
        },

        'airing': {
            'enabled': False,
            'mode': 'overlay',
            'days_ahead': 14,
            'days_behind': 14,
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Currently Airing',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'AIRING',
                'weight': 50,
                'banner_back_color': '#006580',
                'status_font_color': '#FFFFFF',
            },
        },

        'airing_next': {
            'enabled': False,
            'mode': 'overlay',
            'days_ahead': 14,
            'days_behind': 14,
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Airing Next',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'AIRING {{MM}}/{{DD}}',
                'weight': 55,
                'banner_back_color': '#006580',
                'status_font_color': '#FFFFFF',
            },
        },

        'new': {
            'enabled': False,
            'mode': 'overlay',
            'considered_new': 14,
            'collection_dir': 'collections/',
            'collection': {
                'name': 'New Series',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'NEW',
                'weight': 60,
                'banner_back_color': '#008001',
                'status_font_color': '#FFFFFF',
            },
        },

        'new_airing_next': {
            'enabled': False,
            'mode': 'overlay',
            'considered_new': 14,
            'collection_dir': 'collections/',
            'collection': {
                'name': 'New - Airing',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'NEW - AIRING {{MM}} / {{DD}}',
                'weight': 65,
                'banner_back_color': '#008001',
                'status_font_color': '#FFFFFF',
            },
        },

        'upcoming': {
            'enabled': False,
            'mode': 'all',
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Upcoming',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'U P C O M I N G',
                'weight': 90,
                'banner_back_color': '#FC4E03',
                'status_font_color': '#FFFFFF',
            },
        },

        'returning': {
            'enabled': False,
            'mode': 'overlay',
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Recently Returned',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'R E T U R N I N G',
                'weight': 30,
                'banner_back_color': '#81007F',
                'status_font_color': '#FFFFFF',
            },
        },

        'ended': {
            'enabled': False,
            'mode': 'overlay',
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Ended',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'status_text': 'E N D E D',
                'weight': 20,
                'banner_back_color': '#000000',
                'status_font_color': '#FFFFFF',
            },
        },

        'canceled': {
            'enabled': False,
            'mode': 'overlay',
            'collection_dir': 'collections/',
            'collection': {
                'name': 'Canceled',
                'collection_order': 'custom',
                'sync_mode': 'sync',
            },
            'overlay': {
                'text': 'C A N C E L E D',
                'weight': 20,
                'banner_back_color': '#CF142B',
                'status_font_color': '#FFFFFF',
            },
        },
    }

    info(
        "Core",
        "Loading Extended Status settings"
    )

    core_settings = get_core_settings(
        'extended_status',
        1,
        default_settings
    )

    info(
        "Core",
        f"Found {len(core_settings)} library configuration(s)"
    )

    for library_name, instances in core_settings.items():
        info(
            "Core",
            f"Processing: {library_name}"
        )

        ## load stored dates and update cache for this library
        cached = load_cache(library_name)

        ## get a clean library name for files
        library_slug = clean_string(library_name)

        ## define and check template files for overlays
        template_file = os.path.join(
            pattrmm_base_path(),
            'data',
            'templates',
            config.settings_slug,
            f'{library_slug}-extended_status-template.yml'
        )

        source_file = os.path.join(
            pattrmm_base_path(),
            'cores',
            '_templates',
            'template-extended_status-overlay.yml'
        )

        ensure_overlay_template(
            library_name=library_name,
            template_file=template_file,
            source_file=source_file
        )

        ## Load the overlay template once for this library.
        with open(
            template_file,
            'r',
            encoding='utf-8'
        ) as template:
            overlay_data = yaml.load(template) or {}

        overlays = overlay_data.setdefault(
            'overlays',
            {}
        )

        ## loop through extended_status settings instance
        for extended_status in instances:

######################
### Returning Soon ###
######################

            settings = extended_status.get(
                'returning_soon',
                {}
            )

            returning_soon = ReturningSoon(**settings)

            if returning_soon.enabled:

                library_info(
                    library_name,
                    "Returning Soon",
                    "checking"
                )

                cutoff = (
                    today
                    + timedelta(days=returning_soon.days_ahead)
                )

                selected = []

                for show in cached.values():

                    status_value = show.status

                    if status_value != 'Returning Series':
                        continue

                    next_air = show.next_episode.air_date
                    last_air = show.last_episode.air_date
                    plex_id = show.id.guid

                    if not plex_id:
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

                    selected.append(show)

                selected.sort(
                    key=lambda item: item.next_episode.air_date
                )

                library_info(
                    library_name,
                    "Returning Soon",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Returning Soon",
                        f"  {item.title} "
                        f"({item.next_episode.air_date})"
                    )

                write_collection = (
                    returning_soon.mode in ('all', 'collection')
                )

                write_overlay = (
                    returning_soon.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='returning_soon',
                        collection_dir=returning_soon.collection_dir,
                        collection=returning_soon.collection
                    )

                    library_info(
                        library_name,
                        "Returning Soon",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    dated_overlays = build_date_overlays(
                        selected=selected,
                        library_slug=library_slug,
                        status_name='Returning',
                        overlay=returning_soon.overlay
                    )

                    overlays.update(dated_overlays)


#######################
### New Airing Next ###
#######################

            settings = extended_status.get(
                'new_airing_next',
                {}
            )

            new_airing_next = NewStatus(**settings)

            if new_airing_next.enabled:

                library_info(
                    library_name,
                    "New - Airing Next",
                    "checking"
                )

                cutoff = (
                    today
                    - timedelta(
                        days=new_airing_next.considered_new
                    )
                ).isoformat()

                selected = []

                for show in cached.values():

                    first_air = show.dates.first_air_date
                    next_air = show.next_episode.air_date
                    plex_id = show.id.guid

                    if not plex_id:
                        continue

                    if not first_air or first_air == 'null':
                        continue

                    if first_air < cutoff:
                        continue

                    if first_air > today.isoformat():
                        continue

                    if not next_air or next_air == 'null':
                        continue

                    selected.append(show)

                selected.sort(
                    key=lambda item: item.next_episode.air_date
                )

                library_info(
                    library_name,
                    "New - Airing Next",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "New - Airing Next",
                        f"  {item.title} "
                        f"({item.next_episode.air_date})"
                    )

                write_collection = (
                    new_airing_next.mode in ('all', 'collection')
                )

                write_overlay = (
                    new_airing_next.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='new_airing_next',
                        collection_dir=new_airing_next.collection_dir,
                        collection=new_airing_next.collection
                    )

                    library_info(
                        library_name,
                        "New - Airing Next",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_date_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='New_Airing_Next',
                            overlay=new_airing_next.overlay
                        )
                    )


###########
### New ###
###########

            settings = extended_status.get(
                'new',
                {}
            )

            new_status = NewStatus(**settings)

            if new_status.enabled:

                library_info(
                    library_name,
                    "New",
                    "checking"
                )

                cutoff = (
                    today
                    - timedelta(
                        days=new_status.considered_new
                    )
                ).isoformat()

                selected = []

                for show in cached.values():

                    first_air = show.dates.first_air_date
                    plex_id = show.id.guid

                    if not plex_id:
                        continue

                    if not first_air or first_air == 'null':
                        continue

                    if first_air < cutoff:
                        continue

                    if first_air > today.isoformat():
                        continue

                    selected.append(show)

                selected.sort(
                    key=lambda item: item.dates.first_air_date
                )

                library_info(
                    library_name,
                    "New",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "New",
                        f"  {item.title}"
                    )

                write_collection = (
                    new_status.mode in ('all', 'collection')
                )

                write_overlay = (
                    new_status.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='new_series',
                        collection_dir=new_status.collection_dir,
                        collection=new_status.collection
                    )

                    library_info(
                        library_name,
                        "New",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='New_Series',
                            overlay=new_status.overlay
                        )
                    )


###################
### Airing Next ###
###################

            settings = extended_status.get(
                'airing_next',
                {}
            )

            airing_next = Airing(**settings)

            if airing_next.enabled:

                library_info(
                    library_name,
                    "Airing Next",
                    "checking"
                )

                selected = get_airing_shows(
                    cached,
                    today,
                    airing_next.days_ahead,
                    airing_next.days_behind
                )

                library_info(
                    library_name,
                    "Airing Next",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Airing Next",
                        f"  {item.title} "
                        f"({item.next_episode.air_date})"
                    )

                write_collection = (
                    airing_next.mode in ('all', 'collection')
                )

                write_overlay = (
                    airing_next.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='airing_next',
                        collection_dir=airing_next.collection_dir,
                        collection=airing_next.collection
                    )

                    library_info(
                        library_name,
                        "Airing Next",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    dated_overlays = build_date_overlays(
                        selected=selected,
                        library_slug=library_slug,
                        status_name='Airing_Next',
                        overlay=airing_next.overlay
                    )

                    overlays.update(dated_overlays)


##############
### Airing ###
##############

            settings = extended_status.get(
                'airing',
                {}
            )

            airing = Airing(**settings)

            if airing.enabled:

                library_info(
                    library_name,
                    "Airing",
                    "checking"
                )

                selected = get_airing_shows(
                    cached,
                    today,
                    airing.days_ahead,
                    airing.days_behind
                )

                library_info(
                    library_name,
                    "Airing",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Airing",
                        f"  {item.title} "
                        f"({item.next_episode.air_date})"
                    )

                write_collection = (
                    airing.mode in ('all', 'collection')
                )

                write_overlay = (
                    airing.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='airing',
                        collection_dir=airing.collection_dir,
                        collection=airing.collection
                    )

                    library_info(
                        library_name,
                        "Airing",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='Airing',
                            overlay=airing.overlay
                        )
                    )

#################
### Returning ###
#################

            settings = extended_status.get(
                'returning',
                {}
            )

            returning = GeneralStatus(**settings)

            if returning.enabled:

                library_info(
                    library_name,
                    "Returning Series",
                    "checking"
                )

                selected = get_shows_by_status(
                    cached,
                    "Returning Series"
                )

                library_info(
                    library_name,
                    "Returning Series",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Returning Series",
                        f"  {item.title} "
                    )

                write_collection = (
                    returning.mode in ('all', 'collection')
                )

                write_overlay = (
                    returning.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='returning',
                        collection_dir=returning.collection_dir,
                        collection=returning.collection
                    )

                    library_info(
                        library_name,
                        "Returning Series",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='Returning',
                            overlay=returning.overlay
                        )
                    )

################
### Canceled ###
################

            settings = extended_status.get(
                'canceled',
                {}
            )

            canceled = GeneralStatus(**settings)

            if canceled.enabled:

                library_info(
                    library_name,
                    "Canceled",
                    "checking"
                )

                selected = get_shows_by_status(
                    cached,
                    "Canceled"
                )

                library_info(
                    library_name,
                    "Canceled",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Canceled",
                        f"  {item.title} "
                    )

                write_collection = (
                    canceled.mode in ('all', 'collection')
                )

                write_overlay = (
                    canceled.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='canceled',
                        collection_dir=canceled.collection_dir,
                        collection=canceled.collection
                    )

                    library_info(
                        library_name,
                        "Canceled",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='Canceled',
                            overlay=canceled.overlay
                        )
                    )

#############
### Ended ###
#############

            settings = extended_status.get(
                'ended',
                {}
            )

            ended = GeneralStatus(**settings)

            if ended.enabled:

                library_info(
                    library_name,
                    "Ended",
                    "checking"
                )

                selected = get_shows_by_status(
                    cached,
                    "Ended"
                )

                library_info(
                    library_name,
                    "Ended",
                    f"{len(selected)} title(s)"
                )

                for item in selected:
                    library_info(
                        library_name,
                        "Ended",
                        f"  {item.title} "
                    )

                write_collection = (
                    returning.mode in ('all', 'collection')
                )

                write_overlay = (
                    returning.mode in ('all', 'overlay')
                )

                if write_collection:
                    count = write_collection_files(
                        selected_list=selected,
                        library_slug=library_slug,
                        description='ended',
                        collection_dir=ended.collection_dir,
                        collection=ended.collection
                    )

                    library_info(
                        library_name,
                        "Ended",
                        f"Collection files written: "
                        f"{count} title(s)"
                    )

                if write_overlay:
                    overlays.update(
                        build_overlays(
                            selected=selected,
                            library_slug=library_slug,
                            status_name='Ended',
                            overlay=ended.overlay
                        )
                    )

######### Other status filters go here
        ## Write the complete overlay document once after
        ## all enabled status sections.
        if overlays:
            count = write_overlay_file(
                overlay_data=overlay_data,
                library_slug=library_slug,
                description='extended_status',
                overlay_dir=extended_status.get('overlay_dir', 'overlays/')
            )
            library_info(
                library_name,
                "Core",
                f"Overlay written: {count} overlay(s)"
            )

    info(
        "Core",
        "Extended Status complete"
    )


if __name__ == '__main__':
    run()
