#!/bin/bash
# Steady pace just under YouTube's documented guest cap (~300 videos/h) until every video is done.
# If YouTube blocks anyway, stop, re-check every 5 min, resume. Then re-fetch missing captions and rebuild docs.
# Optional: pass a cookies.txt path as $1 to run signed in (cap ~2000/h, so pacing is lighter).
cd /d/NaturalHypertrophy/videos
M=../_meta
log() { echo "$(date '+%F %T') $*" >> $M/fast_loop.log; }
if [ -n "$1" ]; then AUTH=(--cookies "$1"); PACE=(); else AUTH=(); PACE=(--sleep-requests 1.2 --sleep-subtitles 4); fi
PROBE=https://www.youtube.com/watch?v=__Tev4BM7rg
lastdone=-1
while true; do
  before=$(wc -l < $M/archive.txt)
  [ "$before" = "$lastdone" ] && { log "no progress in last run, moving on"; break; }
  lastdone=$before
  errstart=$(wc -l < $M/pass1_errors.log)
  log "steady run start, done=$before, signed_in=${1:+yes}"
  python -m yt_dlp --js-runtimes node "${AUTH[@]}" \
    -a $M/urls.txt --download-archive $M/archive.txt \
    --skip-download --force-write-archive --extractor-args "youtube:skip=hls,dash" \
    --write-info-json --write-description --write-thumbnail \
    --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
    -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
    --windows-filenames --no-overwrites --ignore-errors --no-progress \
    "${PACE[@]}" --retries 10 --extractor-retries 5 \
    >> $M/pass1.log 2>> $M/pass1_errors.log &
  pid=$!
  blocked=0
  while kill -0 $pid 2>/dev/null; do
    sleep 10
    hits=$(tail -n +$((errstart+1)) $M/pass1_errors.log | grep -cE "rate-limited|Video unavailable")
    [ "$hits" -ge 3 ] && { blocked=1; break; }
  done
  powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | ? { \$_.CommandLine -match 'yt_dlp' -and \$_.CommandLine -match 'urls\.txt' } | % { Stop-Process -Id \$_.ProcessId -Force }"
  log "steady run end, done=$(wc -l < $M/archive.txt), blocked=$blocked"
  [ $blocked = 0 ] && break
  until python -m yt_dlp --js-runtimes node "${AUTH[@]}" --skip-download --extractor-args "youtube:skip=hls,dash" \
        --print id $PROBE >/dev/null 2>&1; do log "still blocked"; sleep 300; done
  log "block lifted"
done
log "repair start"; bash $M/repair_transcripts.sh "$1"
log "ALL DONE, done=$(wc -l < $M/archive.txt)"
