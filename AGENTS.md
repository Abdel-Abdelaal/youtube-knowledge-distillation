# AGENTS.md: working with the Bodybuilding Book kit

This folder is a cited reference of Natural Hypertrophy's (NH) teachings, distilled from 1,411 YouTube videos. Read `README.md` for the layout.

## Answering questions (default use)
- Search first, answer second. Run `python ask.py "<terms>"` (add `--only principles`, `--topic VOL`, `--since 2024` as needed), or query `reference/nh_reference.db` directly with SQL. Base answers on what comes back.
- **Cite principle IDs** (e.g. `RST-21`) and their video links. If nothing in the reference supports a statement, say so; don't fill gaps from general fitness knowledge without labelling it as yours.
- Respect each principle's `confidence` and `status`. "changed" and "contradicted" principles have the history in the "contradictions & evolution" appendix (`reference/chapters/A1_contradictions.md`). Prefer his most recent stance unless asked about history.
- Keep NH's position separate from your own inference. Allegations he made about real people are his unverified claims.

## Checking a program or claim
- Walk through `reference/CHECKLIST.md` topic by topic. For each check, say pass / fail / not applicable, with the principle ID and a one-line reason. Then summarise the gaps and what to change.
- For numbers (sets, reps, RIR, frequency, rest, calories, protein, bulk/cut rates), read the principle's `numbers` and `scope` fields (beginner vs advanced, natural, goal) before judging.

## Useful tables in `reference/nh_reference.db`
- `principles` (+ `principles_fts`): id, chapter, section, title, statement, numbers, scope, confidence, confidence_level, status, check_q, citations ("videoId@seconds" list)
- `claims` (+ `claims_fts`): ~23.7k one-line claims with video_id, ts_sec, date, topic, subtopic, type, numbers_json
- `exercises` (name, cues, why), `stats` (his bodyweight/measurements over time), `training_log` (lifts parsed from video titles), `videos` (id, date, title, duration, views, transcript_source), `citations`, `topics`, `chapters`
- Video link: `https://youtu.be/<video_id>?t=<ts_sec>`. Ids longer than 11 characters are community posts: `https://www.youtube.com/post/<id>`.

## Rebuilding / extending (only if the user asks)
- Scripts in `pipeline/` assume the root `D:\NaturalHypertrophy` (with `_meta/`, `videos/`, `bodybuilding_book/`). Before running anything, set up that layout under the user's chosen folder and replace the hard-coded root in the copied scripts.
- Order: `1_archive/run_pass1_media.sh` (or the faster `parallel.sh` when signed in) → `repair_transcripts.sh` → Whisper (`fetch_missing.sh`, `whisper_transcribe.py`) for videos without captions → `build_docs.py` → `2_book` per `README_original.md` (manifest → make_batches → map agents with MAP_INSTRUCTIONS.md → stub_notes / check → build_db → reduce.py → synthesis agents → chapter agents → principles.py → assemble.py → check.py).
- New videos only: archive them, map just the ids without notes (`make_batches.py` skips existing ones), then rerun build_db → reduce → re-synthesise only the affected topics → assemble.

## Lessons learned (save the user time and usage)
- **YouTube rate limits:** signed out, the cap is about 300 videos/hour; above that YouTube blocks the IP for about an hour ("This content isn't available"). With `--skip-download`, `--sleep-interval` does nothing, so pace with `--sleep-requests`. Signed in (a cookies.txt the user exports themselves from a spare account), the cap is about 2,000/hour: 4 parallel yt-dlp jobs worked. Never extract browser cookies yourself.
- Pulling **every comment** for 1,400 videos is very slow (days). Skip it unless it's essential.
- **Whisper:** faster-whisper + `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` works on a 4 GB GPU (medium, int8, VAD on). PyAV ≥ 15 breaks faster-whisper's decoder, which is why `whisper_transcribe.py` decodes audio itself. Run one process per GPU. YouTube auto-captions sometimes misdetect the language ("ru-orig" garbage): treat those as uncaptioned.
- **Usage limits:** the map step is the expensive part (~5M words). What helped:
  - fresh, lean orchestrator sessions (don't let one session's history balloon)
  - batches packed by word count (~60k), filler-stripped transcripts, compact note schema
  - no agents for near-empty transcripts
  - script-based reduce
  - committing + README status after every wave so a limit stop loses nothing
- When killing background jobs on Windows/Git Bash, stop the parent bash script before its python child. Otherwise the script's "after" steps run. Never edit a bash script while it's running: bash reads it incrementally.


## Engineering and observability

Follow the [fleet handbook](https://github.com/Abdel-Abdelaal/.github/tree/main/standards).
Changes use Conventional Commit PR titles and full-SHA workflow/action pins.
The default branch is master. Do not run archive, transcription or AI synthesis
pipelines as CI checks: they need external data, credentials and explicit approval.
No dependency environment or full pipeline test suite is defined in this kit.

Shared CI checks workflow policy, secret history, dependencies and Python/Actions
CodeQL. Advisory AI review and weekly audits produce signed records when the
repository AI secret is configured; fix PR creation additionally needs the App.
Records are linked from the [public metrics dashboard](https://abdel-abdelaal.github.io/github-governance/).
Historical extraction/synthesis runs predate telemetry and are not measured by it.
Never commit cookies, credentials or raw third-party transcripts.

## Glossary

| Name | Meaning |
|---|---|
| NH | Natural Hypertrophy, the creator whose teaching is cited |
| principle | A synthesized teaching with a stable ID and source citations |
| map | Extract structured claims from one source video |
| reduce | Group claims by topic before synthesis |
| telemetry | Signed evidence from the shared advisory CI runner |
