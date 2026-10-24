# Builds derived/comments_digest.md: per video, NH's own replies (with the comment he answered)
# and the most-liked viewer questions. Input for the FAQ chapter.
import os, re, csv
BASE = r'D:\NaturalHypertrophy'
BOOK = os.path.join(BASE, 'bodybuilding_book')
rows = list(csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8')))
head = re.compile(r'^((?:> )+)?\*\*@(\S+)\*\*(.*?)· (\d[\d,.]*K?) likes? · (.*)$')

def likes(s):
    s = s.replace(',', '')
    return int(float(s[:-1]) * 1000) if s.endswith('K') else int(float(s))

out, nq, nr = [], 0, 0
for r in rows:
    p = os.path.join(BASE, 'videos', r['folder'], 'comments.md')
    if not os.path.exists(p): continue
    lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
    items, cur = [], None
    for ln in lines:
        m = head.match(ln)
        if m:
            cur = dict(reply=bool(m.group(1)), user=m.group(2), creator='[CREATOR]' in m.group(3),
                       likes=likes(m.group(4)), text=[])
            items.append(cur)
        elif cur is not None and ln.strip() and ln.strip() != '---':
            cur['text'].append(re.sub(r'^(>\s?)+', '', ln).strip())
    parent, qa, qs = None, [], []
    for it in items:
        txt = ' '.join(it['text'])[:600]
        if not it['reply']:
            parent = (it, txt)
            if not it['creator'] and '?' in txt and it['likes'] >= 3:
                qs.append((it['likes'], txt))
        elif it['creator'] and parent:
            qa.append((parent[1][:400], txt))
    if not qa and not qs: continue
    qs = sorted(qs, reverse=True)[:6]
    out.append(f"### {r['id']} | {r['date']} | {r['title']}")
    for q, a in qa:
        out.append(f"- Q: {q}\n  NH: {a}"); nr += 1
    for l, q in qs:
        out.append(f"- ({l} likes) {q}"); nq += 1
    out.append('')
open(os.path.join(BOOK, 'derived', 'comments_digest.md'), 'w', encoding='utf-8').write(
    f'# Comment digest: {nr} NH replies, {nq} top viewer questions\n\n' + '\n'.join(out))
print(nr, 'NH replies', nq, 'questions')
