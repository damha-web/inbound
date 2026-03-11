# 📚 마케팅 제안서 자동화 시스템 — 프로젝트 참조 문서

> **목적:** 이 문서는 다른 프로젝트에서 본 시스템을 참조하거나 기능을 재사용할 때 활용하는 기술 레퍼런스입니다.
> **최종 업데이트:** 2026-03-10
> **프로젝트 위치:** `H:\inbound`

---

## 1. 프로젝트 개요

### 무엇을 만들었는가

고객사 기본 정보(이름, 주소, 업종, 타겟)를 입력하면 **4단계 AI 에이전트**가 자동으로 마케팅 제안서(HTML)를 생성하는 시스템.

### 버전 현황

| 버전 | 상태 | 설명 |
|------|------|------|
| **V1** | ✅ 완료 | Python CLI → HTML 제안서 생성 |
| **V2** | 🔄 계획 중 | 웹 폼 → 구글 시트 → 자동 Gmail 발송 → 웹훅 알림 |

---

## 2. V1 시스템 아키텍처

### 4단계 에이전트 파이프라인

```
입력정보 (고객사명/주소/업종/타겟)
    │
    ▼
Step 1: Data Research Agent
    - 상권 분석 (유동인구, 상업지구 특성)
    - 경쟁사 분석 (Top 5, 강약점)
    - 기회 요인 도출
    │
    ▼
Step 2: Marketing Consultant Agent
    - Target-Fit 채널 선택 (타겟별 최적 채널)
    - AS-IS → TO-BE 포지셔닝
    - 온라인/오프라인 채널 진단
    │
    ▼
Step 3: Content Planner Agent
    - 브랜드 슬로건 3개 생성
    - 4주 콘텐츠 로드맵
    - 법규 준수 카피 검수
    │
    ▼
Step 4: Styling Expert Agent
    - 최종 HTML 제안서 렌더링
    - 이메일 호환 버전 생성
    - Quality Gates 7/7 검사
```

### Target-Fit 채널 선택 로직

```python
# 타겟 연령대별 채널 우선순위
target_channel_map = {
    "30-50대": ["네이버 블로그", "당근마켓", "네이버 플레이스", "엘리베이터 TV"],
    "20-30대": ["인스타그램 릴스", "유튜브 숏폼", "강남언니 앱"],
    "전연령":  ["네이버 블로그", "인스타그램", "네이버 플레이스"]
}
```

### CLI 실행 인터페이스

```bash
python src/run_proposal.py \
  --client-name "리팅성형외과" \
  --industry "성형외과" \
  --region "부산 부산진구" \
  --budget-range "추후협의" \
  --target-segments "30-50대 여성" \
  --backend openai \           # mock | openai
  --output-format html \       # html | markdown | both
  --table-policy forbid        # 테이블 사용 금지 (웹 브로슈어 스타일)
```

### Quality Gates (7개)

| Gate | 내용 |
|------|------|
| 1 | 필수 입력값 검증 |
| 2 | 업종별 법규 키워드 금지어 검사 |
| 3 | HTML 문법 유효성 |
| 4 | 테이블 사용 금지 (웹용) |
| 5 | 최소 콘텐츠 길이 확인 |
| 6 | 채널 추천 포함 여부 |
| 7 | CTA(행동 유도 문구) 포함 여부 |

---

## 3. 법규 자동 감지 및 준수

### 업종별 금지 표현

