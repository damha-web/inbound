# AI Marketing Proposal Pipeline

## Overview
이 저장소는 4개 에이전트(Research -> Consultant -> Content/Brand -> Styling)를 사용해
마케팅 제안서를 생성합니다.

주요 기능:
- 에이전트 프롬프트 구조화
- LLM 어댑터(`mock`, `openai`)
- OpenAI 네트워크 재시도(지수 백오프)
- 품질 게이트 자동 점검 및 자동 보정 루프
- 업종별 컴플라이언스 금지 표현 점검/치환
- Markdown/HTML 렌더링
- 실행 로그 및 JSON 리포트 저장

## Quick Start
PowerShell 기준:

```powershell
$env:PYTHONPATH="H:\inbound\src"
python H:\inbound\src\run_proposal.py `
  --client-name "샘플의원" `
  --industry "의료" `
  --region "부산 해운대구" `
  --budget-range "월 500~800만원" `
  --target-segments "20대 여성,30대 여성" `
  --constraints "의료광고 심의 준수,과장표현 금지" `
  --backend mock `
  --output-format both `
  --table-policy forbid `
  --save-json-report
```

결과물 기본 위치:
- `proposals/generated/*.md`
- `proposals/generated/*.html`
- `proposals/generated/*.report.json`

## OpenAI Backend
`openai` 백엔드 사용 시 환경변수:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_MODEL="gpt-4.1-mini"   # optional
$env:OPENAI_BASE_URL="https://api.openai.com/v1"  # optional
```

또는 루트 `.env` 파일에 저장해 자동 로드할 수 있습니다.
기본 `.gitignore`에 `.env`가 포함되어 커밋에서 제외됩니다.

실행 옵션:
- `--backend openai`

## Policy (표 정책 단일화)
표 사용 정책은 전역적으로 하나만 사용합니다.
- `--table-policy forbid` (기본): 카드/리스트 기반
- `--table-policy allow`: 표 허용

또는 환경변수:
- `PROPOSAL_TABLE_POLICY=forbid|allow`

## Tests
```powershell
$env:PYTHONPATH="H:\inbound\src"
python -m unittest discover -s H:\inbound\tests -p "test_*.py"
```

또는 스크립트 사용:
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_tests.ps1
```

## Automation Scripts
- `scripts/run_tests.ps1`: 전체 테스트 실행
- `scripts/run_mock.ps1`: 모의 백엔드로 제안서 생성
- `scripts/run_openai.ps1`: OpenAI 백엔드로 제안서 생성
- `scripts/run_batch_mock.ps1`: CSV 기반 배치 생성(mock)

## Batch Run
입력 CSV 예시: `scripts/sample_clients.csv`

```powershell
$env:PYTHONPATH="H:\inbound\src"
python H:\inbound\src\run_batch_proposals.py `
  --input-csv H:\inbound\scripts\sample_clients.csv `
  --backend mock `
  --output-dir H:\inbound\proposals\generated_batch `
  --strict-quality
```

출력:
- 배치별 `*.md`, `*.html`, `*.report.json`
- 집계 `*_summary.csv`

## File Map
- `src/agents/prompts.py`: 에이전트 프롬프트/구조/품질게이트
- `src/agents/proposal_generator.py`: 프롬프트 조립 + 품질 평가
- `src/agents/config.py`: 정책 설정
- `src/agents/compliance.py`: 업종별 컴플라이언스 룰
- `src/agents/llm_adapter.py`: LLM 백엔드 어댑터
- `src/agents/pipeline.py`: 엔드투엔드 생성/보정 파이프라인
- `src/agents/renderer.py`: Markdown/HTML 렌더러
- `src/agents/pipeline.py`: 실행 로그 포함 파이프라인
- `src/run_proposal.py`: CLI 실행 진입점
- `src/run_batch_proposals.py`: 배치 실행 진입점(CSV 입력)

상세 기능 설명:
- `docs/system-capabilities.md`
