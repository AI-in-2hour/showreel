# 이미지: 생성·실제 사진·누끼·후처리

## 목차

- 어떤 이미지를 쓸지 정하기
- Antigravity 내장 Gemini (image-generator)로 생성하기
- 사람이 나오는 사진풍 이미지 프롬프트 설계
- 실제 사진 쓰기
- 후처리와 확인
- 영상에 넣는 방식

## 어떤 이미지를 쓸지 정하기

| 상황 | 쓸 이미지 |
| --- | --- |
| 실존 인물 소개 | 실제 사진만(사용자 제공·공식·보도). 분위기 컷(무대, 사무실, 도시 야경)은 얼굴 없이 생성 |
| 기업·제품 | 공식 로고·제품 화면 + 코드로 그린 UI 목업. 생성 이미지는 배경 질감으로 |
| 행사 | 생성 인물은 뒷모습·실루엣·군중. 연사는 실명·소속 텍스트만 |
| 연구·데이터 | 코드로 그린 도식(캔버스·SVG). "설명을 위해 그린 그림" 고지 |
| 반려동물·제품 | 실제 사진을 참조하거나 특징을 상세히 묘사해 새 장면에 생성 |
| 이미지 없이 | 타이포·도형·파티클·데이터 시각화만으로 구성 |

실존 인물의 얼굴은 생성하지 않는다. 사칭이나 오해를 부를 수 있다. 실존 인물이면 실제 사진을 쓰고 생성은 가상 인물·뒷모습에만 쓴다고 알린다.

## Antigravity 내장 Gemini (`image-generator`)로 생성하기

Antigravity 환경에서는 별도의 외부 CLI 설치 없이 내장된 **`image-generator`** 서브에이전트(`invoke_subagent` 도구에서 `TypeName: "image-generator"` 지정)를 호출해 고품질 이미지를 생성할 수 있다.

1. `invoke_subagent`로 `TypeName: "image-generator"`를 호출하며, 프롬프트와 원하는 비율(예: 16:9 가로 구도)을 전달한다.
2. 서브에이전트가 생성된 이미지 파일 경로를 반환하면 `<프로젝트>/assets/gen/` 폴더로 복사(`01_stage.png`, `02_city.png` 등)한다.
3. 여러 장이 필요하면 서브에이전트에 한 번에 요청하거나 여러 서브에이전트를 병렬로 띄우고 그동안 다른 작업(장면 코드 작성, 오디오 믹스 등)을 진행한다.
4. 생성된 이미지는 `prep_images.py`로 레터박스 제거 및 2400px 업스케일을 거친다.

### 프롬프트 틀

한 구간의 컷에는 같은 **공통 꼬리**를 붙여 톤을 맞춘다. 꼬리에 넣는 빛·팔레트·질감 문구는 그 구간의 `concept.md` 아트 디렉션을 영어로 옮겨 적는다.

```
<장면 묘사: 장소·대상·구도·빛>. <concept.md 구간의 빛·팔레트·질감을 영어로>, wide 16:9 landscape frame,
large empty negative space on the left for typography, absolutely no text, no letters, no logos, no watermark
```

- 비율은 "wide 16:9 landscape frame"처럼 말로 적는다. "16:9 (1536x1024)"처럼 비율과 해상도가 어긋나게 쓰면 모델이 위아래에 검은 띠를 그려 넣는다(`prep_images.py`가 잘라 내지만 해상도를 잃는다).
- 글자를 올릴 자리(negative space)를 지정한다. 인물·사물은 화면 3분의 1에 둔다.
- 화면 속 모니터·간판은 "blank glowing screens with abstract color only"처럼 글자가 없게 한다. 한글 글자는 거의 항상 뭉개진다.
- 사람은 "seen only from behind as silhouettes, no faces visible"로 쓴다.
- 이미지 안에 그래픽을 합성할 자리를 비워 둘 수 있다: "the screen is pure deep black, reserved for compositing graphics later"

