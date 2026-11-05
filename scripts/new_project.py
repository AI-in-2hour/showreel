#!/usr/bin/env python3
"""쇼릴 프로젝트 폴더를 만든다: 폴더 구조 + 엔진 템플릿 + 한글 폰트 + 렌더러 의존성.

사용법:
  python new_project.py <프로젝트 폴더> [--ratio 16:9|9:16|1:1] [--duration 60] [--fps 30] [--force-engine]
                        [--fonts "Hahmlet:wght@300;900" --fonts "Gowun Batang:wght@400;700"]

- 이미 있는 폴더에 다시 실행해도 안전하다: scenes.js·index.html 은 덮어쓰지 않고(엔진 engine.js·fx.js 만 최신으로),
  폰트는 없는 것만 받는다. --force-engine 은 index.html·scenes.js 까지 처음 상태로 되돌린다.
- scenes.js 는 REEL.config 만 들어 있는 빈 파일로 만든다. 엔진 예시 장면은 reel/_example_scenes.js 로 복사한다(불러오지 않는다).
  예시 화면이 새 영상의 출발점이 되지 않게 하려는 것이다.
- 폰트는 로컬 또는 스킬 캐시(assets/fonts_cache)에 있으면 복사(파일명은 ASCII 로), 없으면 내려받는다(Pretendard·Google Fonts, 모두 SIL OFL).
  실제로 확보된 폰트만 reel/fonts/fonts.css 에 @font-face 로 적는다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
ENGINE = SKILL / "assets" / "engine"
FONT_CACHE = SKILL / "assets" / "fonts_cache"
SCRIPTS = SKILL / "scripts"
SCENES_STUB = """/* 장면 코드. concept.md 의 구간별 아트 디렉션에서 새로 쓴다.
 * API 사용 예시는 _example_scenes.js(불러오지 않는다)와 references/engine.md 에 있다. 예시 화면을 출발점으로 삼지 않는다.
 * 구간이 많으면 scenes_s01.js … 로 나누고 index.html 에 script 태그를 더한다. */
