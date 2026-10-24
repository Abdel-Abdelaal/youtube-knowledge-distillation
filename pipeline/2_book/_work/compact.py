# Compact map input: _work/compact/<id>.txt for every video in _work/batches.json (run make_batches.py first).
# Same content as the batch files, minus filler words, stutters, link-only description lines and extra whitespace.
# [t=<sec>] paragraph timestamps are kept so citations still work. Originals in videos/ are never touched.
import os, re, csv, json
BASE = r'D:\NaturalHypertrophy'
BOOK = os.path.join(BASE, 'bodybuilding_book')
OUT = os.path.join(BOOK, '_work', 'compact')
FENCE = '`' * 3
TINY = 150
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
rows = {r['id']: r for r in csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8'))}
meta = json.load(open(os.path.join(BOOK, '_work', 'batches.json')))

I = re.I
KEEP_YK = {'do', 'did', 'if', 'to', 'as', 'what', "didn't", "don't", 'you', 'they', 'we', 'i', 'he', 'she', 'ever', 'now'}
FILLERS = [  # (pattern, replacement); conservative: only forms that carry no meaning
    (r'\[(Music|Applause|Laughter|Music Playing)\]\s*', ''),
    (r'\b(?:uh+|um+|uhm+|erm+|er|ah+|hmm+|mhm+)\b[,.]? ?', ''),
    (r"([\w']+)? ?\byou know\b(?! (?:what|how|why|that|if|the|about|it|when|where|who|which|this|a|your|my|me|him|her|them|more|exactly)\b)[,.]?",
     lambda m: m.group(0) if (m.group(1) or '').lower() in KEEP_YK else (m.group(1) or '')),
    (r'\bI mean\b(?! (?:by|it|that|this)\b)[,.]? ?', ''),
    (r'\b(?:basically|literally)\b[,.]? ?', ''),
    (r'\b(?:so yeah|yeah so|okay so|alright so|all right so)\b', 'so'),
    (r'\b(and|but|so|or) like\b', r'\1'),
    (r'\blike,? like\b', 'like'),
    (r'\b(?:yeah|okay|ok|right|so)(?:[,.]? (?:yeah|okay|ok|right|so))+\b', lambda m: m.group(0).split()[0].strip(',.')),
    (r'\b(\w+(?: \w+){0,2})(?: \1\b)+', r'\1'),  # stutters: "the the", "I think I think"
]
FILLERS = [(re.compile(p, I), r) for p, r in FILLERS]

def ts(m):
    s = 0
    for x in m.group(1).split(':'): s = s * 60 + int(x)
    return f'[t={s}]'

def clean(body):
    body = re.sub(r'\[(\d+(?::\d+)+)\]', ts, body)
    for p, r in FILLERS: body = p.sub(r, body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r' ([,.?!])', r'\1', body)
    body = re.sub(r'\n\s*\n+', '\n', body)
    return '\n'.join(l.strip() for l in body.split('\n') if l.strip() and not re.fullmatch(r'\[t=\d+\]', l.strip()))

def render(r):
    p = os.path.join(BASE, 'videos', r['folder'])
    rp = os.path.join(p, 'README.md')
    rd = open(rp, encoding='utf-8').read() if os.path.exists(rp) else ''
    tags = re.search(r'\*\*Tags:\*\* (.*)', rd)
    chap = re.search(r'## Chapters\n\n(.*?)\n\n', rd, re.S)
    desc = re.search(r'## Description\n\n' + FENCE + r'\n(.*?)' + FENCE, rd, re.S)
    d = desc.group(1).strip() if desc else ''
    d = re.sub(r'https?://\S+', '<link>', d)
    d = '\n'.join(l for l in d.split('\n') if l.strip() and not re.fullmatch(r'[^<]{0,60}<link>\s*', l.strip()))
    if len(d) > 2000: d = d[:2000] + ' …'
    out = [f"=== VIDEO {r['id']} | {r['date']} | {r['secs']}s | {r['title']}"]
    if tags: out.append('TAGS: ' + tags.group(1)[:300])
    if chap: out.append('CHAPTERS:\n' + chap.group(1).replace('- ', ''))
    if d: out.append('DESCRIPTION:\n' + d)
    tp = os.path.join(p, 'transcript.txt')
    if int(r['words']) < TINY:
        out.append('TRANSCRIPT: (none - use title+description only)')
    elif os.path.exists(tp):
        t = open(tp, encoding='utf-8', errors='replace').read()
        src = re.search(r'Transcript source: (.*)', t)
        s = src.group(1) if src else '?'
        s = 'auto-captions' if 'auto-generated' in s else ('whisper ' + s.rsplit(':', 1)[-1].strip() if 'Whisper' in s else s)
        out.append(f"TRANSCRIPT ({s}):\n" + clean(t.split('\n', 3)[-1].strip()))
    return '\n'.join(out) + '\n'

before = after = 0
words = {}
for b in meta:
    for i in b['ids']:
        txt = render(rows[i])
        open(os.path.join(OUT, i + '.txt'), 'w', encoding='utf-8').write(txt)
        before += int(rows[i]['words']); after += words.setdefault(i, len(txt.split()))
print(f'{len(words)} compact files; {before} -> {after} words ({100 - 100 * after // max(before, 1)}% smaller)')

# Repack into smaller batches (<= MAXW words): an agent reads its whole batch in one turn and writes all notes
# in the next, so a smaller context per agent is cheaper than fewer, bigger agents.
MAXW = 40000
ids = [i for b in meta for i in b['ids']]
start = int(meta[0]['batch'][1:])
packed, cur, w = [], [], 0
for i in sorted(ids, key=lambda i: -words[i]):  # first-fit decreasing
    for p in packed:
        if p[1] + words[i] <= MAXW: p[0].append(i); p[1] += words[i]; break
    else: packed.append([[i], words[i]])
meta = [dict(batch=f'b{n:03d}', n=len(p[0]), words=p[1], ids=p[0]) for n, p in enumerate(packed, start)]
json.dump(meta, open(os.path.join(BOOK, '_work', 'batches.json'), 'w'), indent=0)
print(len(meta), 'batches; max words', max(m['words'] for m in meta))
