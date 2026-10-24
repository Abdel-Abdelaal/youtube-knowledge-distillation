# Transcribe videos that have no YouTube captions, from their temporary audio, with faster-whisper on the GPU.
# Writes <id>.whisper.json (segments) per folder, then deletes the audio. Re-runnable: skips finished folders.
# Usage: python whisper_transcribe.py [model]   (default: medium)
import glob, json, os, re, site, sys, time

# make the pip-installed CUDA libraries (nvidia-cublas-cu12, nvidia-cudnn-cu12) visible on Windows
for sp in site.getsitepackages() + [site.getusersitepackages()]:
    for sub in ('cublas', 'cudnn'):
        p = os.path.join(sp, 'nvidia', sub, 'bin')
        if os.path.isdir(p):
            os.add_dll_directory(p)
            os.environ['PATH'] = p + os.pathsep + os.environ['PATH']

import av
import numpy as np
from faster_whisper import WhisperModel


def decode(path, sr=16000):
    """Decode to 16 kHz mono float32 ourselves: faster-whisper's decoder passes an option av>=15 removed."""
    out = []
    with av.open(path) as c:
        rs = av.AudioResampler(format='s16', layout='mono', rate=sr)
        for frame in c.decode(audio=0):
            for f in rs.resample(frame):
                out.append(f.to_ndarray().reshape(-1))
        for f in rs.resample(None):
            out.append(f.to_ndarray().reshape(-1))
    return (np.concatenate(out).astype(np.float32) / 32768.0) if out else np.zeros(0, np.float32)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'videos'))
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'medium'
model = WhisperModel(MODEL, device='cuda', compute_type='int8')

jobs = []
for d in sorted(glob.glob(os.path.join(glob.escape(ROOT), '*'))):
    m = re.search(r'\[([\w-]{11})\]$', d)
    if not m:
        continue
    vid = m.group(1)
    audio = [p for p in (os.path.join(d, f'{vid}.{e}') for e in ('m4a', 'webm', 'opus', 'mp4')) if os.path.exists(p)]
    # optional filter so several processes can split the work: argv[2] = only:<id,id> or skip:<id,id>
    flt = sys.argv[2] if len(sys.argv) > 2 else ''
    only = flt[5:] if flt.startswith('only:') else None
    skip = flt[5:] if flt.startswith('skip:') else ''
    if (only and vid not in only.split(',')) or vid in skip.split(','):
        continue
    if audio and not os.path.exists(os.path.join(d, f'{vid}.whisper.json')):
        jobs.append((vid, d, audio[0]))

print(f'{len(jobs)} files to transcribe with {MODEL}', flush=True)
t_start, audio_secs = time.time(), 0.0
for n, (vid, d, audio) in enumerate(jobs, 1):
    segments, info = model.transcribe(decode(audio), beam_size=5, vad_filter=True,
                                      vad_parameters={'min_silence_duration_ms': 700},
                                      condition_on_previous_text=False)
    segs = [{'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip()} for s in segments]
    json.dump({'model': MODEL, 'language': info.language, 'language_probability': round(info.language_probability, 3),
               'duration': info.duration, 'speech_duration': info.duration_after_vad, 'segments': segs},
              open(os.path.join(d, f'{vid}.whisper.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.remove(audio)
    audio_secs += info.duration
    el = time.time() - t_start
    print(f'[{n}/{len(jobs)}] {vid} lang={info.language} segs={len(segs)} | {audio_secs / el:.1f}x realtime, '
          f'eta {el / n * (len(jobs) - n) / 60:.0f} min', flush=True)
print('done', flush=True)
