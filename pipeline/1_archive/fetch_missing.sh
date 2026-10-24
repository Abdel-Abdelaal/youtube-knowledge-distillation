#!/bin/bash
# Signed in: re-fetch captions for videos whose captions were refused earlier (429s),
# and download temporary audio for videos with no YouTube captions (for Whisper; deleted after).
# Usage: fetch_missing.sh <cookies.txt>
COOK="$1"
cd /d/NaturalHypertrophy/videos
M=../_meta
OUT='%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s'
cp "$COOK" $M/cookies_c.txt
python -m yt_dlp --js-runtimes node --cookies $M/cookies_c.txt -a $M/refetch_caps.txt \
  --skip-download --extractor-args "youtube:skip=hls,dash" \
  --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt --sleep-subtitles 2 \
  -o "$OUT" --windows-filenames --ignore-errors --no-progress \
  >> $M/fetch_missing.log 2>&1 &
for n in 1 2 3; do
  cp "$COOK" $M/cookies_a$n.txt
  python -m yt_dlp --js-runtimes node --cookies $M/cookies_a$n.txt -a $M/audio_$n.txt \
    -f "ba[ext=m4a]/ba" -o "$OUT" --windows-filenames --no-overwrites --ignore-errors --no-progress \
    --retries 10 >> $M/fetch_missing.log 2>&1 &
done
wait
rm -f $M/cookies_c.txt $M/cookies_a*.txt
echo "$(date '+%F %T') fetch_missing done" >> $M/fast_loop.log
