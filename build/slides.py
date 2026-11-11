"""16:9 영상 프레임 디자인 — design-diversity 'korea-policy-navy' 스펙 기반.
상단 12% 네이비 헤더 밴드, 플랫(그라데이션·그림자 없음), 반경 2~4px, Pretendard,
번호 칩, 좌측 보더 정보/주의 상자, 헤어라인 #C5D2E3, 강조색은 블루 하나.
하단 170px은 자막 영역으로 비워 둔다.
"""
import html
esc = html.escape

NAVY, BLUE, TINT, INK, SUB, HAIR = '#0B2C5C', '#1B66C9', '#E8F1FB', '#1A1A1A', '#5C6470', '#C5D2E3'
RED, GREEN, AMBER = '#E03B3B', '#1F9D57', '#B4690E'
TAG = {'law': ('법령·규정', NAVY), 'gov': ('교육청 지침·안내', BLUE), 'case': ('사례·실무 권장', AMBER)}

CSS = r"""
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css');
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{font-family:'Pretendard Variable',Pretendard,sans-serif;background:#fff;color:#1A1A1A;word-break:keep-all;-webkit-font-smoothing:antialiased;letter-spacing:-.015em;position:relative}
.band{position:absolute;left:0;right:0;top:0;height:130px;background:#0B2C5C;color:#fff;display:flex;align-items:center;gap:28px;padding:0 84px}
.chip{flex:none;min-width:74px;height:74px;padding:0 14px;border-radius:4px;background:#fff;color:#0B2C5C;font-weight:850;font-size:34px;display:flex;align-items:center;justify-content:center;letter-spacing:-.02em}
.bt{display:flex;flex-direction:column;gap:4px;min-width:0}
.bt small{font-size:23px;font-weight:600;color:rgba(255,255,255,.72)}
.bt b{font-size:44px;font-weight:800;line-height:1.15;letter-spacing:-.025em}
.src{margin-left:auto;flex:none;display:flex;align-items:center;gap:12px;background:#fff;color:#1A1A1A;border-radius:4px;padding:10px 18px;font-size:22px;font-weight:700}
.src i{width:14px;height:14px;border-radius:2px;display:block}
.body{position:absolute;left:84px;right:84px;top:178px;bottom:176px;display:flex;flex-direction:column}
.mid{margin:auto 0;width:100%}
.foot{position:absolute;left:84px;right:84px;bottom:28px;display:flex;justify-content:space-between;font-size:18px;color:#8A93A3;font-weight:600}
/* page */
.pg{display:grid;grid-template-columns:auto 1fr;gap:64px;height:100%}
.thumb{position:relative;height:100%;aspect-ratio:595/842;border:1px solid #C5D2E3;border-radius:2px;overflow:hidden;background:#fff}
.thumb img{width:100%;height:100%;display:block}
.hl{position:absolute;border:4px solid #1B66C9;background:rgba(27,102,201,.08);box-shadow:0 0 0 9999px rgba(11,44,92,.28)}
.right{display:flex;flex-direction:column;gap:30px;min-width:0;min-height:0}
.zoom{border:1px solid #C5D2E3;border-top:6px solid #1B66C9;border-radius:2px;padding:18px;flex:0 1 auto;min-height:0;display:flex;justify-content:center;background:#fff}
.zoom img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.pts{list-style:none;display:flex;flex-direction:column;flex:none;border-top:1px solid #C5D2E3}
.pts li{display:flex;gap:18px;align-items:baseline;font-size:31px;font-weight:600;line-height:1.4;padding:13px 0;border-bottom:1px solid #C5D2E3}
.pts li::before{content:"";flex:none;width:12px;height:12px;background:#1B66C9;transform:translateY(-4px)}
/* rows (항목 목록) */
.rows{display:grid;column-gap:64px;border-top:2px solid #0B2C5C}
.row{display:flex;gap:28px;align-items:flex-start;padding:30px 4px;border-bottom:1px solid #C5D2E3}
.n{font-style:normal;flex:none;width:62px;height:62px;border-radius:4px;background:#0B2C5C;color:#fff;font-weight:800;font-size:30px;display:flex;align-items:center;justify-content:center}
.row b{display:block;font-size:40px;font-weight:800;line-height:1.25}
.row span{display:block;font-size:30px;color:#5C6470;line-height:1.45;margin-top:8px;font-weight:500}
.rows.dense .row{padding:24px 4px}.rows.dense .row b{font-size:36px}.rows.dense .row span{font-size:28px}
/* flow (타임라인) */
.flow{display:grid;column-gap:0;row-gap:56px}
.st{position:relative;padding:0 28px 0 0}
.st .ln{position:relative;height:62px;display:flex;align-items:center;margin-bottom:26px}
.st .ln::after{content:"";position:absolute;left:62px;right:0;top:50%;height:3px;background:#C5D2E3}
.st:last-child .ln::after,.st.end .ln::after{display:none}
.st .n{background:#1B66C9}
.st b{display:block;font-size:36px;font-weight:800;line-height:1.3;padding-right:12px}
.st span{display:block;font-size:28px;color:#5C6470;line-height:1.45;margin-top:12px;font-weight:500;padding-right:16px}
/* check */
.chk{border-top:2px solid #0B2C5C}
.chk div{display:flex;gap:28px;align-items:center;font-size:40px;font-weight:650;padding:26px 4px;border-bottom:1px solid #C5D2E3}
.chk div::before{content:"✓";flex:none;width:58px;height:58px;border-radius:4px;background:#1F9D57;color:#fff;font-size:34px;font-weight:900;display:flex;align-items:center;justify-content:center}
/* callout */
.call{background:#E8F1FB;border-left:8px solid #1B66C9;padding:56px 64px}
.call.warn{background:#FDECEC;border-left-color:#E03B3B}
.call.law{background:#EEF1F6;border-left-color:#0B2C5C}
.call .k{font-size:28px;font-weight:800;color:#1B66C9;margin-bottom:18px}
.call.warn .k{color:#C62828}.call.law .k{color:#0B2C5C}
.call p{font-size:46px;line-height:1.6;font-weight:600}
/* cover */
.cv{position:absolute;inset:0;display:grid;grid-template-columns:700px 1fr}
.cv .l{background:#0B2C5C;color:#fff;padding:0 84px;display:flex;flex-direction:column;justify-content:center}
.cv .no{font-size:200px;font-weight:900;line-height:.9;letter-spacing:-.05em;color:#fff}
.cv .no.sm{font-size:132px}
.cv .bar{width:96px;height:8px;background:#1B66C9;margin:44px 0 36px}
.cv .ti{font-size:70px;font-weight:850;line-height:1.15;letter-spacing:-.03em}
.cv .su{font-size:32px;color:rgba(255,255,255,.74);margin-top:20px;line-height:1.45;font-weight:500}
.cv .r{padding:0 100px 120px 100px;display:flex;flex-direction:column;justify-content:center;gap:44px}
.cv .r .k{font-size:28px;font-weight:800;color:#1B66C9}
.cv .r p{font-size:46px;line-height:1.55;font-weight:700;margin-top:-26px}
.sum{border-top:3px solid #0B2C5C;border-bottom:3px solid #0B2C5C;padding:26px 4px;display:grid;grid-template-columns:150px 1fr;row-gap:16px;font-size:30px;line-height:1.5}
.sum dt{font-weight:800;color:#0B2C5C}.sum dd{color:#5C6470;font-weight:500}
.cv .brand{position:absolute;left:84px;bottom:64px;font-size:22px;color:rgba(255,255,255,.6);font-weight:600}
"""


