<div align="center">

# showreel (Antigravity / Gemini Edition)

**An end-to-end Korean motion-graphics video production skill & harness for Google Antigravity (Gemini).<br/>Concept, research, script, audio synthesis/voiceover, Gemini image generation, deterministic HTML/WebGL rendering, critique loop, audio mastering, and automated QA in one prompt.**

[English](README.md) · [한국어 (Korean Guide)](README.ko.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-f5b942.svg)](LICENSE)
[![Antigravity Skill](https://img.shields.io/badge/Google%20Antigravity-Gemini%20Skill-4285F4.svg)](https://antigravity.google/docs/skills)
[![Platform: Windows | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-3fe3ff.svg)](#requirements)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](https://www.python.org/)
[![Node.js 20+](https://img.shields.io/badge/node-20%2B-339933.svg)](https://nodejs.org/)

<img src="docs/media/showreel-preview.gif" alt="Preview of a motion graphics video created with showreel" width="720">

</div>

---

## Overview

`showreel (Antigravity / Gemini Edition)` ports [revfactory/showreel](https://github.com/revfactory/showreel) to **Google Antigravity (Gemini)** with full **Windows, macOS, and Linux** support.

> 한국어 상세 설치 및 수업·실습 가이드는 **[README.ko.md](README.ko.md)**를 참고하세요!

### Key Enhancements in the Antigravity / Gemini Edition
- **Works Out-of-the-Box Without Paid API Keys**: Uses the built-in deterministic NumPy synthesizer (`synth_music.py`) for multi-layered background music & 23 sound effects, and Antigravity's native Gemini **`image-generator`** subagent for AI image generation (ElevenLabs TTS/Music remains optionally supported if `ELEVENLABS_API_KEY` is provided).
- **Full Windows + macOS + Linux Compatibility**: Native UTF-8 file/console handling on Windows, automatic Chrome/Edge detection, Windows font discovery + local font caching (`assets/fonts_cache`), and cross-platform FFmpeg concat paths.
- **Dual-Mode Setup (`GEMINI.md` + `SKILL.md`)**: Open this cloned repository directly as an Antigravity Workspace (auto-activates via `GEMINI.md`), or install it globally under `~/.gemini/config/skills/showreel`.

---

## Quick Start

### Option A: Open Directly as an Antigravity Workspace (Recommended for Classes)

```bash
git clone https://github.com/AI-in-2hour/showreel.git
cd showreel
python -m pip install numpy pillow
cd scripts && npm install && cd ..
```

Open the `showreel` folder in **Google Antigravity**, select a **Gemini** model, and prompt:

```text
당신이 얼마나 놀라운 모션 그래픽 디자이너인지 보여주는 역동적인 한글버전 15초 모션그래픽 비디오를 만들어 보세요. 이력서용 쇼릴처럼요. 전력을 다해요.
```

### Option B: Install as a Global Antigravity Skill

```bash
# macOS / Linux
git clone https://github.com/AI-in-2hour/showreel.git ~/.gemini/config/skills/showreel
cd ~/.gemini/config/skills/showreel/scripts && npm install

# Windows (PowerShell)
git clone https://github.com/AI-in-2hour/showreel.git "$HOME\.gemini\config\skills\showreel"
cd "$HOME\.gemini\config\skills\showreel\scripts"; npm install
```

---

## License & Credits

- Distributed under the [MIT License](LICENSE).
- Original skill and motion engine: [revfactory/showreel](https://github.com/revfactory/showreel) by [@revfactory](https://github.com/revfactory)
- Antigravity / Gemini & Cross-Platform Edition: [AI-in-2hour](https://github.com/AI-in-2hour)
