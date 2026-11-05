# Showreel — Antigravity (Gemini) 모션그래픽 제작 하네스

이 워크스페이스는 요청 한 번으로 한국어 모션그래픽 영상(쇼릴, 티저, 홍보 영상, 브랜드 필름, 소개 영상 등)을 기획부터 오디오 합성·타임라인 싱크·모션 블러 렌더링·마스터링·자동 검수까지 수행하는 **Showreel (Antigravity / Gemini Edition)** 하네스입니다.

## 에이전트 필수 행동 지침

1. 사용자가 모션그래픽 영상, 쇼릴, 홍보/소개/티저 영상 제작을 요청하면 **반드시 현재 폴더의 [`SKILL.md`](./SKILL.md)를 먼저 읽고** 그 절차(0단계 환경 점검 ~ 11단계 자동 검수·납품 보고)를 엄격히 따르세요.
2. 이 워크스페이스의 스크립트 폴더 경로(`$S`)는 `./scripts` 입니다.
   - 환경 점검: `python scripts/preflight.py`
   - 새 프로젝트 생성: `python scripts/new_project.py <프로젝트폴더> --ratio 16:9 --duration <초>`
   - 합성 음악/효과음 생성(API 키 불필요): `python scripts/synth_music.py ...`
   - 이미지 생성: Antigravity 내장 `image-generator` 서브에이전트(`invoke_subagent` — `TypeName: "image-generator"`) 활용
   - 렌더러: `node scripts/render.mjs ...`
   - 검수 시트 확인: 생성된 PNG 시트(`qa/*.png`)는 반드시 `read_file` 도구로 직접 열어서 시각적으로 확인하세요.
3. 상세 가이드는 [`references/`](./references/) 폴더의 각 문서(`brief.md`, `story.md`, `audio.md`, `images.md`, `design.md`, `engine.md`, `techniques.md`, `qa.md`)를 단계별로 읽어 반영하세요.
