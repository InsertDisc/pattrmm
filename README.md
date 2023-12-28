
PATTRMM (Plex Assistant To The Regional Meta Manager) is a python script that automates generating
overlay and metadata files for non 'out-of-the-box' collections for Plex Meta Manager. This may include
lists that need sorted in specific ways or that need dynamically generated text for overlays.

Requirements:    
    Trakt MUST be setup in your PMM installation to post 'returning soon' series and various 'extensions' to.
    This is also what the *-returning-soon.yml and *-in-history.yml files will pull from.
    The only must-have module is ruamel.yaml. This is included in requirements.txt. 
    Note, some environments may also need 'requests' installed.
    If you want to use the default template font you will also need the font 
    from the extras folder in your pmm fonts folder.

For stand-alone setup:
    
    Just drop pattrymm.py in a subfolder of your Plex Meta Manager config folder 
    (i.e. Plex-meta-manager/config/pattrmm/pattrmm.py) and run it. 
    A settings file will be created in the newly created preferences folder. 
    The script will stop so you can fill in the appropriate settings in preferences/settings.yml.
    You can modify the appearance of the generated overlays file using the
    preferences/*-returning-soon-template.yml files. 
    Run the script again after you make your changes to initiate a full cycle.

    UPDATING: To update the stand-alone version, you need to delete OR replace vars.py and replace pattrmm.py.

Docker Compose:
```
services:
  pattrmm:
    image: ghcr.io/insertdisc/pattrmm:develop
    container_name: pattrmm
    environment:
      - PUID=1000
      - GUID=1000
      - TZ=America/New_York
      - PATTRMM_TIME=02:00  # Schedule run time
    volumes:
      - ./pattrmm/data:/data
      - ./pattrmm/preferences:/preferences
      - ./pmm/config:/config
    restart: unless-stopped  
```
If using the docker version, you can initialize the settings file with this command.
```
docker run --rm -it -v "./pattrmm/preferences:/preferences" ghcr.io/insertdisc/pattrmm:develop --run
```
The DEVELOP branch is slightly ahead of the latest branch. 
Extensions have been added and will continue to expand.
```
Extensions Available:
  in_history
    This extension uses the Originally Available At date within Plex to create Trakt lists
    based on a specified range per library and a corresponding 'in-history' metadata file
    for use with that library.
  by_size
    This extension uses information available within Plex to approximate Movie sizes, without
    needing access to the filesystem, to create an ordered and filtered trakt list and accompanying
    'by-size' metadata file for use with each corresponding 'Movie' library.
```
Settings

```
libraries:                
  Anime:
  - extra_overlays: # Will default to all True
  - returning_soon:
      save_folder: metadata/anime/
      overlay_save_folder: overlays/anime/
      trakt_list_privacy: private                          
      refresh: 7     
      days_ahead: 90
      text: "RETURNING"          # Text to display before the dates.
      bgcolor: "#008001"
      font_color: "#FFFFFF"

  Series:
  - extra_overlays:
      new: True
      new_next_air: False
      upcoming: True
      returning: True
      airing: True
      airing_next_air: False
      canceled: True
      ended: True
      
  - returning_soon:
      save_folder: metadata/series/
      overlay_save_folder: overlays/series/
      trakt_list_privacy: public
      refresh: 30
      returning-soon: False
      days_ahead: 45
      text: "RETURNING"          # Text to display before the dates.
      bgcolor: "#008001"
      font_color: "#FFFFFF"
      collection_title: Returning Soon

  - in_history:
      trakt_list_privacy: public
      save_folder: metadata/series/
      range: week
      collection_title: This {{range}} in history.
      starting: 1990
      increment: 5
          
  Movies:
  - in_history:
      range: month
      collection_title: Released This {{Range}} In History
      save_folder: collections/
      trakt_list_privacy: public  # Set privacy for in-history trakt lists, can be set per library
      starting: 1975
      ending: 2020
      increment: 10
      meta:
        sort_title: "!!020"
        collection_mode: hide
        visible_home: true
        visible_shared: true
        sync_mode: sync
        collection_order: critic_rating.desc
        summary: Movies released this {{range}} in history

  - by_size:
      minimum: 25                # Size in GB
      maximum: 90
      order_by: size.desc
      collection_title: Movies sorted by size
      save_folder: collections/
      trakt_list_privacy: public  # Set privacy for in-history trakt lists, can be set per library
      meta:
        sort_title: "!!010"
        collection_mode: hide
        visible_home: true
        visible_shared: true
        sync_mode: sync
        collection_order: custom
        summary: Movies sorted by size between 25 and 90 GB

date_settings:
  date_style: 1                        # 1 for mm/dd, 2 for dd/mm
  leading_zeros: True                  # 01/14 vs 1/14 for dates. True or False
  date_delimiter: "/"                  # Delimiter for dates. Can be "/", "-", "." or "_", e.g. 01/14, 01-14, 01.14, 01_14
  year_in_dates: False                 # Show year in dates: 01/14/22 vs 01/14. True or False


extra_overlays:
  new:
    bgcolor: "#008001"
    font_color: "#FFFFFF"
    text: "N E W  S E R I E S"
    horizontal_align: center
    vertical_align: top
    horizontal_offset: 0
    vertical_offset: 0

  new_next_air:
    bgcolor: "#343399"
    font_color: "#FFFFFF"
    text: "New · Airing"
    
  upcoming:
    bgcolor: "#fc4e03"
    font_color: "#FFFFFF"
    text: "U P C O M I N G"
    horizontal_align: center
    vertical_align: top

  airing:
    bgcolor: "#343399"
    font_color: "#FFFFFF"
    text: "A I R I N G"

  airing_next_air:
    bgcolor: "#343399"
    font_color: "#FFFFFF"
    text: "A I R I N G"

  returning:
    bgcolor: "#81007F"
    font_color: "#FFFFFF"
    text: "R E T U R N I N G"

  ended:
    bgcolor: "#000000"
    font_color: "#FFFFFF"
    text: "E N D E D"

  canceled:
    bgcolor: "#CF142B"
    font_color: "#FFFFFF"
    text: "C A N C E L E D"
```

Date sytle options
```
date_style: 1
        This changes how the dates are formatted in the generated overlay files.
          1
            Will display dates as mm/dd (12/31) for December 31st
          2
            Will display dates as dd/mm (31/12) for December 31st

date_delimiter: "/"
        Delimiter for dates. Can be "/", "-", "." or "_", e.g. 01/14, 01-14, 01.14, 01_14
        Default is '/'

year_in_dates: False
        Show year in dates: 01/14/22 vs 01/14. True or False
        Default is False

```
Core settings

returning_soon:
Enables the 'Returning Soon' core for a library.
![returning_soon](https://github.com/InsertDisc/pattrmm-develop/assets/31751462/13fe4fba-eab9-4e3b-be86-fa55e5dedf38)

```
save_folder: collections/
        Specify a location to write the returning soon metadata file to. Your PMM config folder
        (where your config.yml is), will always be the BASE location.
        So, a save_folder of 'collections/'
        would put your file in a 'collections' sub-folder. If this directory does not exist
        PATTRMM will ATTEMPT to create it.
        Default location is beside your config.yml and does not need specified.

overlay_save_folder: overlay-files/
        Specify a location to write the returning soon overlay file to. Your PMM config folder
        (where your config.yml is), will always be the BASE location.
        So, a save_folder of 'overlay-files/'
        would put your file in a 'overlay-files' sub-folder. If this directory does not exist
        PATTRMM will ATTEMPT to create it.
        Default location is the default PMM 'overlays' folder and does not need specified.

trakt_list_privacy: private
        Specify public/private trakt list privacy for returning soon list. Can be set per library.
        Default is private and does not need specified.

refresh: 30
        Invterval in days to do a full refresh of the libraries airing status.
        Sometimes things change.
        This makes sure you stay up to date.

days_ahead: 45
        How far ahead a title should still be considered 'Returning Soon'.
        For example, 45, would consider any title that has a 'Returning' status
        and airs again within the next 45 days to be 'Returning Soon'.
```

in_history:
Enables the 'In History' core for a library.
![this_month_in_history](https://github.com/InsertDisc/pattrmm-develop/assets/31751462/71575460-c575-4b12-9e77-77ec6a8a59e5)
![this_week_in_history](https://github.com/InsertDisc/pattrmm-develop/assets/31751462/f412f703-1d81-4bd1-9a0b-87b10789f271)

```
  In History specific settings

  range: month
      This sets the range you would like to filter for.
      Options are month, week, day.
      For example

        In 'December', having a 'month' range would filter items throughout the years
        that were released in December

        During the first week of December, December 1st - December 7th, having a range of 'week'
        would filter items released on December 1st - December 7th of qualified years.

        On December 5th, having a range of 'day' would filter items releasd on December 5th
        of qualified years.

  starting: 1975
        Allows you to specify the 'earliest' year the filter will go back till.
        A setting of 1975 would not include anything released prior to 1975.
        If this declaration is missing then all items up to the 'earliest' will be included.

  ending: 1999
        Allows you to specify the 'latest' year the filter will go up to.
        1999 Would not include anything released after that year.
        If this delcaration is missing then up to the current year will be included.

  increment: 10
        Allows you to specify the 'spacing' between valid years.
        Given an 'ending' year of 2003, would only match to titles released every 10 years out.
        So, 2003, 1993, 1983, 1973
        If an 'ending' year is not specified then the current year will be used as the initial year.

  save_folder: collections/
        Specify a location to write the extension metadata file to. Your PMM config folder
        (where your config.yml is), will always be the BASE location.
        So, a save_folder of 'collections/'
        would put your file in a 'collections' sub-folder. If this directory does not exist
        PATTRMM will ATTEMPT to create it.

  trakt_list_privacy: private
        Specify public/private trakt list privacy for this extension list. Can be set per library.
        Default is private and does not need specified.

  collection_title: Released this {{range}} in history.
        Title for the collection in the generated metadata yml file.
        This can be manually written entirely or you can use {{range}}
        to fill in the range automatically.
        Given a range of 'month',
        Released this {{range}} in history, would generate:
            Released this month in history
        {{Range}} can be used instead for a capitalized range.
        Released This {{Range}} In History, would generate:
            Released This Month In History
        The {{range}} and {{Range}} placeholders will also work in a 'summary'
        if you decide to add one to meta options.

  meta:
        Here's where you can apply your 'touch'.

        A default generated metadata yml, with no meta options might look something like:

        collections:
          Released This Month In History:
            trakt_list: https://trakt.tv/users/username/lists/in-history-Movies
            visible_home: true
            visible_shared: true
            collection_order: custom
            sync_mode: sync

        Any of the options under 'Released This Month In History'
        can be overwritten with meta options.
        meta:
          visible_home: false
          collection_order: critic_rating.desc

        Would generate:

        collections:
          Released This Month In History:
            trakt_list: https://trakt.tv/users/username/lists/in-history-Movies
            visible_home: false
            visible_shared: true
            collection_order: critic_rating.desc
            sync_mode: sync

        Notice how the two options were overwritten. Take care not to overwrite your trakt_list.
        You can also use meta to ADD any additional in-line options.

        meta:
          visible_home: false
          collection_order: critic_rating.desc
          sort_title: "!+007"

        Generates:

        collections:
          Released This Month In History:
            trakt_list: https://trakt.tv/users/username/lists/in-history-Movies
            visible_home: false
            visible_shared: true
            collection_order: critic_rating.desc
            sync_mode: sync
            sort_title: "!+007"

        Note:
        As of now, only 'sort_title' will correctly carry over the " around the values.

```
by_size:
Enables the 'By Size' core for a library.
![sorted_by_size](https://github.com/InsertDisc/pattrmm/assets/31751462/e53b748e-8ffc-461f-88b3-b752289f7b3e)
```
  By Size specific settings

  minimum: 25
      This sets the minimum filesize to be included in the filtered list.
      The default value is 0 and does not need specified.

  maximum: 90
      This sets the maximum filesize to be included in the filtered list.
      The default value has no upper limit. To use this extension with no
      top limit, leave out this setting.
        
  order_by: size.desc
      Further sorting of the filtered list is possible with this option.
      The default value is size.desc and does not need specified.
      Available options are:
        size, title, added (date added to Plex), released (Movie release date)
      Each option is compatible with two sort directions but are not required.
        asc - Sort items by ascending order
        desc - Sort items by descending order
        Default sort direction is 'desc' for everything but 'title'.
        
        For example, to sort by a Movie's 'added to plex' date, with the oldest appearing first
        order_by: added.asc

  save_folder: collections/
        Specify a location to write the extension metadata file to. Your PMM config folder
        (where your config.yml is), will always be the BASE location.
        So, a save_folder of 'collections/'
        would put your file in a 'collections' sub-folder. If this directory does not exist
        PATTRMM will ATTEMPT to create it.

  trakt_list_privacy: private
        Specify public/private trakt list privacy for this extension list. Can be set per library.
        Default is private and does not need specified.

  collection_title: Sorted by size
        Title for the collection in the generated metadata yml file.
        

  meta:
        Here's where you can apply your 'touch'.

        A default generated metadata yml, with no meta options might look something like:

        collections:
          Sorted by size:
            trakt_list: https://trakt.tv/users/username/lists/Sorted-by-size-Movies
            visible_home: true
            visible_shared: true
            collection_order: custom
            sync_mode: sync

        Any of the options under 'Sorted by size'
        can be overwritten with meta options.
        meta:
          visible_home: false
          collection_order: critic_rating.desc

        Would generate:

        collections:
          Sorted by size:
            trakt_list: https://trakt.tv/users/username/lists/Sorted-by-size-Movies
            visible_home: false
            visible_shared: true
            collection_order: critic_rating.desc
            sync_mode: sync

        Notice how the two options were overwritten. Take care not to overwrite your trakt_list.
        You can also use meta to ADD any additional in-line options.

        meta:
          visible_home: false
          collection_order: critic_rating.desc
          sort_title: "!+007"

        Generates:

        collections:
          Sorted by size:
            trakt_list: https://trakt.tv/users/username/lists/Sorted-by-size-Movies
            visible_home: false
            visible_shared: true
            collection_order: critic_rating.desc
            sync_mode: sync
            sort_title: "!+007"

        Note:
        As of now, only 'sort_title' will correctly carry over the " around the values.     
          
Each extension can only be used within a library ONCE, otherwise an error will occur.
In-History supports ONE range per library.
```
extra_overlays:
Enables additional status overlays.
If extra_overlays: is enabled for a library, all available extra overlays will be enabled for that library.
These can be disabled
```
 Series:
  - extra_overlays:
      new_next_air: False
      airing_next_air: False
```

What now:

    Add your generated metadata files under the appropriate 
    metadata section of the corresponding library 
    that you are having it scan.
    Add the generated overlay files under the appropriate 
    overlay section of the same library.

When to run:

    Docker version runs daily at the specified PATTRMM_TIME. This is a 24 hour format.

