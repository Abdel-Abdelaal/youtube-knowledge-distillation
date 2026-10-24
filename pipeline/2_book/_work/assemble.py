# Assembles book/chapters/*.md into book/THE_BODYBUILDING_BOOK.md (+ .html):
#   {{id@sec}} markers -> [title, YYYY-MM](https://youtu.be/<id>?t=<sec>)   (community posts -> youtube.com/post/<id>)
#   runs of adjacent markers become one bracketed source list.
# Also builds the strength-log appendix from derived/strength_progression.md if it doesn't exist.
# Prints unknown ids (exit 1 if any). No third-party packages: the HTML converter below covers the
# Markdown subset the chapters use (headings, lists, tables, bold/italic, links, blockquotes, code).
import os, re, json, glob, html, sys, datetime
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
CH = os.path.join(BOOK, 'book', 'chapters')
OUT_MD = os.path.join(BOOK, 'book', 'THE_BODYBUILDING_BOOK.md')
OUT_HTML = os.path.join(BOOK, 'book', 'THE_BODYBUILDING_BOOK.html')

cites = json.load(open(os.path.join(BOOK, 'derived', 'cite_index.json'), encoding='utf-8'))
for p in glob.glob(os.path.join(BOOK, 'raw', '*.json')):          # posts + Ko-fi are not in the manifest
    i = os.path.basename(p)[:-5]
    if i not in cites:
        n = json.load(open(p, encoding='utf-8'))
        cites[i] = dict(title=n.get('title') or 'Community post', date=n.get('date', ''), post=True)

def url(i, t):
    if i == 'kofi': return 'https://ko-fi.com/naturalhypertrophy'
    if cites.get(i, {}).get('post'): return f'https://www.youtube.com/post/{i}'
    return f'https://youtu.be/{i}' + (f'?t={t}' if int(t) else '')

PID_HEAD = re.compile(r'^###\s+[A-Z]{3}-\d{2,3}\b', re.M)
MARK = re.compile(r'\{\{([\w-]+)@(\d+)\}\}')
RUN = re.compile(r'(?:\s*\{\{[\w-]+@\d+\}\})+')
unknown = []

def expand(text):
    def one(m):
        refs = []
        for i, t in MARK.findall(m.group(0)):
            c = cites.get(i)
            if not c: unknown.append(f'{i}@{t}'); refs.append(f'[unknown source {i}@{t}]'); continue
            title = c['title'].replace('[', '(').replace(']', ')').replace('|', '/')
            refs.append(f"[{title}, {c['date'][:7]}]({url(i, t)})")
        return ' (' + '; '.join(refs) + ')'
    return RUN.sub(one, text)

PID = re.compile(r'(?<![\w/=#-])([A-Z]{3}-\d{2,3})(?![\w-])')

