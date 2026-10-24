#!/bin/bash
# Pass 2: every comment (with replies) per video, written to <id>.comments.info.json
# in the same per-video folder as pass 1. Usage: run_pass2_comments.sh <shard number 1-3>
# Resumable: finished videos are recorded in archive_comments_<n>.txt.
N=$1
cd /d/NaturalHypertrophy/videos
python -m yt_dlp --js-runtimes node \
  -a ../_meta/urls_shard$N.txt --download-archive ../_meta/archive_comments_$N.txt \
  --skip-download --write-info-json --write-comments \
  -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
  -o "infojson:%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.comments" \
  --force-write-archive \
  --windows-filenames --ignore-errors --no-progress \
  --sleep-requests 1 --sleep-interval 5 --max-sleep-interval 10 --retries 10 --extractor-retries 5 \
  >> ../_meta/pass2_$N.log 2>> ../_meta/pass2_${N}_errors.log
echo "DONE exit=$?" >> ../_meta/pass2_$N.log
