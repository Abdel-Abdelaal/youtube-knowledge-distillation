#!/bin/bash
# Fast transcript pass (~700 videos/h). When YouTube starts rate-limiting, kill yt-dlp,
# probe every 10 min until the block lifts, then resume. Progress is kept in archive.txt.
cd /d/NaturalHypertrophy/videos
M=../_meta
PROBE=https://www.youtube.com/watch?v=__Tev4BM7rg
log() { echo "$(date '+%F %T') $*" >> $M/fast_loop.log; }

while true; do
  before=$(wc -l < $M/archive.txt)
  errstart=$(wc -l < $M/pass1_errors.log)
  log "run start, done=$before"
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
    # 3+ "unavailable"/"rate-limited" errors since this run started = we're being blocked
    hits=$(tail -n +$((errstart+1)) $M/pass1_errors.log | grep -cE "rate-limited|Video unavailable")
    if [ "$hits" -ge 3 ]; then
      blocked=1; kill $pid 2>/dev/null
      powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | ? { \$_.CommandLine -match 'yt_dlp' -and \$_.CommandLine -match 'urls\.txt' } | % { Stop-Process -Id \$_.ProcessId -Force }"
      break
    fi
  done
  wait $pid 2>/dev/null
  log "run end, done=$(wc -l < $M/archive.txt), blocked=$blocked"
  if [ $blocked = 0 ]; then log "finished without block"; break; fi
  # blocked but nothing new got done = the errors are genuinely unavailable videos, not a block
  if [ "$(wc -l < $M/archive.txt)" -le "$before" ] && [ "${lastzero:-0}" = 1 ]; then log "no progress twice, stopping"; break; fi
  [ "$(wc -l < $M/archive.txt)" -le "$before" ] && lastzero=1 || lastzero=0
  # wait for the block to lift
  until python -m yt_dlp --js-runtimes node --skip-download --extractor-args "youtube:skip=hls,dash" \
        --print id $PROBE >/dev/null 2>&1; do log "still blocked"; sleep 600; done
  log "block lifted"
done
bash $M/repair_transcripts.sh
log "ALL DONE"
