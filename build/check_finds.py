import sys, pymupdf
sys.path.insert(0, 'build')
from content import CH
d = pymupdf.open(r'국제교류 업무매뉴얼_최종수정본(2026.11.10).pdf')
n = 0
for c in CH:
    for s in c['scenes']:
        n += 1
        if s['kind'] == 'page':
            r = d[s['p'] - 1].search_for(s['find'])
            print(('OK ' if r else 'MISS'), c['id'], s['p'], s['find'], [round(x.y0) for x in r][:3])
print('chapters', len(CH), 'scenes', n, 'sentences', sum(len(s['say']) for c in CH for s in c['scenes']),
      'chars', sum(len(x) for c in CH for s in c['scenes'] for x in s['say']))
