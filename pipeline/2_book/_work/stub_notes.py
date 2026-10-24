# Writes a "no spoken content" stub note to raw/ for every video whose transcript has < 150 words and no note yet
# (silent lift clips, music edits). No agent is spent on them; their lift data comes from lift_titles.py.
import os, re, csv, json
BASE = r'D:\NaturalHypertrophy'
BOOK = os.path.join(BASE, 'bodybuilding_book')
MINW = 150
FENCE = '`' * 3
n = 0
for r in csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8')):
    out = os.path.join(BOOK, 'raw', r['id'] + '.json')
    if int(r['words']) >= MINW or os.path.exists(out): continue
    rp = os.path.join(BASE, 'videos', r['folder'], 'README.md')
    rd = open(rp, encoding='utf-8').read() if os.path.exists(rp) else ''
    m = re.search(r'## Description\n\n' + FENCE + r'\n(.*?)' + FENCE, rd, re.S)
    desc = re.sub(r'https?://\S+', '', m.group(1)).strip()[:500] if m else ''
    note = dict(id=r['id'], date=r['date'], title=r['title'].replace('⧸', '/'), kind='no_speech',
                summary=desc, topics=[], claims=[], exercises=[], stats=[], training_log=[], quotes=[],
                viewer_questions=[], quality='no_spoken_content', stub=True, transcript_words=int(r['words']))
    json.dump(note, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    n += 1
print(n, 'stub notes written')
