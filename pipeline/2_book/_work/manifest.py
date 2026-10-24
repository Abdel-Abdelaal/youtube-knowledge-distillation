# Builds _work/manifest.csv from the video folders (index.csv may lag the folders).
import os, re, csv, sys
root = r'D:\NaturalHypertrophy\videos'
out = r'D:\NaturalHypertrophy\bodybuilding_book\derived\manifest.csv'
rows = []
for d in sorted(os.listdir(root)):
    m = re.match(r'(\d{4}-\d{2}-\d{2}) - (.*) \[([\w-]{11})\]$', d)
    if not m: continue
    date, title, vid = m.groups()
    p = os.path.join(root, d)
    dur = ''; src = ''; words = 0; nospeech = False
    try:
        rd = open(os.path.join(p, 'README.md'), encoding='utf-8').read()
        mm = re.search(r'\*\*Duration:\*\* ([\d:]+)', rd); dur = mm.group(1) if mm else ''
    except Exception: rd = ''
    tp = os.path.join(p, 'transcript.txt')
    if os.path.exists(tp):
        t = open(tp, encoding='utf-8', errors='replace').read()
        mm = re.search(r'Transcript source: (.*)', t); src = mm.group(1).strip() if mm else ''
        body = re.sub(r'\[\d+:\d+(:\d+)?\]', ' ', t.split('\n', 3)[-1])
        body = re.sub(r'\[(Music|Applause|Laughter)\]', ' ', body)
        words = len(body.split())
        nospeech = 'no speech' in t.lower()[:400]
    secs = 0
    for x in dur.split(':'):
        if x: secs = secs*60 + int(x)
    rows.append(dict(date=date, id=vid, title=title, secs=secs, words=words, src=src,
                     comments=os.path.exists(os.path.join(p, 'comments.md')), nospeech=nospeech, folder=d))
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'videos', sum(r['words'] for r in rows), 'words')
import collections
print(collections.Counter(r['src'] for r in rows).most_common(10))
print('nospeech', sum(r['nospeech'] for r in rows), '<60 words', sum(r['words']<60 for r in rows))
