# 🚀 마케팅 제안서 자동화 시스템 V2 계획안

**작성일:** 2026-03-10
**기반:** V1 (H:\inbound) 완료 기준
**목표:** 웹 폼 입력 → 구글 시트 수집 → 제안서 생성 → Gmail 자동 발송 → 웹훅 알림

---

## 🔄 V2 전체 플로우

```
[고객사 담당자]
      │
      ▼
① 웹 수집 폼 (Google Forms / 자체 HTML)
      │  입력: 고객사명, 주소, 업종, 타겟, 예산 등
      ▼
② Google Spreadsheet (자동 저장)
      │  Apps Script 트리거 or Python Polling
      ▼
③ 제안서 생성 엔진 (V1 파이프라인 재사용)
   Step 1: 상권/경쟁사 분석
   Step 2: 마케팅 전략
   Step 3: 브랜딩/카피
   Step 4: HTML 이메일 제안서 생성
      │
      ▼
④ Gmail API 자동 발송
   - 수신: 고객사 이메일
   - 본문: email.html 제안서 (인라인)
   - 첨부: 원본 html 파일
      │
      ▼
⑤ 웹훅 알림 (발송 완료)
   - Slack / Discord / 카카오톡 알림
   - 발송 결과 로그 시트에 기록
```

---

## 📁 V2 디렉토리 구조

```
H:\inbound\
├── v1/                          ← V1 전체 보존 (그대로 유지)
│   ├── src/
│   ├── outputs/
│   └── ...
│
└── v2/                          ← V2 신규 작업 폴더
    ├── web/
    │   └── intake_form.html     ← 자체 수집 폼 (Google Forms 대안)
    ├── src/
    │   ├── sheet_monitor.py     ← Google Sheets 폴링/트리거
    │   ├── proposal_runner.py   ← V1 파이프라인 호출
    │   ├── email_sender.py      ← Gmail API 발송
    │   ├── webhook_notifier.py  ← 웹훅 알림
    │   └── main_pipeline.py     ← 전체 오케스트레이터
    ├── templates/
    │   └── email_wrapper.html   ← 발송용 이메일 래퍼
    ├── logs/
    │   └── dispatch_log.json    ← 발송 기록
    ├── .env.v2                  ← V2 전용 환경변수
    └── README_v2.md
```

---

## 🧩 컴포넌트별 상세

### ① 웹 수집 폼

**옵션 A: Google Forms** (권장 - 빠른 구현)
- 구글 폼 생성 → 응답이 자동으로 Google Sheets에 저장
- 커스텀 브랜딩 불가 (기본 UI)

**옵션 B: 자체 HTML 폼 + Google Apps Script**
- 커스텀 디자인 가능
- 폼 제출 → Apps Script → Sheets 저장
- 호스팅 필요 (GitHub Pages / Netlify 무료 가능)

**수집 필드:**
```
- 고객사명 *
- 담당자명 *
- 이메일 주소 * (제안서 수신)
- 업체 주소 (시/구 단위) *
- 주요 업종 * (드롭다운: 병원/카페/뷰티/음식점/기타)
- 핵심 서비스/상품 *
- 주요 타겟층 * (드롭다운: 20대/30대/40-50대/전연령)
- 월 예산 범위 (선택)
- 현재 고민 / 추가 요청사항 (선택)
```

---

### ② Google Spreadsheet 연동

**시트 구조:**
| 접수번호 | 접수일시 | 고객사명 | 이메일 | 주소 | 업종 | ... | 처리상태 | 발송일시 |
|--------|--------|--------|------|-----|-----|-----|--------|--------|
| 001 | 2026-03-10 | 리팅성형외과 | ... | ... | 의료 | ... | 대기 | - |

**트리거 방식 (2가지):**

**방식 A: Google Apps Script (onFormSubmit 트리거)**
```javascript
// Apps Script: 폼 제출 시 자동으로 Python 서버 웹훅 호출
function onFormSubmit(e) {
  const row = e.values;
  UrlFetchApp.fetch('http://your-server/trigger', {
    method: 'POST',
    payload: JSON.stringify({ data: row })
  });
}
```

**방식 B: Python Polling (서버 불필요)**
```python
# 5분마다 시트 체크 → 처리상태='대기' 행 자동 처리
import schedule
schedule.every(5).minutes.do(check_new_submissions)
```

---

### ③ 제안서 생성 엔진 (V1 재사용)

```python
# v2/src/proposal_runner.py
import subprocess
import sys

def generate_proposal(client_data: dict) -> str:
    """V1 파이프라인 호출하여 email.html 생성"""
    result = subprocess.run([
        sys.executable,
        'v1/src/run_proposal.py',
        '--client-name', client_data['company'],
        '--industry', client_data['industry'],
        '--region', client_data['address'],
        '--target-segments', client_data['target'],
        '--budget-range', client_data.get('budget', '미정'),
        '--backend', 'openai',
        '--output-format', 'html'
    ], capture_output=True, text=True)

    # email.html 경로 반환
    return find_latest_html(client_data['company'])
```

