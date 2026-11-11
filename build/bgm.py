"""내레이션 아래에 배경음을 작게 깔아 site/videos/<id>.mp4 의 오디오를 다시 만든다(영상 스트림은 그대로 복사).

사용: python build/bgm.py [chapter_id ...]   (인자 없으면 전체)
내레이션 원본은 build/cache/<id>.wav 를 쓰므로 여러 번 실행해도 배경음이 겹치지 않는다.
"""
import os, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'build')
FF = r'C:\Users\Ahn\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe'
BGM = os.path.join(B, 'assets', 'bgm.mp3')
BGM_VOL = 0.09      # 약 -21dB: 내레이션보다 약 19dB 작게
FADE_IN, FADE_OUT = 2.0, 3.0


def mix(cid):
    nar = os.path.join(B, 'cache', cid + '.wav')
    mp4 = os.path.join(ROOT, 'site', 'videos', cid + '.mp4')
    with wave.open(nar) as w:
        dur = w.getnframes() / w.getframerate()
    tmp = mp4 + '.tmp.mp4'
    af = (f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo[n];'
          f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={BGM_VOL},'
          f'afade=t=in:st=0:d={FADE_IN},afade=t=out:st={max(0, dur - FADE_OUT):.2f}:d={FADE_OUT}[b];'
          f'[n][b]amix=inputs=2:duration=first:normalize=0[a]')
    subprocess.run([FF, '-v', 'error', '-y', '-i', nar, '-stream_loop', '-1', '-i', BGM, '-i', mp4,
                    '-filter_complex', af, '-map', '2:v', '-map', '[a]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '160k', '-t', f'{dur:.3f}', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, mp4)
    print('bgm', cid, f'{dur / 60:.1f} min', flush=True)


if __name__ == '__main__':
    ids = sys.argv[1:] or [f[:-4] for f in sorted(os.listdir(os.path.join(ROOT, 'site', 'videos'))) if f.endswith('.mp4')]
    for i in ids:
        mix(i)
