#!/bin/bash

# your trakt username slug #
user="YOUR_TRAKT_USERNAME"

# set identifiers #
source ./vars.sh
bearer="$trakt_config_client_token"
api="$trakt_config_client_id"

#### if the correct information is not being pulled using vars then you can fill in the information manually ####
#### just comment out the above variables and fill in the information below ####

#bearer="trakt bearer token"
#api="trakt client_id"

# do not change list #
list="returning-soon"


# delete existing list #

curl --include \
     --request DELETE \
     --header "Content-Type: application/json" \
     --header "Authorization: Bearer $bearer" \
     --header "trakt-api-version: 2" \
     --header "trakt-api-key: $api" \
"https://api.trakt.tv/users/$user/lists/$list"

# pause to avoid rate limit #

sleep 1

# recreate list #

curl --include \
     --request POST \
     --header "Content-Type: application/json" \
     --header "Authorization: Bearer $bearer" \
     --header "trakt-api-version: 2" \
     --header "trakt-api-key: $api" \
     --data-binary "{
    \"name\": \"Returning Soon\",
    \"description\": \"Season premiers within the next 31 days.\",
    \"privacy\": \"private\",
    \"display_numbers\": true,
    \"allow_comments\": false,
    \"sort_by\": \"rank\",
    \"sort_how\": \"asc\"
}" \
"https://api.trakt.tv/users/$user/lists"

# declare needed dates #

tomorrow=$(date +%Y-%m-%d -d "+ 1 day" )
days_out=$(date +%Y-%m-%d -d "+ 31 day" )
days_before=$(date +%Y-%m-%d -d "- 31 day" )

# read cached tmdb data json file #

readarray -t ids < <(cat tmdb_data.json | jq  ' .series |= sort_by(.tmdb_next_air) | .series[] | '\
'select(( .tmdb_next_air != "null" ) '\
'and ( .tmdb_next_air < "'$(echo "$days_out")'" ) '\
'and ( .tmdb_next_air >= "'$(echo "$tomorrow")'" ) '\
'and ( .tmdb_last_air <= "'$(echo "$days_before")'" )) | .tmdb_id')

# count results from tmdb_data.json #

count="${#ids[@]}"

# loop through results and make calls to trakt api #

for i in "${ids[@]}"; do

curl --include \
     --request POST \
     --header "Content-Type: application/json" \
     --header "Authorization: Bearer $bearer" \
     --header "trakt-api-version: 2" \
     --header "trakt-api-key: $api" \
     --data-binary "{
\"shows\": [
    {
      \"ids\": {
        \"tmdb\": $i
               }
    }
  ]
}" \
"https://api.trakt.tv/users/$user/lists/$list/items"

# pause to avoid rate limiting #

sleep 1

# all done #

done
