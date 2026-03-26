#!/usr/bin/env bash
set -e

mkdir -p diff_loadingbg
HAS_DIFF=0

if [ ! -d "last_loadingbg" ]; then
  echo "No previous snapshot, treating all files as diff"
  cp current_loadingbg/* diff_loadingbg/ 2>/dev/null || true
else
  for f in current_loadingbg/*; do
    name=$(basename "$f")
    if [ ! -f last_loadingbg/"$name" ]; then
      cp "$f" diff_loadingbg/
      HAS_DIFF=1
    else
      if ! cmp -s "$f" last_loadingbg/"$name"; then
        cp "$f" diff_loadingbg/
        HAS_DIFF=1
      fi
    fi
  done
fi

# 全量永远打包
zip -r loadingbg_full.zip current_loadingbg

# 有 diff 才打 diff 包
if [ "$(ls -A diff_loadingbg 2>/dev/null)" ]; then
  zip -r loadingbg_diff.zip diff_loadingbg
  echo "true" > has_diff.flag
else
  echo "false" > has_diff.flag
  echo "No diff files detected"
fi
