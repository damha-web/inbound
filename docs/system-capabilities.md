# 시스템 기능 설명서

## 1. 개요
이 시스템은 4개 에이전트 파이프라인으로 마케팅 제안서를 자동 생성합니다.

- Data Research Agent
- Marketing Consultant Agent
- Content Planner & Brand Strategist Agent
- Styling Expert Agent

출력물은 Markdown/HTML 제안서와 JSON 리포트입니다.

## 2. 할 수 있는 작업

### 2.1 제안서 자동 생성
- 고객 정보 입력 기반 단건 제안서 생성
- 리서치 -> 전략 -> 브랜드/콘텐츠 -> 스타일링 순차 생성
- 결과물 저장:
  - `proposals/generated/*.md`
  - `proposals/generated/*.html`
  - `proposals/generated/*.report.json`

### 2.2 배치 제안서 생성
- CSV 여러 건 입력으로 제안서 일괄 생성
- 결과물 저장:
  - `proposals/generated_batch/*.md`
  - `proposals/generated_batch/*.html`
  - `proposals/generated_batch/*.report.json`
  - `proposals/generated_batch/*_summary.csv`

### 2.3 품질 게이트 자동 점검
아래 항목을 자동 검사합니다.
- 기준일(YYYY-MM-DD) 표기
- 출처 표기
- KPI/성과 지표 연결
- 30-60-90 실행 계획
- 컴플라이언스 위험 표현
- 성과 측정 지표 포함 여부
- 필수 섹션 누락 여부

### 2.4 자동 보정 루프
- 품질 게이트 실패 시 자동 보정 시도
- `max_quality_retries` 범위 내 재평가

### 2.5 컴플라이언스 점검/치환
- 업종별 금지 표현 탐지(의료 포함)
- 위험 표현 자동 치환 후 재평가

### 2.6 정책 제어
- 표 사용 정책 전역 제어
  - `forbid`: 카드/리스트 중심
  - `allow`: 표 허용

### 2.7 LLM 백엔드 선택
- `mock`: 로컬 테스트/개발용
- `openai`: 실전 생성용
- OpenAI 호출 재시도(지수 백오프) 지원

## 3. 실행 방법

### 3.1 테스트
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_tests.ps1
```

### 3.2 단건(mock)
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_mock.ps1
```

### 3.3 단건(openai)
`.env`에 API 키 저장 후 실행:
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_openai.ps1
```

### 3.4 배치(mock)
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_batch_mock.ps1
```

## 4. 입력 형식

### 4.1 단건 입력 파라미터
- `client_name`
- `industry`
- `region`
- `budget_range`
- `target_segments` (쉼표 구분)
- `constraints` (쉼표 구분)
- `shared_context` (선택)

### 4.2 배치 CSV 컬럼
- `client_name`
- `industry`
- `region`
- `budget_range`
- `target_segments`
- `constraints`
- `shared_context`

## 5. 출력 설명
- `.md`: 텍스트 중심 제안서
- `.html`: 시각화된 제안서
- `.report.json`: 품질 게이트 결과, 재시도 횟수, 컴플라이언스 카운트, 실행 로그
- `_summary.csv`(배치): 건별 성공/실패 및 파일 경로 집계

## 6. 주요 옵션
- `--table-policy allow|forbid`
- `--max-quality-retries N`
- `--strict-quality` (품질 실패 시 비정상 종료 코드)
- `--save-json-report`
- `--print-execution-log`

## 7. 환경 설정
- `.env` 자동 로드 지원
- `.env`는 `.gitignore`로 커밋 제외
- 샘플 파일: `.env.example`

권장 변수:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (예: `gpt-4.1-mini`)
- `OPENAI_BASE_URL` (기본: `https://api.openai.com/v1`)

## 8. 한계 및 주의사항
- 생성 품질은 입력 컨텍스트 밀도에 영향을 받습니다.
- 컴플라이언스 자동 치환은 1차 방어선이며 최종 법적 검수는 별도 필요합니다.
- OpenAI 키가 없거나 네트워크 이슈가 있으면 `openai` 실행이 실패할 수 있습니다.
- 저장소가 Git repo가 아니면 Git 기반 추적/훅은 동작하지 않습니다.

## 9. 관련 파일
- `src/run_proposal.py`
- `src/run_batch_proposals.py`
- `src/agents/pipeline.py`
- `src/agents/proposal_generator.py`
- `src/agents/llm_adapter.py`
- `src/agents/compliance.py`
- `src/agents/renderer.py`
- `scripts/run_tests.ps1`
- `scripts/run_mock.ps1`
- `scripts/run_openai.ps1`
- `scripts/run_batch_mock.ps1`
