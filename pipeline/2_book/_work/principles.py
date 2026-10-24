# Parses the principle blocks in book/chapters/*.md into:
#   derived/principles.json   one record per principle (id, chapter, section, title, fields, citations)
#   book/CHECKLIST.md         every "Check:" line as a yes/no checklist, grouped by chapter
# Also validates the format (duplicate ids, missing fields, no sources) and exits 1 on problems with --strict.
# build_db.py loads principles.json into the `principles` table. Usage: python _work/principles.py [--strict]
import os, re, json, glob, sys
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
CH = os.path.join(BOOK, 'book', 'chapters')
HEAD = re.compile(r'^###\s+([A-Z]{3}-\d{2,3})\s*[·:\-–—]\s*(.+?)\s*$')
FIELD = re.compile(r'^-\s+\*\*(Statement|Numbers|Scope|Confidence|Status|Check|Sources):\*\*\s*(.*)$')
MARK = re.compile(r'\{\{([\w-]+)@(\d+)\}\}')
REQUIRED = ['Statement', 'Numbers', 'Scope', 'Confidence', 'Status', 'Sources']

def parse():
    out, problems = [], []
    for f in sorted(glob.glob(os.path.join(CH, '*.md'))):
        chapter = os.path.basename(f)[:-3]
        ctitle, section, cur = '', '', None
        for ln in open(f, encoding='utf-8'):
            ln = ln.rstrip('\n')
            if ln.startswith('# '): ctitle = ln[2:].strip(); continue
            if ln.startswith('## '): section = ln[3:].strip(); cur = None; continue
            m = HEAD.match(ln)
            if m:
                cur = dict(id=m.group(1), title=m.group(2), chapter=chapter, chapter_title=ctitle, section=section)
                out.append(cur); continue
            if ln.startswith('#'): cur = None; continue
            m = FIELD.match(ln)
            if m and cur is not None: cur[m.group(1).lower()] = m.group(2).strip()
    seen = {}
    for p in out:
        if p['id'] in seen: problems.append(f"duplicate id {p['id']} ({seen[p['id']]} and {p['chapter']})")
        seen[p['id']] = p['chapter']
        miss = [k for k in REQUIRED if k.lower() not in p]
        if miss: problems.append(f"{p['id']}: missing {', '.join(miss)}")
        p['citations'] = [f'{i}@{t}' for i, t in MARK.findall(p.get('sources', ''))]
        if not p['citations']: problems.append(f"{p['id']}: no citations")
        p['confidence_level'] = (re.match(r'\s*(high|medium|low)', p.get('confidence', ''), re.I) or [None, ''])[1].lower()
        p['status_level'] = (re.match(r'\s*(current|changed|contradicted)', p.get('status', ''), re.I) or [None, ''])[1].lower()
        if not p['confidence_level']: problems.append(f"{p['id']}: confidence not high/medium/low")
        if not p['status_level']: problems.append(f"{p['id']}: status not current/changed/contradicted")
    # cross-references ("see VOL-03") anywhere in the chapters must point at a real principle
    ref = re.compile(r'(?<![\w/=#-])([A-Z]{3}-\d{2,3})(?![\w-])')
    for f in sorted(glob.glob(os.path.join(CH, '*.md'))):
        for m in ref.finditer(open(f, encoding='utf-8').read()):
            if m.group(1) not in seen: problems.append(f"{os.path.basename(f)}: reference to unknown {m.group(1)}")
    return out, problems

def checklist(ps):
    lines = ['# The NH Checklist', '',
             'Yes/no checks built from the key principles in *The Bodybuilding Book*. Use it to test a program, a claim '
             'or an idea against what Natural Hypertrophy teaches: **yes = consistent with his view**. Each check links to '
             'its principle (statement, numbers, scope, confidence, sources). A "no" is not automatically wrong: read the '
             'principle\'s scope first (beginner vs advanced, goal, natural).', '',
             f'_{sum(1 for p in ps if p.get("check"))} checks from {len(ps)} principles. Built by `_work/principles.py`; do not edit by hand._', '']
    chap = None
    for p in ps:
        if not p.get('check'): continue
        if p['chapter'] != chap:
            chap = p['chapter']; lines += ['', f"## {p['chapter_title']}", '']
        tag = '' if p['status_level'] == 'current' else f" *({p['status_level']})*"
        lines.append(f"- [ ] {p['check']} — [{p['id']}](THE_BODYBUILDING_BOOK.html#{p['id']}) {p['title']}"
                     f" · {p['confidence_level']} confidence{tag}")
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    ps, problems = parse()
    json.dump(ps, open(os.path.join(BOOK, 'derived', 'principles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(BOOK, 'book', 'CHECKLIST.md'), 'w', encoding='utf-8').write(checklist(ps))
    # compact index (id | title | statement) for appendix writers that shouldn't read whole chapters
    open(os.path.join(BOOK, 'derived', 'principle_index.txt'), 'w', encoding='utf-8').write(
        '\n'.join(f"{p['id']} | {p['title']} | {p.get('statement', '')}" for p in ps) + '\n')
    by = {}
    for p in ps: by[p['chapter']] = by.get(p['chapter'], 0) + 1
    print(f"{len(ps)} principles, {sum(1 for p in ps if p.get('check'))} checks; problems: {len(problems)}")
    for c, n in by.items(): print(f'  {c:36s} {n}')
    for x in problems[:40]: print('  !', x)
    sys.exit(1 if problems and '--strict' in sys.argv else 0)
