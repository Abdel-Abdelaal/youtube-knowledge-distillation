# The Bodybuilding Book: build workspace

This folder distills Natural Hypertrophy's 1,411 videos (plus 116 community posts and his Ko-fi page) into one cited book. The build runs **map → reduce → write → edit**. Every step is resumable and every derived file can be rebuilt.

## Status
_Updated after every wave; `git log` has the history._

- 2026-10-22 (session 5): **map complete; reduce/write/edit not started.** 1,411/1,411 videos + 117 posts = 1,528 notes, 23,669 claims; check.py clean; nh.db rebuilt; backup book_20261022_114136.zip.
- 2026-10-22 (session 6): **reduce (script) done**: `reduce.py` → `derived/topics/` (28 topics + `_exercises.md`). Next: synthesis agents (`SYNTHESIS_INSTRUCTIONS.md`) → `derived/synthesis/`; to resume, run only topics that have no synthesis file. Then chapters (`CHAPTER_INSTRUCTIONS.md`, `book/OUTLINE.md`) → editor pass → `assemble.py`.
- 2026-10-24 (session 6): **BOOK DONE.** 14 chapters + 4 appendices (A contradictions, B glossary 118 terms, C strength log, D FAQ 59 questions); **2,331 principles** (224 with Check), 9,850 citations, ~292k words. Outputs: `book/THE_BODYBUILDING_BOOK.md` + `.html`, `book/CHECKLIST.md`, `derived/principles.json`, `nh.db` table `principles`, `_work/ask.py`. principles.py --strict, check.py and assemble.py all clean. To rebuild after editing a chapter: `principles.py → build_db.py → check.py → assemble.py`.
- 2026-10-24 (session 6, after limits): scope is now a **principle reference** (IDs, checklist, `ask.py`, `principles` table; no program builder). Syntheses 18/28 committed; last 10 and chapters 01, 03, 05, 06, 08-11 running. To resume: a synthesis is missing if `derived/synthesis/<topic>.md` doesn't exist; a chapter is missing if `book/chapters/NN_*.md` doesn't exist (check the last `###` block is complete).

## Using the book as a reference
The book is a **source of truth** for what NH teaches, not a program. Every principle has a stable ID (`VOL-03`, `NUT-12`…) and the same fields: **Statement · Numbers · Scope** (natural, level, goal) **· Confidence** (how many videos/years, how recent) **· Status** (current / changed / contradicted) **· Check** (yes/no test, key principles only) **· Sources** (video links to the second).
- **Read:** `book/THE_BODYBUILDING_BOOK.html` (principle IDs are anchors: `…html#VOL-03`) or the `.md`.
- **Test a program or claim:** go through `book/CHECKLIST.md`; each "no" links to the principle, so read its Scope before judging.
- **Look something up:** `python _work/ask.py "rest between sets"` searches principles, then the 23k map claims, then raw transcripts (his exact words). `python _work/ask.py VOL-03` prints one principle; `--only claims`, `--topic nutrition` / `--topic NUT`, `--since 2024`, `-n 30`.
- **Query directly:** `derived/principles.json`, or SQL on `derived/nh.db` (table `principles`, see schema below).
- **Changed his mind?** Appendix A lists every change and contradiction by topic; each principle's Status says the same.

