# Script-based reduce (no AI): derived/claims/<topic>.txt -> derived/topics/<topic>.md
# Per topic: near-duplicate claims are merged (TF-IDF cosine, leader clustering), merged claims are grouped
# into themes (body part first where it matters, then looser similarity), ranked by how many distinct videos
# and years support them, and likely contradictions are flagged (similar claims from different years with
# different numbers or opposite stance). Every merged claim keeps its {{id@t}} citations and dates.
# Usage: python _work/reduce.py [topic ...]   (default: all topics)
import os, re, sys, json, math, glob, collections
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
IN = os.path.join(BOOK, 'derived', 'claims')
OUT = os.path.join(BOOK, 'derived', 'topics')
os.makedirs(OUT, exist_ok=True)
DUP, THEME, CONTRA = 0.42, 0.18, 0.30          # cosine thresholds (lexical similarity is weak on paraphrase,
# so duplicates are merged conservatively; themes put related claims next to each other for the synthesis step)
BODY_TOPICS = {'muscle_specific', 'exercise_selection', 'technique', 'injuries'}
LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}) \{\{([\w-]+)@(\d+)\}\} (\S+)(?: \[([\w_]+)\])? (.*?)(  (\{.*\}))?$')
STOP = set('''a an the and or but if of to in on at for with by from as is are was were be been being it its this that these
those he his him she her they them their you your we our i me my not no yes do does did done can could should would will
just than then so very more most less much many some any all also only even about into over under up down out off too
there here what which who whom when where why how because while though although per vs like get got gets one two
nh natural hypertrophy says said say thinks believes argues claims feels according'''.split())
NEG = re.compile(r"\b(not|never|no longer|don'?t|doesn'?t|isn'?t|useless|pointless|overrated|myth|waste|avoid|unnecessary|stopped|no need|bad idea|wrong)\b", re.I)

def stem(w):
    for suf in ('ing', 'ed', 'es', 's'):
        if len(w) > len(suf) + 3 and w.endswith(suf): return w[:-len(suf)]
    return w

def toks(s):
    return [stem(w) for w in re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)?", s.lower()) if w not in STOP and len(w) > 1]

def parse(topic):
    rows = []
    for ln in open(os.path.join(IN, topic + '.txt'), encoding='utf-8'):
        m = LINE.match(ln.rstrip('\n'))
        if not m: continue
        date, vid, t, typ, bp, text, _, nums = m.groups()
        low = text.endswith('(low-confidence)')
        text = text.replace(' (low-confidence)', '').strip()
        try: nums = json.loads(nums) if nums else {}
        except Exception: nums = {}
        rows.append(dict(date=date, vid=vid, t=int(t), type=typ, bp=bp or '', text=text, low=low, nums=nums))
    return rows