const { ease, prog, win, kf, spring, clamp, lerp, rand, noise, split, stagger, css, h, s, cue } = REEL;
REEL.config({ duration: %(dur)s, fps: %(fps)s, width: %(w)s, height: %(h)s, audio: null });   // 미리보기에서 소리를 들으려면 audio: '../audio/mix.wav'
"""

LOCAL_DIRS = [
    FONT_CACHE,
    Path.home() / "Library/Fonts",
    Path("/Library/Fonts"),
    Path.home() / ".local/share/fonts",
    Path("/usr/share/fonts"),
    Path("C:/Windows/Fonts"),
    Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
]
PRETENDARD_URL = "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2"
GOOGLE_CSS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700;900&family=Black+Han+Sans"
              "&family=Anton&family=JetBrains+Mono:wght@400;500;700&display=block")
OPTIONAL_LOCAL = [
    (r"Paperlogy-(\d)\w*\.ttf", "Paperlogy", {4, 6, 7, 8, 9}),
    (r"에이투지체-(\d)\w*\.ttf", "A2Z", {4, 5, 7, 9}),
]


def find_local(name):
    for d in LOCAL_DIRS:
        try:
            if not d.exists():
                continue
            for p in d.rglob(name):
                return p
        except OSError:
            continue
    return None


def curl(url, out=None):
    curl_bin = shutil.which("curl.exe") or shutil.which("curl") or "curl"
    cmd = [curl_bin, "-sfL", "--max-time", "90", url]
    if out:
        cmd += ["-o", str(out)]
    try:
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0 and (out is None or (Path(out).exists() and Path(out).stat().st_size > 0)):
            return r.stdout if not out else out
    except Exception:
        pass
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if out:
            Path(out).write_bytes(data)
            return out
        return data
    except Exception:
        return None


def is_font(p):
    try:
        head = Path(p).read_bytes()[:4]
    except OSError:
        return False
    return head in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"wOF2", b"wOFF", b"ttcf")


def google_faces(css, fdir, faces, notes):
    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    for block in re.findall(r"@font-face\s*{(.*?)}", css, re.S):
        fam_m = re.search(r"font-family:\s*'([^']+)'", block)
        wt_m = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"url\((https://[^)]+)\)", block)
        if not (fam_m and wt_m and url_m):
            continue
        fam, wt, url = fam_m.group(1), wt_m.group(1), url_m.group(1)
        fname = f"{fam.replace(' ', '')}-{wt}.ttf"
        dest = fdir / fname
        cached = FONT_CACHE / fname
        if not (dest.exists() and is_font(dest)):
            if cached.exists() and is_font(cached):
                shutil.copy2(cached, dest)
            elif curl(url, dest) and is_font(dest):
                try:
                    shutil.copy2(dest, cached)
                except OSError:
                    pass
            else:
                dest.unlink(missing_ok=True)
                notes.append(f"{fam} {wt}: 내려받기 실패")
                continue
        if (fam, wt, fname) not in faces:
            faces.append((fam, wt, fname))


def setup_fonts(fdir: Path, extra=()):
    fdir.mkdir(parents=True, exist_ok=True)
    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    faces = []  # (family, weight, file)
    notes = []
    # 1) Pretendard (본문·헤드라인 기본)
    pv = None
    for cand in ("PretendardVariable.ttf", "PretendardVariable.woff2"):
        if (fdir / cand).exists() and is_font(fdir / cand):
            pv = fdir / cand
    if not pv:
        src = find_local("PretendardVariable.ttf") or find_local("PretendardVariable.woff2")
        if src:
            pv = fdir / src.name
            shutil.copy2(src, pv)
            notes.append(f"Pretendard: 로컬/캐시 복사 ({src.name})")
        else:
            pv = fdir / "PretendardVariable.woff2"
            if curl(PRETENDARD_URL, pv) and is_font(pv):
                try:
                    shutil.copy2(pv, FONT_CACHE / pv.name)
                except OSError:
                    pass
                notes.append("Pretendard: 내려받음(jsdelivr npm)")
            else:
                pv.unlink(missing_ok=True)
                pv = None
                notes.append("Pretendard: 확보 실패 — 인터넷 연결을 확인하거나 수동으로 reel/fonts/PretendardVariable.woff2 를 넣을 것")
    if pv:
        faces.append(("Pretendard", "45 920", pv.name))
    # 2) Google Fonts (세리프·임팩트·숫자·모노)
    css_cache = fdir / ".google.css"
    global_css_cache = FONT_CACHE / ".google.css"
    css = None
    if css_cache.exists():
        css = css_cache.read_text(encoding="utf-8")
    elif global_css_cache.exists():
        css = global_css_cache.read_text(encoding="utf-8")
        css_cache.write_text(css, encoding="utf-8")
    if css is None:
        body = curl(GOOGLE_CSS)
        css = body.decode("utf-8", errors="replace") if body else ""
        if css:
            css_cache.write_text(css, encoding="utf-8")
            try:
                global_css_cache.write_text(css, encoding="utf-8")
            except OSError:
                pass
    google_faces(css, fdir, faces, notes)
    if not css:
        notes.append("Google Fonts: 접속 실패 — Noto Serif KR/Black Han Sans/Anton/JetBrains Mono 없이 진행(Pretendard 로 대체)")
    # 2-1) --fonts 로 더한 Google Fonts 서체(이전 실행에서 더한 것도 유지)
    saved = fdir / ".extra_fonts"
    specs = [x for x in (saved.read_text(encoding="utf-8").splitlines() if saved.exists() else []) if x.strip()]
    specs += [x for x in extra if x not in specs]
    for spec in specs:
        body = curl("https://fonts.googleapis.com/css2?family=" + spec.strip().replace(" ", "+") + "&display=block")
        if body and b"@font-face" in body:
            google_faces(body.decode("utf-8", errors="replace"), fdir, faces, notes)
        else:
            notes.append(f"추가 서체 '{spec}': CSS 를 받지 못했다(이름·굵기 표기를 확인. 굵기는 wght@400;700 처럼 나열)")
    if specs:
        saved.write_text("\n".join(specs) + "\n", encoding="utf-8")
    # 3) 로컬 선택 폰트(Paperlogy, 에이투지체) — 파일명을 ASCII 로
    for pat, fam, keep in OPTIONAL_LOCAL:
        for d in LOCAL_DIRS:
            try:
                if not d.exists():
                    continue
                for p in d.glob("*.ttf"):
                    m = re.fullmatch(pat, unicodedata.normalize("NFC", p.name))
                    if not m or int(m.group(1)) not in keep:
                        continue
                    wt = str(int(m.group(1)) * 100)
                    fname = f"{fam}-{wt}.ttf"
                    if not (fdir / fname).exists():
                        shutil.copy2(p, fdir / fname)
                    if (fam, wt, fname) not in faces:
                        faces.append((fam, wt, fname))
            except OSError:
                continue
    lines = ["/* new_project.py 가 만든다. 실제로 있는 폰트만 적는다. 쓰는 굵기와 font-weight 가 맞아야 대체 글꼴이 안 나온다. */"]
    for fam, wt, fname in sorted(faces, key=lambda f: (f[0], f[1])):
        fmt = "woff2" if fname.endswith(".woff2") else "truetype"
        lines.append(f'@font-face {{ font-family: "{fam}"; src: url("{fname}") format("{fmt}"); font-weight: {wt}; font-display: block; }}')
    (fdir / "fonts.css").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return faces, notes


def ensure_node_deps():
    if (SCRIPTS / "node_modules" / "playwright-core").exists():
        return "playwright-core: 있음"
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm") or "npm"
    r = subprocess.run([npm_cmd, "install", "--no-audit", "--no-fund", "--silent"], cwd=SCRIPTS, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return "playwright-core: 설치 실패 — `cd \"%s\" && npm install` 을 직접 실행할 것\n%s" % (SCRIPTS, r.stderr[-400:])
    return "playwright-core: 설치함"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--ratio", default="16:9", choices=["16:9", "9:16", "1:1", "4:5"])
    ap.add_argument("--duration", type=float, default=60)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--force-engine", action="store_true")
    ap.add_argument("--fonts", action="append", default=[], help='더할 Google Fonts 서체. 예: "Hahmlet:wght@300;900"')
    a = ap.parse_args()

    root = Path(a.project).resolve()
    for sub in ["research", "assets/img", "assets/photos", "assets/gen", "assets/cutout", "assets/logo",
                "audio/vo", "audio/music", "audio/sfx", "reel", "qa", "out"]:
        (root / sub).mkdir(parents=True, exist_ok=True)
    reel = root / "reel"
    for f in ["engine.js", "fx.js"]:
        shutil.copy2(ENGINE / f, reel / f)
    if a.force_engine or not (reel / "index.html").exists():
        shutil.copy2(ENGINE / "index.html", reel / "index.html")
    shutil.copy2(ENGINE / "scenes.js", reel / "_example_scenes.js")
    if not (reel / "timeline.js").exists():
        (reel / "timeline.js").write_text("window.TL = window.TL || { cues: {}, vo: [], scenes: [] };\n", encoding="utf-8")

    W, H = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350)}[a.ratio]
    sj = reel / "scenes.js"
    if a.force_engine or not sj.exists():
        sj.write_text(SCENES_STUB % {"dur": f"{a.duration:g}", "fps": a.fps, "w": W, "h": H}, encoding="utf-8")

    faces, notes = setup_fonts(reel / "fonts", a.fonts)
    dep = ensure_node_deps()
    meta = {"ratio": a.ratio, "width": W, "height": H, "fps": a.fps, "duration": a.duration}
    (root / "project.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"프로젝트: {root}")
    print(f"규격: {W}x{H} {a.fps}fps, 목표 {a.duration:g}초  (REEL.config 에 같은 값을 쓸 것)")
    print("폰트: " + ", ".join(sorted({f'{f[0]} {f[1]}' for f in faces})))
    for n in notes:
        print("  - " + n)
    print(dep)
    print("미리보기: node \"%s\" --dir \"%s\" --serve" % (SCRIPTS / "render.mjs", reel))


if __name__ == "__main__":
    main()
