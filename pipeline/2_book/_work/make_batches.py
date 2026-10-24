# Packs videos into batch text files for the map agents: _work/batches/bNNN.txt + batches.json
# Skips videos that already have a note in raw/ (resumable). Run manifest.py and stub_notes.py first.
import os, re, csv, json, sys
BASE = r'D:\NaturalHypertrophy'
BOOK = os.path.join(BASE, 'bodybuilding_book')
OUT = os.path.join(BOOK, '_work', 'batches')
MAXW, MAXV, TINY = 60000, 200, 150  # tiny (<150 words) videos get stub notes instead (stub_notes.py)
FENCE = '`' * 3
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
rows = list(csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8')))
done = {f[:-5] for f in os.listdir(os.path.join(BOOK, 'raw')) if f.endswith('.json')}
rows = [r for r in rows if r['id'] not in done]

def ts(m):
    s = 0
    for x in m.group(1).split(':'): s = s * 60 + int(x)
    return f'[t={s}]'

def render(r):
    p = os.path.join(BASE, 'videos', r['folder'])
    rp = os.path.join(p, 'README.md')
    rd = open(rp, encoding='utf-8').read() if os.path.exists(rp) else ''
    tags = re.search(r'\*\*Tags:\*\* (.*)', rd)
    chap = re.search(r'## Chapters\n\n(.*?)\n\n', rd, re.S)
    desc = re.search(r'## Description\n\n' + FENCE + r'\n(.*?)' + FENCE, rd, re.S)
    d = desc.group(1).strip() if desc else ''
    d = re.sub(r'https?://\S+', '<link>', d)
    if len(d) > 2500: d = d[:2500] + ' …'
    out = [f"=== VIDEO {r['id']} | {r['date']} | {r['secs']}s | {r['title']}"]
    if tags: out.append('TAGS: ' + tags.group(1)[:400])
    if chap: out.append('CHAPTERS:\n' + chap.group(1))
    if d: out.append('DESCRIPTION:\n' + d)
    tp = os.path.join(p, 'transcript.txt')
    if int(r['words']) < TINY:
        out.append('TRANSCRIPT: (none / no meaningful speech - use title+description only)')
    elif os.path.exists(tp):
        t = open(tp, encoding='utf-8', errors='replace').read()
        src = re.search(r'Transcript source: (.*)', t)
        body = t.split('\n', 3)[-1].strip()
        body = re.sub(r'\[(\d+(?::\d+)+)\]', ts, body)
        body = re.sub(r'\[(Music|Applause|Laughter)\]\s*', '', body)
        body = re.sub(r'\b(?:uh+|um+)\b,? ?', '', body, flags=re.I)  # fillers cost tokens, carry nothing
        body = re.sub(r'\b(\w+)(?: \1\b)+', r'\1', body)  # caption stutter: "the the the"
        body = re.sub(r'\n{2,}', '\n', body)
        out.append(f"TRANSCRIPT (source: {src.group(1) if src else '?'}):\n" + body)
    return '\n'.join(out) + '\n\n'

big = [r for r in rows if int(r['words']) >= TINY]
tiny = [r for r in rows if int(r['words']) < TINY]
batches, cur, w = [], [], 0
for r in big:  # chronological order keeps related videos together
    rw = int(r['words'])
    if cur and (w + rw > MAXW or len(cur) >= MAXV):
        batches.append(cur); cur, w = [], 0
    cur.append(r); w += rw
if cur: batches.append(cur)
meta = []
start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for i, b in enumerate(batches, start):
    name = f'b{i:03d}'
    with open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8') as f:
        for r in b: f.write(render(r))
    meta.append(dict(batch=name, n=len(b), words=sum(int(r['words']) for r in b), ids=[r['id'] for r in b]))
json.dump(meta, open(os.path.join(BOOK, '_work', 'batches.json'), 'w'), indent=0)
print(len(rows), 'videos ->', len(batches), 'batches; max words', max(m['words'] for m in meta))
