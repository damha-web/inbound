# AI 맞춤형 마케팅 제안서 생성 시스템 Design Document

> Version: 1.0.0 | Created: 2026-03-09 | Status: Draft

## 1. Overview (개요)
본 시스템은 고객사 정보를 입력받아 `Research -> Consult -> Content -> Style`의 순차적 에이전트 협업을 통해 최종 마케팅 제안서를 생성합니다. 모든 결과물은 표(Table) 없이 리스트와 인용구 기반의 이메일 호환 레이아웃을 따릅니다.

## 2. System Architecture (시스템 구조)

### 2.1. Agent Workflow
1.  **Input**: 고객사명, 위치(옵션), 타겟팅, 광고예산
2.  **Research Agent**: 웹 검색을 통한 주소 확인, 상권 분석, 30km 내 경쟁사(Top 4) 발굴 및 평판 조사
3.  **Consultant Agent**: 리서치 데이터를 바탕으로 채널별(플레이스/블로그/SNS) 진단 및 마케팅 믹스 전략 수립
4.  **Content Agent**: 전략에 기반한 핵심 메시지 도출 및 4주간의 콘텐츠 로드맵(의료법 준수) 작성
5.  **Styling Agent**: 최종 텍스트를 6단계 제안서 템플릿에 맞춰 시각화 및 톤앤매너 보정

## 3. Data Model (데이터 모델)

### 3.1. Agent Data Schema (JSON)
```typescript
interface MarketingProposalData {
  client: {
    name: string;
    address: string;
    mainService: string; // 진료과목/주력메뉴
    reputation: string; // 평판/리뷰 요약
  };
  marketAnalysis: {
    geography: string;
    demand: string; // 배후 수요
    competitors: Array<{
      name: string;
      location: string;
      strengths: string[];
      keywords: string[];
    }>;
  };
  strategy: {
    channels: Array<{ name: string; reason: string; priority: number }>;
    diagnostics: {
      place: string;
      blog: string;
      sns: string;
    };
  };
  branding: {
    tone: string;
    coreMessage: string;
    copies: string[];
  };
  calendar: Array<{
    week: number;
    theme: string;
    contents: Array<{
      channel: string;
      hook: string;
      message: string;
      cta: string;
    }>;
  }>;
}
```

## 4. Agent Personas (에이전트 정의)

### 4.1. Data Research Agent
-   **Role**: 정밀 시장 조사관
-   **Task**: Google/Naver 검색을 활용하여 고객사의 정확한 위치와 반경 30km 내 상위 경쟁사를 리서치.
-   **Focus**: 주소 확인, 유동 인구, 배후 세대, 경쟁사 키워드, 네이버 플레이스 순위.

### 4.2. Marketing Consultant Agent
-   **Role**: 전략 컨설턴트
-   **Task**: 리서치 데이터를 바탕으로 타겟 맞춤형 온/오프라인 채널 비중 결정 및 진단.
-   **Focus**: ROI 극대화, 채널별 약점 보완 전략, 예산 최적화 배분.

### 4.3. Content Planner Agent
-   **Role**: 전문 콘텐츠 기획자
-   **Task**: 마케팅 전략을 실행 가능한 4주간의 콘텐츠 캘린더로 변환.
-   **Focus**: 제목(Hook)의 매력도, 의료법 준수 표현, 명확한 CTA.

### 4.4. Styling Expert Agent
-   **Role**: 브랜드 경험 디자이너
-   **Task**: 모든 텍스트를 "표(Table) 없이" 시각적으로 풍부한 웹 브로슈어 스타일로 변환.
-   **Focus**: 이모지 활용, 불렛 포인트 가독성, 프리미엄 톤앤매너 유지.

## 5. UI/Layout Design Rules (제안서 시각화 규칙)
-   **No Tables**: 모든 데이터는 `###` 헤더와 `-` 불렛 포인트로 표시.
-   **Visual Blocks**: 인용구(`>`)를 사용하여 핵심 인사이트 강조.
-   **Visual Hierarchy**: `##` (섹션), `###` (소주제), `**Bold**` (강조어) 체계 엄수.
-   **Email Compatibility**: 복잡한 스크립트 없이 순수 마크다운/HTML 스타일 유지.

## 6. Test Plan (검증 계획)
-   **검증 1**: 반경 30km 내 실제 경쟁사가 리서치 되는가?
-   **검증 2**: 의료법 위반 표현(최고, 유일 등)이 포함되지 않았는가?
-   **검증 3**: 모든 출력물에 표(Table)가 하나도 없는가?
