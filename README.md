# pattrmm:develop
[Join our Discord](https://discord.com/invite/7yUYdqgxkn)

![returning_soon](https://github.com/InsertDisc/pattrmm-develop/assets/31751462/13fe4fba-eab9-4e3b-be86-fa55e5dedf38)

PATTRMM (Plex Assistant To The Regional Meta Manager) is a python script that automates a 'Returning Soon' Trakt list in chronological order by date and matching metadata and overlay file for use in Plex Meta Manager.
Extensions have been added to further PATTRMM's capabilities.

NOTE !! : The latest update changes the *-returning-soon.yml to *-returning-soon-metadata.yml.
Make sure to update your pmm config file with the new filename if you've updated your script.
If you want to use the new alignment options then you will also need to delete your old
'pattrmm/preferences/' template files.

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
  in-history
    This extension uses the Originally Available At date within Plex to create Trakt lists
    based on a specified range per library and a corresponding 'in-history' metadata file
    for use with that library.
```
Settings

```
libraries:                
  Anime:
    save_folder: metadata/anime/
    overlay_save_folder: overlays/anime/
    trakt_list_privacy: private                          
    refresh: 7     
    days_ahead: 90 
  Series:
    save_folder: metadata/series/
    overlay_save_folder: overlays/series/
    trakt_list_privacy: public
    refresh: 30
    returning-soon: False
    days_ahead: 45
    extensions:
      in-history:
        trakt_list_privacy: public
        save_folder: metadata/series/
        range: week
        collection_title: This {{range}} in history.
        starting: 1990
        increment: 5                   
  Movies:
    extensions:
      in-history:
        range: month
        collection_title: Released This {{Range}} In History
        save_folder: collections/
        trakt_list_privacy: public  # Set privacy for in-history trakt lists, can be set per library
        starting: 1975
        ending: 2020
        increment: 10
        meta:
          sort_title: "!!020"
          collection_mode: visible
          visible_home: true
          visible_shared: true
          sync_mode: sync
          collection_order: critic_rating.desc
          summary: Movies released this {{range}} in history
date_style: 1                        # 1 for mm/dd, 2 for dd/mm
overlay_prefix: "RETURNING"          # Text to display before the dates.
horizontal_align: center
vertical_align: top
horizontal_offset: 0
vertical_offset: 0
leading_zeros: True                  # 01/14 vs 1/14 for dates. True or False
date_delimiter: "/"                  # Delimiter for dates. Can be "/", "-", "." or "_", e.g. 01/14, 01-14, 01.14, 01_14
year_in_dates: False                 # Show year in dates: 01/14/22 vs 01/14. True or False
returning_soon_bgcolor: "#81007F"
returning_soon_fontcolor: "#FFFFFF"

extra_overlays:
  new:
    use: True
    bgcolor: "#008001"
    font_color: "#FFFFFF"
    text: "N E W  S E R I E S"
    horizontal_align: center
    vertical_align: top
    horizontal_offset: 0
    vertical_offset: 0
    
  upcoming:
    use: True
    bgcolor: "#fc4e03"
    font_color: "#FFFFFF"
    text: "U P C O M I N G"
    horizontal_align: center
    vertical_align: top
  airing:
    use: True
    bgcolor: "#343399"
    font_color: "#FFFFFF"
    text: "A I R I N G"
  returning:
    use: True
    bgcolor: "#81007F"
    font_color: "#FFFFFF"
    text: "R E T U R N I N G"
  ended:
    use: True
    bgcolor: "#000000"
    font_color: "#FFFFFF"
    text: "E N D E D"
  canceled:
    use: True
    bgcolor: "#CF142B"
    font_color: "#FFFFFF"
    text: "C A N C E L E D"
```
Standard library options:
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

returning-soon: False
        For those that would like to only run extensions on a 'show' library.
        This will disable PATTRMM's default 'Returning Soon' operations on this library.
        The default setting is True and does not need declared.
```
Standard PATTRMM options
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

extra_overlays:
Included here are various settings used to customize additional 'airing status' overlays
to be included in the generated overlay yml.
If they are not wanted they will need to be disabled with
use: False
as the default behavior is to have them enabled.

Note: These do not need disabled in a 'Movies' only setup.
'Returning Soon' is not compatible with 'Movies' libraries and will skip those libraries.
```
Extension settings

in-history:
Enables the 'In History' extension for a library.
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
          
Each extension can only be used within a library ONCE, otherwise an error will occur.
In-History supports ONE range per library.
```
What now:

    Add the ?-returning-soon.yml under the appropriate metadata section 
    of the corresponding library you are having it scan.
    Add the overlays/?-returning-soon-overlay.yml 
    under the appropriate overlay section of the same library.
    Don't forget to add any additional metadata files 
    that any 'extensions' you are using create as well.

When to run:
    
    I've tried my best to optimize how PATTRMM runs, meaning, 
    you can run it on a daily basis using whatever scheduling service your OS utilizes. 
    After the initial full cycle, only new entries in Plex will get detailed searches. 
    Any series that are not considered a returning series will not be
    updated upon following runs. 
    Any series that loses it's 'Returning Series' status will be updated accordingly 
    and removed from further searches. 
    This greatly speeds up the process of daily executions.

    Docker version runs daily at the specified PATTRMM_TIME. This is a 24 hour format.

