#!/bin/bash

set extglob

SOURCE_FILE=README.md

FDROID_SETTINGS=$( \
            grep -ni "https://f-droid.org/repository/browse/?" ${SOURCE_FILE} \
            | sed "s/.*https:\/\/f-droid.org\/repository\/browse\/?//g" \
            | sed "s/)].*/;/g" \
            )


FAILED=0

while IFS=';' read -ra TOK; do
    for i in "${TOK[@]}"; do
        echo -ne "Check '${i}' ... "

        if [[ "${i}" =~ ^fdid=([[:alnum:]]|[\._-])+$ ]];
        then
            echo "OK"
        else
            echo "INVALID"
            let "FAILED += 1"
        fi

    done
done <<< "${FDROID_SETTINGS}"

if [[ ${FAILED} -ge 1 ]];
then
    echo "Invalid Urls: ${FAILED}"
    exit 1
fi

