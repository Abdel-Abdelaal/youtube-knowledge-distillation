#!/bin/bash
# Resumable archive of @NaturalHypertrophy: audio + metadata + description + subs + all comments
cd /d/NaturalHypertrophy/videos
python -m yt_dlp --js-runtimes node \
  -a ../_meta/urls.txt --download-archive ../_meta/archive.txt \
  -f "ba[ext=m4a][format_note*=original]/ba[ext=m4a]/ba" \
  --write-info-json --write-description --write-thumbnail \
  --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
  --write-comments \
  -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
  --windows-filenames --no-overwrites --ignore-errors --no-progress \
  --sleep-interval 2 --max-sleep-interval 5 --retries 10 --extractor-retries 5 \
  >> ../_meta/download.log 2>> ../_meta/download_errors.log
echo "DONE exit=$?" >> ../_meta/download.log
