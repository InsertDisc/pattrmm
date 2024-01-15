from dataclasses import dataclass, fields, asdict
from modules.utilities import get_core_settings
from modules.utilities import path_constructor
from modules.utilities import clean_string
from modules.utilities import ConfigLoader
from modules.utilities import base_path
from modules.plex import PlexApi
from modules.plex import ItemDetails, ItemID, ItemDate
plex = PlexApi()
configuration_data = ConfigLoader()
library_settings = configuration_data.settings
pmm_config = configuration_data.pmm_config

@dataclass
class BySize:
    trakt_list_privacy: str = 'private'
    direction: str = 'desc'
    minimum: int = 0
    maximum: int = None
    metadata_save_folder: str = 'metadata/'
    collection_title: str = 'Sorted by size'
    collection: dict = {
        'visible_home': 'true',
        'visible_shared': 'true',
        'collection_order': 'custom',
        'sync_mode': 'sync'
    }



def run():
    allowed_instances = 1

    # Define default settings
    default_settings = BySize()

    core_name = 'by_size'
    core_settings = get_core_settings(core_name, allowed_instances, default_settings)
    for library_name, core_settings_list in core_settings.items():
        # Library loop starts here

        library_slug = clean_string(library_name) # Get a clean library name for trakt
        print(f"Library slug: {library_slug}")

        print(f"Library: {library_name}")

        



        for settings in core_settings_list:

            library = plex.library(library_name)
            library_list = library.contents()
            if library.type == 'show':
                content_list = []
                for media in library_list:
                    show = plex.show(media.id.rating_key)
                    print(f"Calculating size for {show.title} - {show.size}")
                    content_list.append(ItemDetails(
                        title=show.title,
                        id=ItemID(
                            tmdb=show.id.tmdb,
                            imdb=show.id.imdb,
                            tvdb=show.id.tvdb
                        ),
                        date=ItemDate(
                            added_date=show.date.added_date,
                            year=show.date.year,
                            available_date=show.date.available_date
                        ),
                        size=show.size
                    ))
                    #content_list.append({'title': show.title, 'rating_key': show.id.rating_key, 'size': show.size})
                size_sorted_list = sorted(content_list, key=lambda x: x.size, reverse=True)

            if library.type == 'movie':
                # size is built in to the movie response data
                size_sorted_list = sorted(library_list, key=lambda x: x.size, reverse=True)


            # Instance of core per library starts here. Main operations of the Core should be in this indent.

            by_size = BySize(**settings) # Unpack instance settings into dataclass.
            by_size.meta['trakt_list_url'] = f"https://trakt.tv/users/{pmm_config.trakt.username}/lists/sorted-by-size-{library_slug}"

            # Settings can be referenced by dataclass now
            print(by_size.maximum)
            print(by_size.collection_title)
            for key, value in by_size.meta.items():
                print(f"\tmeta: {key} - {value}")

            # Or as a loop
            by_size_dict = asdict(by_size) # Turn dataclass instance into a dictionary item
            for item, value in by_size_dict.items(): # Iterate through dictionary
                if item == 'meta':
                    for keys, values in value.items():
                        print(f"{keys} - {values}")
                else:
                    print(f"{item} - {value}")




            size_in_range_list = [
                    item for item in size_sorted_list
                    if (
                        by_size.minimum <= item.size and
                        (by_size.maximum is None or item.size <= by_size.maximum)
                    )
                ]
            for v in size_in_range_list:
                print(f"Title: {v.title}, Size: {v.size} GB")

            # uploading to trakt or any functions this instance needs goes in this indent
            # for instance, i'd upload the size_in_range_list here and remove unused collections from plex here
            

        # path_constructor uses base path for file locations
        print(base_path())
        # define any files you need
        metadata_file = f"{library_slug}-by-size-metadata.yml"

        # get your save path
        metadata_file_path = path_constructor(by_size.metadata_save_folder, metadata_file)
        print(metadata_file_path)
        
