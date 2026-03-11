"""Render proposal package into markdown or HTML."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from .config import ProposalPolicy
from .proposal_generator import ProposalPackage


@dataclass(frozen=True)
class RenderedOutputs:
    markdown: str
    html: str


def render_markdown(package: ProposalPackage) -> str:
    return (
        "# AI 맞춤형 마케팅 제안서\n\n"
        "## 1. 정밀 상권 및 포지션 분석\n"
        f"{package.research.strip()}\n\n"
        "## 2. 브랜딩 및 마케팅 추천 전략\n"
        f"{package.strategy.strip()}\n\n"
        "## 3. 브랜드 방향성 및 콘텐츠\n"
        f"{package.brand_content.strip()}\n\n"
        "## 4. 최종 시각화 문서\n"
        f"{package.styled_document.strip()}\n"
    ).strip()


def render_html(package: ProposalPackage, policy: ProposalPolicy) -> str:
    table_hint = (
        "<p style='margin:0;color:#5a6b88;'>표 정책: 허용</p>"
        if policy.allow_tables
        else "<p style='margin:0;color:#5a6b88;'>표 정책: 금지(카드/리스트만 사용)</p>"
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI 맞춤형 마케팅 제안서</title>
</head>
<body style="margin:0;background:#f5f7fb;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:980px;margin:0 auto;padding:20px;">
    <div style="background:#1A2B48;color:#fff;padding:18px 20px;border-radius:12px;">
      <h1 style="margin:0;font-size:24px;">AI 맞춤형 마케팅 제안서</h1>
      {table_hint}
    </div>
    {_section_card("1. 정밀 상권 및 포지션 분석", package.research)}
    {_section_card("2. 브랜딩 및 마케팅 추천 전략", package.strategy)}
    {_section_card("3. 브랜드 방향성 및 콘텐츠", package.brand_content)}
    {_section_card("4. 최종 시각화 문서", package.styled_document)}
  </div>
</body>
</html>"""


def render_outputs(package: ProposalPackage, policy: ProposalPolicy) -> RenderedOutputs:
    return RenderedOutputs(
        markdown=render_markdown(package),
        html=render_html(package, policy=policy),
    )


def _section_card(title: str, body: str) -> str:
    safe_title = escape(title)
    safe_body = (
        escape(body.strip())
        .replace("\n\n", "<br /><br />")
        .replace("\n", "<br />")
    )
    return (
        "<section style='margin-top:16px;background:#fff;border:1px solid #e3e9f2;"
        "border-left:6px solid #C5A059;border-radius:10px;padding:16px;'>"
        f"<h2 style='margin:0 0 10px 0;color:#1A2B48;font-size:20px;'>{safe_title}</h2>"
        f"<div style='color:#22324f;line-height:1.65;font-size:14px;'>{safe_body}</div>"
        "</section>"
    )
