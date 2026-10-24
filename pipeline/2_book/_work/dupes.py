# Edit-pass helper: lists principle pairs in DIFFERENT chapters whose statements are near-identical
# (TF-IDF cosine >= threshold), so cross-chapter duplication can be reviewed. Usage: python _work/dupes.py [0.55]
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reduce import vectors, dot, leader   # same similarity code as the reduce step
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
thr = float(sys.argv[1]) if len(sys.argv) > 1 else 0.55
ps = json.load(open(os.path.join(BOOK, 'derived', 'principles.json'), encoding='utf-8'))
vs = vectors([p['title'] + ' ' + p.get('statement', '') for p in ps])
pairs = []
for i in range(len(ps)):
    for j in range(i + 1, len(ps)):
        if ps[i]['chapter'] != ps[j]['chapter']:
            s = dot(vs[i], vs[j])
            if s >= thr: pairs.append((s, ps[i], ps[j]))
pairs.sort(key=lambda x: -x[0])
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
print(f'{len(pairs)} cross-chapter pairs with similarity >= {thr}')
for s, a, b in pairs:
    print(f"{s:.2f} {a['id']} {a['title']}  <->  {b['id']} {b['title']}")
