# 국제교류 실무 영상 강의실 (2026.11.10 최종수정본 기준)

`국제교류 업무매뉴얼_최종수정본(2026.11.10).pdf`를 바탕으로 만든 챕터별 내레이션 영상 9편과 강의 사이트입니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `site/` | 배포할 사이트 전체 (`index.html` 시작 페이지(3D 지구본), `lecture.html` 강의실, `data.js`, `videos/*.mp4`, `posters/*.jpg`, `assets/hero.jpg` 힉스필드 생성 일러스트) |
| `build/content.py` | **내레이션 대본과 장면 구성** — 문장을 고치려면 여기만 수정 |
| `build/tts.py` | Supertonic 3 남성 M2 음성 생성(로컬 TTS). `1장`은 `일장`처럼 서수로 읽도록 변환 |
| `build/slides.py` | 영상 프레임(슬라이드) 디자인 |
| `build/render.py` | 슬라이드 렌더 → 음성 조립 → MP4·자막 큐·`site/data.js` 생성 (원본 PDF가 없으면 기존 영상의 장면 화면을 재사용) |
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

- 사이트 주소: https://intl-exchange-lecture-2026.vercel.app
- Vercel 프로젝트 `intl-exchange-lecture-2026`이 이 GitHub 저장소에 연결되어 있고 Root Directory는 `site`입니다.
- `main` 브랜치에 푸시하면 자동으로 다시 배포됩니다.

```
git add -A
git commit -m "변경 내용"
git push
```

## 자막

- 영상에 자막을 굽지 않고, 사이트가 자체 자막 레이어로 표시합니다(한 번에 한 묶음, 줄마다 독립 배경 → 겹침 없음).
- 자막 크기: 작게 / 보통 / 크게 / 아주 크게, 플레이어 폭에 비례.
- 전체 화면은 플레이어 오른쪽 위 버튼·`F` 키·더블클릭 — 자막이 함께 표시됩니다.
