# damhaDB 프로젝트 레퍼런스

> 병원 마케팅 전문 에이전시 **담하(DAMHA)**의 DB 수집 랜딩 페이지 프로젝트
> 마지막 업데이트: 2026-03-11

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | damha-landing (damhaDB) |
| **목적** | 병원/의원 대상 마케팅 무료 진단 신청 DB 수집 |
| **타입** | SPA (Single Page Application) — React 랜딩 페이지 |
| **배포** | Vercel (GitHub 연동 자동 배포) |
| **GitHub** | `https://github.com/damha-web/damhaDB` |
| **도메인** | `damha.co.kr` (예정) |

---

## 2. 기술 스택

| 카테고리 | 기술 | 버전 |
|----------|------|------|
| **프레임워크** | React | 19.2.0 |
| **빌드 도구** | Vite | 7.x |
| **스타일링** | TailwindCSS | 3.4.x |
| **아이콘** | lucide-react | 0.562.x |
| **CSS 후처리** | PostCSS + Autoprefixer | — |
| **코드 품질** | ESLint | 9.x |
| **배포 플랫폼** | Vercel | — |
| **데이터 저장** | Google Sheets (Apps Script) | — |

---

## 3. 프로젝트 구조

```
damhaDB/
├── public/                     # 정적 에셋 (빌드 시 그대로 복사)
│   ├── logo.png                # 담하 로고 (4.5KB)
│   ├── sub.png                 # 서브 이미지 (89KB)
│   ├── footer_certification.png # 푸터 인증 마크 (210KB)
│   ├── robots.txt              # 검색엔진 크롤러 설정
│   └── sitemap.xml             # 사이트맵
│
├── src/
│   ├── main.jsx                # React 엔트리 포인트
│   ├── App.jsx                 # App 루트 컴포넌트 (DamhaLanding 렌더링)
│   ├── App.css                 # 최소 글로벌 스타일
│   ├── index.css               # TailwindCSS 임포트 + 스크롤바 커스텀
│   ├── DamhaLanding.jsx        # ★ 메인 랜딩 페이지 컴포넌트 (626줄)
│   └── assets/                 # React 에셋
│
├── index.html                  # HTML 템플릿 (SEO 메타태그 포함)
├── package.json                # 의존성 및 스크립트
├── vite.config.js              # Vite 설정
├── tailwind.config.js          # TailwindCSS 설정 (커스텀 애니메이션)
├── postcss.config.js           # PostCSS 설정
├── vercel.json                 # Vercel 배포 설정
├── eslint.config.js            # ESLint 설정
├── .env                        # 환경변수 (Git 미추적, 로컬 전용)
├── .env.example                # 환경변수 템플릿
└── .gitignore                  # Git 제외 목록
```

---

## 4. 핵심 컴포넌트: DamhaLanding.jsx

전체 랜딩 페이지가 하나의 파일(`DamhaLanding.jsx`, 626줄)에 구현되어 있습니다.

### 4-1. 페이지 섹션 구성

| 순서 | 섹션 | 설명 |
|------|------|------|
| 1 | **Navigation** | 고정 헤더 (스크롤 시 배경 변경), 모바일 햄버거 메뉴 |
| 2 | **Hero** | 메인 타이틀 + CTA 버튼 ("성과 무료 진단하기") |
| 3 | **Stats** | 핵심 성과 지표 3개 (+215%, 3.5배, 450%) |
| 4 | **Why DAMHA** | 서비스 차별점 카드 3개 |
| 5 | **Inquiry Form** | ★ DB 수집 폼 (핵심 기능) |
| 6 | **Footer** | 회사 정보 + 인증 마크 |

### 4-2. 회사 정보 설정 (수정 가능)

```javascript
const CONTACT_INFO = {
    companyName: "주식회사 담하",
    representative: "정승우",
    registrationNumber: "187-88-02337",
    address: "부산광역시 동래구 연안로59번길 7, 5층",
    email: "contact@damha.co.kr",
    tel: "051-757-0719"
};
```

### 4-3. 타겟 옵션 (수정 가능)

```javascript
const targetOptions = ["10대", "20대", "30대", "40대 이상", "직장인", "지역주민", "수험생", "기타"];
```

---

## 5. 데이터 수집 흐름 (핵심)

### 5-1. 전체 데이터 플로우

```
[사용자 브라우저]
    ↓ 폼 입력 (병원명, 지역, 타겟, 이메일)
    ↓ POST 요청
[Google Apps Script Web App]
    ↓ 데이터 파싱 및 저장
[Google Sheets]
    ↓ 행 추가 (타임스탬프 자동 생성)
[관리자가 시트에서 확인]
```

