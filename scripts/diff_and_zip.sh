#!/usr/bin/env bash
set -e

mkdir -p diff_loadingbg

# 如果 current_loadingbg 不存在或为空，视为“本次无更新”
if [ ! -d "current_loadingbg" ] || [ -z "$(ls -A current_loadingbg 2>/dev/null)" ]; then
  echo "No current_loadingbg found. Treating as no update."
  echo "false" > has_diff.flag

  # 兜底：如果已有 last_loadingbg，用它生成 full 包
  if [ -d "last_loadingbg" ]; then
    zip -r loadingbg_full.zip last_loadingbg
  else
    echo "No last_loadingbg either, nothing to package."
    touch loadingbg_full.zip
  fi

  exit 0
fi

HAS_DIFF=0

# 有 last_loadingbg 才做 diff 比较
if [ -d "last_loadingbg" ]; then
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
else
  # 首次运行：把所有 current 当成 diff
  cp current_loadingbg/* diff_loadingbg/ || true
  HAS_DIFF=1
fi

# 生成 full 包（以 current 为准）
zip -r loadingbg_full.zip current_loadingbg

if [ "$(ls -A diff_loadingbg 2>/dev/null)" ]; then
  zip -r loadingbg_diff.zip diff_loadingbg
  echo "true" > has_diff.flag
else
  echo "false" > has_diff.flag
fi
