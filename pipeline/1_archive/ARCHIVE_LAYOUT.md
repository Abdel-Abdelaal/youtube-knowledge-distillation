# Natural Hypertrophy: channel archive

Source: https://www.youtube.com/@NaturalHypertrophy (143k subscribers), archived starting 2026-10-20.
1,392 uploads + 19 livestreams = 1,411 videos (~504 hours).

## Layout

| Path | What |
|---|---|
| `INDEX.md` / `index.csv` | One row per video: date, title, length, views/likes, transcript type, comments saved, folder |
| `links.csv` | Every URL found in descriptions and the creator's own comments, with how often and where it's linked |
| `videos/<date> - <title> [<id>]/` | One folder per video (see below) |
| `community_posts/` | All 116 YouTube Community posts: `posts.md` (readable), `posts.json`, `images/` |
| `linked_media/` | Written material linked from the channel (Ko-fi page, plus anything else found in descriptions) |
| `_meta/` | Scripts, logs and resume files. Safe to ignore |

### Inside each video folder

| File | What |
|---|---|
| `README.md` | Title, URL, date, duration, stats, tags, chapters, full description, links |
| `transcript.txt` | Clean English transcript with `[m:ss]` timestamps (creator captions if they exist, otherwise auto-generated) |
| `comments.md` | Every comment, replies nested under their parent, creator/pinned/hearted marked |
| `<id>.info.json` | Full raw YouTube metadata |
| `<id>.comments.info.json` | Raw metadata including all comments |
| `<id>.*.vtt` | Raw caption files |
| `<id>.description`, `<id>.webp` | Raw description and thumbnail |

## Resuming / updating

All downloads are resumable and skip anything already done (`_meta/archive*.txt`). From Git Bash:

- metadata and transcripts: `bash _meta/run_pass1_media.sh`
- comments (3 shards): `bash _meta/run_pass2_comments.sh 1`, then `2`, then `3`
- re-fetch missing transcripts and rebuild docs: `bash _meta/repair_transcripts.sh`
- rebuild docs only: `python _meta/build_docs.py`

To pick up new uploads, regenerate `_meta/urls.txt` (see the flat_*.json listing step) and run the passes again.
