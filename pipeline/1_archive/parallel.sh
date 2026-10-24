#!/bin/bash
# Signed-in, 3 parallel yt-dlp jobs over the videos not yet in archive.txt (account cap ~2000 videos/h).
# Each shard has its own archive + cookie copy; merged into archive.txt at the end, then repair + docs.
# Usage: parallel.sh <cookies.txt>
COOK="$1"; JOBS=${2:-3}; SLEEP=${3:-0}
cd /d/NaturalHypertrophy/videos
M=../_meta
log() { echo "$(date '+%F %T') $*" >> $M/fast_loop.log; }
python -I - <<EOF
N = $JOBS
done_ids = {l.split()[-1] for l in open('$M/archive.txt') if l.strip()}
urls = [u for u in open('$M/urls.txt').read().split() if u.rsplit('=', 1)[-1] not in done_ids]
for i in range(N):
    open(f'$M/rem_{i+1}.txt', 'w').write('\n'.join(urls[i::N]) + '\n')
print(len(urls), 'remaining')
EOF
log "parallel start, done=$(wc -l < $M/archive.txt)"
for n in $(seq 1 $JOBS); do
  cp "$COOK" $M/cookies_$n.txt
  python -m yt_dlp --js-runtimes node --cookies $M/cookies_$n.txt \
    -a $M/rem_$n.txt --download-archive $M/archive_rem_$n.txt \
    --skip-download --force-write-archive --extractor-args "youtube:skip=hls,dash" \
    --write-info-json --write-description --write-thumbnail \
    --write-subs --write-auto-subs --sub-langs "en.*,-live_chat" --sub-format vtt \
    -o "%(upload_date>%Y-%m-%d)s - %(title).80B [%(id)s]/%(id)s.%(ext)s" \
    --windows-filenames --no-overwrites --ignore-errors --no-progress \
    --sleep-requests $SLEEP --retries 10 --extractor-retries 5 \
    >> $M/pass1.log 2>> $M/pass1_errors_p$n.log &
done
wait
cat $M/archive_rem_*.txt >> $M/archive.txt
sort -u $M/archive.txt -o $M/archive.txt
rm -f $M/cookies_*.txt
log "parallel end, done=$(wc -l < $M/archive.txt)"
log "repair start"; bash $M/repair_transcripts.sh "$COOK"
log "ALL DONE, done=$(wc -l < $M/archive.txt)"