예시(실제 사용):

```
Cinematic photoreal still of a television broadcast master control room at night during a live show. A long wall of dozens of
glowing monitors showing blurred colorful stage images, a wide mixing console with hundreds of small illuminated buttons in the
foreground, two crew members seen only from behind as dark silhouettes with headsets, faces not visible. Only practical light from
the screens and console, deep shadows, slight haze, subtle film grain, slightly off-center framing. No readable text, no logos, no letters anywhere.
```

## 사람이 나오는 사진풍 이미지 프롬프트 설계

가상 인물이 나오는 실사풍 컷은 광고 화보처럼 매끈한 결과를 피하고 자연스러운 스냅처럼 보이게 설계한다.

- 카메라 스펙(85mm, f/1.4)을 적으면 과장된 화보 쪽으로 간다.
- "nobody looking at the camera", "framing tilted a degree or two", "natural indoor lighting, subtle sensor grain"이 자연스러움에 효과가 좋다.
- 생성 뒤 손가락 수, 눈동자, 글자 섞임, 나이를 확인한다.

## 실제 사진 쓰기

- 출처를 `research/photos.md`에 표로 남긴다: 파일명 · 원본 URL · 기사 URL · 해상도 · 내용 · 품질.
- 받은 사진을 `read_file`로 열어 본인인지 확인한다. 동명이인을 걸러 낸다.
- 보도 사진·위촉장·명패처럼 서명·직인이 보이는 사진은 납품 보고에 "공개 전 확인"으로 표시한다.
- 해상도가 낮은 기사 사진(500~800px)은 카드·폴라로이드 크기로만 쓰고, 전체 화면 배경에는 흐리게 처리해 쓴다.

## 후처리와 확인

```bash
python <S>/prep_images.py <프로젝트>/assets/gen <프로젝트>/assets/photos --out <프로젝트>/assets/img [--blur] [--cutout]
python <S>/prep_images.py --sheet <프로젝트>/assets/img --out <프로젝트>/qa/sheet_images.png
```

- 레터박스 검은 띠를 자동으로 잘라 내고, 긴 변 2400px로 맞추고, JPG 품질 92로 저장한다.
- `--blur`: 전환·배경용 흐린 버전(`_blur.jpg`)
- `--cutout`: 인물·피사체 누끼(`_cut.png`). macOS에서는 Vision을 쓰고, Windows/Linux에서는 `rembg`가 설치되어 있으면 활용할 수 있다.
- 시트를 `read_file`로 보고 다음을 다시 만든다: 손가락·얼굴 이상, 글자·로고 섞임, 팔레트에서 벗어난 컷, 레터박스가 남은 컷.
- 누끼마다 인물 크기와 위치가 다르면 연속으로 보여 줄 때 화면이 튄다. 알파 채널에서 머리 위치와 폭을 계산해 크기를 맞춘다.

## 영상에 넣는 방식

| 기법 | 쓰는 곳 |
| --- | --- |
| 켄 번스(scale 1.08→1.18, 느린 이동) | 사진을 오래 보여 주는 장면에서 멈춘 사진이 슬라이드처럼 보일 때 |
| 3D 기울인 카드 + 클립 와이프 | 경력·자료 카드, 폴라로이드 |
| 누끼 + 림라이트(누끼를 마스크로 구간 팔레트의 빛을 인물 안쪽 가장자리에만) | 인물 공개, 이름 카드 |
| 글자 안에 사진 채우기(`background-clip: text`) | 오프닝 키워드 |
| 흐리고 어둡게(blur 6~10px, brightness 0.5) | 글자 뒤 배경 질감 |
| 듀오톤·틴트(`mix-blend-mode: color`) | 장면 색을 팔레트에 맞출 때 |

글자를 사진 위에 올릴 때는 글자 쪽에 어두운 그라디언트(스크림)를 깐다. 코드는 `engine.md`의 "사진" 절에 있다.
