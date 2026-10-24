# Builds derived/nh.db (SQLite) from the raw layer. Idempotent: always rebuilds from scratch into a
# temp file and swaps it in, so it is safe to re-run any time (e.g. after every map wave).
# Sources: derived/manifest.csv (run manifest.py first), ../index.csv (views/likes), raw/*.json (notes),
# videos/*/transcript.txt (full-text index), derived/lift_log.csv, derived/topics/*.md, book/chapters/*.md.
import os, re, csv, json, glob, sqlite3, hashlib, datetime
BASE = r'D:\NaturalHypertrophy'
BOOK = os.path.join(BASE, 'bodybuilding_book')
DB = os.path.join(BOOK, 'derived', 'nh.db')
TMP = DB + '.tmp'
if os.path.exists(TMP): os.remove(TMP)
con = sqlite3.connect(TMP)
con.executescript('''
CREATE TABLE videos(id TEXT PRIMARY KEY, date TEXT, title TEXT, duration_sec INT, views INT, likes INT,
  comment_count INT, transcript_source TEXT, words INT, has_comments INT, folder TEXT, kind TEXT DEFAULT 'video');
CREATE TABLE notes(video_id TEXT PRIMARY KEY, kind TEXT, summary TEXT, quality TEXT, topics TEXT, raw_json TEXT);
CREATE TABLE claims(id INTEGER PRIMARY KEY, video_id TEXT, ts_sec INT, date TEXT, topic TEXT, subtopic TEXT,
  type TEXT, claim TEXT, numbers_json TEXT, confidence TEXT);
CREATE TABLE exercises(id INTEGER PRIMARY KEY, video_id TEXT, ts_sec INT, date TEXT, name TEXT, cues TEXT, why TEXT);
CREATE TABLE stats(id INTEGER PRIMARY KEY, video_id TEXT, ts_sec INT, date TEXT, metric TEXT, value TEXT, as_of TEXT);
CREATE TABLE training_log(id INTEGER PRIMARY KEY, video_id TEXT, date TEXT, lift TEXT, load_kg REAL, load_lbs REAL,
  reps INT, sets INT, notes TEXT, source TEXT);
CREATE TABLE quotes(id INTEGER PRIMARY KEY, video_id TEXT, ts_sec INT, date TEXT, text TEXT);
CREATE TABLE viewer_questions(id INTEGER PRIMARY KEY, video_id TEXT, date TEXT, question TEXT);
CREATE TABLE topics(name TEXT PRIMARY KEY, n_claims INT, n_videos INT, first_date TEXT, last_date TEXT, file TEXT, file_sha TEXT);
CREATE TABLE chapters(name TEXT PRIMARY KEY, file TEXT, version TEXT, words INT, n_citations INT, updated TEXT);
CREATE TABLE citations(id INTEGER PRIMARY KEY, chapter TEXT, section TEXT, video_id TEXT, ts_sec INT, claim_id INT);
CREATE VIRTUAL TABLE transcript_fts USING fts5(text, video_id UNINDEXED, date UNINDEXED, ts_sec UNINDEXED,
  tokenize='porter unicode61');
CREATE VIRTUAL TABLE claims_fts USING fts5(claim, content='claims', content_rowid='id', tokenize='porter unicode61');
CREATE VIEW claims_cited AS SELECT c.*, v.title, 'https://youtu.be/' || c.video_id || '?t=' || c.ts_sec AS url
  FROM claims c LEFT JOIN videos v ON v.id = c.video_id;
''')

def num(x):
    try: return int(str(x).replace(',', ''))
    except Exception: return None

# videos
idx = {}
ip = os.path.join(BASE, 'index.csv')
if os.path.exists(ip):
    for r in csv.DictReader(open(ip, encoding='utf-8-sig')): idx[r['id']] = r
for r in csv.DictReader(open(os.path.join(BOOK, 'derived', 'manifest.csv'), encoding='utf-8')):
    i = idx.get(r['id'], {})
    con.execute('INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (r['id'], r['date'], r['title'].replace('⧸', '/'),
        num(r['secs']), num(i.get('views')), num(i.get('likes')), num(i.get('comment_count')), r['src'], num(r['words']),
        int(r['comments'] == 'True'), r['folder'], 'video'))

def ts(x):
    try: return int(float(x or 0))
    except Exception: return 0

