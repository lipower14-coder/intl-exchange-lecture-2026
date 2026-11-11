"""문장별 내레이션 음성 생성 — Supertonic 3(Supertone, 로컬 TTS) 남성 M2 목소리.

캐시: build/cache/tts/<hash>.wav (문장·목소리·설정이 같으면 다시 만들지 않음)
사용: python build/tts.py

- 자막에는 원래 문장(예: '1장')을 그대로 쓰고, 음성 합성에만 읽기용 문장(예: '일장')을 넣는다.
- 모델 라이선스: OpenRAIL-M (기계 생성 음성임을 밝혀야 함 → 사이트에 'AI 음성' 표기)
"""
import hashlib, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))

VOICE = 'M2'
STEPS = 12        # 품질 5~12 (높을수록 좋음)
SPEED = 1.0
OUT = os.path.join(os.path.dirname(__file__), 'cache', 'tts')
os.makedirs(OUT, exist_ok=True)

DIG = '영일이삼사오육칠팔구'


def sino(n):
    """한자어 수사: 1→일, 12→십이, 20→이십"""
    if n < 10:
        return DIG[n]
    if n < 100:
        return ('' if n // 10 == 1 else DIG[n // 10]) + '십' + (DIG[n % 10] if n % 10 else '')
    return str(n)


def speak(text):
    """읽기용 문장: '1장'·'2장의' → '일장'·'이장의' (서수로 읽게)."""
    return re.sub(r'(\d+)(?=\s*장)', lambda m: sino(int(m.group(1))), text)


def key(text):
    return hashlib.sha1(f'supertonic3|{VOICE}|{STEPS}|{SPEED}|{speak(text)}'.encode()).hexdigest()[:16]


def wav_path(text):
    return os.path.join(OUT, key(text) + '.wav')


def main():
    from content import CH
    from supertonic import TTS
    texts = list(dict.fromkeys(t for c in CH for s in c['scenes'] for t in s['say']))
    todo = [t for t in texts if not os.path.exists(wav_path(t))]
    print(f'sentences {len(texts)}, to synthesize {len(todo)}', flush=True)
    if not todo:
        return
    tts = TTS(auto_download=True)
    style = tts.get_voice_style(voice_name=VOICE)
    for n, t in enumerate(todo, 1):
        wav, _ = tts.synthesize(speak(t), voice_style=style, lang='ko', speed=SPEED, total_steps=STEPS, verbose=False)
        tmp = wav_path(t) + '.tmp.wav'
        tts.save_audio(wav, tmp)
        os.replace(tmp, wav_path(t))
        if n % 20 == 0 or n == len(todo):
            print(f'  {n}/{len(todo)}', flush=True)
    print('tts ok', len(texts))


if __name__ == '__main__':
    main()
