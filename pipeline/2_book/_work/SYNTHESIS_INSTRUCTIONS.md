# Synthesis step: one topic file → one synthesis

You are writing the reference synthesis of everything the YouTuber **Natural Hypertrophy** ("NH", French natural bodybuilder, ~1,400 videos 2020-2026) said on one topic. Chapter writers will work **only from your file**, so nothing important may be lost, and nothing may be added that he didn't say.

## Input
`D:\NaturalHypertrophy\bodybuilding_book\derived\topics\<topic>.md` (your prompt names one or more). It is script output: his claims, near-duplicates merged, grouped into rough themes (theme labels are machine keywords; ignore them), each line:
`- [Nv Y1-Y2 types] claim {numbers by month} also: variants {{id@sec}} …`
Nv = distinct videos that said it. Types: P principle, R prescription, O opinion, A anecdote, D data; `?` = garbled caption, inferred. At the end the script flags **possible contradictions** (similar claims, different years, different numbers or stance); many are false alarms, so verify them against the claims.

Read the **whole file** with Read (pages of ~600 lines) before writing. Don't open other files, don't search, don't explore. Claims come from auto-captions via another model: drop junk; if a claim belongs to another topic but is useful, keep it under "Misfiled but useful".

Lexical merging is weak, so the same idea often appears as several 1v lines in different words. **Your main job is merging these**: count the distinct videos behind each merged idea and note the span of years.

## Output: `D:\NaturalHypertrophy\bodybuilding_book\derived\synthesis\<topic>.md`
1. `# <Topic>` then **Bottom line** (3-6 lines): his core positions as of his latest videos.
2. `## Positions`, grouped under `###` sub-themes you choose. One bullet per distinct idea:
   `- **<his position, specific, with numbers>** — <P/R/O…>; ~N videos, YYYY → YYYY; confidence: high/medium/low; <conditions, reasoning, nuance in a few words> {{id@sec}} {{id@sec}} {{id@sec}}`
   - Confidence = how often and how recently he said it: high = repeated across years and still said lately; medium = a few times or only early; low = once, garbled, or contradicted later.
   - Cite 1-4 of the clearest instances, including the earliest and the latest. Copy `{{id@sec}}` markers **exactly** as given; never invent or edit ids or seconds.
   - Keep every concrete number (sets, reps, RIR, rest, frequency, weeks, kcal, g/kg, %, loads). When he gave different values at different times, list them with dates.
   - Order by importance (recurrence × specificity × relevance to building a program).
3. `## Prescriptions table` (if any): `| what | his numbers | context/who for | cites |`. These feed the program builder; be exact.
4. `## How his view changed`: real changes or refinements over time, both sides with dates and cites, which is the later view. "None found" if none.
5. `## Contradictions`: things he said that conflict without a clear evolution (both sides, cites). Mark script flags you checked and rejected as false alarms in one line at the end, briefly.
6. `## Signature examples` (max ~8, one line each, cited): anecdotes that illustrate a principle.
7. `## Misfiled but useful` / `## Uncertain` (cited), only if needed.

## Rules
- Your own words; dense; no padding; no generic fitness knowledge he didn't say. Quotes: at most a few, each under 15 words, in quotation marks.
- Claims about real people, brands or other creators (steroid use, dishonesty, etc.) are **his unverified opinions**; write them that way ("he claims…", "in his view…").
- Length: roughly 1 output line per 5-8 input lines; never drop a distinct idea that has a number or a rule.
- Several topics in your prompt → one output file per topic, same format.

## Finish
Reply with one line per file: `<topic>: <n positions>, <n changes>, <n contradictions>`, nothing else.
