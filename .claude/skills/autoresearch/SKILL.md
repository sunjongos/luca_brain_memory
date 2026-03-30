---
name: autoresearch
description: "Andrej Karpathy 스타일의 자율 ML 실험 파이프라인. AI가 train.py를 수정하고, 학습을 돌리고, val_bpb 메트릭을 확인하여 개선되면 유지/아니면 폐기를 반복하는 완전 자율 연구 루프. /autoresearch 또는 '자율 실험', 'autoresearch 시작', 'ML 실험 돌려줘', 'train.py 최적화' 등의 요청 시 이 스킬을 사용하세요."
---

# AutoResearch: 자율 ML 실험 파이프라인

Andrej Karpathy의 [autoresearch](https://github.com/karpathy/autoresearch) 개념을 CPU 경량 버전으로 구현한 스킬.
AI가 스스로 코드를 수정 → 실험 → 평가 → 개선/폐기를 무한 반복하며 최적의 모델을 찾아갑니다.

## 핵심 원리

- **고정 시간 예산**: 매 실험 2분 (벽시계 기준), 시간당 ~12회 실험 가능
- **단일 메트릭**: `val_bpb` (validation bits per byte) — 낮을수록 좋음
- **단일 파일 수정**: `train.py`만 변경 가능 (모델, 옵티마이저, 하이퍼파라미터 모두)
- **자동 판정**: 개선 → keep + git commit, 미개선 → discard + git reset

## 파이프라인 경로

```
PIPELINE_DIR: autoresearch_pipeline/
```

이 스킬이 활성화되면, 작업 디렉토리를 `autoresearch_pipeline/`으로 이동하여 작업합니다.

## 환경

| 항목 | 값 |
|---|---|
| 디바이스 | CPU only (CUDA 없음) |
| 데이터셋 | TinyStories (HuggingFace) |
| 토크나이저 | byte-level (vocab=257) |
| 시퀀스 길이 | 256 |
| 시간 예산 | 120초 (2분) |
| 베이스라인 | val_bpb ≈ 3.124 |

## Phase 1: 셋업

실험을 시작하기 전에 반드시 다음 단계를 수행:

### 1. 데이터 확인
```bash
ls ~/.cache/autoresearch_lite/data/
```
파일이 없으면 데이터를 준비:
```bash
cd autoresearch_pipeline && python prepare.py --num-shards 1
```

### 2. Git 브랜치 생성
오늘 날짜 기반으로 태그를 정하고 새 브랜치를 생성:
```bash
cd autoresearch_pipeline
git checkout -b autoresearch/<tag>  # e.g. autoresearch/mar15
```
이미 존재하는 브랜치면 숫자를 붙여 고유하게 만든다 (e.g. `mar15-2`).

### 3. 파일 읽기
다음 파일들을 읽어 전체 컨텍스트를 파악:
- `prepare.py` — 고정 상수, 데이터로더, 평가 함수. **수정 불가.**
- `train.py` — 모델, 옵티마이저, 학습 루프. **이 파일만 수정 가능.**

### 4. results.tsv 초기화
```
commit	val_bpb	memory_gb	status	description
```
이 헤더 한 줄만 있는 `results.tsv` 파일을 생성. (git에 커밋하지 않음)

### 5. 베이스라인 실행
첫 실험은 항상 현재 코드를 그대로 실행하여 베이스라인을 잡는다:
```bash
python train.py > run.log 2>&1
grep "^val_bpb:" run.log
```

## Phase 2: 자율 실험 루프

셋업이 끝나면 아래 루프를 **무한 반복**한다. 절대 멈추지 않는다.

```
LOOP FOREVER:
  1. train.py를 실험 아이디어로 수정
  2. git commit -m "experiment: <간단한 설명>"
  3. python train.py > run.log 2>&1
  4. grep "^val_bpb:" run.log → 메트릭 추출
  5. 크래시 시: tail -n 50 run.log로 에러 확인 후 수정 시도
  6. results.tsv에 결과 기록
  7. val_bpb가 개선되면 → keep (브랜치 전진)
  8. val_bpb가 같거나 나빠지면 → git reset --hard HEAD~1 (폐기)
```

### 수정 가능한 영역 (train.py)
- 모델 아키텍처 (레이어 수, 차원, 어텐션 헤드, 활성화 함수)
- 옵티마이저 (AdamW, SGD, 스케줄러)
- 하이퍼파라미터 (배치 크기, 학습률, weight decay)
- 학습 루프 로직 (gradient accumulation, warmup 등)

### 수정 불가 영역
- `prepare.py` (데이터, 토크나이저, 평가 함수)
- 패키지 설치 / 의존성 추가
- `evaluate_bpb()` 함수 (고정 메트릭)

### CPU 최적화 팁
- 배치 크기가 크면 CPU에서 느릴 수 있음 — 최적점을 찾아야 함
- 작은 모델 + 더 많은 스텝 > 큰 모델 + 적은 스텝
- weight tying (wte 가중치를 lm_head와 공유)으로 파라미터 절약
- ReLU² (squared ReLU) 활성화가 GELU보다 나을 수 있음
- cosine 스케줄 외에 linear, warmup-stable-decay 등 시도
- `.reshape()` 사용 (`.view()`는 CPU에서 에러 발생 가능)

### 실험 아이디어 방향
1. **하이퍼파라미터 튜닝**: LR, batch size, warmup ratio, weight decay
2. **아키텍처 변경**: depth, width, head 수, MLP ratio
3. **활성화 함수**: GELU → SiLU, ReLU², Swish
4. **최적화**: 다른 optimizer, gradient clipping 값, beta 조정
5. **정규화**: dropout, layer norm vs RMS norm
6. **Weight tying**: 임베딩/언임베딩 가중치 공유
7. **초기화**: 다른 weight init 전략
8. **복합 변경**: 성공한 개별 변경들의 조합

### 결과 기록 형식 (results.tsv)
탭으로 구분, 쉼표 사용 금지:
```
a1b2c3d	3.124355	0.0	keep	baseline
b2c3d4e	3.018200	0.0	keep	increase LR to 1e-3
c3d4e5f	3.200000	0.0	discard	switch to SiLU activation
d4e5f6g	0.000000	0.0	crash	double model width (CPU too slow)
```

### 타임아웃
실험이 5분을 넘기면 프로세스를 kill하고 crash로 처리한다.

### 절대 멈추지 말 것
실험 루프가 시작되면 사람에게 "계속할까요?"라고 묻지 않는다.
아이디어가 없으면 더 깊이 생각한다 — 이전 실패에서 패턴을 찾고, 성공한 변경들을 조합하고, 더 과감한 아키텍처 변경을 시도한다.
사람이 수동으로 중단할 때까지 루프는 계속된다.

## 참고: 간결성 원칙

- 같은 val_bpb라면 더 단순한 코드가 이긴다
- 0.001 개선에 20줄의 복잡한 코드 추가? → 가치 없음
- 0.001 개선을 코드 삭제로 달성? → 훌륭함
- 개선 없이 코드가 더 깔끔해졌다면? → keep
