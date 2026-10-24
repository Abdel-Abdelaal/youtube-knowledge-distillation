# Turns community_posts/posts.md (+ ko-fi README) into a pseudo-video batch file batches/posts.txt.
# Each post becomes "=== VIDEO <postId> | <approx date> | 0s | Community post" so the map step can treat it like a video.
import re, os, datetime
BASE = r'D:\NaturalHypertrophy'
OUT = os.path.join(BASE, 'bodybuilding_book', '_work', 'batches', 'posts.txt')
TODAY = datetime.date(2026, 10, 20)
s = open(os.path.join(BASE, 'community_posts', 'posts.md'), encoding='utf-8').read()
parts = re.split(r'^## ', s, flags=re.M)[1:]
out = []

def approx(rel):
    m = re.match(r'(\d+) (year|month|week|day)s? ago', rel)
    if not m: return TODAY.isoformat()
    n, u = int(m.group(1)), m.group(2)
    days = {'year': 365, 'month': 30, 'week': 7, 'day': 1}[u] * n
    return (TODAY - datetime.timedelta(days=days)).isoformat()

for p in parts:
    head, _, body = p.partition('\n')
    rel = head.split(' \u00b7 ')[0].strip()
    m = re.search(r'youtube\.com/post/([\w-]+)', body)
    if not m: continue
    body = re.sub(r'!\[\]\([^)]*\)', '', body)
    body = re.sub(r'<https?://\S+>', '', body).replace('---', '').strip()
    out.append(f'=== VIDEO {m.group(1)} | {approx(rel)} | 0s | Community post ({rel}, approx date)\nTRANSCRIPT (source: written post):\n[t=0] {body}\n')
kofi = open(os.path.join(BASE, 'linked_media', 'ko-fi', 'README.md'), encoding='utf-8').read()
out.append(f'=== VIDEO kofi | 2026-10-20 | 0s | Ko-fi page (captured 2026-10-20)\nTRANSCRIPT (source: web page):\n[t=0] {kofi}\n')
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print(len(out), 'items', sum(len(x.split()) for x in out), 'words')
