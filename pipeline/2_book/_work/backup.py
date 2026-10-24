# Zips bodybuilding_book/ (minus .git, temp batches and the rebuildable DB) to
# D:\NaturalHypertrophy\_backups\book_<timestamp>.zip and keeps the newest 5.
import os, zipfile, datetime, glob
BOOK = r'D:\NaturalHypertrophy\bodybuilding_book'
DEST = r'D:\NaturalHypertrophy\_backups'
SKIP_DIRS = {'.git', 'batches', '__pycache__'}
SKIP_FILES = {'nh.db', 'nh.db.tmp'}
os.makedirs(DEST, exist_ok=True)
out = os.path.join(DEST, f"book_{datetime.datetime.now():%Y%m%d_%H%M%S}.zip")
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(BOOK):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f not in SKIP_FILES:
                p = os.path.join(root, f); z.write(p, os.path.relpath(p, os.path.dirname(BOOK)))
for old in sorted(glob.glob(os.path.join(DEST, 'book_*.zip')))[:-5]: os.remove(old)
print(out, f'{os.path.getsize(out) / 1e6:.1f} MB')