```python
LAW_RULES = {
    "의료법": {
        "trigger_keywords": ["병원", "의원", "성형", "치과", "피부과", "한의원"],
        "forbidden": ["최고", "유일", "100% 완치", "부작용 없음", "획기적인 효과", "가장 좋은"],
        "required":  ["개인차가 있습니다", "전문의 상담 후", "도움이 될 수 있습니다"]
    },
    "금융법": {
        "trigger_keywords": ["보험", "투자", "대출", "증권", "펀드"],
        "forbidden": ["수익 보장", "확실한 이익", "원금 보장"],
        "required":  ["투자 원금 손실 가능", "과거 수익이 미래를 보장하지 않습니다"]
    },
    "화장품법": {
        "trigger_keywords": ["뷰티", "스킨케어", "화장품", "미용"],
        "forbidden": ["만능", "질병 치료", "의학적 효과"],
        "required":  ["개인에 따라 다를 수 있습니다"]
    },
    "식품위생법": {
        "trigger_keywords": ["카페", "식당", "음식점", "베이커리"],
        "forbidden": ["건강 음식", "약효", "치료 효과"],
        "required":  []
    }
}
```

---

## 4. 이메일 호환 HTML 생성 규칙 (핵심 노하우)

### 문제: Gmail/Outlook/네이버메일 에서 레이아웃 깨짐

| CSS 속성 | 이메일 지원 | 대안 |
|---------|------------|------|
| `display: grid` | ❌ | `<table>` 2열 구조 |
| `display: flex` | ❌ | `<table>` 행 구조 |
| `cellspacing` 속성 | ❌ Gmail 무시 | `<td width="20">` 스페이서 |
| `padding` on `<table>` | ❌ | `<td style="padding:40px">` |
| `background-color` on `<table>` | ❌ Gmail 무시 | `<td bgcolor="#xxx">` + style |
| `align="center"` 상속 | ⚠️ 하위 전파 | 내부 td에 `align="left"` 명시 |

### 이메일 호환 2열 레이아웃 패턴

```html
<!-- ❌ 잘못된 방법 (이메일에서 깨짐) -->
<table width="100%" cellspacing="10">
  <tr>
    <td width="48%" style="padding:20px; background:#f0f4f8;">...</td>
    <td width="48%" style="padding:20px; background:#f0f4f8;">...</td>
  </tr>
</table>

<!-- ✅ 올바른 방법 (이메일 호환) -->
<!-- 컨테이너 680px 기준, 컨텐츠 영역 600px 기준 -->
<table width="600" cellpadding="0" cellspacing="0">
  <tr>
    <td width="290" valign="top">
      <div style="background-color:#f0f4f8; border-left:3px solid #2c5aa0; padding:15px;">
        내용
      </div>
    </td>
    <td width="20">&nbsp;</td>  <!-- 스페이서 -->
    <td width="290" valign="top">
      <div style="background-color:#f0f4f8; border-left:3px solid #2c5aa0; padding:15px;">
        내용
      </div>
    </td>
  </tr>
</table>
<!-- 290 + 20 + 290 = 600px ✓ -->
```

### 이메일 호환 전체 구조 템플릿

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <!-- viewport 메타태그는 있어도 됨 (이메일에선 무시됨) -->
</head>
<body style="margin:0; padding:0; font-family:Arial,'Malgun Gothic',sans-serif;">

  <!-- 1. 외부 센터링 테이블 -->
  <table width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:20px 0;">

    <!-- 2. 콘텐츠 컨테이너 (680px 고정) -->
    <table width="680" cellpadding="0" cellspacing="0"
           style="background-color:#ffffff; border-radius:8px;">
    <tr>
      <!-- 3. 메인 콘텐츠 td: align="left" 필수 (center 상속 차단) -->
      <td align="left" style="padding:40px; text-align:left;">

        <!-- 4. 배경색 박스: bgcolor 속성 + style 둘 다 사용 -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td bgcolor="#f0f4f8"
              style="background-color:#f0f4f8; border-left:4px solid #2c5aa0; padding:20px;">
            내용
          </td>
        </tr>
        </table>

        <!-- 5. 2열 레이아웃 -->
        <table width="600" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td width="290" valign="top">
            <div style="background-color:#f0f4f8; padding:15px;">왼쪽</div>
          </td>
          <td width="20">&nbsp;</td>
          <td width="290" valign="top">
            <div style="background-color:#f0f4f8; padding:15px;">오른쪽</div>
          </td>
        </tr>
        </table>

      </td>
    </tr>
    </table>

  </td></tr>
  </table>