## Layout
| path | what | in git |
|---|---|---|
| `raw/<id>.json` | **Raw layer.** One map note per video or post. Never edited by hand. | yes |
| `derived/manifest.csv` | Videos straight from the folders (more reliable than `../index.csv`) | yes |
| `derived/nh.db` | **SQLite: single source of truth for queries.** Rebuilt from raw + transcripts. | no (rebuildable; holds transcript text) |
| `derived/claims/<topic>.txt` | Flattened claims per topic (reduce input) | yes |
| `derived/topics/<topic>.md` | Script-reduced topic files (`{{id@sec}}` citations) | yes |
| `derived/synthesis/<topic>.md` | Agent synthesis per topic (chapter input) | yes |
| `derived/cite_index.json` | id → title/date for citation expansion | yes |
| `derived/lift_log.csv`, `strength_progression.md` | Strength log parsed from lift-clip titles | yes |
| `derived/comments_digest.md` | NH's comment replies + top viewer questions (FAQ input) | yes |
| `book/chapters/NN_name.md` | Chapters (`{{id@sec}}` markers) | yes |
| `book/THE_BODYBUILDING_BOOK.md` (+ `.html`/`.pdf`) | Assembled book with expanded citations | yes |
| `_work/` | Scripts + agent instructions; `_work/batches/` is temporary (holds transcript text) | scripts yes, batches no |