def contradictions_appendix():
    """Always rebuilt: the 'How his view changed' + 'Contradictions' sections of every synthesis, by topic."""
    out = ['# Appendix A. Contradictions & how his views changed', '',
           'Collected by script from the topic syntheses: where NH changed his mind over time, and where he said '
           'conflicting things without a clear evolution. The principles in the chapters carry the same information '
           'in their **Status** field; this appendix shows it all in one place.', '']
    for f in sorted(glob.glob(os.path.join(BOOK, 'derived', 'synthesis', '*.md'))):
        topic = os.path.basename(f)[:-3].replace('_', ' ')
        secs, cur = {}, None
        for ln in open(f, encoding='utf-8'):
            ln = ln.rstrip('\n')
            if ln.startswith('## '):
                h = ln[3:].strip().lower()
                cur = 'changed' if h.startswith('how his view') else 'contra' if h.startswith('contradiction') else None
                continue
            if cur and ln.strip() and not re.search(r'false alarm|none found|script flag', ln, re.I):
                secs.setdefault(cur, []).append(ln)
        if not secs: continue
        out.append(f'## {topic.capitalize()}')
        if secs.get('changed'): out += ['', '**Changed over time**', ''] + secs['changed']
        if secs.get('contra'): out += ['', '**Contradictions**', ''] + secs['contra']
        out.append('')
    open(os.path.join(CH, 'A1_contradictions.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

def strength_appendix():
    p = os.path.join(CH, 'A3_strength_log.md')
    if os.path.exists(p): return
    src = open(os.path.join(BOOK, 'derived', 'strength_progression.md'), encoding='utf-8').read()
    src = src.split('\n', 1)[1]
    src = re.sub(r'^## Unparsed.*', '', src, flags=re.S | re.M)
    open(p, 'w', encoding='utf-8').write(
        '# Appendix C. Strength log\n\nEvery set NH put in a lift-clip title, parsed by script (`lift_titles.py`), '
        'grouped by lift. Use it to see how his numbers moved over time; see chapters 1 and 7 for context.\n' + src)

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    s = re.sub(r'(?<![\w"=/])(https?://[^\s<)]+)', r'<a href="\1">\1</a>', s)
    s = PID.sub(r'<a href="#\1">\1</a>', s)       # principle cross-references
    return s

def to_html(md, toc):
    out, lines, i = [], md.split('\n'), 0
    para, lst = [], []
    def flush():
        nonlocal para
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para = []
    def close_lists(depth=0):
        while len(lst) > depth: out.append(f'</li></{lst.pop()}>')
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            flush(); close_lists(); i += 1; continue
        if re.fullmatch(r'<a id="[\w-]+"></a>', ln.strip()): i += 1; continue   # md-only anchor; HTML uses the heading id
        m = re.match(r'^(#{1,6})\s+(.*)', ln)
        if m:
            flush(); close_lists(); lvl = len(m.group(1)); txt = m.group(2)
            pid = re.match(r'([A-Z]{3}-\d{2,3})\b', txt)
            hid = pid.group(1) if pid else slug(txt)
            body = PID.sub('', html.escape(txt), count=1) if pid else inline(txt)
            if pid: body = f'<a class="pid" href="#{hid}">{hid}</a>{body}'
            out.append(f'<h{lvl} id="{hid}">{body}</h{lvl}>'); i += 1; continue
        if ln.startswith('```'):
            flush(); close_lists(); j = i + 1; code = []
            while j < len(lines) and not lines[j].startswith('```'): code.append(lines[j]); j += 1
            out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>'); i = j + 1; continue
        if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            flush(); close_lists()
            cells = lambda r: [c.strip() for c in r.strip().strip('|').split('|')]
            out.append('<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells(ln)) + '</tr></thead><tbody>')
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells(lines[i])) + '</tr>'); i += 1
            out.append('</tbody></table></div>'); continue
        if ln.startswith('>'):
            flush(); close_lists(); q = []
            while i < len(lines) and lines[i].startswith('>'): q.append(lines[i].lstrip('> ')); i += 1
            out.append('<blockquote>' + inline(' '.join(q)) + '</blockquote>'); continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)', ln)
        if m:
            flush(); depth = len(m.group(1).replace('\t', '    ')) // 2 + 1
            tag = 'ol' if m.group(2)[0].isdigit() else 'ul'
            if depth > len(lst):
                while depth > len(lst): out.append(f'<{tag}><li>'); lst.append(tag)
            else:
                close_lists(depth); out.append('</li><li>')
            out.append(inline(m.group(3))); i += 1; continue
        if re.match(r'^\s*(---|\*\*\*)\s*$', ln): flush(); close_lists(); out.append('<hr>'); i += 1; continue
        if lst: out.append(' ' + inline(ln.strip())); i += 1; continue
        para.append(ln.strip()); i += 1
    flush(); close_lists()
    nav = '\n'.join(f'<li><a href="#{slug(t)}">{html.escape(t)}</a></li>' for t in toc)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Bodybuilding Book</title><style>
