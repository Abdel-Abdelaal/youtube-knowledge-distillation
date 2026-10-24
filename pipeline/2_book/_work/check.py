# Validation, run before every commit: python _work/check.py [--strict]
# Reports videos without a note, malformed or incomplete notes, claims without a usable citation,
# and chapter/topic citations that point at unknown video ids. Exit code 1 if --strict and problems.
import os, re, csv, json, glob, sys
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
vids = {r['id']: r for r in csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8'))}
notes, malformed, incomplete, uncited = {}, [], [], 0
for p in glob.glob(os.path.join(BOOK, 'raw', '*.json')):
    i = os.path.basename(p)[:-5]
    try: n = json.load(open(p, encoding='utf-8'))
    except Exception as e: malformed.append(f'{i}: {str(e)[:60]}'); continue
    notes[i] = n
    if n.get('id') != i or not n.get('date'): incomplete.append(i)
    for c in n.get('claims') or []:
        t = c.get('t') if isinstance(c, dict) else (c[5] if isinstance(c, list) and len(c) > 5 else None)
        if t is None or str(t).strip() == '': uncited += 1
missing = sorted(v for v in vids if v not in notes)
known = set(vids) | set(notes)
bad_cites, bad_ts = [], []
# every timestamp a note mentions (claims, exercises, stats, quotes), so book markers can be checked against them
stamps = {}
for i, n in notes.items():
    ts = {0}
    for key, pos in (('claims', 5), ('exercises', 3), ('stats', 3), ('quotes', 1)):
        for x in n.get(key) or []:
            t = x.get('t') if isinstance(x, dict) else (x[pos] if isinstance(x, list) and len(x) > pos else None)
            try: ts.add(int(float(t)))
            except Exception: pass
    stamps[i] = ts
cite = re.compile(r'\{\{([\w-]+)@(\d+)\}\}|youtu\.be/([\w-]{11})')
for f in (glob.glob(os.path.join(BOOK, 'derived', 'topics', '*.md')) + glob.glob(os.path.join(BOOK, 'derived', 'synthesis', '*.md'))
          + glob.glob(os.path.join(BOOK, 'book', 'chapters', '*.md'))):
    for m in cite.finditer(open(f, encoding='utf-8').read()):
        v = m.group(1) or m.group(3)
        if v not in known: bad_cites.append(f'{os.path.relpath(f, BOOK)} -> {v}')
        elif m.group(1) and v in stamps and int(m.group(2)) not in stamps[v]:
            bad_ts.append(f'{os.path.relpath(f, BOOK)} -> {v}@{m.group(2)}')
problems = len(malformed) + len(incomplete) + uncited + len(bad_cites) + len(bad_ts)
print(f'videos {len(vids)} | notes {len(notes)} | missing notes {len(missing)} | malformed {len(malformed)} | '
      f'incomplete {len(incomplete)} | claims without timestamp {uncited} | bad citations {len(bad_cites)} | '
      f'citations with a second no note mentions {len(bad_ts)}')
for x in malformed + [f'incomplete: {i}' for i in incomplete] + bad_cites[:30] + [f'unmatched second: {x}' for x in bad_ts[:30]]: print('  ', x)
if '--missing' in sys.argv: print('missing:', ' '.join(missing))
sys.exit(1 if '--strict' in sys.argv and (problems or missing) else 0)