</body>
</html>
```

### 배경색 일괄 수정 Python 스크립트

기존 HTML에서 `<table style="background-color:...">` → `<td bgcolor="..." style="background-color:...">` 로 일괄 변환:

```python
import re

def fix_email_table_bg(html: str) -> str:
    """이메일 호환: table의 background-color를 td로 이동"""
    lines = html.split('\n')
    result = []
    i = 0
    replacements = 0

    while i < len(lines):
        line = lines[i]
        m = re.match(
            r'(\s*<table[^>]+?)style="([^"]*background-color:\s*#[0-9a-fA-F]{3,6}[^"]*?)"(>)',
            line
        )
        if m and i + 1 < len(lines):
            next_line = lines[i + 1]
            td_m = re.match(r'(\s*<tr><td) style="([^"]*)"(>)', next_line)
            if td_m:
                table_style = m.group(2)
                bg_m = re.search(r'background-color:\s*(#[0-9a-fA-F]{3,6})', table_style)
                bl_m = re.search(r'border-left:[^;]+', table_style)

                bgcolor = bg_m.group(1) if bg_m else ''
                bg_css = f'background-color:{bgcolor};' if bgcolor else ''
                bl_css = (bl_m.group(0) + ';') if bl_m else ''

                new_table_style = re.sub(r'\s*background-color:[^;]+;\s*', ' ', table_style)
                new_table_style = re.sub(r'\s*border-left:[^;]+;\s*', ' ', new_table_style).strip()

                if new_table_style:
                    new_table = f'{m.group(1)}style="{new_table_style}"{m.group(3)}'
                else:
                    new_table = m.group(1).rstrip() + m.group(3)

                new_td_styles = f'{bg_css} {bl_css} {td_m.group(2)}'.strip()
                new_td = f'{td_m.group(1)} bgcolor="{bgcolor}" style="{new_td_styles}"{td_m.group(3)}'

                result.extend([new_table, new_td])
                replacements += 1
                i += 2
                continue

        result.append(line)
        i += 1

    print(f"수정된 박스: {replacements}개")
    return '\n'.join(result)
```

---

## 5. 환경 설정

### .env 구조

```env
PYTHONPATH=H:\inbound\src
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1
PROPOSAL_TABLE_POLICY=forbid
PROPOSAL_MAX_QUALITY_RETRIES=2
```

### .claude/launch.json (개발 서버 3종)

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "Marketing Proposal Generator",
      "runtimeExecutable": "python",
      "runtimeArgs": ["src/run_proposal.py", "--client-name", "TestClient",
                      "--industry", "consulting", "--region", "Seoul",
                      "--budget-range", "1M-5M", "--backend", "mock"],
      "port": 8000
    },
    {
      "name": "Batch Proposal Generator",
      "runtimeExecutable": "python",
      "runtimeArgs": ["src/run_batch_proposals.py",
                      "--input", "scripts/sample_clients.csv", "--backend", "mock"],
      "port": 8001
    },
    {
      "name": "HTML Preview Server",
      "runtimeExecutable": "python",
      "runtimeArgs": ["-m", "http.server", "8080", "--directory", "outputs"],
      "port": 8080
    }
  ]
}
```

---

## 6. V2 추가 기능 계획

### 전체 플로우

```
웹 수집 폼 → Google Sheets → 제안서 생성(V1 재사용) → Gmail API 발송 → 웹훅 알림
```

### 추가 필요 모듈