### 5-2. 수집 데이터 필드

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| `companyName` | string | ✅ | 병원/기업명 | "담하치과" |
| `location` | string | ✅ | 지역/주소 | "서울 강남구" |
| `targets` | string[] | ✅ (1개 이상) | 주요 타겟 고객층 | ["20대", "30대", "직장인"] |
| `email` | string | ✅ (형식 검증) | 제안서 수신 이메일 | "test@example.com" |

### 5-3. 폼 유효성 검사

| 검사 항목 | 적용 방법 |
|-----------|-----------|
| 공백만 입력 방지 | `trim()` 후 빈 문자열 체크 |
| 타겟 최소 1개 선택 | `targets.length === 0` 검사 |
| 이메일 형식 검증 | 실시간 정규식 검증 (입력 시마다 체크) |
| 개인정보 동의 필수 | `isAgreed` 체크 안 하면 제출 버튼 비활성화 |
| GOOGLE_SCRIPT_URL 검증 | 환경변수 미설정 시 에러 메시지 표시 |

### 5-4. API 호출 방식

```javascript
// Google Apps Script 호출
const response = await fetch(GOOGLE_SCRIPT_URL, {
    method: 'POST',
    headers: {
        // ★ 핵심: text/plain을 사용하여 CORS Preflight 방지
        'Content-Type': 'text/plain;charset=utf-8',
    },
    body: JSON.stringify({
        companyName: formData.companyName,
        location: formData.location,
        targets: finalTargets,     // 배열 → "20대, 30대" 형태
        email: formData.email,
    }),
    redirect: 'follow',            // Apps Script 리다이렉트 자동 처리
});
```

**핵심 포인트:**
- `Content-Type: text/plain` → CORS Preflight(OPTIONS) 요청을 우회
- `redirect: 'follow'` → Apps Script의 302 리다이렉트를 자동 처리
- 응답은 JSON: `{ success: true/false, message?: string }`

### 5-5. "기타" 타겟 처리

사용자가 "기타"를 선택하면 커스텀 입력 필드가 나타나며, 전송 시 `기타(사용자입력값)` 형태로 병합됩니다.

```javascript
const finalTargets = formData.targets.map(t =>
    (t === '기타' && formData.customTarget) ? `기타(${formData.customTarget})` : t
);
```

---

## 6. 환경 변수

| 변수명 | 용도 | 필수 | 설정 위치 |
|--------|------|------|-----------|
| `VITE_GOOGLE_SCRIPT_URL` | Google Apps Script 웹 앱 URL | ✅ | `.env` (로컬), Vercel Environment Variables (배포) |

### 로컬 설정

```bash
# .env 파일 생성
VITE_GOOGLE_SCRIPT_URL=https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec
```

### Vercel 배포 설정

Vercel 대시보드 → Project → Settings → Environment Variables에서 동일 키-값 등록 후 재배포(Redeploy) 필요.

---

## 7. UI/UX 디자인 시스템

### 7-1. 컬러 팔레트

| 용도 | 클래스 | 색상 |
|------|--------|------|
| **포인트 컬러** | `orange-600` / `#ea580c` | 주황 (CTA, 포커스, 체크박스) |
| **호버** | `orange-700` | 어두운 주황 |
| **배경** | `stone-50` | 밝은 베이지 |
| **텍스트 (본문)** | `stone-900` | 진한 갈색-검정 |
| **텍스트 (보조)** | `stone-500` | 중간 회색 |
| **카드 배경** | `white` / `stone-100` | 흰색~밝은 베이지 |
| **에러** | `red-500` | 빨강 |
| **성공** | `green-500` | 초록 |

### 7-2. 주요 인터랙션

- **헤더**: 스크롤 50px 이후 → 투명 → 흰색 글래스모피즘(`backdrop-blur-md`)
- **Floating Label**: 입력 필드 포커스 시 라벨이 상단으로 애니메이션 이동
- **타겟 태그**: 클릭으로 토글, 선택 시 `orange-600` 보더 + 배경
- **제출 버튼**: `isAgreed` false일 때 `disabled` (회색 처리)
- **성공 화면**: 폼 제출 성공 시 체크마크 + 안내 메시지로 전환

### 7-3. 반응형 브레이크포인트

| 브레이크포인트 | 대상 | 주요 변경 |
|---------------|------|-----------|
| `< md (768px)` | 모바일 | 햄버거 메뉴, 세로 스택 레이아웃 |
| `≥ md (768px)` | 태블릿 이상 | 가로 그리드, 데스크탑 네비게이션 |
| `≥ lg (1024px)` | 데스크탑 | 2컬럼 폼 레이아웃 |

