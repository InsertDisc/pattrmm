# pattrmm
Plex Meta Manager helper script for a chronological Returning Soon collection with dates.

Requirements:
    The only must-have other than a bash environment to run the scripts is 'jq'.
    JQ is used to query and sort certain JSON data.

About use:
    The tmdb_data_pull script will try it's best to get the matching tmdb id of all the shows in the library that you have it scanning.
    Upon completion it creates tmdb_data.json that stores that information. The schedule you run this at is entirely up to you.
    However, it should be scheduled a time before trakt_update, or you may not get the most up to date information. I run mine
    weekly at 11 p.m. and the other two just after 12 a.m. daily. On my setup, I think it takes about 3 minutes to finish.
    
    The trakt_update script will filter through the tmdb_data.json to get a list of shows that have not aired in the last month,
    that have an air date that falls within the next 31 days. With that information in hand, trakt_update will attempt to delete
    the existing Returning Soon list from your Trakt.tv account, recreate the list, then populate the list chronologically with the
    shows that matched the filter. This should be scheduled daily before your PMM run and is dependant on an existing tmdb_data.json file
    created by tmdb_data_pull.

    The returning-soon.yml metadata file, once you fill in your trakt username slug, will pull that list upon being ran in PMM.

    The series_overlay_returning.sh script is responsible for creating the dated overlays to go along with the Returning Soon collection.
    This script should be ran daily as well before PMM runs and is not dependant on the order that trakt_update.sh is ran.

What you need to do:
    Place the included files in their exisiting structure, into your PMM folder. The only thing you SHOULD have to do is fill in your
    Plex library source number in tmdb_data_pull.sh, and enter your Trakt username into trakt_update and series-returning.yml. I would manually run all three
    scripts (series_overlay_returning.sh <- in the overlays folder, tmdb_data_pull.sh <- in scripts, and trakt_update) in that order, to create the initial files
    and give you an idea of what each one does. If you're getting 404's or connection
    errors it's likely that vars.sh isn't pulling the correct data. In that case you can manually enter your keys and whatknot in the tmdb and trakt scripts.
    I've included a few lines of my config.yml so you can see what needs added there as well.

Note:
    I know the code is a mess and vars.sh is... not 100% reliable, but these weren't really intended for public consumption but people are asking. I've started rewriting
    everything in Python, but I'm learning as I go. The best of luck to any that use this.
