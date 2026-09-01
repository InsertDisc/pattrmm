# PATTRMM

PATTRMM (Personal Assistant To The Regional Meta Manager) is a Python script that automates generating overlay and metadata files for collections in Kometa that are not easily handled out of the box.

This can include things like lists that need to be sorted in specific ways, dynamically generated collections, or collections with overlays whose contents change based on dates or other information.

## Requirements

A currently working Kometa installation.

## Stand-alone Setup

Extract this repo into a subfolder of your Kometa config folder.

For example:

```text
Kometa/
├── config/
│   ├── config.yml
│   ├── collections/
│   ├── overlays/
│   └── pattrmm/
│       ├── pattrmm.py
│       ├── cores/
│       ├── modules/
│       └── settings/
```

Run PATTRMM with:

```bash
python3 pattrmm.py --run
```

PATTRMM uses the Kometa config directory as its base for generated collection and overlay files.

Settings are stored as YAML files in the `settings/` directory.

## Docker Compose

```yaml
services:
  pattrmm:
    image: ghcr.io/insertdisc/pattrmm:neo
    container_name: pattrmm
    environment:
      - PUID=1000
      - GUID=1000
      - PATTRMM_TIMES=02:00,13:00
      - PATTRMM_SETTINGS=server1.yml,server2.yml
      - TZ=America/New_York
    volumes:
      - ./pattrmm/data:/data
      - ./pattrmm/settings:/settings
      - ./kometa/config:/config
    restart: unless-stopped
```

`PATTRMM_TIMES` specifies the time or times PATTRMM should run each day, using 24-hour time.

`PATTRMM_SETTINGS` specifies which settings files to use. Multiple files can be separated with commas.

For example:

```text
PATTRMM_SETTINGS=server1.yml,server2.yml
```

This is useful if you have multiple Plex servers or multiple Kometa configurations. Each settings file can point to a different Kometa config.

If `PATTRMM_SETTINGS` isn't specified, PATTRMM will use all `.yml` and `.yaml` files in the `settings/` directory.

## Launch Arguments

### `--run`

Run PATTRMM immediately instead of waiting for the scheduled time.

```bash
python3 pattrmm.py --run
```

### `--times`

Specify the time or times PATTRMM should run.

```bash
python3 pattrmm.py --times "02:00,13:00"
```

Multiple times can be separated with commas.

### `--settings`

Specify which settings files to use.

```bash
python3 pattrmm.py --settings "server1.yml,server2.yml"
```

The files are loaded from the `settings/` directory.

## The NEO Branch

The NEO branch is a complete restructure of the old code.

PATTRMM is now divided into individual **cores**. Each core is responsible for a particular operation.

New cores can be authored and placed into the `cores` directory. They are automatically discovered and run by PATTRMM.

# Settings

Settings are organized around your Plex libraries.

A settings file can contain one or more libraries, with each library containing the cores you want to use.

For example:

```yaml
libraries:

  Movies:

    - by_size:
        enabled: true
        order_by: size.desc
        minimum: 0
        maximum: null
        limit: 500
        collection_dir: collections/
        collection:
          name: Movies by Size
          collection_order: custom
          sync_mode: sync
          url_poster: https://example.com/poster.jpg

    - in_history:
        enabled: true
        range: month
        starting: 0
        ending: null
        increment: 1
        collection_dir: collections/
        collection:
          name: Movies This {{range}} in history
          collection_order: custom
          sync_mode: sync
          url_poster: https://example.com/poster.jpg

    - in_history:
        enabled: false
        range: week
        starting: 0
        ending: 2020
        increment: 2
        collection_dir: collections/
        collection:
          name: Movies This {{range}} in history - Every 2 Years
          collection_order: custom
          sync_mode: sync

  Series:

    - by_size:
        enabled: false
        order_by: title.asc
        minimum: 0
        maximum: null
        limit: 100
        collection_dir: collections/
        collection:
          name: Series by Size
          collection_order: custom
          sync_mode: sync

    - in_history:
        enabled: true
        range: month
        starting: 0
        ending: null
        increment: 1
        collection_dir: collections/
        collection:
          name: Series This {{range}} in history
          collection_order: custom
          sync_mode: sync
          url_poster: https://example.com/poster.jpg

    - in_history:
        enabled: false
        range: week
        starting: 1990
        ending: 2020
        increment: 5
        collection_dir: collections/
        collection:
          name: Series This {{range}} in history - Every 5 Years
          collection_order: custom
          sync_mode: sync

    - new_shows:
        enabled: true
        first_episode_aired: 45
        collection_dir: collections/
        collection:
          name: New Shows
          collection_order: custom
          sync_mode: sync
          url_poster: https://example.com/poster.jpg

    - extended_status:

        overlay_dir: overlays/

        season_finale:
          enabled: true
          mode: overlay
          overlay:
            status_text: SEASON FINALE [{{DDD}} || {{MM}}/{{DD}}]

        returning_soon:
          enabled: true
          use_today: true
          today_text: Returning Today
          mode: collection
          days_ahead: 45
          days_behind: 14
          collection_dir: collections/
          collection:
            name: Returning Soon
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: RETURNING {{MM}}/{{DD}}
            weight: 35
            banner_back_color: '#81007F'
            status_font_color: '#FFFFFF'

        airing:
          enabled: true
          mode: overlay
          days_ahead: 14
          days_behind: 14
          collection_dir: collections/
          collection:
            name: Currently Airing
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: AIRING
            weight: 50
            banner_back_color: '#006580'
            status_font_color: '#FFFFFF'

        airing_next:
          enabled: false
          use_today: true
          today_text: Airing Today
          mode: overlay
          days_ahead: 14
          days_behind: 14
          collection_dir: collections/
          collection:
            name: Airing Next
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: AIRING {{MM}}/{{DD}}
            weight: 55
            banner_back_color: '#006580'
            status_font_color: '#FFFFFF'

        new:
          enabled: true
          mode: overlay
          days_considered_new: 14
          collection_dir: collections/
          collection:
            name: New Series
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: NEW
            weight: 60
            banner_back_color: '#008001'
            status_font_color: '#FFFFFF'

        new_airing_next:
          enabled: false
          mode: overlay
          days_considered_new: 14
          collection_dir: collections/
          collection:
            name: New - Airing
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: NEW - AIRING {{MM}} / {{DD}}
            weight: 65
            banner_back_color: '#008001'
            status_font_color: '#FFFFFF'

        returning:
          enabled: true
          mode: overlay
          collection_dir: collections/
          collection:
            name: Returned Series
            collection_order: custom
            sync_mode: sync
          overlay:
            text: R E T U R N I N G
            weight: 30
            banner_back_color: '#81007F'
            status_font_color: '#FFFFFF'

        ended:
          enabled: false
          mode: overlay
          collection_dir: collections/
          collection:
            name: Ended
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: E N D E D
            weight: 20
            banner_back_color: '#000000'
            status_font_color: '#FFFFFF'

        canceled:
          enabled: false
          mode: overlay
          collection_dir: collections/
          collection:
            name: Canceled
            collection_order: custom
            sync_mode: sync
          overlay:
            status_text: C A N C E L E D
            weight: 20
            banner_back_color: '#CF142B'
            status_font_color: '#FFFFFF'

settings:
  kometa_config: config.yml
  data_source: tmdb
```

The `settings/` directory is intended for separate settings files. You can have something like:

```text
settings/
├── server1.yml
├── server2.yml
```

Each file can reference a different Kometa configuration.

For example:

```yaml
settings:
  kometa_config: config.yml
  data_source: tmdb
```

Or:

```yaml
settings:
  kometa_config: server2/config.yml # Based from default config.yml location
  data_source: tmdb
```

# Cores

## All currently available cores default to enabled: False and must be explicitly enabled.

## `extended_status`

`extended_status` handles dynamically generated collections and overlays based on the current status of TV series.

The available statuses are:

* `season_finale (dated overlay)`
* `returning_soon (dated overlay)`
* `airing`
* `airing_next (dated overlay)`
* `new`
* `new_airing_next (dated overlay)`
* `upcoming`
* `returning`
* `ended`
* `canceled`

Each status can be enabled independently.

The available modes are:

```text
all
overlay
collection
```
`all` generates both overlay and collection files.

`overlay` generates the overlay information for the selected titles.

`collection` generates the collection information for the selected titles.

Some statuses can be more useful with different modes.

### `overlay_dir`

```yaml
overlay_dir: overlays/
```

Specifies where the generated extended status overlay file is written.

The Kometa config directory is always the base location.

For example:

```yaml
overlay_dir: overlays/
```

would result in:

```text
/config/overlays/
```

If the directory doesn't exist, PATTRMM will attempt to create it.

The default is `overlays/`.

### Status settings
#### `season_finale`

```yaml
season_finale:
  enabled: false
  mode: overlay
  overlay:
    status_text: SEASON FINALE {{MM}}/{{DD}}
```

Used for series that have a next episode of 'finale'.
#### `returning_soon`

