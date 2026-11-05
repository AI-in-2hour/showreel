#!/usr/bin/env python3
"""완성된 산출물 폴더의 파일들을 바탕화면/다운로드 '쇼릴_결과물' 폴더로 복사하고 파일 탐색기(Explorer/Finder)로 연다."""
import sys
from pathlib import Path
from finish import export_easy_access

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    outdir = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    files = [
        f for f in outdir.iterdir()
        if f.is_file() and f.suffix.lower() in (".mp4", ".jpg", ".png", ".srt")
        and f.name not in ("video.mp4", "draft.mp4", "test_s1.mp4")
    ]
    export_easy_access(files, no_open="--no-open" in sys.argv)


if __name__ == "__main__":
    main()
