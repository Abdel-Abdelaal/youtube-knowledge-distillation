# Write step: one chapter of The Bodybuilding Book (principle reference)

The book is a **source of truth** for what the YouTuber **Natural Hypertrophy** ("NH", French natural bodybuilder, ~1,400 videos 2020-2026) teaches: a structured reference that programs, claims and ideas can be checked against. It is **not** a prose book and **not** a program: no example weeks, no programs of your own.

Read `D:\NaturalHypertrophy\bodybuilding_book\book\OUTLINE.md` for your chapter's place, prefixes and scope, then read **all** the input files your prompt names (syntheses in `derived\synthesis\`, plus extras), and nothing else.

## Output: `D:\NaturalHypertrophy\bodybuilding_book\book\chapters\<NN_name>.md`

```
# <N>. <Title>

<2-4 sentence orientation: what this chapter covers and his overall stance.>

## <Section>

<1-3 sentences connecting the principles below, if useful.>

### VOL-01 · <short title, max ~8 words>
- **Statement:** <his position in plain words, one or two sentences>
- **Numbers:** <every number/range he gives, with dates if they changed; "—" if none>
- **Scope:** <who/when it applies to: natural, beginner/intermediate/advanced, goal (muscle/strength/look), exceptions>
- **Confidence:** <high|medium|low> — ~N videos, YYYY→YYYY<, still said in YYYY>
- **Status:** <current|changed|contradicted> — <for changed/contradicted: the old vs new view with dates>
- **Check:** <optional: a yes/no question a program or claim can be tested with, only for key principles>
- **Sources:** {{id@sec}} {{id@sec}} {{id@sec}}
```

- **IDs:** use only the prefixes your prompt assigns, numbered 01, 02, … in the order they appear. One principle = one ID = one distinct rule or position. Merge duplicates across your inputs; split a bullet that holds two separate rules.
- **Order:** sections in a logical order; most important principles first within each section.
- **Field rules:** keep the six fields and their order exactly (Check is optional) so a script can parse them. One line per field. Use the synthesis confidence/years; status `changed` = he moved from one view to another over time, `contradicted` = conflicting statements without a clear evolution.
- **Check:** give a Check line to the ~5-15 most important principles per chapter (the ones a program or claim should be tested against). Phrase so that "yes" = consistent with NH. E.g. "Do most working sets end within 0-3 reps of failure?"
- **Cross-references:** refer to other principles by ID when you know it is in your own chapter; otherwise "see ch. N".
- Tables are allowed for reference material that isn't a principle (e.g. a cue table for the main lifts, a stats timeline), still cited.

## Rules
- **Citations:** every principle has 1-4 `{{id@sec}}` markers copied exactly from the inputs (include the earliest and the latest). Never invent or alter ids or seconds.
- **Only what he says.** No generic fitness knowledge. If a short connecting sentence adds your own interpretation, mark it *[inference]*.
- **People:** claims about real people (steroid use, dishonesty…) are his unverified opinions, written as such ("he claims…").
- Your own words, plain and tight. Quotes rare, under 15 words, in quotation marks.
- Don't cover material the outline gives to another chapter.

## Finish
Reply with one line: `<file>: <n principles> principles (<prefixes>), <n with Check>, <n citations>`.