def get(o, k, i):
    """Notes may use objects (original schema) or compact arrays; read field k / position i."""
    if isinstance(o, dict): return o.get(k)
    if isinstance(o, (list, tuple)) and len(o) > i: return o[i]
    return None

TYPES = {'P': 'principle', 'R': 'prescription', 'O': 'opinion', 'A': 'anecdote', 'D': 'data'}
bad = []
for p in sorted(glob.glob(os.path.join(BOOK, 'raw', '*.json'))):
    try: n = json.load(open(p, encoding='utf-8'))
    except Exception as e: bad.append(os.path.basename(p)); continue
    vid, date = n.get('id') or os.path.basename(p)[:-5], n.get('date', '')
    if not con.execute('SELECT 1 FROM videos WHERE id=?', (vid,)).fetchone():  # community posts / ko-fi
        con.execute('INSERT INTO videos(id,date,title,kind) VALUES(?,?,?,?)', (vid, date, n.get('title'), 'post'))
    con.execute('INSERT OR REPLACE INTO notes VALUES(?,?,?,?,?,?)', (vid, n.get('kind'), n.get('summary'), n.get('quality'),
        ','.join(n.get('topics') or []), json.dumps(n, ensure_ascii=False)))
    for c in n.get('claims') or []:
        text = get(c, 'claim', 0)
        if not text: continue
        typ = get(c, 'type', 1) or ''
        conf = get(c, 'confidence', 99) or ('low' if typ.endswith('?') else 'high')
        typ = TYPES.get(typ.rstrip('?'), typ.rstrip('?'))
        con.execute('INSERT INTO claims(video_id,ts_sec,date,topic,subtopic,type,claim,numbers_json,confidence) VALUES(?,?,?,?,?,?,?,?,?)',
            (vid, ts(get(c, 't', 5)), date, get(c, 'topic', 2) or 'other', get(c, 'body_part', 3) or None, typ, text,
             json.dumps(get(c, 'numbers', 4) or {}, ensure_ascii=False), conf))
    for e in n.get('exercises') or []:
        cues = get(e, 'cues', 1)
        con.execute('INSERT INTO exercises(video_id,ts_sec,date,name,cues,why) VALUES(?,?,?,?,?,?)', (vid, ts(get(e, 't', 3)), date,
            get(e, 'name', 0), '; '.join(cues) if isinstance(cues, list) else cues, get(e, 'why', 2)))
    for s in n.get('stats') or []:
        con.execute('INSERT INTO stats(video_id,ts_sec,date,metric,value,as_of) VALUES(?,?,?,?,?,?)', (vid, ts(get(s, 't', 3)), date,
            get(s, 'metric', 0), str(get(s, 'value', 1)), get(s, 'as_of', 2)))
    for l in n.get('training_log') or []:
        con.execute('INSERT INTO training_log(video_id,date,lift,load_kg,load_lbs,reps,sets,notes,source) VALUES(?,?,?,?,?,?,?,?,?)',
            (vid, date, get(l, 'lift', 0), get(l, 'load_kg', 1), get(l, 'load_lbs', 2), get(l, 'reps', 3), get(l, 'sets', 4),
             get(l, 'notes', 5), 'note'))
    for q in n.get('quotes') or []:
        con.execute('INSERT INTO quotes(video_id,ts_sec,date,text) VALUES(?,?,?,?)', (vid, ts(get(q, 't', 1)), date, get(q, 'text', 0)))
    for q in n.get('viewer_questions') or []:
        con.execute('INSERT INTO viewer_questions(video_id,date,question) VALUES(?,?,?)', (vid, date, q))
con.execute("INSERT INTO claims_fts(claims_fts) VALUES('rebuild')")

# lift-clip titles (lift_titles.py)
lp = os.path.join(BOOK, 'derived', 'lift_log.csv')
if os.path.exists(lp):
    for r in csv.DictReader(open(lp, encoding='utf-8')):
        con.execute('INSERT INTO training_log(video_id,date,lift,load_kg,load_lbs,reps,notes,source) VALUES(?,?,?,?,?,?,?,?)',
            (r['id'], r['date'], r['lift'], float(r['kg']), float(r['lbs']), num(r['reps']), r['extra'], 'title'))

