# pattrmm
PATTRMM (Plex Assistant To The Regional Meta Manager) is a python script that automates a 'Returning Soon' Trakt list in chronological order by date and matching metadata and overlay file for use in Plex Meta Manager.
Requirements:
    Trakt MUST be setup in your PMM installation to post 'returning soon' series to.
    This is also what the returning-soon.yml will pull from.
    The only must-have module is ruamel.yaml. This is included in requirements.txt.

About use:
    PATTRMM will try it's best to get the matching tmdb id of all the shows in the library that you have it scanning.
    Fill in the appropriate settings in preferences/settings.yml. This file is created on the first run and the script will
    exit to give you a chance to make these changes. You can modify the appearance of the generated overlays file using the
    preferences/returning-soon-template.yml. Run the script again after you make your changes to initiate a full cycle.

What now:
    Add the returning-soon.yml under the appropriate metadata section of the corresponding library you are having it scan.
    Add the overlays/returning-soon-overlay.yml under the appropriate overlay section of the same library.

When to run:
    I've tried my best to optimize how PATTRMM runs, meaning, you can run it on a daily basis. After the initial full cycle,
    only new entries in Plex will get detailed searches. Any series that are not considered a returning series will not be
    updated upon following runs. Any series that loses it's 'Returning Series' status will be updated accordingly and removed
    from further searches. This greatly speeds up the process of daily executions.

Update notes:
    Recent changes require the deletion of preferences/settings.yml to use the newest features.
