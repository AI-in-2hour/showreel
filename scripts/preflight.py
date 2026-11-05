#!/usr/bin/env python3
"""제작 전 환경 점검 (Antigravity / Gemini 에디션).
무엇이 있고 무엇이 없는지, 없으면 어떻게 설치하는지(Windows · macOS · Linux) 한 번에 보여 준다.

사용법: python preflight.py [--voice ibCGc01503OQd2R6i1n1] [--json]
결과의 '쓸 수 있는 경로'를 콘셉트에 반영한다(예: 나레이션 불가 → 음악·화면만으로 전하는 콘셉트, Music 불가 → 합성 음악).
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
IS_WIN = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"


def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 127, str(e)


def find_chrome():
    env_path = os.environ.get("REEL_CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ]
    for c in candidates:
        try:
            if c.exists():
                return str(c)
        except OSError:
            pass
    for b in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        w = shutil.which(b)
        if w:
            return w
    return None


def find_pretendard():
    dirs = [
        HERE.parent / "assets" / "fonts_cache",
        Path.home() / "Library/Fonts",
        Path("/Library/Fonts"),
        Path.home() / ".local/share/fonts",
        Path("/usr/share/fonts"),
        Path("C:/Windows/Fonts"),
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
    ]
    found = []
    for d in dirs:
        try:
            if d.exists():
                found.extend(d.glob("Pretendard*"))
        except OSError:
            pass
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="ibCGc01503OQd2R6i1n1")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows, fix, caps = [], [], {}

    def row(name, ok, info, how=None):
        rows.append(("✓" if ok else "✗", name, info))
        if not ok and how:
            fix.append(f"{name}: {how}")

    # 필수 도구
    code, out = run(["node", "--version"])
    node_how = "winget install OpenJS.NodeJS.LTS (또는 https://nodejs.org)" if IS_WIN else "brew install node (또는 https://nodejs.org)"
    row("node", code == 0, out.splitlines()[0] if code == 0 and out else "없음", node_how)

    code, out = run(["ffmpeg", "-hide_banner", "-filters"])
    has_ff = code == 0
    flt = {f: (f" {f} " in out) for f in ("loudnorm", "ebur128", "tmix", "freezedetect", "signalstats")}
    ff_how = "winget install Gyan.FFmpeg" if IS_WIN else "brew install ffmpeg"
    row("ffmpeg", has_ff and all(flt.values()), "필터 " + ", ".join(k for k, v in flt.items() if v) if has_ff else "없음", ff_how)

    chrome = find_chrome()
    row("Chrome/Chromium", bool(chrome), f"사용 가능 ({Path(chrome).name})" if chrome else "없음",
        "Google Chrome 설치 또는 REEL_CHROME_PATH=<실행 파일 경로>")

    pw = (HERE / "node_modules" / "playwright-core").exists()
    row("playwright-core", pw, "설치됨" if pw else "없음 (new_project.py 가 자동 설치)",
        f"cd \"{HERE}\" && npm install")

    try:
        import numpy  # noqa
        import PIL  # noqa
        row("python numpy·Pillow", True, f"python {sys.version.split()[0]}")
    except ImportError as e:
        row("python numpy·Pillow", False, str(e), f'"{sys.executable}" -m pip install numpy pillow')

    fonts = find_pretendard()
    row("한글 폰트(Pretendard)", True, "로컬 있음" if fonts else "없음 → new_project.py 가 자동 다운로드")

    if IS_MAC:
        swift = bool(shutil.which("swiftc"))
        row("누끼(swiftc/rembg)", swift, "macOS Vision 사용 가능" if swift else "불가 — 인물 누끼 없이 진행", "xcode-select --install")
    else:
        has_rembg = bool(shutil.which("rembg"))
        row("누끼(선택 기능)", True, "rembg 사용 가능" if has_rembg else "생략 (필요 시 pip install rembg, 기본 모션그래픽은 불필요)")

    # 이미지 생성 (Antigravity 내장 image-generator 서브에이전트 기본 지원)
    row("이미지 생성(Gemini)", True, "Antigravity 내장 image-generator 서브에이전트 사용 가능")
    caps["image_gen"] = True

    # ElevenLabs
    sys.path.insert(0, str(HERE))
    import eleven
    key = eleven.api_key()
    if not key:
        row("ElevenLabs API 키(선택)", True, "없음 → 나레이션 없이 음악(synth_music.py)·타이포 쇼릴로 진행 가능")
        caps.update(narration=False, music_api=False)
    else:
        try:
            json.loads(eleven.request("GET", "/v1/models", retries=1))
            row("ElevenLabs API 키", True, "유효")
            try:
                v = json.loads(eleven.request("GET", f"/v1/voices/{a.voice}", retries=1))
                row("점검 보이스(--voice)", True, v.get("name", a.voice)[:50])
                caps["narration"] = True
            except eleven.ElevenError as e:
                row("점검 보이스(--voice)", False, str(e)[:80], "Free 플랜이면 라이브러리 보이스가 막힌다 → 유료 플랜 또는 eleven.py voices 로 다른 보이스")
                caps["narration"] = "other_voice"
            try:
                s = json.loads(eleven.request("GET", "/v1/user/subscription", retries=1))
                left = (s.get("character_limit") or 0) - (s.get("character_count") or 0)
                row("요금제·크레딧", True, f"{s.get('tier')} · 남은 크레딧 {left:,}")
                caps["music_api"] = s.get("tier") not in (None, "free")
            except eleven.ElevenError:
                row("요금제·크레딧", True, "확인 불가(키에 User Read 권한 없음) — Music 은 첫 생성 시도로 판단")
                caps["music_api"] = None
        except eleven.ElevenError as e:
            row("ElevenLabs API 키", False, str(e).splitlines()[0][:80], "키 권한·유효성 확인 (나레이션 없이 진행 가능)")
            caps.update(narration=False, music_api=False)

    if a.json:
        print(json.dumps({"rows": rows, "fix": fix, "caps": caps}, ensure_ascii=False, indent=1))
        return
    for ok, name, info in rows:
        print(f"{ok} {name:24s} {info}")
    render_ok = all(r[0] == "✓" for r in rows[:3]) and rows[4][0] == "✓"
    print("\n쓸 수 있는 경로:")
    print(f"  렌더링        {'가능' if render_ok else '필수 도구 설치 필요'}")
    print("  이미지 생성    Antigravity 내장 image-generator 서브에이전트 (또는 코드 그래픽·사용자 사진)")
    n = caps.get("narration")
    print(f"  나레이션      {'ElevenLabs (점검 보이스 사용 가능)' if n is True else '다른 보이스 필요' if n == 'other_voice' else '키 없음 → 음악·타이포그래피 중심 쇼릴로 진행 (권장)'}")
    m = caps.get("music_api")
    print(f"  음악          {'ElevenLabs Music' if m else 'NumPy 자체 합성 음악 (synth_music.py — API 키 불필요)' if m is False else 'ElevenLabs Music 시도 → 402 면 synth_music.py 합성 음악'}")
    if fix:
        print("\n고칠 것:")
        for f in fix:
            print("  - " + f)


if __name__ == "__main__":
    main()
