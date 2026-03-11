# Proposal Pipeline Operations Guide

## 1) Local Test
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_tests.ps1
```

## 2) Mock Generation
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_mock.ps1
```

## 3) OpenAI Generation
사전 조건:
- `OPENAI_API_KEY` 설정

```powershell
$env:OPENAI_API_KEY="sk-..."
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_openai.ps1
```

## 4) Batch Generation
```powershell
powershell -ExecutionPolicy Bypass -File H:\inbound\scripts\run_batch_mock.ps1
```

CSV 컬럼:
- `client_name, industry, region, budget_range, target_segments, constraints, shared_context`

## 5) Quality Gate Failure Handling
1. `.report.json`에서 `quality_results` 확인
2. 실패 게이트의 `details`를 기반으로 입력 컨텍스트 보강
3. `--max-quality-retries` 값을 1~3 범위에서 조정

## 6) Compliance Failure Handling
1. 의료 업종은 과장/확정 표현 사용 금지
2. 자동 치환 후에도 부적합 문구가 남아있으면 수동 검수
3. 최종 발송 전 법무/심의 체크리스트 확인