:root{{--bg:#fbfaf7;--fg:#1e1d1a;--mut:#6b675e;--line:#e3dfd5;--acc:#9a3412;--card:#f3f0e8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#151412;--fg:#e9e6df;--mut:#a39e93;--line:#34312b;--acc:#f0a070;--card:#1f1d1a}}}}
body{{background:var(--bg);color:var(--fg);font:17px/1.65 Georgia,'Iowan Old Style',serif;margin:0}}
main{{max-width:46rem;margin:0 auto;padding:2rem 16px 6rem}}
nav.toc{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem 1.25rem;margin:2rem 0}}
nav.toc ol{{margin:0;padding-left:1.2rem;columns:2;column-gap:2rem}} @media(max-width:640px){{nav.toc ol{{columns:1}}}}
h1{{font-size:2rem;line-height:1.2;margin:3.5rem 0 1rem;border-top:3px solid var(--fg);padding-top:1rem}}
h2{{font-size:1.35rem;margin:2.5rem 0 .6rem}} h3{{font-size:1.1rem;margin:1.8rem 0 .4rem}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
p a,li a,td a{{font-size:.82em;font-family:system-ui,sans-serif}}
.tw{{overflow-x:auto;margin:1rem 0}} table{{border-collapse:collapse;font:14px/1.45 system-ui,sans-serif;min-width:100%}}
th,td{{border-bottom:1px solid var(--line);padding:.4rem .55rem;text-align:left;vertical-align:top}} th{{background:var(--card)}}
blockquote{{margin:1rem 0;padding:.5rem 1rem;border-left:3px solid var(--acc);background:var(--card)}}
code{{font-size:.9em;background:var(--card);padding:0 .25em;border-radius:3px}} pre{{overflow-x:auto;background:var(--card);padding:1rem}}
li{{margin:.25rem 0}} h3[id] a.pid{{font-family:ui-monospace,monospace;font-size:.85em;color:var(--mut);margin-right:.2em}}
h3+ul{{list-style:none;padding-left:0;font-size:.95rem}} h3+ul>li{{margin:.15rem 0}} .meta{{color:var(--mut);font-size:.9rem}}
</style></head><body><main>
<p class="meta">Built {datetime.date.today()} from {len(cites)} sources. Citations link to the exact second of the video.</p>
<nav class="toc"><strong>Contents</strong><ol>{nav}</ol></nav>
{chr(10).join(out)}
</main></body></html>'''

if __name__ == '__main__':
    strength_appendix()
    contradictions_appendix()
    files = sorted(glob.glob(os.path.join(CH, '*.md')), key=lambda p: (os.path.basename(p)[0].isalpha(), os.path.basename(p)))
    parts, toc, n = [], [], 0
    for f in files:
        txt = open(f, encoding='utf-8').read().strip()
        n += len(MARK.findall(txt))
        h = re.search(r'^# (.+)$', txt, re.M)
        if h: toc.append(h.group(1).strip())
        txt = re.sub(r'^(###\s+)([A-Z]{3}-\d{2,3})\b', r'<a id="\2"></a>\n\1\2', txt, flags=re.M)  # md anchors
        parts.append(expand(txt))
    np = sum(len(PID_HEAD.findall(open(f, encoding='utf-8').read())) for f in files)
    head = ('# The Bodybuilding Book\n\n*A source of truth for what Natural Hypertrophy teaches about muscle, strength and '
            f'the gym look: {np} principles with stable IDs, distilled from his videos and posts (2020-2026). '
            f'Built {datetime.date.today()}.*\n\n'
            'Each principle: **Statement · Numbers · Scope · Confidence · Status · Check · Sources**. '
            'Search it with `python _work/ask.py "<words>"`; test a program against `book/CHECKLIST.md`.\n\n## Contents\n'
            + '\n'.join(f'{k + 1}. [{t}](#{slug(t)})' for k, t in enumerate(toc)) + '\n')
    md = head + '\n\n' + '\n\n---\n\n'.join(parts) + '\n'
    open(OUT_MD, 'w', encoding='utf-8').write(md)
    open(OUT_HTML, 'w', encoding='utf-8').write(to_html('\n\n'.join(parts), toc))
    print(f'{len(files)} chapters, {n} citations, {len(md.split())} words -> {OUT_MD} (+ .html); unknown ids: {len(unknown)}')
    for u in unknown[:20]: print('  unknown', u)
    sys.exit(1 if unknown else 0)
