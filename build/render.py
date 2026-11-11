"""장면 슬라이드 렌더 → 내레이션 조립 → 챕터 MP4 + 자막 큐 + 사이트 데이터(site/data.js) 생성.

사용: python build/render.py [chapter_id ...]   (인자 없으면 전체)
"""
import html, json, os, re, shutil, subprocess, sys, wave
try:
    import pymupdf          # 원본 PDF로 슬라이드를 새로 그릴 때만 필요
except ImportError:
    pymupdf = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'build')
sys.path.insert(0, B)
from content import CH
from tts import key, wav_path

PDF = os.path.join(ROOT, '국제교류 업무매뉴얼_최종수정본(2026.11.10).pdf')
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or os.path.expandvars(
    r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe')
TTS = os.path.join(B, 'cache', 'tts')
WAVC = os.path.join(B, 'cache', 'wav')
IMG = os.path.join(B, 'cache', 'img')
SITE = os.path.join(ROOT, 'site')
for d in (WAVC, IMG, os.path.join(SITE, 'videos'), os.path.join(SITE, 'posters')):
    os.makedirs(d, exist_ok=True)

LEAD, GAP, COMMA_TAIL, TAIL = 0.55, 0.42, 0.0, 0.85
SR = 44100
TAG = {'law': ('법령·규정', '#1d3a72'), 'gov': ('교육청 지침·안내', '#0f7d70'), 'case': ('사례·실무 권장', '#c5631c')}


class _LazyDoc:
    """원본 PDF는 슬라이드를 새로 그릴 때만 연다."""
    _d = None

    def __getitem__(self, i):
        if self._d is None:
            self._d = pymupdf.open(PDF)
        return self._d[i]


doc = _LazyDoc()
esc = html.escape


# ───────────────────────── 이미지 자산
def page_png(p):
    f = os.path.join(IMG, f'page{p:03d}.png')
    if not os.path.exists(f):
        doc[p - 1].get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(f)
    return f


def crop_rect(s):
    pg = doc[s['p'] - 1]
    r = pg.search_for(s['find'])[0]
    y0 = max(20, r.y0 - 10)
    y1 = min(pg.rect.height - 24, y0 + s.get('h', 220))
    return pymupdf.Rect(22, y0, pg.rect.width - 46, y1)


def crop_png(s, idx):
    f = os.path.join(IMG, f"crop_{s['p']:03d}_{idx}.png")
    rc = crop_rect(s)
    doc[s['p'] - 1].get_pixmap(matrix=pymupdf.Matrix(3.2, 3.2), clip=rc).save(f)
    return f, rc


def uri(path):
    import base64
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


# ───────────────────────── 슬라이드 HTML
CSS = r"""
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css');
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{font-family:'Pretendard Variable',Pretendard,'Malgun Gothic',sans-serif;background:#f4f6fa;color:#141b2d;word-break:keep-all;
  -webkit-font-smoothing:antialiased;letter-spacing:-.01em;position:relative}
.top{position:absolute;left:72px;right:72px;top:44px;display:flex;align-items:center;gap:16px}
.pill{background:#14264d;color:#fff;font-weight:800;font-size:24px;border-radius:999px;padding:9px 22px;letter-spacing:.02em}
.tag{font-weight:700;font-size:21px;border-radius:999px;padding:7px 18px;color:#fff}
.brand{margin-left:auto;font-size:21px;color:#6b7590;font-weight:600}
.brand b{color:#14264d;font-weight:800}
.stage{position:absolute;left:72px;right:72px;top:118px;bottom:180px;display:flex;flex-direction:column}
.stage>.grid,.stage>.flow,.stage>.chk,.stage>.call{margin-top:auto!important;margin-bottom:auto}
.eyebrow{font-size:26px;font-weight:800;color:#0f7d70;letter-spacing:.02em}
h1{font-size:60px;font-weight:850;line-height:1.2;letter-spacing:-.025em;margin-top:6px}
/* page */
.pg{display:grid;grid-template-columns:auto 1fr;gap:56px;height:100%}
.thumb{position:relative;height:100%;aspect-ratio:595/842;background:#fff;border-radius:14px;box-shadow:0 10px 30px rgba(20,38,77,.14);overflow:hidden;border:1px solid #e1e5ee}
.thumb img{width:100%;height:100%;display:block}
.hl{position:absolute;border:4px solid #e8792c;border-radius:6px;background:rgba(232,121,44,.10);box-shadow:0 0 0 9999px rgba(20,27,45,.32)}
.right{display:flex;flex-direction:column;gap:22px;min-width:0}
.zoom{background:#fff;border:3px solid #e8792c;border-radius:18px;padding:16px;box-shadow:0 14px 34px rgba(232,121,44,.16);overflow:hidden;flex:0 1 auto;min-height:0;display:flex;justify-content:center}
.zoom img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.pts{display:flex;flex-direction:column;gap:12px;flex:none}
.pts li{list-style:none;display:flex;gap:16px;align-items:flex-start;font-size:30px;font-weight:600;line-height:1.38;color:#1f2940}
.pts li::before{content:"";flex:none;width:12px;height:12px;border-radius:3px;background:#0f7d70;margin-top:15px}
/* cards */
.grid{display:grid;gap:22px;margin-top:34px}
.card{background:#fff;border:1px solid #e1e5ee;border-radius:24px;padding:40px 40px;box-shadow:0 8px 24px rgba(20,38,77,.07);display:flex;gap:26px;align-items:flex-start;min-height:190px}
.num{flex:none;width:68px;height:68px;border-radius:16px;background:#14264d;color:#fff;font-weight:850;font-size:32px;display:flex;align-items:center;justify-content:center}
.card b{display:block;font-size:42px;font-weight:800;line-height:1.25;color:#141b2d}
.card span{display:block;font-size:31px;color:#4d5873;line-height:1.45;margin-top:12px;font-weight:500}
/* flow */
.flow{display:grid;gap:18px;margin-top:40px;align-items:stretch}
.step{background:#fff;border:1px solid #e1e5ee;border-top:10px solid #0f7d70;border-radius:22px;padding:38px 32px;position:relative;box-shadow:0 8px 24px rgba(20,38,77,.07);min-height:230px}
.step:nth-child(even){border-top-color:#14264d}
.step b{display:block;font-size:38px;font-weight:800;line-height:1.3}
.step span{display:block;font-size:30px;color:#4d5873;line-height:1.45;margin-top:14px;font-weight:500}
.step i{position:absolute;right:-17px;top:50%;transform:translateY(-50%);width:16px;height:16px;border-top:4px solid #9aa4bb;border-right:4px solid #9aa4bb;rotate:45deg;z-index:2}
.step:last-child i{display:none}
/* check */
.chk{display:flex;flex-direction:column;gap:20px;margin-top:36px;width:100%}
.chk div{background:#fff;border:1px solid #e1e5ee;border-radius:20px;padding:26px 34px;display:flex;gap:26px;align-items:center;font-size:40px;font-weight:650}
.chk div::before{content:"✓";flex:none;width:56px;height:56px;border-radius:14px;background:#0f7d70;color:#fff;font-size:36px;font-weight:900;display:flex;align-items:center;justify-content:center}
/* callout */
.call{margin-top:60px;width:100%;background:#fff;border-radius:28px;padding:60px 70px;border-left:16px solid #e8792c;box-shadow:0 14px 40px rgba(20,38,77,.10)}
.call.law{border-left-color:#14264d}.call.info{border-left-color:#0f7d70}
.call p{font-size:46px;line-height:1.6;font-weight:600;color:#1f2940}
/* cover */
.cover{position:absolute;inset:0;display:grid;grid-template-columns:640px 1fr}
.cover .l{background:linear-gradient(160deg,#14264d 0%,#0d1a36 100%);color:#fff;padding:120px 72px;display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden}
.cover .l::after{content:"";position:absolute;right:-180px;bottom:-180px;width:520px;height:520px;border-radius:50%;border:70px solid rgba(63,192,173,.16)}
.cover .no{font-size:190px;font-weight:900;line-height:1;color:#5fd3c0;letter-spacing:-.04em}
.cover .no.sm{font-size:120px}
.cover .ti{font-size:66px;font-weight:850;margin-top:24px;line-height:1.2}
.cover .su{font-size:30px;opacity:.78;margin-top:18px;line-height:1.4;font-weight:500}
.cover .r{padding:120px 96px 200px;display:flex;flex-direction:column;justify-content:center;gap:40px}
.cover .r .k{font-size:30px;font-weight:800;color:#0f7d70}
.cover .r p{font-size:46px;line-height:1.55;font-weight:700;color:#1f2940}
.cover .r .goal{border-left:8px solid #e8792c;padding-left:30px;font-size:34px;color:#4d5873;font-weight:500;line-height:1.5}
.cover .r .pgs{font-size:30px;color:#6b7590;font-weight:700}
.safe{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(to top,rgba(20,38,77,.05),transparent)}
"""


def top(c, s):
    lab = 'INTRO' if c['no'] == 'INTRO' else ('APPENDIX' if c['no'] == 'APPENDIX' else 'CHAPTER ' + c['no'])
    t = ''
    if s.get('src'):
        n, col = TAG[s['src']]
        t = f'<span class="tag" style="background:{col}">{n}</span>'
    return f'<div class="top"><span class="pill">{lab} · {esc(c["title"])}</span>{t}<span class="brand"><b>국제교류수업 운영 매뉴얼</b> · 실무 영상 강의</span></div>'


def slide(c, s, idx):
    k = s['kind']
    if k == 'cover':
        big = 'IN' if c['no'] == 'INTRO' else ('부록' if c['no'] == 'APPENDIX' else c['no'])
        return f'''<div class="cover"><div class="l"><div class="no{' sm' if len(big) > 2 else ''}">{big}</div><div class="ti">{esc(c['title'])}</div><div class="su">{esc(c['sub'])}</div></div>
        <div class="r"><div class="k">이 장을 따로 구성한 이유</div><p>{esc(c['why'])}</p><div class="goal"><b>교육 목표</b> · {esc(c['goal'])}</div><div class="pgs">매뉴얼 {esc(c['pages'])}</div></div></div>'''
    head = f'<div class="eyebrow">{"매뉴얼 " + esc(s["page"]) if s.get("page") else "핵심 정리"}</div><h1>{esc(s.get("head", s["label"]))}</h1>'
    if k == 'page':
        pf = page_png(s['p'])
        cf, rc = crop_png(s, idx)
        W, H = doc[s['p'] - 1].rect.width, doc[s['p'] - 1].rect.height
        hl = f'left:{rc.x0 / W * 100:.2f}%;top:{rc.y0 / H * 100:.2f}%;width:{rc.width / W * 100:.2f}%;height:{rc.height / H * 100:.2f}%'
        pts = ''.join(f'<li>{esc(x)}</li>' for x in s.get('points', []))
        body = f'''<div class="pg"><div class="thumb"><img src="{uri(pf)}"><div class="hl" style="{hl}"></div></div>
        <div class="right">{head}<div class="zoom"><img src="{uri(cf)}"></div><ul class="pts">{pts}</ul></div></div>'''
    elif k == 'cards':
        it = s['items']
        cols = 3 if len(it) in (3, 5, 6) else (2 if len(it) == 4 else len(it))
        if len(it) == 5:
            cols = 3
        body = head + f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">' + ''.join(
            f'<div class="card"><div class="num">{i + 1}</div><div><b>{esc(a)}</b><span>{esc(b)}</span></div></div>' for i, (a, b) in enumerate(it)) + '</div>'
    elif k == 'flow':
        it = s['items']
        cols = len(it) if len(it) <= 5 else 3
        body = head + f'<div class="flow" style="grid-template-columns:repeat({cols},1fr);column-gap:30px">' + ''.join(
            f'<div class="step"><b>{esc(a)}</b><span>{esc(b)}</span>{"<i></i>" if (i + 1) % cols else ""}</div>' for i, (a, b) in enumerate(it)) + '</div>'
    elif k == 'check':
        body = head + '<div class="chk">' + ''.join(f'<div>{esc(x)}</div>' for x in s['items']) + '</div>'
    elif k == 'callout':
        body = head + f'<div class="call {s.get("tone", "warn")}"><p>{esc(s["body"])}</p></div>'
    return f'{top(c, s)}<div class="stage">{body}</div><div class="safe"></div>'


