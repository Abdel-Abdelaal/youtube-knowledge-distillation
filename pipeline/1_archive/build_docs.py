# Build readable documentation from the raw yt-dlp output in ../videos.
# Per video folder:  README.md (metadata + description + links), transcript.txt, comments.md
# Top level:         INDEX.md, index.csv, links.csv
# Safe to re-run at any time; it only reads what has been downloaded so far.
import csv, glob, html, json, os, re, sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VID = os.path.join(ROOT, 'videos')
URL_RE = re.compile(r'https?://[^\s<>()"\']+')


def hms(sec):
    sec = int(sec or 0)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def fmt_date(d):
    return f'{d[:4]}-{d[4:6]}-{d[6:]}' if d and len(d) == 8 else (d or '')


def load(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return None


def vtt_to_text(path):
    """Collapse YouTube's rolling auto-caption cues into deduplicated, timestamped lines."""
    out, last = [], ''
    cue_time = None
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        m = re.match(r'(\d+):(\d\d):(\d\d)\.\d+ -->', line) or re.match(r'(\d\d):(\d\d)\.\d+ -->', line)
        if m:
            g = [int(x) for x in m.groups()]
            cue_time = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        if not line.strip() or line.startswith(('WEBVTT', 'Kind:', 'Language:', 'NOTE')) or cue_time is None:
            continue
        txt = html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
        if not txt or txt == last:
            continue
        if last and txt.startswith(last):  # rolling caption grew
            txt = txt[len(last):].strip()
            if not txt:
                continue
        out.append((cue_time, txt))
        last = line and html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
    # group into ~30s paragraphs
    paras, cur, start = [], [], None
    for t, txt in out:
        if start is None:
            start = t
        cur.append(txt)
        if t - start >= 30 and txt.endswith(('.', '?', '!')) or t - start >= 60:
            paras.append(f'[{hms(start)}] ' + ' '.join(cur))
            cur, start = [], None
    if cur:
        paras.append(f'[{hms(start)}] ' + ' '.join(cur))
    return '\n\n'.join(paras)


def pick_sub(folder, vid, info):
    manual = set((info or {}).get('subtitles') or {})
    files = glob.glob(os.path.join(glob.escape(folder), f'{vid}.*.vtt'))
    langs = {os.path.basename(f)[len(vid) + 1:-4]: f for f in files}
    for lang in ['en', 'en-US', 'en-GB']:  # creator-uploaded captions first
        if lang in langs and lang in manual:
            return langs[lang], 'manual'
    for lang in ['en-orig', 'en', 'en-US', 'en-GB'] + sorted(langs):
        if lang in langs:
            return langs[lang], 'auto-generated'
    return None, None


def comments_md(title, comments):
    kids = defaultdict(list)
    for c in comments:
        kids[c.get('parent', 'root')].append(c)
    lines = [f'# Comments: {title}', '', f'{len(comments)} comments downloaded '
             f'({len(kids["root"])} top-level). Sorted as YouTube returned them (top comments first).', '']

    def one(c, depth):
        who = c.get('author') or '?'
        tags = []
        if c.get('author_is_uploader'): tags.append('CREATOR')
        if c.get('is_pinned'): tags.append('PINNED')
        if c.get('is_favorited'): tags.append('hearted')
        when = c.get('_time_text') or ''
        head = f"**{who}**{' [' + ', '.join(tags) + ']' if tags else ''} · {c.get('like_count') or 0} likes · {when}"
        body = (c.get('text') or '').replace('\n', '\n' + '> ' * depth if depth else '\n')
        pre = '> ' * depth
        lines.append(pre + head)
        lines.append(pre + body)
        lines.append('')
        for r in kids.get(c.get('id'), []):
            one(r, depth + 1)

    for c in kids['root']:
        one(c, 0)
        lines.append('---')
        lines.append('')
    return '\n'.join(lines)


def main():
    rows, links = [], defaultdict(set)
    folders = sorted(d for d in glob.glob(os.path.join(VID, '*')) if os.path.isdir(d))
    for folder in folders:
        m = re.search(r'\[([\w-]{11})\]$', folder)
        if not m:
            continue
        vid = m.group(1)
        info = load(os.path.join(folder, f'{vid}.info.json'))
        if not info:
            continue
        cinfo = load(os.path.join(folder, f'{vid}.comments.info.json'))
        comments = (cinfo or {}).get('comments') or info.get('comments') or []
        title = info.get('title', '')
        desc = info.get('description') or ''

        sub_path, sub_kind = pick_sub(folder, vid, info)
        whisper = load(os.path.join(folder, f'{vid}.whisper.json'))
        if sub_path:
            with open(os.path.join(folder, 'transcript.txt'), 'w', encoding='utf-8') as f:
                f.write(f'{title}\nhttps://www.youtube.com/watch?v={vid}\nTranscript source: {sub_kind} English captions\n\n')
                f.write(vtt_to_text(sub_path))
        elif whisper:
            sub_path = True
            segs = whisper['segments']
            sub_kind = 'whisper' if segs else 'no speech'
            with open(os.path.join(folder, 'transcript.txt'), 'w', encoding='utf-8') as f:
                f.write(f'{title}\nhttps://www.youtube.com/watch?v={vid}\n'
                        f'Transcript source: Whisper {whisper["model"]} speech-to-text from the audio '
                        f'(YouTube has no captions for this video), language: {whisper["language"]}\n\n')
                f.write('\n'.join(f'[{hms(s["start"])}] {s["text"]}' for s in segs) if segs
                        else '(No speech detected: the video is music/ambient sound only.)')
        if comments:
            open(os.path.join(folder, 'comments.md'), 'w', encoding='utf-8').write(comments_md(title, comments))

        vlinks = sorted(set(u.rstrip('.,;:!?)]') for u in URL_RE.findall(desc)))
        creator_comment_links = sorted(set(u.rstrip('.,;:!?)]') for c in comments if c.get('author_is_uploader')
                                           for u in URL_RE.findall(c.get('text') or '')))
        for u in vlinks:
            links[u].add(('description', vid))
        for u in creator_comment_links:
            links[u].add(('creator comment', vid))

        audio = [f'{vid}.{ext}' for ext in ('m4a', 'webm', 'opus') if os.path.exists(os.path.join(folder, f'{vid}.{ext}'))]
        chapters = info.get('chapters') or []
        md = [f'# {title}', '',
              f'- **URL:** https://www.youtube.com/watch?v={vid}',
              f'- **Published:** {fmt_date(info.get("upload_date"))}',
              f'- **Duration:** {hms(info.get("duration"))}',
              f'- **Views / likes / comments (at download):** {info.get("view_count")} / {info.get("like_count")} / {info.get("comment_count")}',
              f'- **Type:** {"livestream" if info.get("was_live") else "video"}',
              f'- **Tags:** {", ".join(info.get("tags") or []) or "-"}',
              f'- **Categories:** {", ".join(info.get("categories") or [])}',
              f'- **Files:** {", ".join(audio) or "(audio not downloaded yet)"}'
              f'{", transcript.txt" if sub_path else ", (no English captions)"}'
              f'{", comments.md (" + str(len(comments)) + ")" if comments else ""}', '']
        if chapters:
            md += ['## Chapters', ''] + [f'- {hms(c["start_time"])} {c["title"]}' for c in chapters] + ['']
        md += ['## Description', '', '```', desc, '```', '']
        if vlinks or creator_comment_links:
            md += ['## Links', ''] + [f'- {u}' for u in vlinks] + [f'- {u} (from creator comment)' for u in creator_comment_links] + ['']
        open(os.path.join(folder, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md))

        rows.append({'date': fmt_date(info.get('upload_date')), 'id': vid, 'title': title,
                     'duration': hms(info.get('duration')), 'views': info.get('view_count'),
                     'likes': info.get('like_count'), 'comment_count': info.get('comment_count'),
                     'comments_saved': len(comments), 'transcript': sub_kind or '',
                     'audio': 'yes' if audio else 'no', 'livestream': 'yes' if info.get('was_live') else '',
                     'folder': os.path.relpath(folder, ROOT).replace('\\', '/')})

    rows.sort(key=lambda r: r['date'])
    with open(os.path.join(ROOT, 'index.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['id'])
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(ROOT, 'links.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['url', 'times_linked', 'where', 'video_ids'])
        for u, src in sorted(links.items(), key=lambda kv: -len(kv[1])):
            w.writerow([u, len(src), ';'.join(sorted({s for s, _ in src})), ' '.join(sorted({v for _, v in src}))])
    with open(os.path.join(ROOT, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write(f'# Natural Hypertrophy archive: {len(rows)} videos\n\n')
        f.write('| Date | Title | Length | Transcript | Comments | Folder |\n|---|---|---|---|---|---|\n')
        for r in rows:
            t = r['title'].replace('|', '\\|')
            folder = r['folder'].replace(' ', '%20').replace('[', '%5B').replace(']', '%5D')
            f.write(f"| {r['date']} | {t}{' (live)' if r['livestream'] else ''} | {r['duration']} | {r['transcript'] or '-'} | {r['comments_saved']} | [open]({folder}/README.md) |\n")
    print(f'{len(rows)} videos documented, {sum(1 for r in rows if r["transcript"])} with transcripts, '
          f'{sum(r["comments_saved"] for r in rows)} comments, {len(links)} unique links')


if __name__ == '__main__':
    main()
