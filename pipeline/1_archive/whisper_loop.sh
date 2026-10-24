#!/bin/bash
# Keep transcribing new audio with Whisper until the audio downloads have finished and no audio is left,
# then rebuild all docs.
cd /d/NaturalHypertrophy/_meta
while true; do
  python -I whisper_transcribe.py medium >> whisper.log 2>&1
  left=$(find ../videos -name '*.m4a' | wc -l)
  if grep -q "fetch_missing done" fast_loop.log && [ "$left" -eq 0 ]; then break; fi
  sleep 20
done
python -I build_docs.py >> whisper.log 2>&1
echo "$(date '+%F %T') WHISPER DONE" >> fast_loop.log
