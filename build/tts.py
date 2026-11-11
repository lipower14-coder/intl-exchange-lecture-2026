"""문장별 SunHi 음성 + 단어 경계 타이밍 생성 (캐시: build/cache/tts/<hash>.mp3/.json)."""
import asyncio, hashlib, json, os, sys
import edge_tts

sys.path.insert(0, os.path.dirname(__file__))
from content import CH

VOICE = 'ko-KR-SunHiNeural'
RATE = '-4%'      # 띄어쓰기 단위가 또렷하게 들리도록 약간 느리게
OUT = os.path.join(os.path.dirname(__file__), 'cache', 'tts')
os.makedirs(OUT, exist_ok=True)


def key(text):
    return hashlib.sha1(f'{VOICE}|{RATE}|{text}'.encode()).hexdigest()[:16]


async def one(text, sem):
    k = key(text)
    mp3, js = os.path.join(OUT, k + '.mp3'), os.path.join(OUT, k + '.json')
    if os.path.exists(mp3) and os.path.exists(js):
        return
    async with sem:
        for attempt in range(4):
            try:
                com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary='WordBoundary')
                words, audio = [], bytearray()
                async for ch in com.stream():
                    if ch['type'] == 'audio':
                        audio += ch['data']
                    elif ch['type'] == 'WordBoundary':
                        words.append([ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7, ch['text']])
                open(mp3, 'wb').write(audio)
                json.dump(words, open(js, 'w', encoding='utf-8'), ensure_ascii=False)
                return
            except Exception as e:
                print('retry', attempt, text[:20], e)
                await asyncio.sleep(2 + attempt * 3)
        raise RuntimeError('TTS failed: ' + text)


async def main():
    sem = asyncio.Semaphore(6)
    texts = [t for c in CH for s in c['scenes'] for t in s['say']]
    await asyncio.gather(*(one(t, sem) for t in texts))
    print('tts ok', len(texts))

if __name__ == '__main__':
    asyncio.run(main())