---

### ④ Gmail API 자동 발송

**설정 필요:**
- Google Cloud Console → Gmail API 활성화
- OAuth 2.0 인증 또는 서비스 계정
- `credentials.json` 발급

```python
# v2/src/email_sender.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

def send_proposal_email(to_email: str, company_name: str, html_path: str):
    """Gmail API로 제안서 발송"""
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'[마케팅 제안서] {company_name} 맞춤 마케팅 전략'
    msg['From'] = 'your@gmail.com'
    msg['To'] = to_email

    # HTML 본문 (이메일 호환 버전)
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # 발송
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return True
```

---

### ⑤ 웹훅 알림

**지원 대상 (선택 적용):**

| 플랫폼 | 방식 | 난이도 |
|--------|------|--------|
| **Slack** | Incoming Webhook URL | ⭐ 쉬움 |
| **Discord** | Webhook URL | ⭐ 쉬움 |
| **카카오톡** | 카카오 알림톡 API | ⭐⭐ 중간 |
| **커스텀 서버** | HTTP POST | ⭐ 쉬움 |

```python
# v2/src/webhook_notifier.py
import requests

def notify(webhook_url: str, company: str, email: str, status: str):
    payload = {
        "text": f"📧 제안서 발송 완료\n고객사: {company}\n수신: {email}\n상태: {status}"
    }
    requests.post(webhook_url, json=payload)
```

---

### 🔧 메인 오케스트레이터

```python
# v2/src/main_pipeline.py
def process_submission(row: dict):
    company = row['고객사명']
    email = row['이메일']

    try:
        # 1. 제안서 생성
        update_status(row['접수번호'], '생성중')
        html_path = generate_proposal(row)

        # 2. Gmail 발송
        update_status(row['접수번호'], '발송중')
        send_proposal_email(email, company, html_path)

        # 3. 웹훅 알림
        notify(WEBHOOK_URL, company, email, '✅ 발송완료')

        # 4. 시트 상태 업데이트
        update_status(row['접수번호'], '완료', sent_at=now())

    except Exception as e:
        notify(WEBHOOK_URL, company, email, f'❌ 오류: {e}')
        update_status(row['접수번호'], '오류')
```

---

## 🔐 V2 환경변수 (.env.v2)

```env
# Google API
GOOGLE_CREDENTIALS_PATH=v2/credentials.json
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_SHEET_NAME=제안서요청

# Gmail
GMAIL_FROM=your@gmail.com
GMAIL_TOKEN_PATH=v2/token.json

# 웹훅 (사용할 것 선택)
WEBHOOK_SLACK_URL=https://hooks.slack.com/...
WEBHOOK_DISCORD_URL=https://discord.com/api/webhooks/...

# OpenAI (V1과 공유)
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini

# 처리 설정
POLLING_INTERVAL_MINUTES=5
PROPOSAL_OUTPUT_DIR=v2/outputs
```

---

## 📅 구현 단계 (권장 순서)

| 단계 | 작업 | 예상 소요 |
|------|------|---------|
| **Phase 1** | V2 폴더 구조 생성, Google Forms + Sheets 연동 테스트 | 1일 |
| **Phase 2** | sheet_monitor.py 구현 (폴링 or Apps Script) | 1일 |
| **Phase 3** | proposal_runner.py (V1 파이프라인 호출) | 0.5일 |
| **Phase 4** | Gmail API 인증 설정 + email_sender.py | 1일 |
| **Phase 5** | webhook_notifier.py + main_pipeline.py 통합 | 0.5일 |
| **Phase 6** | 엔드투엔드 테스트 (폼 → 시트 → 생성 → 발송 → 알림) | 1일 |

---

## ⚠️ 주요 고려사항

- **Google API 인증:** OAuth 2.0 초기 설정 필요 (브라우저 1회 인증)
- **OpenAI 비용:** 제안서 1건당 gpt-4.1-mini 기준 약 $0.01~0.05
- **처리 시간:** 제안서 생성 2~5분 소요 → 비동기 처리 필요
- **이메일 스팸 방지:** Gmail 발신자 도메인 SPF/DKIM 설정 권장
- **폼 스팸 방지:** reCAPTCHA 또는 Google Forms 기본 스팸 필터 활용

---

## 🔗 관련 파일

- V1 소스: `H:\inbound\src\`
- V1 이메일 호환 제안서: `H:\inbound\outputs\리팅성형외과_마케팅제안서_202603_email.html`
- V1 계획 문서: `H:\inbound\marketing_proposal_automation.md`
- 메모리: `C:\Users\yap18\.claude\projects\H--inbound\memory\MEMORY.md`
