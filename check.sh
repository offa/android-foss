#!/bin/bash

SOURCE_FILE=README.md

LINKS=$(grep "http" "$SOURCE_FILE" \
| grep -oP "http.*" \
| sed "s|)$||" \
| sed "s|) .*||" \
| grep -v img.shields.io \
| grep -v travis-ci.org)

mapfile -t LINKS <<< "$LINKS"


FDROID_LINKS=$(grep -oP "https://f-droid.*" "$SOURCE_FILE" \
| sed "s|)].*||" \
| grep -v "https://f-droid.org/)")

mapfile -t FDROID_LINKS <<< "$FDROID_LINKS"

count=0
while [ "$count" -lt 1000 ]
do
    link="${LINKS[$count]}"
    if [ -n "$link" ]
    then
        echo "Testing $link"
        STATUS_CODE=$(curl -LI "$link" -o /dev/null -w '%{http_code}\n' -s)
        if [[ "$STATUS_CODE" != "200" ]]
        then
            FALSE_LINKS+=("$link")
        fi
    fi
    link="${FDROID_LINKS[$count]}"
    if [ -n "$link" ]
    then
        echo "Testing $link"
        STATUS_CODE=$(curl -LI "$link" -o /dev/null -w '%{http_code}\n' -s)
        if [[ "$STATUS_CODE" != "200" ]]
        then
            FALSE_LINKS+=("$link")
        fi
    fi
    ((count++))
done

if [ -n "${FALSE_LINKS[*]}" ]
then
    echo "Some links weren't reachable."
    for link in "${FALSE_LINKS[@]}"
    do
        echo "$link"
    done
    exit 1
else
    echo "No false link was found"
fi
