#!/bin/bash

wget https://raw.githubusercontent.com/offa/android-foss/master/README.md

SOURCE_FILE=README.md

LINKS=$(grep "http" "$SOURCE_FILE" \
| grep -oP "http.*" \
| sed "s|)$||" \
| sed "s|) .*||" \
| grep -v img.shields.io \
| grep -v travis-ci.org)

mapfile -t LINKS <<< "$LINKS"

for link in "${LINKS[@]}"
do
    echo "Testing $link"
    STATUS_CODE="$(curl -LI "$link" -o /dev/null -w '%{http_code}\n' -s)"
    if [[ "$STATUS_CODE" != "200" ]]
    then
        FALSE_LINKS+=("$link")
    fi
done

FDROID_LINKS=$(grep -oP "https://f-droid.*" "$SOURCE_FILE" \
| sed "s|)].*||" \
| grep -v "https://f-droid.org/)")

mapfile -t FDROID_LINKS <<< "$FDROID_LINKS"

for link in "${FDROID_LINKS[@]}"
do
    echo "Testing $link"
    STATUS_CODE="$(curl -LI "$link" -o /dev/null -w '%{http_code}\n' -s)"
    if [[ "$STATUS_CODE" != "200" ]]
    then
        FALSE_LINKS+=("$link")
    fi
done

if [ -n "${FALSE_LINKS[*]}" ]
then
    clear
    echo "Some links weren't reachable."
    for link in "${FALSE_LINKS[@]}"
    do
        echo "$link"
    done
    exit 1
else
    echo "No false link was found"
fi