# transcripts: one FTS row per [m:ss] paragraph
tsre = re.compile(r'^\[(\d+(?::\d+)+)\]\s*(.*)$')
for vid, date, folder in con.execute('SELECT id, date, folder FROM videos WHERE folder IS NOT NULL').fetchall():
    tp = os.path.join(BASE, 'videos', folder, 'transcript.txt')
    if not os.path.exists(tp): continue
    rows = []
    for ln in open(tp, encoding='utf-8', errors='replace'):
        m = tsre.match(ln.strip())
        if not m: continue
        s = 0
        for x in m.group(1).split(':'): s = s * 60 + int(x)
        rows.append((m.group(2), vid, date, s))
    con.executemany('INSERT INTO transcript_fts(text,video_id,date,ts_sec) VALUES(?,?,?,?)', rows)

# topics + chapters + citations
sha = lambda p: hashlib.sha1(open(p, 'rb').read()).hexdigest()[:10]
for name, n, nv, a, b in con.execute('SELECT topic, COUNT(*), COUNT(DISTINCT video_id), MIN(date), MAX(date) FROM claims GROUP BY topic').fetchall():
    f = os.path.join(BOOK, 'derived', 'topics', f'{name}.md')
    con.execute('INSERT INTO topics VALUES(?,?,?,?,?,?,?)', (name, n, nv, a, b, os.path.relpath(f, BOOK) if os.path.exists(f) else None,
                                                              sha(f) if os.path.exists(f) else None))
cite = re.compile(r'\{\{([\w-]+)@(\d+)\}\}|youtu\.be/([\w-]{11})\?t=(\d+)')
for f in sorted(glob.glob(os.path.join(BOOK, 'book', 'chapters', '*.md'))):
    name, section, nc = os.path.basename(f)[:-3], '', 0
    text = open(f, encoding='utf-8').read()
    for ln in text.split('\n'):
        if ln.startswith('#'): section = ln.lstrip('# ').strip()
        for m in cite.finditer(ln):
            vid, t = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
            cid = con.execute('SELECT id FROM claims WHERE video_id=? ORDER BY ABS(ts_sec-?) LIMIT 1', (vid, int(t))).fetchone()
            con.execute('INSERT INTO citations(chapter,section,video_id,ts_sec,claim_id) VALUES(?,?,?,?,?)',
                        (name, section, vid, int(t), cid[0] if cid else None)); nc += 1
    con.execute('INSERT INTO chapters VALUES(?,?,?,?,?,?)', (name, os.path.relpath(f, BOOK), sha(f), len(text.split()), nc,
        datetime.datetime.fromtimestamp(os.path.getmtime(f)).isoformat(timespec='seconds')))

# principles (from derived/principles.json, built by principles.py)
con.executescript('''
CREATE TABLE principles(id TEXT PRIMARY KEY, chapter TEXT, section TEXT, title TEXT, statement TEXT, numbers TEXT,
  scope TEXT, confidence TEXT, confidence_level TEXT, status TEXT, status_level TEXT, check_q TEXT, citations TEXT);
CREATE VIRTUAL TABLE principles_fts USING fts5(id UNINDEXED, title, statement, numbers, scope, check_q, tokenize='porter unicode61');
''')
pj = os.path.join(BOOK, 'derived', 'principles.json')
for p in (json.load(open(pj, encoding='utf-8')) if os.path.exists(pj) else []):
    row = (p['id'], p['chapter'], p['section'], p['title'], p.get('statement'), p.get('numbers'), p.get('scope'),
           p.get('confidence'), p['confidence_level'], p.get('status'), p['status_level'], p.get('check'), ' '.join(p['citations']))
    con.execute('INSERT OR REPLACE INTO principles VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
    con.execute('INSERT INTO principles_fts VALUES(?,?,?,?,?,?)', (p['id'], p['title'], p.get('statement'), p.get('numbers'),
                                                                  p.get('scope'), p.get('check')))

for t in ['claims(topic)', 'claims(video_id)', 'claims(date)', 'exercises(name)', 'citations(video_id)', 'training_log(lift)']:
    con.execute(f'CREATE INDEX IF NOT EXISTS ix_{re.sub(r"[^a-z]", "_", t)} ON {t}')
con.commit(); con.close()
os.replace(TMP, DB)
con = sqlite3.connect(DB)
print('nh.db:', ', '.join(f'{t}={con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]}' for t in
      ['videos', 'notes', 'claims', 'exercises', 'stats', 'training_log', 'quotes', 'transcript_fts', 'chapters', 'citations', 'principles']),
      '| malformed notes:', bad)