```yaml
returning_soon:
  enabled: false
  use_today: true
  today_text: Returning Today
  mode: collection
  days_ahead: 45
  collection_dir: collections/
  collection:
    name: Returning Soon
    collection_order: custom
    sync_mode: sync
  overlay:
    status_text: RETURNING {{MM}}/{{DD}}
    weight: 35
    banner_back_color: '#81007F'
    status_font_color: '#FFFFFF'
```

`days_ahead` determines how far into the future a returning series can be before it is no longer considered "Returning Soon."
`days_behind` determines how long ago the last episode must have aired to be considered "Returning Soon."

For example, `days_ahead: 45` means a returning series airing within the next 45 days can be included.
While `days_behind: 14` means an episode must not have aired within the past 14 days.
#### `airing`

```yaml
airing:
  enabled: false
  mode: overlay
  days_ahead: 14
  days_behind: 14
```

`days_ahead` and `days_behind` determine the window used to identify currently airing series.

#### `airing_next`

```yaml
airing_next:
  enabled: false
  mode: overlay
  days_ahead: 14
  days_behind: 14
```

Used for series with an upcoming episode.

#### `new`

```yaml
new:
  enabled: false
  mode: overlay
  considered_new: 14
```

`days_considered_new` specifies how many days after a series begins that it should continue to be considered new.

#### `new_airing_next`

```yaml
new_airing_next:
  enabled: false
  mode: overlay
  days_considered_new: 14
```

Combines the new-series criteria with an upcoming episode.

#### `upcoming`

```yaml
## Not currently implemented
upcoming:
  enabled: false
  mode: collection
```

Used for series that have not aired yet.

#### `returning`

```yaml
returning:
  enabled: false
  mode: overlay
```

Used for series that have recently returned.

#### `ended`

```yaml
ended:
  enabled: false
  mode: overlay
```

Used for ended series.

#### `canceled`

```yaml
canceled:
  enabled: false
  mode: overlay
```

Used for canceled series.

## Overlay Settings

Each status can contain an `overlay:` block.

PATTRMM supports three ways of targeting values inside Kometa's overlay configuration.

### Banner settings

Keys beginning with `banner_` are placed into the Kometa `banner` section.

For example:

```yaml
overlay:
  banner_back_color: '#81007F'
```

results in the setting being applied to the banner configuration.

### Status text settings

Keys beginning with `status_` are placed into the Kometa `text` section.

For example:

```yaml
overlay:
  status_text: RETURNING
```

targets the `text overlay` section.

### Direct settings

Keys without either prefix can be used for settings that apply directly to both sections.

For example:

```yaml
overlay:
  weight: 35
```

This allows an overlay configuration to contain a mixture of banner, text, and shared settings.

For example:

```yaml
overlay:
  status_text: RETURNING {{MM}}/{{DD}}
  weight: 35
  banner_back_color: '#81007F'
  status_font_color: '#FFFFFF'
```

### Date placeholders

Dated overlay text can use:

```text
{{M}}    4
{{MM}}   04
{{mmm}}  Apr
{{MMM}}  APR
{{mmmm}} April
{{MMMM}} APRIL

{{D}}    9
{{DD}}   09
{{ddd}}  Tue
{{DDD}}  TUE
{{dddd}} Tuesday
{{DDDD}} TUESDAY

{{YY}}    26
{{YYYY}}  2026
```
For example
```yaml
status_text: RETURNING {{MM}}/{{DD}}
```

could produce:

```text
RETURNING 04/09
```
### Conditional Placeholders

Dated overlays support conditional text using the `[... || ...]` format.

```yaml
status_text: 'Airing [{{DDD}} || {{MM}} / {{DD}}]'
```

* The section **before** `||` is used when the next air date is **less than 7 days away**.
* The section **after** `||` is used when the next air date is **7 or more days away**.

For example, with today being **2026-08-31**:

```text
Next air date: 2026-09-01
Result: Airing TUE
```

```text
Next air date: 2026-09-08
Result: Airing 09 / 08
```

The conditional format can be used with any supported date placeholders.

### Today Replacement

Every *dated* overlay supports the following settings:

```yaml
use_today: true
today_text: 'Airing Today'
```

When `use_today` is enabled and the next air date is **today**, the entire `status_text` is replaced with the value of `today_text`.

For example, with today being **2026-08-31** and:

```yaml
use_today: true
today_text: 'Airing Today'
```

The result will be:

```text
Airing Today
```

This applies regardless of whether the `status_text` uses conditional placeholders:

```yaml
status_text: 'Airing [{{DDD}} || {{MM}} / {{DD}}]'
```

or standard date placeholders:

```yaml
status_text: 'Airing {{MM}} / {{DD}}'
```

Both will result in:

```text
Airing Today
```

