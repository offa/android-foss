#!/bin/bash

set extglob

SOURCE_FILE=README.md

FDROID_SETTINGS=$( \
            grep -ni "https://f-droid.org/app" ${SOURCE_FILE} \
            | sed "s/.*https:\/\/f-droid.org\/app\///g" \
            | sed "s/)].*/;/g" \
            )

FAILED=0

while IFS=';' read -ra TOK; do
    for i in "${TOK[@]}"; do
        echo -ne "Check '${i}' ... "

        if [[ "${i}" =~ ^([[:alnum:]]|[\._-])+$ ]];
        then
            echo -e "\e[0;32m OK \e[0m"
        else
            echo -e "\e[0;31m INVALID \e[0m"
            let "FAILED += 1"
        fi

    done
done <<< "${FDROID_SETTINGS}"

if [[ ${FAILED} -ge 1 ]];
then
    echo "Invalid Urls: ${FAILED}"
    exit 1
fi
