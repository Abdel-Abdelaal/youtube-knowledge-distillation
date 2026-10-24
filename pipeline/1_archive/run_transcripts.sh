#!/bin/bash
# Transcripts only, one slow job: remaining videos, then re-fetch any missing captions, then rebuild docs.
cd /d/NaturalHypertrophy/_meta
echo "pass1 start $(date)" >> resume.log; bash run_pass1_media.sh
echo "repair start $(date)" >> resume.log; bash repair_transcripts.sh
echo "ALL DONE $(date)" >> resume.log
