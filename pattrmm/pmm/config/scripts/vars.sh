#!/bin/bash
declare -a trakt_conn=()
declare -a plex_conn=()
declare -a tmdb_conn=()

trakt_conn+=($(grep "trakt:" ../config.yml -A 9 ))
plex_conn+=($(grep "clean_bundles" ../config.yml -B 3 ))
tmdb_conn+=($(grep "tmdb:" ../config.yml -A 1 ))

plex_config_url="${plex_conn[1]%?}"
plex_config_token="${plex_conn[3]}"
tmdb_config_api="${tmdb_conn[2]}"
trakt_config_client_id="${trakt_conn[2]}"
trakt_config_client_secret="${trakt_conn[4]}"
trakt_config_client_token="${trakt_conn[7]}"

