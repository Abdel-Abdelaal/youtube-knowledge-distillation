# The Bodybuilding Book: outline

A **source of truth** for what Natural Hypertrophy teaches: chapters are organized lists of principles, each with a stable ID (e.g. `VOL-03`) and fixed fields (statement, numbers, scope, confidence, status, check, sources). No programs or example weeks.

Chapters are written from `derived/synthesis/<topic>.md` (+ extra inputs) into `book/chapters/NN_name.md`, keeping `{{id@sec}}` markers until assembly. Scripts then build `principles.json`, the `principles` table in `nh.db`, `book/CHECKLIST.md` and the combined book.

| # | file | chapter | ID prefixes | inputs (`derived/synthesis/`) | extra inputs |
|---|---|---|---|---|---|
| 01 | `01_journey.md` | His journey & stats | JRN | personal_journey | `derived/claims/_stats.txt`, `derived/strength_progression.md` |
| 02 | `02_mindset.md` | Mindset, natural vs enhanced, genetics | MND, NAT, GEN | mindset, natural_vs_enhanced, genetics_potential | |
| 03 | `03_volume_intensity_frequency.md` | Volume, intensity & failure, frequency & splits, rest between sets | VOL, INT, FRQ, RST | volume, intensity_failure, frequency_split, rest_periods | |
| 04 | `04_progression_fatigue.md` | Progression, fatigue & deloads, sleep & recovery | PRG, FAT, SLP | progression, fatigue_deload, sleep_recovery | |
| 05 | `05_exercises_technique.md` | Exercise selection & technique (+ cue table for main lifts) | EXS, TEC | exercise_selection, technique | `derived/topics/_exercises.md` (cue compendium, skim top ~60 exercises) |
| 06 | `06_body_parts.md` | Body-part playbook | CHE, BAK, SHO, ARM, LEG, CLF, ABS, NCK, FOR | muscle_specific | |
| 07 | `07_strength.md` | Strength & the big lifts | STR | strength | `derived/strength_progression.md` |
| 08 | `08_aesthetics.md` | Aesthetics & the gym look | AES | aesthetics | |
| 09 | `09_injuries.md` | Injuries | INJ | injuries | |
| 10 | `10_nutrition.md` | Nutrition & supplements | NUT, SUP | nutrition, supplements | |
| 11 | `11_bulk_cut.md` | Bulking, cutting & cardio | BLK, CAR | bulk_cut, cardio | |
| 12 | `12_beginners_equipment.md` | Beginners, training levels & equipment | BEG, EQP | beginners, equipment_home_gym | |
| 13 | `13_industry_science.md` | The fitness industry & reading science | IND, SCI | fitness_industry, science_evidence | |
| 14 | `14_philosophy_culture.md` | Life philosophy, culture & manga | PHI, CUL | life_philosophy, culture_manga, other | |
| A1 | `A1_contradictions.md` | Contradictions & how his views changed | — | script: "How his view changed" + "Contradictions" of every synthesis | |
| A2 | `A2_glossary.md` | Glossary of his terms | — | written last, from the chapters | |
| A3 | `A3_strength_log.md` | Strength log | — | script: `derived/strength_progression.md` | |
| A4 | `A4_faq.md` | FAQ: common viewer questions answered from the principles | — | `derived/principle_index.txt`, `derived/claims/_questions.txt` (`_work/APPENDIX_INSTRUCTIONS.md`) | |

Built by script after the chapters: `book/CHECKLIST.md` (all `Check:` lines, grouped by chapter), `derived/principles.json`, `nh.db` table `principles`, `book/THE_BODYBUILDING_BOOK.md` + `.html` (principle IDs as anchors).
