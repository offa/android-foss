#!/bin/bash

SOURCE_FILE=README.md

LINKS=$(grep -oP "http.*" "$SOURCE_FILE" \
| sed -e "s|)$||" -e "s|) .*||" \
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

GITHUB_LINKS=$(grep -o "https://github.com/.*" README.md \
    | sed 's|).*||')

mapfile -t GITHUB_LINKS <<< "$GITHUB_LINKS"

for link in "${GITHUB_LINKS[@]}"
do
    echo "Checking if repo $link is not deprecated"
    DEPRECATED=$(curl "$link" -s | awk -v result='false' \
        '/This repository has been archived by the owner. It is now read-only./ \
	    {result="true"} END {print result}')
    if [[ "$DEPRECATED" == "true" ]]
    then
        GITHUB_DEPRECATED_LINKS+=("$link")
    fi
done

if [ -n "${GITHUB_DEPRECATED_LINKS[*]}" ]
then
    clear
    echo "Deprecated Github Repos were found:"
    for link in "${GITHUB_DEPRECATED_LINKS[@]}"
    do
        echo "$link"
    done
    exit 1
else
    echo "No deprecated repo was found"
fi
