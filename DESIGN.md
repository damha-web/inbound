# Project Design Document

## 1. 개요 (Overview)

- **프로젝트명:** 마케팅 제안서 자동화 시스템
- **V1:** AI 4단계 파이프라인 (Python CLI)으로 제안서 생성
- **V2 (자동화2):** damhaDB 데이터 수집 + V1 파이프라인 + 웹 대시보드 통합

> **[Global AI Instruction]**
> - **최신 UI 우선 안내:** 외부 플랫폼(Google Cloud, Railway, Vercel 등) 설정 방법을 설명할 때는 **반드시 가장 최신 버전의 UI/UX를 기준**으로 단계별 설명을 제공할 것.
> - **불확실 시 검색 도입:** UI가 자주 변경되는 서비스의 경우, 웹 검색이나 최신 문서를 교차 검증하여 답변할 것.

## 2. 기술 스택 (Tech Stack)

### V1 (기존)
- Python, OpenAI GPT-4.1-mini, Markdown/HTML 렌더링

### V2 (자동화2)
- **Frontend:** React 19 + Vite 7 + TailwindCSS 3 + lucide-react
- **Backend:** Python FastAPI + Google Sheets API + Gmail API
- **AI Engine:** V1 파이프라인 재사용 (subprocess 호출)
- **인증:** JWT (관리자 단일 계정)

## 3. 주요 기능 (Features)

1. Google Sheets 수집 데이터 조회 (정렬/필터/검색)
2. AI 제안서 자동 생성 (비동기 Background Task)
3. 제안서 미리보기 (데스크탑/모바일 뷰)
4. Gmail API를 통한 이메일 발송
5. 발송 상태 추적 (시트 자동 업데이트)

## 4. 구조 (Architecture & Directory)

```
H:\inbound\
├── src/agents/          # V1 AI Pipeline
├── v2/
│   ├── backend/         # FastAPI (Port 8000)
│   │   ├── main.py
│   │   ├── routers/     # submissions, proposals, email
│   │   └── services/    # sheets, proposal, email, auth
│   └── frontend/        # React + Vite (Port 5173)
│       └── src/
│           ├── pages/   # Login, Dashboard, ProposalPreview
│           └── components/ # Layout, StatusBadge
```