Transcripts and audio stay in `..\videos\` and are never copied into git.

## Scripts (`_work/`, run from anywhere with `python _work/<script>`)
| script | does |
|---|---|
| `manifest.py` | Scans `videos/` → `derived/manifest.csv` (id, date, title, secs, words, transcript source, comments?) |
| `make_batches.py [start]` | Packs videos **with no note in raw/** into `_work/batches/bNNN.txt` (≤38k words / ≤22 videos; 60 per batch for no-speech clips). **Wipes batches/ first**, so run `posts_batch.py` afterwards. |
| `posts_batch.py` | Community posts + Ko-fi → `batches/posts.txt` (post id = YouTube post id) |
| `MAP_INSTRUCTIONS.md` | Brief for map agents: note schema + topic taxonomy |
| `explode.py` | raw → `derived/claims/*.txt` + `cite_index.json` |
| `reduce.py [topic…]` | **Script reduce** (no AI): claims → `derived/topics/<topic>.md` (near-dups merged, themes, support counts Nv/years, contradiction flags) + `_exercises.md` cue compendium |
| `SYNTHESIS_INSTRUCTIONS.md` | Brief for synthesis agents: topic file → `derived/synthesis/<topic>.md` |
| `CHAPTER_INSTRUCTIONS.md` | Brief for chapter writers (`book/OUTLINE.md` maps chapters to syntheses) |
| `assemble.py` | Chapters → `book/THE_BODYBUILDING_BOOK.md` + `.html`, markers expanded to linked citations; builds the strength-log appendix |
| `principles.py [--strict]` | Parses principle blocks in chapters → `derived/principles.json` + `book/CHECKLIST.md`; validates IDs/fields. Run before `build_db.py` |
| `ask.py "<words>"` | **Search the reference**: principles, claims and transcripts with citations (see "Using the book as a reference") |
| `REDUCE_INSTRUCTIONS.md` | Superseded by `reduce.py` + `SYNTHESIS_INSTRUCTIONS.md` |
| `lift_titles.py` | Lift-clip titles → `derived/lift_log.csv`, `strength_progression.md` |
| `comments_digest.py` | comments.md files → `derived/comments_digest.md` |
| `build_db.py` | Rebuilds `derived/nh.db` from everything above (idempotent, ~10 s) |
| `check.py [--missing] [--strict]` | Validation: missing/malformed notes, claims without timestamp, citations to unknown ids. **Run before each commit.** |
| `backup.py` | Zips the folder (without .git, batches, db) to `..\_backups\book_<ts>.zip`, keeps the last 5 |

## Database schema (`derived/nh.db`)
- `videos(id, date, title, duration_sec, views, likes, comment_count, transcript_source, words, has_comments, folder, kind)`: kind is `video` or `post`
- `notes(video_id, kind, summary, quality, topics, raw_json)`
- `claims(id, video_id, ts_sec, date, topic, subtopic, type, claim, numbers_json, confidence)`: subtopic = body part
- `exercises(video_id, ts_sec, date, name, cues, why)`, `stats(video_id, ts_sec, date, metric, value, as_of)`, `quotes(...)`, `viewer_questions(...)`
- `training_log(video_id, date, lift, load_kg, load_lbs, reps, sets, notes, source)`: source is `title` (parsed) or `note` (map agent)
- `topics(name, n_claims, n_videos, first_date, last_date, file, file_sha)`
- `chapters(name, file, version, words, n_citations, updated)`: version = content sha
- `citations(chapter, section, video_id, ts_sec, claim_id)`: each citation in the book, linked to the nearest claim
- `principles(id, chapter, section, title, statement, numbers, scope, confidence, confidence_level, status, status_level, check_q, citations)` + `principles_fts`: the book's principles (from `principles.json`)
- `transcript_fts` (FTS5: one row per `[m:ss]` paragraph, with video_id/date/ts_sec), `claims_fts` (FTS5 over claims)
- view `claims_cited`: claims with title + `youtu.be` URL

Example queries:
```sql
SELECT date, video_id, ts_sec, snippet(transcript_fts,0,'[',']','…',12) FROM transcript_fts WHERE transcript_fts MATCH 'deload' ORDER BY date;
SELECT date, claim, url FROM claims_cited WHERE id IN (SELECT rowid FROM claims_fts WHERE claims_fts MATCH 'protein') ORDER BY date;
SELECT topic, COUNT(*) FROM claims GROUP BY topic ORDER BY 2 DESC;
```

## Resume / extend
1. `python _work/manifest.py && python _work/make_batches.py 201 && python _work/posts_batch.py`. This only batches videos that have no note yet.
2. Map: for each batch in `_work/batches.json`, spawn an agent with "Read _work/MAP_INSTRUCTIONS.md and follow it for batch bNNN". Run **6–8 in parallel**. After each wave: `build_db.py` → `check.py` → update Status → `git commit`.
3. `python _work/explode.py && python _work/reduce.py` → `derived/topics/`. Then one synthesis agent per topic ("Read _work/SYNTHESIS_INSTRUCTIONS.md and follow it for topic: X") → `derived/synthesis/`.
4. Chapter agents ("Read _work/CHAPTER_INSTRUCTIONS.md and follow it. Chapter: …, Prefixes: …, Inputs: …", per `book/OUTLINE.md`) write `book/chapters/` with `{{id@sec}}` markers. Then `principles.py` → `build_db.py` → `check.py` → `assemble.py` (expands markers to `[title, YYYY-MM](https://youtu.be/<id>?t=<sec>)`, posts → `youtube.com/post/<id>`).
5. **Adding new videos later:** archive them into `videos/`, then run `manifest → make_batches → map → build_db → explode`. Re-run reduce only for topics whose claim counts changed (compare the `topics` table before and after), then re-run the chapters that cite those topics.
6. End of each phase: `check.py`, `git commit`, `backup.py`.

## Cost
A map agent uses about 150k tokens per batch (~37k transcript words). **Don't pass `model: sonnet/haiku`** to agents: in this environment every alias maps to a nonexistent model (`mimo-v2.5`). Agents must inherit the parent model, or the alias env vars must be fixed first.

## Chapters and principle ID prefixes
Defined in `book/OUTLINE.md`: 1 Journey & stats (JRN) · 2 Mindset, natural vs enhanced, genetics (MND NAT GEN) · 3 Volume, intensity, frequency, rest (VOL INT FRQ RST) · 4 Progression, fatigue, sleep (PRG FAT SLP) · 5 Exercise selection & technique (EXS TEC) · 6 Body-part playbook (CHE BAK SHO ARM FOR LEG CLF ABS NCK) · 7 Strength (STR) · 8 Aesthetics (AES) · 9 Injuries (INJ) · 10 Nutrition & supplements (NUT SUP) · 11 Bulk, cut, cardio (BLK CAR) · 12 Beginners & equipment (BEG EQP) · 13 Industry & science (IND SCI) · 14 Philosophy & culture (PHI CUL) · Appendices: A contradictions & evolution (script), B glossary, C strength log (script).
The program builder was dropped on 2026-10-22: the book is a reference to check programs against, not a program.