---

## 8. SEO 설정

### index.html 메타태그

```html
<title>주식회사 담하 - 병원 마케팅의 정답</title>
<meta name="description" content="철저한 데이터 분석과 타겟 최적화..." />
<meta property="og:title" content="주식회사 담하 - 데이터로 증명하는 병원 마케팅" />
<meta property="og:description" content="감에 의존하는 광고는 끝났습니다..." />
<meta property="og:type" content="website" />
<meta property="og:image" content="/og-image.png" />
<meta property="og:url" content="https://damha.co.kr" />
<meta name="twitter:card" content="summary_large_image" />
```

### SEO 파일

- `public/robots.txt` — 모든 크롤러 허용
- `public/sitemap.xml` — 메인 페이지 등록

---

## 9. 배포 설정

### Vercel (`vercel.json`)

```json
{
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "framework": "vite",
    "rewrites": [
        { "source": "/api/(.*)", "destination": "/api/$1" }
    ]
}
```

### 빌드 결과 (Production)

| 파일 | 크기 | Gzip |
|------|------|------|
| `index.html` | 1.44 KB | 0.68 KB |
| `index-*.css` | ~28 KB | ~5.3 KB |
| `index-*.js` | ~216 KB | ~68 KB |

---

## 10. 개인정보 처리

### 수집 항목 및 고지 내용 (폼 내 표시됨)

| 항목 | 내용 |
|------|------|
| **수집 항목** | 병원/기업명, 지역, 주요 타겟, 이메일 |
| **수집 목적** | 맞춤형 마케팅 제안서 발송 및 컨설팅 |
| **보유 기간** | 제안서 발송 완료 후 6개월 (이후 파기) |
| **동의 방식** | 체크박스 필수 동의 (미동의 시 제출 불가) |

"개인정보 수집 및 이용" 링크 클릭 시 상세 안내 패널이 토글됩니다.

---

## 11. 로컬 개발 가이드

### 설치 및 실행

```bash
# 1. 의존성 설치
npm install

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 열고 실제 Google Apps Script URL 입력

# 3. 개발 서버 실행
npm run dev
# → http://localhost:5173/

# 4. 프로덕션 빌드
npm run build
# → dist/ 폴더에 생성
```

### npm scripts

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | Vite 개발 서버 실행 (HMR) |
| `npm run build` | 프로덕션 빌드 |
| `npm run preview` | 빌드 결과 미리보기 |
| `npm run lint` | ESLint 실행 |

---

## 12. 다른 프로젝트 연동 시 참고사항

### 12-1. 이 프로젝트의 데이터를 다른 시스템에서 활용하려면

- **Google Sheets API**를 통해 수집된 데이터를 읽을 수 있습니다.
- **Google Apps Script에 Webhook 추가**: 폼 제출 시 다른 서버로 POST 요청을 보내도록 Apps Script를 수정할 수 있습니다.

### 12-2. 이 프로젝트의 폼을 다른 사이트에 재사용하려면

1. `DamhaLanding.jsx` 에서 `InquiryForm` 컴포넌트 부분(약 330~626줄)을 별도 파일로 분리
2. `CONTACT_INFO`, `targetOptions` 상수를 props로 변경
3. `VITE_GOOGLE_SCRIPT_URL` 환경변수를 새 프로젝트에 동일하게 설정

### 12-3. 자동 제안서 생성 파이프라인 연동 (계획됨)

```
[damhaDB 폼 제출]
    ↓ Google Sheets 저장
    ↓ Webhook POST (Apps Script → Python 서버)
[inbound 프로젝트 - AI 제안서 생성 파이프라인]
    ↓ 4단계 AI 에이전트가 맞춤형 제안서 HTML 생성
    ↓ Gmail API로 자동 발송
[고객 이메일 수신]
```

관련 프로젝트: `h:\inbound` (Python, AI 제안서 생성 V1 파이프라인)

---

## 13. 보안 주의사항

| 항목 | 상태 | 설명 |
|------|------|------|
| `.env` 파일 | ✅ `.gitignore` | Git에 커밋되지 않음 |
| Firebase JSON | ✅ `.gitignore` | `cool-ea4bc-firebase-adminsdk-*.json` 패턴 제외 |
| `console.log` | ✅ 제거됨 | 프로덕션에 디버그 로그 없음 |
| `alert()` | ✅ 제거됨 | 인라인 에러 메시지로 대체 |
| 에러 메시지 | ✅ 사용자 친화적 | 내부 정보 미노출 |

---

*이 문서는 damhaDB 프로젝트의 현재 상태를 기준으로 작성되었습니다.*
