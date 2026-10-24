# The Bodybuilding Book kit: Natural Hypertrophy, decoded

A structured, cited reference of what the YouTube creator **Natural Hypertrophy** (NH, @NaturalHypertrophy) teaches about natural bodybuilding. It was built from all **1,411 of his videos (2020–2026)** plus his 117 community posts.

Use it as a **source of truth**: look up what he actually says, check a program or a claim against his principles, and see where he changed his mind. Every principle links to the exact second of the video it came from, so you can always verify it.

> This is an independent fan-made summary, written in our own words. It isn't affiliated with or endorsed by NH. Follow the timestamp links to hear him say it. It isn't medical advice.

## What's inside

| Path | What |
|---|---|
| `reference/THE_BODYBUILDING_BOOK.html` | **Start here.** The full book: 14 chapters + appendices (contradictions & how his views changed, strength log, glossary, FAQ). Open it in any browser. |
| `reference/THE_BODYBUILDING_BOOK.md`, `reference/chapters/` | Same content as Markdown |
| `reference/CHECKLIST.md` | Yes/no checks per topic, for testing any program or claim against his rules |
| `reference/principles.json` | All **2,331 principles** as data. Each has an ID (e.g. `VOL-03`, `RST-21`), his position, numbers, scope, confidence, status (current / changed / contradicted) and citations |
| `reference/nh_reference.db` | SQLite: principles, ~23.7k claims, exercises & cues, his stats, strength log, video list, citations (with full-text search) |
| `ask.py` | Search tool (Python 3, no installs) |
| `CLAUDE.md` | Instructions for your Claude: how to use this as a reference, and how to rebuild or extend it |
| `pipeline/` | Every script and agent instruction used to build it (see "Rebuild" below) |

## Quick start

```bash
python ask.py "rest between sets"          # principles + claims, best matches first, with video links
python ask.py VOL-03                       # one principle in full
python ask.py deload --only principles
python ask.py protein --topic nutrition --since 2024
```

Or open the folder with Claude Code and ask things like *"what does NH say about training to failure?"* or *"check my program against the checklist"*. `CLAUDE.md` tells it how.

## Not included, and why

- **Raw transcripts, the transcript search index and verbatim quote snippets.** These are NH's own words copied word for word, and they're his to publish. You can regenerate them yourself from YouTube with `pipeline/1_archive` (a few hours); `ask.py` then also searches them.
- **Viewer comments and questions.** These are other people's posts and usernames.
- Audio, video, logs and login cookies.

## Rebuild or extend it (e.g. new videos, or another creator)

1. **`pipeline/1_archive/`** downloads metadata + English captions with `yt-dlp`, transcribes uncaptioned videos with Whisper (GPU), and builds per-video `README.md` / `transcript.txt` (`build_docs.py`).
2. **`pipeline/2_book/`** turns transcripts into the book:
   - **map:** AI agents write one JSON note per video into `raw/` (included, quotes stripped)
   - **reduce:** a script groups claims by topic, with no AI needed
   - **synthesis**, then **chapters:** AI agents
   - **assemble + check:** scripts
   `_work/*_INSTRUCTIONS.md` are the exact agent briefs. `README_original.md` documents every script.

The scripts were written for one Windows machine and assume the root folder `D:\NaturalHypertrophy` (Git Bash + Python 3.12). Ask your Claude to point them at your own folder; see `CLAUDE.md` for this and for the lessons learned (rate limits, usage limits, Whisper setup).