def chlabel(c):
    return 'IN' if c['no'] == 'INTRO' else ('부록' if c['no'] == 'APPENDIX' else c['no'])


def band(c, s, title):
    t = ''
    if s.get('src'):
        n, col = TAG[s['src']]
        t = f'<span class="src"><i style="background:{col}"></i>{n}</span>'
    sub = esc(c['title']) + (f' · 매뉴얼 {esc(s["page"])}' if s.get('page') else '')
    return f'<div class="band"><span class="chip">{chlabel(c)}</span><span class="bt"><small>{sub}</small><b>{esc(title)}</b></span>{t}</div>'


def foot(c, idx):
    return f'<div class="foot"><span>국제교류수업 운영 매뉴얼 · 실무 영상 강의</span><span>{idx + 1:02d} / {len(c["scenes"]):02d}</span></div>'


def make_slide(c, s, idx, page_uri=None, crop=None):
    """crop: (crop_uri, hl_style) for page kind."""
    k = s['kind']
    if k == 'cover':
        big = chlabel(c)
        return f'''<div class="cv"><div class="l"><div class="no{' sm' if len(big) > 2 else ''}">{big}</div><div class="bar"></div>
        <div class="ti">{esc(c['title'])}</div><div class="su">{esc(c['sub'])}</div><div class="brand">국제교류수업 운영 매뉴얼 · 2026</div></div>
        <div class="r"><div class="k">이 장을 따로 구성한 이유</div><p>{esc(c['why'])}</p>
        <dl class="sum"><dt>교육 목표</dt><dd>{esc(c['goal'])}</dd><dt>매뉴얼</dt><dd>{esc(c['pages'])}</dd></dl></div></div>'''
    title = s.get('head', s['label'])
    if k == 'page':
        cu, hl = crop
        pts = ''.join(f'<li>{esc(x)}</li>' for x in s.get('points', []))
        body = f'''<div class="pg"><div class="thumb"><img src="{page_uri}"><div class="hl" style="{hl}"></div></div>
        <div class="right"><div class="zoom"><img src="{cu}"></div><ul class="pts">{pts}</ul></div></div>'''
    elif k == 'cards':
        it = s['items']
        cols = 1 if len(it) <= 3 else 2
        dense = ' dense' if len(it) >= 5 else ''
        body = f'<div class="mid"><div class="rows{dense}" style="grid-template-columns:repeat({cols},1fr)">' + ''.join(
            f'<div class="row"><i class="n">{i + 1}</i><div><b>{esc(a)}</b><span>{esc(b)}</span></div></div>' for i, (a, b) in enumerate(it)) + '</div></div>'
    elif k == 'flow':
        it = s['items']
        cols = len(it) if len(it) <= 5 else 3
        body = f'<div class="mid"><div class="flow" style="grid-template-columns:repeat({cols},1fr)">' + ''.join(
            f'<div class="st{" end" if (i + 1) % cols == 0 else ""}"><div class="ln"><i class="n">{i + 1}</i></div><b>{esc(a.lstrip("①②③④⑤⑥ "))}</b><span>{esc(b)}</span></div>'
            for i, (a, b) in enumerate(it)) + '</div></div>'
    elif k == 'check':
        body = '<div class="mid"><div class="chk">' + ''.join(f'<div>{esc(x)}</div>' for x in s['items']) + '</div></div>'
    elif k == 'callout':
        tone = s.get('tone', 'warn')
        lab = {'warn': '주의', 'info': '참고 사례', 'law': '원칙'}[tone]
        body = f'<div class="mid"><div class="call {tone}"><div class="k">{lab}</div><p>{esc(s["body"])}</p></div></div>'
    return f'{band(c, s, title)}<div class="body">{body}</div>{foot(c, idx)}'
