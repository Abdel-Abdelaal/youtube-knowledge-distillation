# Reduce step: consolidate one topic's claims

You are consolidating everything the YouTuber **Natural Hypertrophy** ("NH", French natural bodybuilder, videos 2020-2026) said on one topic, extracted from ~1,400 of his videos, into a dense reference file that book-chapter writers will rely on. They will NOT see the raw claims, so nothing important may be lost.

## Input
One or more files under `D:\NaturalHypertrophy\bodybuilding_book\derived\claims\` (your prompt names them, maybe with a line range). Each line is one extracted claim, chronological:
`YYYY-MM-DD {{videoId@seconds}} type [body_part] claim text  {numbers}`
`type` is principle / prescription / opinion / anecdote / data. Read ALL your assigned lines (page with Read offset/limit, ~400 lines at a time, until the end). Claims were machine-extracted from auto-captions: a few are garbled or misfiled; drop junk, and if a claim clearly belongs to another topic still keep it under a "Misfiled but useful" heading at the end.

## Output
Write the file your prompt names (Markdown). Structure:

1. `# <Topic>` then a 3-6 line **Bottom line**: NH's core position(s) as of his latest videos.
2. **Positions**, grouped under `##` sub-themes you choose. One bullet per distinct idea, after merging duplicates:
   `- **<position in your own words, specific, with numbers>** — <type(s)>; said in N videos, YYYY-MM → YYYY-MM; <nuance/conditions/reasoning in a few words> {{id@t}} {{id@t}} {{id@t}}`
   - N = how many distinct videos expressed it (count the distinct ids you merged). Cite 1-4 of the clearest instances, always including the earliest and the latest; copy the `{{id@t}}` markers exactly as given (never invent ids or seconds).
   - Keep every concrete number and range (sets, reps, RIR, rest, frequency, kcal, g/kg, %, weeks…). When he gives several values for the same thing, list them with dates.
   - Order bullets by importance (recurrence × specificity).
3. `## Prescriptions table` (only if the topic has any): `| what | NH's numbers | context | cites |`.
4. `## Evolution & contradictions`: where he changed his mind, refined a view, or said conflicting things. Give both sides with dates and cites, and say which is his later view. Write "None found" if none.
5. `## Signature anecdotes & examples` (max ~8, one line each, cited) — only those that illustrate a principle.
6. `## Open/uncertain` — claims that were low-confidence or garbled but potentially important (cited).

Rules: your own words, dense, no padding, no generic fitness knowledge that NH didn't say. Never quote more than 15 words verbatim. Length scales with input: aim for roughly 1 output line per 6-10 input claims, but never drop a distinct idea.

## Finish
Reply with one line: `<output file>: <n positions>, <n contradictions>` and nothing else.
