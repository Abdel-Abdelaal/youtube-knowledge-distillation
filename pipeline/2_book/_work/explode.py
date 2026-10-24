# Flattens raw/*.json into per-topic claim files for the reduce step:
#   derived/claims/<topic>.txt   one claim per line: YYYY-MM-DD {{id@t}} type [body_part] claim  {numbers}
#   derived/claims/_exercises.txt, _stats.txt, _training_log.txt, _quotes.txt, _questions.txt, _summaries.txt
#   derived/cite_index.json      id -> {title, date} for citation expansion
import os, json, glob, collections, csv
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
OUT = os.path.join(BOOK, 'derived', 'claims')
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, '*.txt')): os.remove(f)
by = collections.defaultdict(list)
extra = collections.defaultdict(list)
bad = []
notes = []
for p in sorted(glob.glob(os.path.join(BOOK, 'raw', '*.json'))):
    try: notes.append(json.load(open(p, encoding='utf-8')))
    except Exception as e: bad.append((os.path.basename(p), str(e)[:80]))
notes.sort(key=lambda n: (n.get('date', ''), n.get('id', '')))
cites = {r['id']: dict(title=r['title'].replace('⧸', '/').replace('？', '?'), date=r['date'])
         for r in csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8'))}
json.dump(cites, open(os.path.join(BOOK, 'derived', 'cite_index.json'), 'w', encoding='utf-8'), ensure_ascii=False)

TYPES = {'P': 'principle', 'R': 'prescription', 'O': 'opinion', 'A': 'anecdote', 'D': 'data'}

def get(o, k, i):
    """Notes use objects (first 280) or compact arrays (MAP_INSTRUCTIONS v2); read field k / position i."""
    if isinstance(o, dict): return o.get(k)
    if isinstance(o, (list, tuple)) and len(o) > i: return o[i]
    return None

def tag(n, t):
    try: t = int(float(t or 0))
    except Exception: t = 0
    return f"{n.get('date','')} {{{{{n['id']}@{t}}}}}"

for n in notes:
    extra['_summaries'].append(f"{tag(n, 0)} [{n.get('kind','')}] {n.get('title','')}: {n.get('summary','')}")
    for c in n.get('claims') or []:
        text = get(c, 'claim', 0)
        if not text: continue
        typ = get(c, 'type', 1) or '?'
        low = ' (low-confidence)' if get(c, 'confidence', 99) == 'low' or typ.endswith('?') else ''
        typ = TYPES.get(typ.rstrip('?'), typ.rstrip('?'))
        topic = (get(c, 'topic', 2) or 'other').strip()
        bp = get(c, 'body_part', 3)
        bp = f" [{bp}]" if bp else ''
        nums = get(c, 'numbers', 4) or {}
        nums = ('  ' + json.dumps(nums, ensure_ascii=False)) if nums else ''
        by[topic].append(f"{tag(n, get(c, 't', 5))} {typ}{bp} {text}{low}{nums}")
    for x in n.get('exercises') or []:
        name, cues = get(x, 'name', 0), get(x, 'cues', 1)
        if name:
            cues = '; '.join(cues) if isinstance(cues, list) else (cues or '')
            extra['_exercises'].append(f"{tag(n, get(x, 't', 3))} {name} | cues: {cues} | why: {get(x, 'why', 2) or ''}")
    for s in n.get('stats') or []:
        extra['_stats'].append(f"{tag(n, get(s, 't', 3))} {get(s, 'metric', 0)}: {get(s, 'value', 1)} (as of {get(s, 'as_of', 2)})")
    for l in n.get('training_log') or []:
        extra['_training_log'].append(f"{tag(n, 0)} {get(l, 'lift', 0)} {get(l, 'load_kg', 1)}kg/{get(l, 'load_lbs', 2)}lbs x{get(l, 'reps', 3)} sets={get(l, 'sets', 4)} {get(l, 'notes', 5) or ''}")
    for q in n.get('quotes') or []:
        if get(q, 'text', 0):
            extra['_quotes'].append(f"{tag(n, get(q, 't', 1))} \"{get(q, 'text', 0)}\"")
    for q in n.get('viewer_questions') or []:
        extra['_questions'].append(f"{tag(n, 0)} {q}")

for k, v in list(by.items()) + list(extra.items()):
    open(os.path.join(OUT, f'{k}.txt'), 'w', encoding='utf-8').write('\n'.join(v) + '\n')
print(len(notes), 'notes;', sum(len(v) for v in by.values()), 'claims; bad:', bad[:10])
for k, v in sorted(list(by.items()) + list(extra.items()), key=lambda kv: -len(kv[1])):
    words = sum(len(x.split()) for x in v)
    print(f'  {k:22s} {len(v):6d} lines {words:8d} words')
