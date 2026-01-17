#!/bin/bash

SOURCE_FILE=README.md

function check_deprecated_repos() {
  GITHUB_LINKS=$(grep -o "https://github.com/.*" "$SOURCE_FILE" \
    | sed 's|).*||')

  mapfile -t GITHUB_LINKS <<< "$GITHUB_LINKS"

  for link in "${GITHUB_LINKS[@]}"; do
    echo "Checking if repo $link is not deprecated"
    DEPRECATED=$(curl "$link" -s | awk -v depr_repo_res='false' \
      '/This repository has been archived by the owner. It is now read-only./ \
        {depr_repo_res="true"} END {print depr_repo_res}')
    if [[ "$DEPRECATED" == "true" ]]; then
      deprecated_repos+=("$link")
    fi
  done

  if [ -n "${deprecated_repos[*]}" ]; then
    depr_repo_res=1
  fi
}

function check_false_links() {
  LINKS=$(grep -oP "http.*" "$SOURCE_FILE" \
  | sed -e "s|)$||" -e "s|).*||" \
  | grep -v img.shields.io \
  | grep -v travis-ci.org)

  mapfile -t LINKS <<< "$LINKS"

  for link in "${LINKS[@]}"
  do
      echo "Checking $link"
      STATUS_CODE="$(curl -LI "$link" -o /dev/null -w '%{http_code}\n' -s)"
      if [[ "$STATUS_CODE" != "200" ]]
      then
          bad_links+=("$link")
      fi
  done

  if [ -n "${bad_links[*]}" ]
  then
      link_res=1
  fi
}

function check_links() {
  local depr_repo_res=0
  local deprecated_repos
  check_deprecated_repos

  local link_res=0
  local bad_links
  check_false_links

  clear
  if [[ link_res -eq "1" ]]; then
    echo "Unreachable links were found:"
    for link in "${bad_links[@]}"; do
      echo "$link"
    done
  fi

  if [[ depr_repo_res -eq "1" ]]; then
    echo "Deprecated repo were found:"
    for link in "${deprecated_repos[@]}"; do
      echo "$link"
    done
  fi

  if [[ depr_repo_res -eq 0 && link_res -eq 0 ]]; then
    echo "All links are validated!"
  fi
}

check_links
