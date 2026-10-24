#!/bin/bash
# Two Whisper processes in parallel: the 85-min video on its own, everything else in the other.
# Then rebuild docs and write the WHISPER DONE marker the book session is waiting for.
cd /d/NaturalHypertrophy/_meta
BIG=nmR3tXZ5YRI
# one process only: a single Whisper already keeps the 4 GB GPU ~85% busy; more copies just fight over it
python -I whisper_transcribe.py medium >> whisper.log 2>&1
echo "audio left after whisper: $(find ../videos -name '*.m4a' | wc -l)" >> whisper.log
python -I build_docs.py >> whisper.log 2>&1
echo "$(date '+%F %T') WHISPER FINAL (last 4 transcripts added)" >> fast_loop.log
