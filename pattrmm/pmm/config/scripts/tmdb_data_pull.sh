#!/bin/bash
# This section will attempt to pull the required information
# from your pmm config.yml, if it fails you'll have to comment 
# these 4 lines out and fill in the section below it.
source ./vars.sh
plex_url="$plex_config_url"
plex_token="$plex_config_token"
tmdb_apiKey="$tmdb_config_api"

#### if the correct information is not being pulled using vars then you can fill in the information manually ####
#### just comment out the above variables and fill in the information below ####

#### use this section if the above isn't working correctly
#plex_url="plex url, i.e. http://192.xxx.xxx.x:32400"
#plex_token="plex token"
#tmdb_apiKey="TMDB API KEY"

## To get your library identifier, on Plex web version, navigate to your "TV Shows" library and look for "source=? where ? is the identifier of the Library"
libraryKey="3"

#Query Plex API, create array of titles and years of existing Plex titles in Series Library

echo "Preparing Plex data..."

readarray -t series < <(curl --silent --request GET \
     --url "$plex_url/library/sections/$libraryKey/all?X-Plex-Token=$plex_token" \
     --header 'accept: application/json' \
| jq --raw-output ' .MediaContainer.Metadata[] | .ratingKey + "^" + .title + "^" + (.originallyAvailableAt|tostring)')

#declare arrays to be filled and processed
declare -a ratingKey=()
declare -a title=()
declare -a title_cleaned=()
declare -a title_url_encode=()
declare -a plex_or_av_date=()
declare -a plex_first_air_date_year=()
progress="0"
prev="0"

#Get count and loop through array results

numresult="${#series[@]}"

num="1"

for i in "${series[@]}"

do

printf "\rParsing Series: ($num/$numresult)"

#Split previously joined array by the ^ delimeter used.

ratingKey_field=$(echo "$i" | cut -f1 -d^)
#title_field=$(echo "$i" | cut -f2 -d^)
title_clean=$(echo "$i" | cut -f2 -d^ | sed 's/\s([^)]*)//g')
title_url=$(echo "$title_clean" | jq -Rr @uri)
or_av_date_field=$(echo "$i" | cut -f3 -d^)
first_air_date_year=$(echo "$or_av_date_field" | cut -f1 -d-)

#show_prog="$(printf '%.2f\n' $(echo "$progress" | bc -l))"
#echo "Preparing data: $show_prog%"

prev="$progress"
#echo "Preparing data for $ratingKey_field"
#echo "Scrubbing title --> $title_clean"
#echo "Preparing URL --> $title_url"
sleep .0


        if [[ "$or_av_date_field" == "" ]] || [[ "$or_av_date_field" == "null" ]];

		then
            		:
        	else



		#Add formatted variables to their respective arrays

		ratingKey+=("$ratingKey_field")
		title_cleaned+=("$title_clean")
		title_url_encode+=("$title_url")
		plex_or_av_date+=("$or_av_date_field")
		plex_first_air_date_year+=("$first_air_date_year")

        fi

((num+=1))

done

#With our search array ready...
#Lets get the id values of our array using the name and available date to search
#It should be safe to match on the originally available date

#fist set an id array

declare -a tmdb_id=()

#array to store used search year

declare -a year=()

#set a stopping count

count="${#title_cleaned[@]}"

#loop through and gather ids

iteration="1"

for((n=0; n<"$count"; n++))

  do

#### Some informational messages ####

whichTitle="${title_cleaned[$n]}"

echo "Searching for TMDB ID --> ${title_cleaned[$n]}..."
echo "https://api.themoviedb.org/3/search/tv?query=${title_url_encode[$n]}&first_air_date_year=${plex_first_air_date_year[$n]}"


  ################################ iteration 1 ############################


			if [[ "$iteration" == "1" ]]; then

			search_year="${plex_first_air_date_year[$n]}"

read -r id_query < <(curl --silent --request GET \
     --url "https://api.themoviedb.org/3/search/tv?query=${title_url_encode[$n]}&first_air_date_year=${plex_first_air_date_year[$n]}&api_key=$tmdb_apiKey" \
     --header 'accept: application/json' \
| jq --raw-output '.results[] | '\
'select((.first_air_date == "'"${plex_or_av_date[$n]}"'") '\
'or (.first_air_date = "'"${plex_or_av_date[$n]}"'*") '\
'or (.first_air_date = "'$(echo "${plex_or_av_date[$n]%?}")'*") '\
'or (.first_air_date = "'$(echo "$search_year")'*")) '\
'| .id')


					if [[ "$id_query" == "" ]]; then

						echo "No results for search year ${plex_first_air_date_year[$n]}"

						iteration="2"

						((plex_first_air_date_year[$n]+=1))

								search_year="${plex_first_air_date_year[$n]}"

						echo "Trying search year (${plex_first_air_date_year[$n]})..."

						sleep .0

					else

						echo "Success..."

						echo "Found --> $id_query <-- for ${title_cleaned[$n]}..."

						sleep .0

					fi


			fi

################################ iteration 2 ##############################


			if [[ "$iteration" == "2" ]]; then

			search_year="${plex_first_air_date_year[$n]}"


