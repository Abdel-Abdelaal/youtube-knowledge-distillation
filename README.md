# YouTube knowledge distillation: Natural Hypertrophy, decoded

A proof of concept: **turning an entire YouTube channel into a structured, cited, queryable knowledge base, end to end with AI** (Claude Code orchestrating multi-agent pipelines). Built in about 4 days.

The subject is the natural-bodybuilding channel **Natural Hypertrophy** (NH): 1,411 videos over 6 years. The output is *The Bodybuilding Book*, a source-of-truth reference of everything he teaches. Every principle is traceable to the exact second of the video it came from.

> Unofficial and fan-made, written in our own words. Not affiliated with or endorsed by Natural Hypertrophy. Not medical advice.

## What was built

| | |
|---|---|
| Videos processed | **1,411** (1,392 uploads + 19 livestreams, ~504 hours) + 117 community posts |
| Transcripts | 5.4M words: 1,064 from YouTube captions, 343 transcribed locally with **Whisper** on a 4 GB GPU |
| Extraction | **23,669 claims** and **3,722 exercise cues** pulled from every transcript by parallel AI agents (map step) |
| Synthesis | claims grouped by script into 28 topics, then synthesised by agents into **2,331 principles** across 14 chapters + appendices (~290k words) |
| Traceability | **9,850 citations**, each validated against a real video id and timestamp |
| Interfaces | HTML/Markdown book, `CHECKLIST.md` (224 yes/no checks), `principles.json`, SQLite DB with full-text search, `ask.py` CLI |

## How it works

```
YouTube channel
  └─ 1. Archive    yt-dlp (metadata + captions; rate-limit aware, resumable, parallel when signed in)
                   + Whisper for uncaptioned videos → per-video folders, index
  └─ 2. Map        ~200 AI agent batches → one JSON note per video (claims, numbers, exercises, stats, timestamps)
  └─ 3. Reduce     Python: group / de-duplicate / count support / flag contradictions per topic (no AI)
  └─ 4. Synthesise AI agents per topic → positions, numbers, how his views changed over time, confidence
  └─ 5. Write      AI agents per chapter → principles with stable IDs (VOL-03, RST-21 …), scope, status, citations
  └─ 6. Assemble   Python: SQLite + FTS5, JSON export, HTML/MD book, citation checks, git commit + backup per phase
```

Built to survive interruptions: every step is idempotent and resumable, progress is committed after each wave, and usage-limit stops lost no work.

## Try it

```bash
python ask.py "rest between sets"     # principles + claims with video links
python ask.py VOL-03                  # one principle in full
```

Or open `reference/THE_BODYBUILDING_BOOK.html` in a browser. Open the folder with Claude Code and it follows `CLAUDE.md`: ask it questions, or have it check a training program against the checklist.

Example principle:

```
[PRG-01] Progressive overload is non-negotiable   (04_progression_fatigue)
    Without progressive overload there is no muscle gain; something has to go up for the muscles to go up.
    Scope: All trainees, especially naturals.
    Confidence: high (~15 videos, 2020→2024)  |  Status: current
    - https://youtu.be/YIIWlqhoNA0?t=251 …
```

## Searching

`ask.py` takes a query plus optional filters:

- **`query`** — one or more words, joined with spaces. Plain words are AND-matched with prefix matching; explicit FTS5 syntax is passed through (`OR`, `AND`, `NOT`, `"phrases"`, `prefix*`). A query that is a single principle ID (e.g. `VOL-03`) shows that principle in full.
- **`--only {principles,claims,transcripts}`** — search one layer only; the default is all layers. Transcripts are searched only if the DB has a `transcript_fts` table — the kit does not ship transcripts (you rebuild them with the pipeline).
- **`--topic TOPIC`** — filters claims by topic (e.g. `volume`) and principles by ID prefix (e.g. `VOL`); it does not filter transcripts.
- **`--since YYYY|YYYY-MM`** — claims and transcripts on or after that date; it does not apply to principles.
- **`-n N`** — an integer, the maximum results per layer (default 10).

```bash
python ask.py deload --only principles           # search one layer only
python ask.py protein --topic nutrition -n 30    # topic filter, up to 30 results per layer
python ask.py "rir OR failure" --since 2024      # FTS5 operators; on or after 2024
```

## Repo layout

- `reference/`: the book, chapters, checklist, `principles.json`, `nh_reference.db`
- `ask.py`: search CLI
- `pipeline/1_archive/`: download, captions, Whisper and per-video docs scripts
- `pipeline/2_book/`: map/reduce/synthesis/chapter scripts, the exact agent instruction files, and the per-video notes (`raw/`)
- `CLAUDE.md`: how an AI assistant should use and rebuild this, plus lessons learned
- `KIT_GUIDE.md`: detailed usage, and what's deliberately not included

Raw transcripts, verbatim quotes and viewer comments are **not** included: the creator's own words and other people's posts aren't ours to republish. The pipeline regenerates the transcripts from YouTube.


## Engineering checks and AI evidence

PRs run the shared fleet policy and security workflows. Weekly advisory AI audits
and eligible PR reviews retain signed records and publish measured results on the
[fleet dashboard](https://abdel-abdelaal.github.io/github-governance/).
Missing credentials produce explicit skips; historical book-building AI runs have
no retrospective telemetry. The automation App is required for generated fix and
baseline PRs. No archive, transcription or synthesis pipeline is executed by CI.

Original software scripts use the scoped [MIT license](LICENSE). The book and
reference dataset are outside that grant; source videos and other third-party
material retain their own rights.
