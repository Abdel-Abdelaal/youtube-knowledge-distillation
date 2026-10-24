# Map step: one compact JSON note per video

Source: YouTube channel **Natural Hypertrophy** ("NH", French natural bodybuilder: training science, vlogs, rants about lifting/manga/philosophy). Goal: a book of his whole doctrine.

**Input:** the compact transcripts `D:\NaturalHypertrophy\bodybuilding_book\_work\compact\<id>.txt` for the ids your prompt lists (from b801 on; older waves used `_work\batches\<batch>.txt`). Each starts with `=== VIDEO <id> | <YYYY-MM-DD> | <secs>s | <title>`, then TAGS / CHAPTERS / DESCRIPTION / TRANSCRIPT. Transcript lines start with `[t=<seconds>]`. Filler words and stutters are already stripped. **First message:** Read this file and every listed compact file in parallel, each with `allow_large: true` (one Read per file, no paging). Nothing else: no exploring, no globbing, no other files, no re-reading. Auto-captions are unpunctuated and mishear jargon ("are i are" = RIR, "pose reps" = pause reps); fix obvious errors silently. Translate non-English. If a transcript is junk (music, someone else talking), use the title and description.

**Output:** **second message:** Write `D:\NaturalHypertrophy\bodybuilding_book\raw\<id>.json` for every video, all Writes in parallel in that one message (one Write per video; don't re-read files you wrote). Single-line JSON, compact arrays:

```
{"id":"xoLo7fptNA8","date":"2020-02-16","title":"...","kind":"educational","summary":"2-3 sentences",
 "topics":["frequency_split","injuries"],
 "claims":[["To grow the bench you must press it several times a week; one big weekly session fails most people","P","frequency_split","chest",{"frequency":"2-3x/wk"},62]],
 "exercises":[["Paused bench press","pause on chest; no pins","less shoulder stress than touch-and-go",125]],
 "stats":[["bodyweight","80 kg","2020-02",30]],
 "training_log":[["high-bar squat",160,365,6,null,""]],
 "quotes":[["verbatim, under 15 words",300]],
 "viewer_questions":["short topic of a question he answers"]}
```

- `kind`: educational | vlog | lift_clip | rant | qa_stream | story | physique_update | review | other.
- **claims** `[text, type, topic, body_part, numbers, t]`: every concrete idea, rule, prescription, opinion, data point or telling anecdote. One idea per claim, in your own words, self-contained, specific. Keep all numbers. Never invent anything. Typical counts: educational 10-40, vlog/rant 3-15, long Q&A 40-80.
  - type: `P` principle · `R` prescription · `O` opinion · `A` anecdote · `D` data/study. Append `?` (e.g. `"R?"`) if the caption was garbled and you're inferring.
  - topic (exactly one): mindset · natural_vs_enhanced · genetics_potential · volume · intensity_failure · frequency_split · progression · rest_periods · exercise_selection · technique · fatigue_deload · injuries · strength · aesthetics · muscle_specific · nutrition · bulk_cut · sleep_recovery · supplements · cardio · equipment_home_gym · beginners · science_evidence · fitness_industry · personal_journey · life_philosophy · culture_manga · other
  - body_part: chest|back|lats|traps|shoulders|biceps|triceps|forearms|quads|hamstrings|glutes|calves|abs|neck|full_body, or `""`.
  - numbers: `{}` or only the stated quantities (sets, reps, rir, frequency, rest, kcal, protein, weeks, load, bodyfat…).
  - t: the `[t=...]` second where he says it (0 if it comes from title or description).
- **exercises** `[name, cues, why, t]`: every exercise he demonstrates, recommends, criticises or cues.
- **stats** `[metric, value, as_of YYYY-MM, t]`: his own body or strength numbers.
- **training_log** `[lift, kg, lbs, reps, sets, notes]`: sets he performs or reports (null if unknown).
- **quotes**: 0-2, verbatim, under 15 words, only if characteristic. **viewer_questions**: Q&A content only.
- Omit empty arrays. No pretty-printing.

**Finish:** third message, nothing else: `<batch> done: <notes written> notes[, problems]`.
