#!/usr/bin/env bash
set -e

mkdir -p diff_loadingbg

if [ ! -d "last_loadingbg" ]; then
  echo "No previous snapshot, treating all files as diff"
  cp current_loadingbg/* diff_loadingbg/ 2>/dev/null || true
else
  for f in current_loadingbg/*; do
    name=$(basename "$f")
    if [ ! -f last_loadingbg/"$name" ]; then
      cp "$f" diff_loadingbg/
    else
      if ! cmp -s "$f" last_loadingbg/"$name"; then
        cp "$f" diff_loadingbg/
      fi
    fi
  done
fi

zip -r loadingbg_full.zip current_loadingbg

if [ "$(ls -A diff_loadingbg 2>/dev/null)" ]; then
  zip -r loadingbg_diff.zip diff_loadingbg
else
  echo "No diff files to zip"
fi