import slides as SL


def slide_v2(c, s, i):
    if s['kind'] != 'page':
        return SL.make_slide(c, s, i)
    pf = page_png(s['p'])
    cf, rc = crop_png(s, i)
    W, H = doc[s['p'] - 1].rect.width, doc[s['p'] - 1].rect.height
    hl = f'left:{rc.x0 / W * 100:.2f}%;top:{rc.y0 / H * 100:.2f}%;width:{rc.width / W * 100:.2f}%;height:{rc.height / H * 100:.2f}%'
    return SL.make_slide(c, s, i, uri(pf), (uri(cf), hl))


def render_slides(c, page):
    out = []
    for i, s in enumerate(c['scenes']):
        f = os.path.join(IMG, f"{c['id']}_{i:02d}.png")
        page.set_content(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{SL.CSS}</style></head><body>{slide_v2(c, s, i)}</body></html>', wait_until='load')
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(120)
        page.screenshot(path=f)
        out.append(f)
    return out


# ───────────────────────── 오디오/자막
def wav_of(text):
    k = key(text)
    w = os.path.join(WAVC, k + '.wav')
    if not os.path.exists(w):
        subprocess.run([FF, '-v', 'error', '-y', '-i', wav_path(text), '-ac', '1', '-ar', str(SR), '-sample_fmt', 's16', w], check=True)
    with wave.open(w) as f:
        return f.readframes(f.getnframes())


norm = lambda t: re.sub(r'[^0-9A-Za-z가-힣]', '', t)


def token_times(text, words):
    """띄어쓰기 단위 토큰 → (start, end). WordBoundary와 글자 수 누적으로 정렬."""
    toks = text.split()
    if not words:
        return None
    wl = [(a, b, len(norm(t))) for a, b, t in words]
    res, wi, acc_w = [], 0, 0
    total_w = sum(x[2] for x in wl) or 1
    total_t = sum(len(norm(t)) for t in toks) or 1
    cum_t = 0
    for t in toks:
        n = len(norm(t))
        start_frac, end_frac = cum_t / total_t, (cum_t + n) / total_t
        cum_t += n
        # 비율 위치를 단어 경계 시간으로 변환
        def at(frac, end=False):
            target = frac * total_w
            c = 0
            for a, b, l in wl:
                if c + l >= target - 1e-6 and l > 0:
                    r = (target - c) / l if l else 0
                    return a + (b - a) * min(1, max(0, r))
                c += l
            return wl[-1][1]
        res.append((at(start_frac), at(end_frac, True)))
    return toks, res


def char_words(text, dur):
    """Supertonic은 단어 경계 시간을 주지 않으므로 글자 수 비례로 단어 시간을 나눈다(앞뒤 짧은 무음 제외)."""
    toks = text.split()
    n = [len(norm(t)) or 1 for t in toks]
    a0, a1 = min(0.08, dur * .05), max(dur - 0.12, dur * .9)
    tot, c, out = sum(n), 0, []
    for t, k in zip(toks, n):
        out.append([a0 + (a1 - a0) * c / tot, a0 + (a1 - a0) * (c + k) / tot, t])
        c += k
    return out


def slides_from_video(c, old):
    """원본 PDF가 없을 때: 기존 영상에서 장면마다 가운데 프레임을 뽑아 슬라이드로 다시 쓴다(처음 한 번만, 캐시)."""
    ts = [x['t'] for x in old['scenes']] + [old['dur']]
    src = os.path.join(SITE, 'videos', c['id'] + '.mp4')
    out = []
    for i in range(len(c['scenes'])):
        f = os.path.join(IMG, f"{c['id']}_{i:02d}.png")
        if not os.path.exists(f):
            mid = (ts[i] + ts[i + 1]) / 2
            subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{mid:.2f}', '-i', src, '-frames:v', '1', f], check=True)
        out.append(f)
    return out


def chunks(toks, maxc=30):
    """자막 한 줄 단위로 토큰 묶기: 쉼표·마침표 뒤에서 우선 끊고, 최대 maxc 글자."""
    out, cur = [], []
    for i, t in enumerate(toks):
        cur.append(i)
        ln = len(' '.join(toks[j] for j in cur))
        nxt = len(toks[i + 1]) + 1 if i + 1 < len(toks) else 0
        brk = t.endswith((',', '.', '?', '!')) and ln >= 12
        if brk or ln + nxt > maxc:
            out.append(cur)
            cur = []
    if cur:
        if out and len(' '.join(toks[j] for j in cur)) < 7:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def build_audio_and_cues(c):
    pcm = bytearray()
    sil = lambda sec: b'\x00\x00' * int(SR * sec)
    t = 0.0
    scenes, cues = [], []
    for s in c['scenes']:
        st = t
        pcm += sil(LEAD); t += LEAD
        for j, text in enumerate(s['say']):
            a = wav_of(text)
            dur = len(a) / 2 / SR
            tt = token_times(text, char_words(text, dur))
            toks, times = tt if tt else (text.split(), None)
            for grp in chunks(toks):
                if times:
                    a0, a1 = times[grp[0]][0], times[grp[-1]][1]
                else:
                    a0, a1 = dur * grp[0] / len(toks), dur * (grp[-1] + 1) / len(toks)
                cues.append([round(t + a0, 2), round(t + a1, 2), ' '.join(toks[k] for k in grp).rstrip('.')])
            pcm += a; t += dur
            if j < len(s['say']) - 1:
                pcm += sil(GAP); t += GAP
        pcm += sil(TAIL); t += TAIL
        scenes.append(dict(t=round(st, 2), dur=round(t - st, 3)))
    # 큐 다듬기: 겹침 제거, 짧은 공백은 다음 큐 시작까지 연장(최대 0.5초)
    cues.sort(key=lambda q: q[0])
    for i, q in enumerate(cues):
        if i + 1 < len(cues):
            nx = cues[i + 1][0]
            q[1] = round(min(max(q[1], q[0] + 0.8), nx - 0.04) if nx - q[1] > 0.5 else nx - 0.04, 2)
            q[1] = round(min(q[1] + 0.0, nx - 0.04), 2)
        else:
            q[1] = round(q[1] + 0.4, 2)
    wavp = os.path.join(B, 'cache', c['id'] + '.wav')
    with wave.open(wavp, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(bytes(pcm))
    return wavp, scenes, cues, t


def encode(c, slides, scenes, wavp, total):
    lst = os.path.join(B, 'cache', c['id'] + '.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        for p, sc in zip(slides, scenes):
            f.write(f"file '{p}'\nduration {sc['dur']:.3f}\n")
        f.write(f"file '{slides[-1]}'\n")
    out = os.path.join(SITE, 'videos', c['id'] + '.mp4')
    vf = f'fps=30,format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st={max(0, total - 0.6):.2f}:d=0.6'
    subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wavp,
                    '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-tune', 'stillimage', '-crf', '20',
                    '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
    # 포스터(표지 장면)
    subprocess.run([FF, '-v', 'error', '-y', '-i', slides[0], '-vf', 'scale=960:-1', '-q:v', '4', os.path.join(SITE, 'posters', c['id'] + '.jpg')], check=True)
    return out


def main(ids):
    srcs = json.load(open(os.path.join(B, 'srcs.json'), encoding='utf-8'))
    dpath = os.path.join(SITE, 'data.json')
    data = {d['id']: d for d in json.load(open(dpath, encoding='utf-8'))} if os.path.exists(dpath) else {}
    if not data and os.path.exists(os.path.join(SITE, 'data.js')):
        js = open(os.path.join(SITE, 'data.js'), encoding='utf-8').read()
        data = {d['id']: d for d in json.loads(js[js.index('['):js.rindex(']') + 1])}
    todo = [c for c in CH if not ids or c['id'] in ids]
    use_pdf = os.path.exists(PDF) and pymupdf is not None
    if use_pdf:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        br = pw.chromium.launch(channel='msedge')
        page = br.new_page(viewport={'width': 1920, 'height': 1080})
        all_slides = {c['id']: render_slides(c, page) for c in todo}
        br.close(); pw.stop()
    else:
        # 원본 PDF가 없으면 영상을 덮어쓰기 전에 기존 영상에서 장면 화면을 모두 뽑아 둔다
        print('PDF 없음 → 기존 영상의 장면 화면을 재사용', flush=True)
        all_slides = {c['id']: slides_from_video(c, data[c['id']]) for c in todo}
    if True:
        for c in todo:
            slides = all_slides[c['id']]
            if os.environ.get('SLIDES_ONLY'):
                print('slides', c['id'], flush=True)
                continue
            wavp, sc, cues, total = build_audio_and_cues(c)
            encode(c, slides, sc, wavp, total)
            if os.path.exists(os.path.join(B, 'assets', 'bgm.mp3')):
                import bgm
                bgm.mix(c['id'])   # 배경음을 작게 섞기
            data[c['id']] = dict(
                id=c['id'], no=c['no'], title=c['title'], sub=c['sub'], goal=c['goal'], why=c['why'], pages=c['pages'],
                practice=c['practice'], check=c['check'], srcs=srcs.get(c['id'], []), dur=round(total, 2),
                file=f"videos/{c['id']}.mp4", poster=f"posters/{c['id']}.jpg",
                scenes=[dict(t=x['t'], label=s['label'], page=(s.get('page') or ''), act=s.get('act', ''), src=s.get('src', ''))
                        for x, s in zip(sc, c['scenes'])],
                cues=cues)
            print(f"{c['id']}: {total / 60:.1f} min, {len(c['scenes'])} scenes, {len(cues)} cues", flush=True)
    ordered = [data[c['id']] for c in CH if c['id'] in data]
    json.dump(ordered, open(dpath, 'w', encoding='utf-8'), ensure_ascii=False)
    with open(os.path.join(SITE, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('window.LECTURE_DATA=' + json.dumps(ordered, ensure_ascii=False) + ';\n')


if __name__ == '__main__':
    main(sys.argv[1:])
