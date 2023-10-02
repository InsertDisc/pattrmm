# pattrmm
PATTRMM (Plex Assistant To The Regional Meta Manager) is a python script that automates a 'Returning Soon' Trakt list in chronological order by date and matching metadata and overlay file for use in Plex Meta Manager.

Requirements:
    
    Trakt MUST be setup in your PMM installation to post 'returning soon' series to.
    This is also what the *-returning-soon.yml will pull from.
    The only must-have module is ruamel.yaml. This is included in requirements.txt. Note, some environments may also need 'requests' installed.
    If you want to use the default template font you will also need the font from the extras folder in your pmm fonts folder.

For stand-alone setup:
    
    Just drop pattrymm.py in a subfolder of your Plex Meta Manager config folder (i.e. Plex-meta-manager/config/pattrmm/pattrmm.py) and run it. A settings file will be created in
    the newly created preferences folder. The script will stop so you can fill in the appropriate settings in preferences/settings.yml.
    You can modify the appearance of the generated overlays file using the
    preferences/*-returning-soon-template.yml files. Run the script again after you make your changes to initiate a full cycle.

Docker Compose:
```
services:
  pattrmm:
    image: ghcr.io/insertdisc/pattrmm:latest
    container_name: pattrmm
    environment:
      - PUID=1000
      - GUID=1000
      - TZ=America/New_York
      - PATTRMM_TIME=02:00
    volumes:
      - ./pattrmm/data:/data
      - ./pattrmm/preferences:/preferences
      - ./pmm/config:/config
    restart: unless-stopped  
```
If using the docker version, you can initialize the settings file with this command.
```
docker run --rm -it -v "./pattrmm/preferences:/preferences" ghcr.io/insertdisc/pattrmm:latest --run
```
The DEVELOP branch of docker is slightly ahead of the latest branch. Extensions have been added and will continue to expand.
```
Extensions Available:
  in-history
    This extension uses the Originally Available At date within Plex to create Trakt lists based on a specified range per library and a corresponding metadata file for use with that library.
    Available options are, day, week, and month.
Extension Use Example:
  Using PATTRMM's setting file.

libraries:
  Movies:
    extensions:
      in-history:
        range: month
  TV Shows:
    refresh: 30
    days_ahead: 90
    extensions:
      in-history:
        range: week
  Anime:
    returning-soon: False <-- if you only want to use extensions on this 'Show' library.
    refresh: 7
    days_ahead: 45
    extensions:
      in-history:
        range: day

Each extension can only be used within a library ONCE, otherwise an error will occur.
In-History supports ONE range.
```
What now:

    Add the ?-returning-soon.yml under the appropriate metadata section of the corresponding library you are having it scan.
    Add the overlays/?-returning-soon-overlay.yml under the appropriate overlay section of the same library.

When to run:
    
    I've tried my best to optimize how PATTRMM runs, meaning, you can run it on a daily basis using whatever scheduling service your OS utilizes. After the initial full cycle,
    only new entries in Plex will get detailed searches. Any series that are not considered a returning series will not be
    updated upon following runs. Any series that loses it's 'Returning Series' status will be updated accordingly and removed
    from further searches. This greatly speeds up the process of daily executions.

    Docker version runs daily at the specified PATTRMM_TIME. This is a 24 hour format.

Update notes:

Recent changes require updating your settings.yml (or deleting it) and deleting your vars.py file.

Settings file changes are as such...
    
    libraries:
      Your Library:
        refresh: 14 # Sets a full data refresh schedule
        days_ahead: 30 # Can be any number of days between 30 and 90 to be considered 'Returning Soon'
    date_style: 1  # 1 or 2 This is a new setting, sets overlay text date to either mm/dd or dd/mm

