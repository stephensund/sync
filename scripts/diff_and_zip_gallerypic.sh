#!/usr/bin/env bash
set -e

mkdir -p diff_gallerypic

# 如果 current_gallerypic 不存在或为空，视为"本次无更新"
if [ ! -d "current_gallerypic" ] || [ -z "$(ls -A current_gallerypic 2>/dev/null)" ]; then
  echo "No current_gallerypic found. Treating as no update."
  echo "false" > has_diff_gallerypic.flag

  # 兜底：如果已有 last_gallerypic，用它生成 full 包
  if [ -d "last_gallerypic" ]; then
    zip -r gallerypic_full.zip last_gallerypic
  else
    echo "No last_gallerypic either, nothing to package."
  fi

  exit 0
fi

HAS_DIFF=0

# 有 last_gallerypic 才做 diff 比较
if [ -d "last_gallerypic" ]; then
  for f in current_gallerypic/*; do
    name=$(basename "$f")
    if [ ! -f last_gallerypic/"$name" ]; then
      cp "$f" diff_gallerypic/
      HAS_DIFF=1
    else
      if ! cmp -s "$f" last_gallerypic/"$name"; then
        cp "$f" diff_gallerypic/
        HAS_DIFF=1
      fi
    fi
  done
else
  # 首次运行：把所有 current 当成 diff
  cp current_gallerypic/* diff_gallerypic/ || true
  HAS_DIFF=1
fi

# 生成 full 包：合并 last_gallerypic + current_gallerypic（current 覆盖 last）
mkdir -p full_gallerypic
if [ -d "last_gallerypic" ]; then
  cp -r last_gallerypic/* full_gallerypic/ 2>/dev/null || true
fi
if [ -d "current_gallerypic" ]; then
  cp -r current_gallerypic/* full_gallerypic/ 2>/dev/null || true
fi
zip -r gallerypic_full.zip full_gallerypic
rm -rf full_gallerypic

if [ "$(ls -A diff_gallerypic 2>/dev/null)" ]; then
  zip -r gallerypic_diff.zip diff_gallerypic
  echo "true" > has_diff_gallerypic.flag
else
  echo "false" > has_diff_gallerypic.flag
fi
