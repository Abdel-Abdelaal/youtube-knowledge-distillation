# Appendices B (glossary) and D (FAQ) of The Bodybuilding Book

The book is a principle reference for what the YouTuber Natural Hypertrophy ("NH") teaches. Every principle has an ID like `VOL-03`. Your inputs:
- `D:\NaturalHypertrophy\bodybuilding_book\derived\principle_index.txt`: one line per principle, `ID | title | statement`. Read it all.
- `D:\NaturalHypertrophy\bodybuilding_book\derived\claims\_questions.txt`: viewer questions he answered in Q&As (one per line, with a `{{id@sec}}` marker). Read it all.
- You may Grep `book\chapters\*.md` to look up a term or a principle's full block. Read nothing else.

## Output 1: `book\chapters\A2_glossary.md`
`# Appendix B. Glossary`, one-line intro, then alphabetical entries:
`- **Term** — plain definition as NH uses it (1-2 sentences). See VOL-03, INT-12.`
Cover his own vocabulary and training jargon that appears in the principles (RIR, junk volume, evolving sets, tonnage, back-off sets, the "trinity", gym look, otter mode, sandbagging, recomp, natty, etc.): ~60-120 entries. Every entry points to 1-3 principle IDs where the term is used; only define terms from what the principles say.

## Output 2: `book\chapters\A4_faq.md`
`# Appendix D. FAQ`, one-line intro, then ~40-60 of the most common or useful viewer questions (merge duplicates), grouped under `##` topics:
`### <question, in plain words>`
`<2-4 sentence answer built only from the principles> → VOL-03, FRQ-12`
Answer only from the principle index; if the principles don't answer a question, skip it. Cite principle IDs, not videos (the principles carry the sources).

## Rules
Your own words, plain and tight. No generic fitness knowledge. Don't invent IDs: every ID you write must exist in principle_index.txt.

## Finish
Reply with one line: `A2_glossary.md: <n> terms; A4_faq.md: <n> questions`.