read -r id_query < <(curl --silent --request GET \
     --url "https://api.themoviedb.org/3/search/tv?query=${title_url_encode[$n]}&first_air_date_year=${plex_first_air_date_year[$n]}&api_key=$tmdb_apiKey" \
     --header 'accept: application/json' \
| jq --raw-output '.results[] | '\
'select((.first_air_date == "'"${plex_or_av_date[$n]}"'") '\
'or (.first_air_date = "'"${plex_or_av_date[$n]}"'*") '\
'or (.first_air_date = "'$(echo "${plex_or_av_date[$n]%?}")'*") '\
'or (.first_air_date = "'$(echo "$search_year")'*")) '\
'| .id')


					if [[ "$id_query" == "" ]]; then

						iteration="3"

						echo "No results for search year ${plex_first_air_date_year[$n]}"

						((plex_first_air_date_year[$n]-=2))

							search_year="${plex_first_air_date_year[$n]}"

						echo "Trying search year (${plex_first_air_date_year[$n]})..."

						sleep .0

					else

						echo "Success..."

						echo "Found --> $id_query <-- for ${title_cleaned[$n]}..."

						sleep .0

					fi


			fi
################################ iteration 3 ###############################



			if [ "$iteration" == "3" ]; then

			search_year="${plex_first_air_date_year[$n]}"

read -r id_query < <(curl --silent --request GET \
     --url "https://api.themoviedb.org/3/search/tv?query=${title_url_encode[$n]}&first_air_date_year=${plex_first_air_date_year[$n]}&api_key=$tmdb_apiKey" \
     --header 'accept: application/json' \
| jq --raw-output '.results[] | '\
'select((.first_air_date == "'"${plex_or_av_date[$n]}"'") '\
'or (.first_air_date = "'"${plex_or_av_date[$n]}"'*") '\
'or (.first_air_date = "'$(echo "${plex_or_av_date[$n]%?}")'*") '\
'or (.first_air_date = "'$(echo "$search_year")'*")) '\
'| .id')


					if [ "$id_query" == "" ]; then

						echo "No results for search year ${plex_first_air_date_year[$n]}"

						echo "#########################################################################"

						echo "There was a problem searching for this entry..."

						echo "This may be an unsupported series type or lack TMDB information."

						echo "TVDB support will be added in the future to help mitigate this."

						echo "#########################################################################"

						sleep .0

					else

						echo "Success..."

						echo "Found --> $id_query <-- for ${title_cleaned[$n]}..."

						sleep .0

					fi


			fi


################################ end search iterations #################################

## reset iterations ##

iteration="1"

if [[ "$id_query" == "" ]]; then

	echo "Skipping empty result"

else
	year+=("$search_year")
	tmdb_id+=("$id_query")

fi

sleep 0.0

done

#unset unused variables
unset series
unset title_cleaned
unset title_url_encode
unset plex_or_av_date
unset n
unset i

#Make some calls to TMDB to get remaining details
#

declare tmdb_results=()
count="${#tmdb_id[@]}"

for((n=0; n<"$count"; n++))

	do

printf "\rGrabbing details from https://api.themoviedb.org/3/tv/${tmdb_id[$n]}...."

#echo "Grabbing details from https://api.themoviedb.org/3/tv/${tmdb_id[$n]}"
	readarray -t tmdb_id_query < <(curl --silent --request GET \
			--url "https://api.themoviedb.org/3/tv/${tmdb_id[$n]}?api_key=$tmdb_apiKey" \
			--header 'accept: application/json' \
			| jq --raw-output '(.next_episode_to_air.air_date // "" | if . == "" then "null" else . end) + "^" + .first_air_date + "^" + .last_air_date + "^" + .status + "^" + (.popularity|tostring) + "^" + .name')
			#| jq '(.next_episode_to_air.air_date // "" | if . == "" then "null" else . end) + "@" +	.first_air_date + "@" + .last_air_date + "@" + (.status // "Returning Series" | if . == "Returning Series" then "returning" else . end)+ "@" + (.popularity|tostring)')



#next episode date
#first air date
#last air date
#status
#popularity

tmdb_results+=("$tmdb_id_query")

	done

		#prepare for processing
		unset n
		declare tmdb_next_air=()
		declare tmdb_first_air=()
		declare tmdb_last_air=()
		declare tmdb_status=()
		declare tmdb_pop=()
		declare tmdb_name=()

		#recreate empty file for updated information

cat > tmdb_data.json << EOF
{
  "series": [
EOF


	n="0"

	comma="1"

	count="${#tmdb_results[@]}"
echo ""
echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "Finalizing..."
echo ""
	for t in "${tmdb_results[@]}"

		do

			if [[ "$comma" == "$count" ]];

				then

					punc=""

				else

					punc=","

			fi

printf "\rWriting entries to file: ($comma/$count)"

cat >> tmdb_data.json << EOF
    {
	  "name": "$(echo "$t" | cut -f6 -d^)",
	  "ratingKey": "${ratingKey[$n]}",
	  "tmdb_id": "${tmdb_id[$n]}",
	  "tmdb_next_air": "$(echo "$t" | cut -f1 -d^)",
	  "tmdb_first_air": "$(echo "$t" | cut -f2 -d^)",
	  "tmdb_last_air": "$(echo "$t" | cut -f3 -d^)",
	  "tmdb_status": "$(echo "$t" | cut -f4 -d^)",
	  "tmdb_pop": "$(echo "$t" | cut -f5 -d^)",
          "year": "${year[$n]}"
    }$punc
EOF
			((n+=1))

			((comma+=1))

		done
cat >> tmdb_data.json << EOF
  ]
}
EOF

printf "\n"
printf "done"
printf "\n"

#			tmdb_next_air+=($(echo "$t" | cut -f1 -d^))
#			tmdb_first_air+=($(echo "$t" | cut -f2 -d^))
#			tmdb_last_air+=($(echo "$t" | cut -f3 -d^))
#			tmdb_status+=("$(echo "$t" | cut -f4 -d^)")
#			tmdb_pop+=($(echo "$t" | cut -f5 -d^))
#			tmdb_name+=("$(echo "$t" | cut -f6 -d^)")

