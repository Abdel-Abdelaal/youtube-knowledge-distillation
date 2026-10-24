#!/bin/bash
# Pass 1 (fast): metadata + description + thumbnail + English subtitles. No audio/video, no comments.
# Resumable: finished videos are recorded in archive.txt.
cd /d/NaturalHypertrophy/videos
python -m yt_dlp --js-runtimes node \
  -a ../_meta/urls.txt --download-archive ../_meta/archive.txt \
  --skip-download --force-write-archive --extractor-args "youtube:skip=hls,dash" \
  --write-info-json --write-description --write-thumbnail \
  --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
  -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
  --windows-filenames --no-overwrites --ignore-errors --no-progress \
  --sleep-requests 1.5 --sleep-subtitles 5 --retries 10 --extractor-retries 5 \
  >> ../_meta/pass1.log 2>> ../_meta/pass1_errors.log
echo "DONE exit=$?" >> ../_meta/pass1.log
