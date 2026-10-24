#!/bin/bash
# Re-fetch English captions for any video folder that has no .vtt (e.g. after HTTP 429s), then rebuild docs.
cd /d/NaturalHypertrophy/videos
: > ../_meta/missing_subs.txt
for d in */; do
  id=$(echo "$d" | sed -E 's/.*\[([A-Za-z0-9_-]{11})\]\/$/\1/')
  ls "$d"*.vtt >/dev/null 2>&1 || echo "https://www.youtube.com/watch?v=$id" >> ../_meta/missing_subs.txt
done
echo "missing: $(wc -l < ../_meta/missing_subs.txt)"
# optional $1 = cookies.txt to run signed in
python -m yt_dlp --js-runtimes node ${1:+--cookies "$1"} -a ../_meta/missing_subs.txt \
  --skip-download --extractor-args "youtube:skip=hls,dash" --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
  -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
  --windows-filenames --ignore-errors --no-progress --sleep-requests 1.5 --sleep-subtitles 5 \
  >> ../_meta/repair.log 2>&1
python -I ../_meta/build_docs.py
