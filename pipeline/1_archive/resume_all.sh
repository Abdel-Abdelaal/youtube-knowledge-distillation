#!/bin/bash
# YouTube rate-limited this IP at ~17:58. Wait until ~19:05, then transcripts only, one slow job.
cd /d/NaturalHypertrophy/_meta
echo "waiting from $(date)" >> resume.log
sleep 3300
echo "pass1 start $(date)" >> resume.log; bash run_pass1_media.sh
echo "repair start $(date)" >> resume.log; bash repair_transcripts.sh
echo "ALL DONE $(date)" >> resume.log
