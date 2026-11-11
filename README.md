# 국제교류 실무 영상 강의실 (2026.11.10 최종수정본 기준)

`국제교류 업무매뉴얼_최종수정본(2026.11.10).pdf`를 바탕으로 만든 챕터별 내레이션 영상 9편과 강의 사이트입니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `site/` | 배포할 사이트 전체 (`index.html`, `data.js`, `videos/*.mp4`, `posters/*.jpg`) |
| `build/content.py` | **내레이션 대본과 장면 구성** — 문장을 고치려면 여기만 수정 |
| `build/tts.py` | SunHi(ko-KR-SunHiNeural) 음성 생성, 단어 경계 타이밍 저장 |
| `build/slides.py` | 영상 프레임(슬라이드) 디자인 |
| `build/render.py` | 슬라이드 렌더 → 음성 조립 → MP4·자막 큐·`site/data.js` 생성 |
| `build/serve.py` | 로컬 미리보기 서버(영상 탐색 지원) |

## 대본을 고친 뒤 다시 만들기

```
python build/tts.py              # 바뀐 문장만 새로 합성(캐시 사용)
python build/render.py ch03      # 특정 챕터만 다시 렌더 (인자 없으면 전체)
```

## 로컬에서 보기

```
python build/serve.py 5178
```
브라우저에서 http://localhost:5178 을 엽니다.

## Vercel에 배포

`site/` 폴더를 그대로 정적 사이트로 배포하면 됩니다 (기존 `intl-exchange-lecture` 프로젝트에 덮어쓰려면 해당 프로젝트에 연결 후 배포).

```
npx vercel deploy site --prod
```

## 자막

- 영상에 자막을 굽지 않고, 사이트가 자체 자막 레이어로 표시합니다(한 번에 한 묶음, 줄마다 독립 배경 → 겹침 없음).
- 자막 크기: 작게 / 보통 / 크게 / 아주 크게, 플레이어 폭에 비례.
- 전체 화면은 플레이어 오른쪽 위 버튼·`F` 키·더블클릭 — 자막이 함께 표시됩니다.
