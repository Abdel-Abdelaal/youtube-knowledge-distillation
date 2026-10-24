# Search what NH said: principles (the book), claims (map notes) and raw transcripts, with citations.
#   python _work/ask.py "rest between sets"              all three layers, best matches first
#   python _work/ask.py deload --only principles         one layer: principles | claims | transcripts
#   python _work/ask.py protein --topic nutrition -n 30  filter claims by topic (or principles by ID prefix, e.g. NUT)
#   python _work/ask.py VOL-03                           show one principle in full
#   python _work/ask.py "rir OR failure" --since 2024    FTS5 syntax works (OR, NOT, "phrases", prefix*)
# Reads derived/nh.db (python _work/build_db.py rebuilds it).
import os, re, sys, sqlite3, argparse, textwrap
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derived', 'nh.db')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

ap = argparse.ArgumentParser(description='Search Natural Hypertrophy principles, claims and transcripts.')
ap.add_argument('query', nargs='+')
ap.add_argument('--only', choices=['principles', 'claims', 'transcripts'])
ap.add_argument('--topic', help='claims topic (e.g. volume) or principle ID prefix (e.g. VOL)')
ap.add_argument('--since', help='YYYY or YYYY-MM: claims/transcripts on or after this date')
ap.add_argument('-n', type=int, default=10, help='max results per layer (default 10)')
a = ap.parse_args()
q = ' '.join(a.query)
con = sqlite3.connect(DB)
url = lambda v, t: f'https://www.youtube.com/post/{v}' if len(v) > 11 else f'https://youtu.be/{v}?t={t}'
wrap = lambda s, ind='    ': textwrap.fill(s or '', 110, initial_indent=ind, subsequent_indent=ind)

def fts(s):
    """Plain words -> AND query with prefix matching; leave explicit FTS syntax alone."""
    if re.search(r'["*]|\b(OR|AND|NOT|NEAR)\b', s): return s
    return ' '.join(f'"{w}"*' for w in re.findall(r"[\w'-]+", s))

def show_principle(r):
    pid, chap, title, st, nums, scope, conf, status, chk, cites = r
    print(f'\n[{pid}] {title}   ({chap})')
    print(wrap(st))
    if nums and nums != '—': print(wrap('Numbers: ' + nums))
    print(wrap('Scope: ' + (scope or '')))
    print(wrap(f'Confidence: {conf}  |  Status: {status}'))
    if chk: print(wrap('Check: ' + chk))
    for c in (cites or '').split():
        v, t = c.rsplit('@', 1)
        title = con.execute('SELECT title, date FROM videos WHERE id=?', (v,)).fetchone()
        print(f'    - {url(v, t)}  {title[1][:7] + " " + title[0] if title else ""}')

PCOLS = 'p.id, p.chapter, p.title, p.statement, p.numbers, p.scope, p.confidence, p.status, p.check_q, p.citations'
if re.fullmatch(r'[A-Za-z]{3}-\d{2,3}', q):
    r = con.execute(f'SELECT {PCOLS} FROM principles p WHERE p.id=?', (q.upper(),)).fetchone()
    show_principle(r) if r else print('No principle', q.upper()); sys.exit()

since = a.since or ''
if a.only in (None, 'principles'):
    try:
        sql = f'''SELECT {PCOLS} FROM principles_fts f JOIN principles p ON p.id = f.id
                  WHERE principles_fts MATCH ? {"AND p.id LIKE ?" if a.topic else ""} ORDER BY bm25(principles_fts) LIMIT ?'''
        args = [fts(q)] + ([a.topic.upper() + '-%'] if a.topic else []) + [a.n]
        rows = con.execute(sql, args).fetchall()
    except sqlite3.OperationalError: rows = []
    print(f'=== PRINCIPLES ({len(rows)})')
    for r in rows: show_principle(r)

if a.only in (None, 'claims'):
    sql = f'''SELECT c.date, c.topic, c.type, c.claim, c.video_id, c.ts_sec, v.title FROM claims_fts f
              JOIN claims c ON c.id = f.rowid LEFT JOIN videos v ON v.id = c.video_id
              WHERE claims_fts MATCH ? AND c.date >= ? {"AND c.topic = ?" if a.topic else ""}
              ORDER BY bm25(claims_fts) LIMIT ?'''
    args = [fts(q), since] + ([a.topic.lower()] if a.topic else []) + [a.n]
    rows = con.execute(sql, args).fetchall()
    print(f'\n=== CLAIMS ({len(rows)}; from map notes, one line each)')
    for d, tp, ty, cl, v, t, ti in rows:
        print(f'\n{d} [{tp}/{ty}] {url(v, t)}\n{wrap(cl)}\n    ({ti})')

if a.only in (None, 'transcripts'):
    rows = con.execute('''SELECT date, video_id, ts_sec, snippet(transcript_fts, 0, '[', ']', '…', 24) FROM transcript_fts
                          WHERE transcript_fts MATCH ? AND date >= ? ORDER BY bm25(transcript_fts) LIMIT ?''',
                       (fts(q), since, a.n)).fetchall()
    print(f'\n=== TRANSCRIPTS ({len(rows)}; raw auto-captions, his exact words)')
    for d, v, t, s in rows:
        print(f'\n{d} {url(v, t)}\n{wrap(s)}')
