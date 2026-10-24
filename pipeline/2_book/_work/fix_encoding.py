# Repairs double-encoded UTF-8 (mojibake such as "Â·" for "·", "â€”" for "—") in chapter/synthesis files.
# Usage: python _work/fix_encoding.py <file.md> [...]   Rewrites only files that change; prints what it fixed.
import sys, re

def fix(text):
    # re-decode runs of Latin-1-looking characters that are really UTF-8 bytes
    def rep(m):
        s = m.group(0)
        try: return s.encode('cp1252').decode('utf-8')
        except Exception:
            try: return s.encode('latin-1').decode('utf-8')
            except Exception: return s
    return re.sub(r'[Â-ô][\u0080-¿ŒœŠšŸŽžƒˆ˜–—‘-„†-•…‰‹›€™]{1,3}', rep, text)

for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    for _ in range(3):              # some files were double-encoded twice
        f = fix(t)
        if f == t: break
        t2, t = t, f
    orig = open(p, encoding='utf-8').read()
    if t != orig:
        open(p, 'w', encoding='utf-8').write(t)
        print(f'{p}: fixed {sum(1 for a, b in zip(orig, t) if a != b)}+ chars')
    else:
        print(f'{p}: clean')