def vectors(docs):
    df = collections.Counter()
    tf = [collections.Counter(toks(d)) for d in docs]
    for c in tf: df.update(c.keys())
    n = len(docs)
    out = []
    for c in tf:
        v = {w: (1 + math.log(k)) * math.log((n + 1) / (df[w] + 0.5)) for w, k in c.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        out.append({w: x / norm for w, x in v.items()})
    return out

def dot(a, b):
    if len(a) > len(b): a, b = b, a
    return sum(x * b.get(w, 0) for w, x in a.items())

def centroid(vs):
    c = collections.Counter()
    for v in vs: c.update(v)
    norm = math.sqrt(sum(x * x for x in c.values())) or 1
    return {w: x / norm for w, x in c.items()}

def leader(items, vecs, thr, key=None):
    """Greedy leader clustering; items visited in the given order, joined to the most similar leader >= thr."""
    leaders, groups, inv = [], [], collections.defaultdict(set)
    for i in items:
        v = vecs[i]
        cand = set()
        for w in v: cand |= inv[w]
        best, bs = None, thr
        for g in cand:
            if key and key(leaders[g]) != key(i): continue
            s = dot(v, vecs[leaders[g]])
            if s >= bs: best, bs = g, s
        if best is None:
            leaders.append(i); groups.append([i])
            for w in v: inv[w].add(len(leaders) - 1)
        else:
            groups[best].append(i)
    return groups

def fmt_nums(members):
    """Distinct number sets with the month they were said, so changes over time stay visible."""
    seen, out = set(), []
    for r in sorted(members, key=lambda r: r['date']):
        if not r['nums']: continue
        s = json.dumps(r['nums'], ensure_ascii=False, sort_keys=True)
        if s in seen: continue
        seen.add(s); out.append(f"{r['date'][:7]} {s}")
    return out

def pick_cites(members, k=5):
    by_vid = {}
    for r in sorted(members, key=lambda r: r['date']):
        by_vid.setdefault(r['vid'], r)
    vs = list(by_vid.values())
    if len(vs) <= k: chosen = vs
    else:
        step = (len(vs) - 1) / (k - 1)
        chosen = [vs[round(i * step)] for i in range(k)]   # earliest, latest and evenly spread between
    return ' '.join(f"{{{{{r['vid']}@{r['t']}}}}}" for r in chosen)

def reduce_topic(topic):
    rows = parse(topic)
    if not rows: return None
    vecs = vectors([r['text'] for r in rows])
    # longest (most specific) claim first so it becomes the representative of its cluster
    order = sorted(range(len(rows)), key=lambda i: (rows[i]['low'], -len(rows[i]['text'])))
    bpkey = (lambda i: rows[i]['bp']) if topic in BODY_TOPICS else None
    clusters = []
    for g in leader(order, vecs, DUP, bpkey):
        mem = [rows[i] for i in g]
        vids = {r['vid'] for r in mem}
        years = sorted({r['date'][:4] for r in mem})
        dates = sorted(r['date'] for r in mem)
        clusters.append(dict(rep=rows[g[0]], mem=mem, vec=centroid([vecs[i] for i in g]), nv=len(vids),
                             years=years, first=dates[0], last=dates[-1],
                             types=''.join(sorted({r['type'][0].upper() for r in mem})),
                             low=all(r['low'] for r in mem), bp=rows[g[0]]['bp']))
    # rank: distinct videos, then distinct years, then recency
    clusters.sort(key=lambda c: (-c['nv'], -len(c['years']), c['low'], c['last']), reverse=False)
    # theme vectors drop words that appear in >6% of the topic's claims ("volume" in the volume topic, etc.)
    df = collections.Counter(w for c in clusters for w in c['vec'])
    common = {w for w, k in df.items() if k > 0.06 * len(clusters)}
    def strip(v):
        v = {w: x for w, x in v.items() if w not in common}
        n = math.sqrt(sum(x * x for x in v.values())) or 1
        return {w: x / n for w, x in v.items()}
    cvecs = [strip(c['vec']) for c in clusters]
    ckey = (lambda i: clusters[i]['bp']) if topic in BODY_TOPICS else None
    themes = leader(list(range(len(clusters))), cvecs, THEME, ckey)
    for _ in range(2):   # k-means style refinement: move each claim to its most similar theme centroid
        cents = [centroid([cvecs[i] for i in t]) for t in themes]
        new = [[] for _ in themes]
        for ti, t in enumerate(themes):
            for i in t:
                best, bs = ti, dot(cvecs[i], cents[ti])
                for tj, c in enumerate(cents):
                    if tj != ti and (not ckey or ckey(themes[tj][0]) == ckey(i)) and len(themes[tj]) > 1:
                        s = dot(cvecs[i], c)
                        if s > bs + 0.02: best, bs = tj, s
                new[best].append(i)
        themes = [t for t in new if t]
    # small themes -> one "other" bucket per body part
    big, small = [t for t in themes if len(t) >= 3], [i for t in themes if len(t) < 3 for i in t]
    if small:
        if topic in BODY_TOPICS:
            byb = collections.defaultdict(list)
            for i in small: byb[clusters[i]['bp']].append(i)
            big += list(byb.values())
        else:
            # attach each leftover to the closest real theme; only truly unrelated ones stay in a misc bucket
            cents = [centroid([cvecs[i] for i in t]) for t in big]
            misc = []
            for i in small:
                sims = [dot(cvecs[i], c) for c in cents]
                j = max(range(len(sims)), key=sims.__getitem__) if sims else None
                if j is not None and sims[j] >= 0.08: big[j].append(i)
                else: misc.append(i)
            if misc: big.append(misc)

    def label(t):
        c = collections.Counter()
        for i in t: c.update(cvecs[i])
        words = [w for w, _ in c.most_common(4)]
        bp = clusters[t[0]]['bp'] if topic in BODY_TOPICS else ''
        return (f"[{bp or 'general'}] " if topic in BODY_TOPICS else '') + ' / '.join(words)
    big.sort(key=lambda t: ((clusters[t[0]]['bp'] if topic in BODY_TOPICS else ''), -sum(clusters[i]['nv'] for i in t)))

    # contradictions: similar clusters, different years, differing numbers on a shared key or opposite stance
    contra = []
    for t in big:
        for a in range(len(t)):
            for b in range(a + 1, len(t)):
                A, B = clusters[t[a]], clusters[t[b]]
                if A['first'][:4] == B['first'][:4] and A['last'][:4] == B['last'][:4]: continue
                s = dot(A['vec'], B['vec'])
                if s < CONTRA: continue
                why = []
                na = {k: str(v) for r in A['mem'] for k, v in r['nums'].items()}
                nb = {k: str(v) for r in B['mem'] for k, v in r['nums'].items()}
                diff = [k for k in set(na) & set(nb) if na[k] != nb[k]]
                if diff: why.append('numbers differ: ' + ', '.join(f"{k} {na[k]} vs {nb[k]}" for k in diff[:3]))
                if bool(NEG.search(A['rep']['text'])) != bool(NEG.search(B['rep']['text'])): why.append('stance flips')
                if why: contra.append((s, A, B, '; '.join(why)))
    contra.sort(key=lambda x: -x[0])

    nv_total = len({r['vid'] for r in rows})
    lines = [f"# {topic}",
             f"_{len(rows)} claims from {nv_total} videos, {min(r['date'] for r in rows)} → {max(r['date'] for r in rows)}; "
             f"merged into {len(clusters)} distinct claims. Script output (reduce.py), not edited by hand._",
             "",
             "Line format: `- [Nv Y1-Y2 types] claim {numbers by month} cites` — Nv = distinct videos that said it; "
             "types P principle, R prescription, O opinion, A anecdote, D data; `?` = low-confidence caption; "
             "`also:` = differently-worded variants merged into it.", ""]
    for t in big:
        lines.append(f"## {label(t)} ({len(t)})")
        for i in sorted(t, key=lambda i: (-clusters[i]['nv'], -len(clusters[i]['years']), clusters[i]['first'])):
            c = clusters[i]
            yr = c['years'][0] if len(c['years']) == 1 else f"{c['years'][0]}-{c['years'][-1]}"
            nums = fmt_nums(c['mem'])
            nums = (' {' + ' | '.join(nums) + '}') if nums else ''
            # keep up to 2 alternative phrasings from other videos when they carry extra words (nuance)
            alts, seen = [], {c['rep']['vid']}
            for r in sorted(c['mem'][1:], key=lambda r: -len(r['text'])):
                if r['vid'] in seen or len(alts) >= 2: continue
                if len(set(toks(r['text'])) - set(toks(c['rep']['text']))) >= 4:
                    alts.append(f"{r['date'][:7]}: {r['text']}"); seen.add(r['vid'])
            alt = (' also: ' + ' // '.join(alts)) if alts else ''
            lines.append(f"- [{c['nv']}v {yr} {c['types']}{'?' if c['low'] else ''}] {c['rep']['text']}{nums}{alt} {pick_cites(c['mem'])}")
        lines.append('')
    lines.append(f"## Possible contradictions / changes over time ({len(contra[:25])} flagged by script; verify)")
    if not contra: lines.append('None flagged.')
    for s, A, B, why in contra[:25]:
        a, b = sorted([A, B], key=lambda c: c['first'])
        lines.append(f"- ({why}) {a['first'][:7]}: {a['rep']['text']} {pick_cites(a['mem'], 2)} ⟷ "
                     f"{b['last'][:7]}: {b['rep']['text']} {pick_cites(b['mem'], 2)}")
    open(os.path.join(OUT, topic + '.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    return len(rows), len(clusters), len(big), len(contra)

EX = re.compile(r'^(\d{4}-\d{2}-\d{2}) \{\{([\w-]+)@(\d+)\}\} (.*?) \| cues: (.*?) \| why: (.*)$')

def reduce_exercises():
    """_exercises.txt -> topics/_exercises.md: one entry per exercise name with all distinct cues and reasons."""
    groups = collections.defaultdict(list)
    for ln in open(os.path.join(IN, '_exercises.txt'), encoding='utf-8'):
        m = EX.match(ln.rstrip('\n'))
        if not m: continue
        date, vid, t, name, cues, why = m.groups()
        key = ' '.join(sorted(set(stem(w) for w in re.findall(r'[a-z0-9]+', name.lower().replace('-', ' ')))))
        groups[key].append(dict(date=date, vid=vid, t=int(t), name=name, cues=cues, why=why))

    def dedup(items):
        out, seen = [], []
        for txt, r in items:
            v = set(toks(txt))
            if not v or any(len(v & u) >= 0.7 * min(len(v), len(u)) for u in seen): continue
            seen.append(v); out.append(f"{txt} {{{{{r['vid']}@{r['t']}}}}}")
        return out
    ent = sorted(groups.values(), key=lambda g: -len({r['vid'] for r in g}))
    lines = ['# _exercises', f'_{sum(len(g) for g in ent)} exercise mentions merged into {len(ent)} exercises, '
             'most-discussed first. Cues and reasons are de-duplicated; each keeps one citation. Script output (reduce.py)._', '']
    for g in ent:
        g.sort(key=lambda r: r['date'])
        names = collections.Counter(r['name'] for r in g).most_common(3)
        nv = len({r['vid'] for r in g})
        lines.append(f"## {names[0][0]} ({nv}v, {g[0]['date'][:7]} → {g[-1]['date'][:7]})"
                     + (f" — also called: {', '.join(n for n, _ in names[1:])}" if len(names) > 1 else ''))
        cues = dedup([(c.strip(), r) for r in g for c in r['cues'].split(';') if c.strip()])
        whys = dedup([(r['why'].strip(), r) for r in g if r['why'].strip()])
        if cues: lines.append('- cues: ' + ' · '.join(cues))
        if whys: lines.append('- why/verdict: ' + ' · '.join(whys))
        if not cues and not whys: lines.append('- mentioned ' + pick_cites(g, 3))
        lines.append('')
    open(os.path.join(OUT, '_exercises.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    return len(ent)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or '_exercises' in args:
        print('_exercises: merged into', reduce_exercises(), 'exercises')
    topics = [a for a in args if a != '_exercises'] if args else sorted(
        os.path.basename(p)[:-4] for p in glob.glob(os.path.join(IN, '*.txt')) if not os.path.basename(p).startswith('_'))
    for tp in topics:
        r = reduce_topic(tp)
        if r:
            words = len(open(os.path.join(OUT, tp + '.md'), encoding='utf-8').read().split())
            print(f'{tp:22s} claims {r[0]:5d} -> merged {r[1]:5d} | themes {r[2]:3d} | contradictions {r[3]:3d} | {words} words')
