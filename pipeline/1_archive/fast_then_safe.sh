#!/bin/bash
# Phase 1: fast (~550-700/h) until 450 more videos are done (or YouTube starts blocking).
# Phase 2: safe pace (~220/h, under the documented ~300/h guest cap) for the rest, then repair + docs.
cd /d/NaturalHypertrophy/videos
M=../_meta
log() { echo "$(date '+%F %T') $*" >> $M/fast_loop.log; }
# ~55 videos already went through fast since the block lifted, so 420 keeps the total under 500
start=$(wc -l < $M/archive.txt); target=$((start + 420))
errstart=$(wc -l < $M/pass1_errors.log)
log "fast phase start, done=$start, target=$target"
python -m yt_dlp --js-runtimes node \
  -a $M/urls.txt --download-archive $M/archive.txt \
  --skip-download --force-write-archive --extractor-args "youtube:skip=hls,dash" \
  --write-info-json --write-description --write-thumbnail \
  --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
  -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
  --windows-filenames --no-overwrites --ignore-errors --no-progress \
  --sleep-requests 1 --retries 10 --extractor-retries 5 \
  >> $M/pass1.log 2>> $M/pass1_errors.log &
pid=$!
blocked=0
while kill -0 $pid 2>/dev/null; do
  sleep 10
  [ "$(wc -l < $M/archive.txt)" -ge $target ] && break
  hits=$(tail -n +$((errstart+1)) $M/pass1_errors.log | grep -cE "rate-limited|Video unavailable")
  [ "$hits" -ge 3 ] && { blocked=1; break; }
done
powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | ? { \$_.CommandLine -match 'yt_dlp' -and \$_.CommandLine -match 'urls\.txt' } | % { Stop-Process -Id \$_.ProcessId -Force }"
log "fast phase end, done=$(wc -l < $M/archive.txt), blocked=$blocked"
if [ $blocked = 1 ]; then
  until python -m yt_dlp --js-runtimes node --skip-download --extractor-args "youtube:skip=hls,dash" \
        --print id https://www.youtube.com/watch?v=__Tev4BM7rg >/dev/null 2>&1; do log "still blocked"; sleep 300; done
  log "block lifted"
fi
log "safe phase start"
bash $M/run_transcripts.sh
log "ALL DONE, done=$(wc -l < $M/archive.txt)"
