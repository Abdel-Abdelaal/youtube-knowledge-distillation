# Parses lift-clip titles ("365lbs (160 kg) highbar squat for 6") into derived/lift_log.csv
# and writes a best-set-per-lift progression table to derived/strength_progression.md
import csv, re, os, collections
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
rows = list(csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8')))
pat = re.compile(r'^(?P<lbs>[\d.]+)\s*lbs?\.?\s*(?:\(\s*(?P<kg>[\d.]+)\s*kg\s*\))?\s*(?P<lift>.+?)'
                 r'(?:\s+(?:for|x)\s*(?P<reps>\d+)(?:\s*reps?)?(?P<rest>\s.*)?)?$', re.I)
pat_kg_first = re.compile(r'^(?P<kg>[\d.]+)\s*kg\s*\(\s*(?P<lbs>[\d.]+)\s*lbs?\s*\)\s*(?P<lift>.+?)'
                          r'(?:\s+(?:for|x)\s*(?P<reps>\d+)(?:\s*reps?)?(?P<rest>\s.*)?)?$', re.I)
log, miss = [], []
for r in rows:
    t = r['title'].replace('⧸', '/').strip()
    m = pat.match(t) or pat_kg_first.match(t)
    if not m:
        if re.match(r'^[\d.]+\s*(lbs?|kg)', t, re.I): miss.append(t)
        continue
    lift = re.sub(r'\s+', ' ', m.group('lift')).strip(' ,-')
    log.append(dict(date=r['date'], id=r['id'], lift=lift, kg=float(m.group('kg')) if m.group('kg') else round(float(m.group('lbs'))*0.4536,1), lbs=float(m.group('lbs')),
                    reps=int(m.group('reps')) if m.group('reps') else '', extra=(m.group('rest') or '').strip(), title=t))
with open(os.path.join(BOOK, 'derived', 'lift_log.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)

def norm(l):
    l = l.lower()
    l = re.sub(r'\b(paused|pause)\b', 'paused', l)
    return l

def e1rm(kg, reps):
    return kg * (1 + reps / 30) if reps else kg

by = collections.defaultdict(list)
for x in log: by[norm(x['lift'])].append(x)
lines = ['# Strength log from lift-clip titles', '',
         f'{len(log)} titled sets parsed from {len(rows)} videos (unparsed numeric titles: {len(miss)}). '
         'e1RM = Epley estimate (kg x (1 + reps/30)), only to compare sets across rep counts.', '']
for lift, xs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    xs.sort(key=lambda x: x['date'])
    lines.append(f'## {lift} ({len(xs)} sets)')
    lines.append('| date | kg | lbs | reps | e1RM kg | video |')
    lines.append('|---|---|---|---|---|---|')
    for x in xs:
        lines.append(f"| {x['date']} | {x['kg']:g} | {x['lbs']:g} | {x['reps']} | {e1rm(x['kg'], x['reps'] or 0):.0f} | https://youtu.be/{x['id']} |")
    lines.append('')
lines.append('## Unparsed numeric titles'); lines += [f'- {t}' for t in miss]
open(os.path.join(BOOK, 'derived', 'strength_progression.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print(len(log), 'parsed;', len(by), 'distinct lifts;', len(miss), 'missed')
for t in miss[:15]: print('  MISS', t)
for lift, xs in sorted(by.items(), key=lambda kv: -len(kv[1]))[:25]: print(f'  {len(xs):3d} {lift}')