`use_today` is supported by all dated statuses:

* `returning_soon`
* `season_finale`
* `airing_next`
* `new_airing_next`


# `in_history`

Enables the `In History` core for a library.

`In History` creates collections containing titles released during the current day, week, or month across a range of years.

### Settings

```yaml
in_history:
  enabled: true
  range: month
  starting: 1975
  ending: 2025
  increment: 10
  collection_dir: collections/
  collection:
    name: This {{range}} in history
    collection_order: custom
    sync_mode: sync
```

### `range`

The range to filter.

Available options:

```text
day
week
month
```

A `month` range during December finds titles released during December in the selected years.

A `week` range finds titles released during the current Monday-Sunday week in the selected years.

A `day` range finds titles released on the current day in the selected years.

### `starting`

The earliest year to include.

```yaml
starting: 1975
```

Anything released before 1975 will be excluded.

### `ending`

The latest year to include.

```yaml
ending: 2025
```

Anything released after 2025 will be excluded.

If omitted, the current year is used.

### `increment`

Controls the spacing between years.

```yaml
ending: 2025
increment: 10
```

would check:

```text
2025
2015
2005
1995
...
```

If `ending` isn't specified, the current year is used as the starting year.

`In History` can be configured multiple times for the same library.

For example:

```yaml
- in_history:
    enabled: true
    range: month
    starting: 0
    ending: null
    increment: 1
    collection_dir: collections/
    collection:
      name: This {{range}} in history
      collection_order: custom
      sync_mode: sync

- in_history:
    enabled: false
    range: week
    starting: 1990
    ending: 2020
    increment: 5
    collection_dir: collections/
    collection:
      name: This {{range}} in history - Every 5 Years
      collection_order: custom
      sync_mode: sync
```

## `by_size`

Enables the `By Size` core for a library.

```yaml
by_size:
  enabled: true
  order_by: size.desc
  minimum: 0
  maximum: null
  limit: 500
  collection_dir: collections/
  collection:
    name: By Size
    collection_order: custom
    sync_mode: sync
```

### `minimum`

Minimum size to include.

```yaml
minimum: 25
```

### `maximum`

Maximum size to include.

```yaml
maximum: 90
```

Leaving this as `null` means there is no maximum.

### `limit`

Maximum number of titles to put into the collection.

```yaml
limit: 500
```

### `order_by`

Controls how the results are sorted.

Available fields:

```text
size
title
added
released
release_date
```

Available directions:

```text
asc
desc
```

Examples:

```yaml
order_by: size.desc
order_by: size.asc
order_by: title.asc
order_by: added.asc
order_by: released.desc
```

`size.desc` is the default.

For titles, ascending order is the default direction if no direction is supplied.

## `new_shows`

Enables the `New Shows` core for a show library.

```yaml
new_shows:
  enabled: true
  first_episode_aired: 45
  collection_dir: collections/
  collection:
    name: New Shows
    collection_order: custom
    sync_mode: sync
```

`first_episode_aired` determines how many days back the first episode of a series can have aired while still being considered a new show.

For example:

```yaml
first_episode_aired: 45
```

will include shows whose first episode aired within the last 45 days.

`new_shows` only operates on Plex libraries whose type is `show`.

# Collection Settings

Every core that creates a collection has a `collection:` section.

For example:

```yaml
collection:
  name: My Collection
  collection_order: custom
  sync_mode: sync
```

PATTRMM passes the collection settings through to the generated Kometa collection configuration.

This means you can add other Kometa collection options here as well.

For example:

```yaml
collection:
  name: My Collection
  collection_order: custom
  sync_mode: sync
  poster_url: https://example.com/poster.jpg
```

PATTRMM does not need to explicitly know about every Kometa collection option.

Additional options can be added to the `collection:` block and will be carried into the generated collection configuration.

# Generated Files

PATTRMM generates the files needed by Kometa.

Collections are written to the configured `collection_dir` and overlays are written to the configured `overlay_dir`.

The generated files can then be referenced from the corresponding Kometa library using:

```yaml
collection_files:
  - collections/example.yml

overlay_files:
  - overlays/example.yml
```

The paths are relative to the Kometa config directory.

# Running PATTRMM

For a manual run:

```bash
python3 pattrmm.py --run
```

For Docker, PATTRMM will run automatically according to `PATTRMM_TIMES`.

For example:

```yaml
environment:
  - PATTRMM_TIMES=02:00,13:00
```

will run PATTRMM every day at 2:00 AM and 1:00 PM.

PATTRMM will process the settings files specified by `PATTRMM_SETTINGS`, or all settings files in the `settings/` directory if none are specified.
