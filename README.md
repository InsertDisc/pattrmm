# pattrmm
PATTRMM (Plex Assistant To The Regional Meta Manager) is a python script that automates a 'Returning Soon' Trakt list in chronological order by date and matching metadata and overlay file for use in Plex Meta Manager.

Requirements:
    
    Trakt MUST be setup in your PMM installation to post 'returning soon' series to.
    This is also what the *-returning-soon.yml will pull from.
    The only must-have module is ruamel.yaml. This is included in requirements.txt. Note, some environments may also need 'requests' installed.
    If you want to use the default template font you will also need the font from the extras folder in your pmm fonts folder.

Installation/Use:
    
    Just drop pattrymm.py in a subfolder of your Plex Meta Manager config folder and run it. A settings file will be created in
    the new preferences folder. The script will stop so you can fill in the appropriate settings in preferences/settings.yml.
    You can modify the appearance of the generated overlays file using the
    preferences/*-returning-soon-template.yml files. Run the script again after you make your changes to initiate a full cycle.

What now:
    
    Add the ?-returning-soon.yml under the appropriate metadata section of the corresponding library you are having it scan.
    Add the overlays/?-returning-soon-overlay.yml under the appropriate overlay section of the same library.

When to run:
    
    I've tried my best to optimize how PATTRMM runs, meaning, you can run it on a daily basis. After the initial full cycle,
    only new entries in Plex will get detailed searches. Any series that are not considered a returning series will not be
    updated upon following runs. Any series that loses it's 'Returning Series' status will be updated accordingly and removed
    from further searches. This greatly speeds up the process of daily executions.

Update notes:

Recent changes require updating your settings.yml (or deleting it) and deleting your vars.py file.

Settings file changes are as such...
    
    libraries:
      Your Library:
        refresh: 14 # Sets a full data refresh schedule
        days_ahead: 30 # Can be any number of days between 30 and 90 to be considered 'Returning Soon'

