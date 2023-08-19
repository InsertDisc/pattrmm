#!/bin/bash

today=$(date +%m/%d/%Y)
after=$(date +%m/%d/%Y -d "- 15 day")

cat > /home/captain/pmm/config/overlays/series_overlay_returning.yml << EOF
templates:
  # TEXT CENTER
  TV_Top_TextCenter:
    sync_mode: sync
    builder_level: show
    overlay:
      name: text(<<text>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 0
      vertical_align: top
      font: config/fonts/Juventus-Fans-Bold.ttf
      font_size: 70
      font_color: <<color>>
      group: TV_Top_TextCenter
      weight: <<weight>>
      back_color: <<back_color>>
      back_width: 1920
      back_height: 90



overlays:

  # Airing
  TV_Top_TextCenter_OnAir:
    template:
      - name: TV_Top_TextCenter
        weight: 40
        text: "A I R I N G"
        color: "#FFFFFF" # white
        back_color: "#343399"
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      last_episode_aired.after: $after

 # Airing Today
  TV_Top_TextCenter_Returning_$today:
    template:
      - name: TV_Top_TextCenter
        weight: 39
        text: "A I R I N G"
        color: "#FFFFFF"
        back_color: "#343399"
    tmdb_discover:
      air_date.gte: $today
      air_date.lte: $today
      with_status: 0
      limit: 250

  #Returning
  TV_Top_TextCenter_Returning:
    template:
      - name: TV_Top_TextCenter
        weight: 25
        text: "R E T U R N I N G"
        color: "#FFFFFF"
        back_color: "#81007F"
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
EOF

lea=$(date +%m/%d/%Y -d "- 30 day")

for (( d=1; d<=32; d++ ))
do
thisday=$(date +%m/%d/%Y -d "+ $d day")
thisday_display=$(date +%m/%d -d "+ $d day")
cat >> /home/captain/pmm/config/overlays/series_overlay_returning.yml << EOF

# RETURNING $thisday
  TV_Top_TextCenter_Returning_$thisday:
    template:
      - name: TV_Top_TextCenter
        weight: 30
        text: "RETURNING $thisday_display"
        color: "#FFFFFF"
        back_color: "#81007F"
    tmdb_discover:
      air_date.gte: $thisday
      air_date.lte: $thisday
      with_status: 0
      limit: 250
    filters:
      last_episode_aired.before: $lea
EOF
done