| 파일 | 역할 |
|------|------|
| `v2/src/sheet_monitor.py` | Google Sheets 폴링 / 신규 접수 감지 |
| `v2/src/proposal_runner.py` | V1 파이프라인 subprocess 호출 |
| `v2/src/email_sender.py` | Gmail API OAuth 발송 |
| `v2/src/webhook_notifier.py` | Slack/Discord 웹훅 알림 |
| `v2/src/main_pipeline.py` | 전체 오케스트레이터 |

### 추가 환경변수 (V2)

```env
GOOGLE_CREDENTIALS_PATH=v2/credentials.json
GOOGLE_SHEET_ID=your_spreadsheet_id
GMAIL_FROM=your@gmail.com
WEBHOOK_SLACK_URL=https://hooks.slack.com/...
POLLING_INTERVAL_MINUTES=5
```

---

## 7. 산출물 파일 목록

| 파일 | 설명 | 재사용 가능 여부 |
|------|------|----------------|
| `src/run_proposal.py` | CLI 진입점 | ✅ 그대로 사용 |
| `src/run_batch_proposals.py` | 배치 처리 | ✅ 그대로 사용 |
| `outputs/리팅성형외과_마케팅제안서_202603.html` | 웹용 제안서 (CSS Grid) | 📋 디자인 참조 |
| `outputs/리팅성형외과_마케팅제안서_202603_email.html` | 이메일 호환 제안서 | ✅ 템플릿으로 재사용 |
| `outputs/리팅성형외과_Step1_데이터분석.md` | 상권분석 출력 예시 | 📋 참조용 |
| `outputs/리팅성형외과_Step2_마케팅전략.md` | 전략 출력 예시 | 📋 참조용 |
| `marketing_proposal_automation.md` | 에이전트 프롬프트 전체 | ✅ 프롬프트 재사용 |
| `docs/v2_plan.md` | V2 상세 계획 | 📋 구현 가이드 |

---

## 8. 다른 프로젝트에서 재사용하는 방법

### A. 이메일 HTML 생성 재사용

1. `outputs/리팅성형외과_마케팅제안서_202603_email.html` 을 **템플릿**으로 사용
2. 섹션 4의 **이메일 호환 규칙** 반드시 준수
3. 배경색 변환 스크립트(`fix_email_table_bg`) 재사용 가능

### B. 4단계 파이프라인 재사용

```python
# 다른 프로젝트에서 V1 파이프라인 호출
import subprocess

result = subprocess.run([
    "python", "H:/inbound/src/run_proposal.py",
    "--client-name", client_name,
    "--industry", industry,
    "--region", region,
    "--budget-range", budget,
    "--backend", "openai",
    "--output-format", "html"
], capture_output=True, text=True)
```

### C. 법규 검사 로직 재사용

`marketing_proposal_automation.md` 내 법규 준수 섹션의 금지어/권장어 리스트를 그대로 복사해서 사용.

---

## 9. 주요 기술 결정 사항 (ADR)

| 결정 | 이유 |
|------|------|
| 이메일 HTML에 `<table>` 레이아웃 사용 | Gmail/Outlook에서 Grid/Flex 미지원 |
| 2열 td 너비 `width="290"` 고정값 사용 | `width="48%"` + padding = 컨테이너 초과 버그 |
| `bgcolor` 속성 + CSS 둘 다 명시 | Gmail이 table의 CSS background-color 무시 |
| 메인 td에 `align="left"` 명시 | 상위 `align="center"` 가 텍스트까지 상속됨 |
| 폰트 `Arial,'Malgun Gothic',sans-serif` | 이메일 클라이언트 웹폰트 미지원 |
| 이메일 컨테이너 너비 680px | 이메일 표준 권장 너비 |
| Python mock 백엔드 제공 | OpenAI API 없이도 테스트 가능 |
| Quality Gates 7개 자동 검사 | 법규 위반 카피 자동 차단 |

---

*이 문서는 `H:\inbound\docs\PROJECT_REFERENCE.md` 에 저장됩니다.*
*V2 상세 계획은 `H:\inbound\docs\v2_plan.md` 참조.*
