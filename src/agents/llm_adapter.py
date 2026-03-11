"""LLM adapter layer with mock and OpenAI-compatible backends."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import time
from typing import Protocol
from urllib import request, error


class LLMAdapter(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class MockLLMAdapter:
    """Deterministic fallback backend for local development and tests."""

    def generate(self, prompt: str) -> str:
        preview = "\n".join(prompt.splitlines()[:8]).strip()
        return (
            "[MOCK_GENERATED]\n"
            "출처: 내부 템플릿\n"
            "기준일: 2026-03-09\n"
            "KPI: CTR 2.2%, CVR 3.1%, ROAS 280%\n"
            "30-60-90 실행 계획 포함\n\n"
            f"요약:\n{preview}\n"
        )


@dataclass(frozen=True)
class OpenAIResponsesAdapter:
    """Minimal OpenAI Responses API client via stdlib urllib.

    Required env vars:
    - OPENAI_API_KEY
    Optional env vars:
    - OPENAI_MODEL (default: gpt-4.1-mini)
    - OPENAI_BASE_URL (default: https://api.openai.com/v1)
    """

    model: str = "gpt-4.1-mini"
    timeout_sec: int = 60
    max_retries: int = 2
    retry_backoff_sec: float = 1.0

    def generate(self, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("OPENAI_MODEL", self.model)

        payload = {
            "model": model,
            "input": prompt,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{base_url}/responses",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        parsed = self._request_with_retries(req)

        text = parsed.get("output_text")
        if isinstance(text, str) and text.strip():
            return text.strip()

        # Fallback parser for unexpected response shape.
        output = parsed.get("output", [])
        chunks: list[str] = []
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content", [])
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            txt = part.get("text")
                            if isinstance(txt, str):
                                chunks.append(txt)
        if chunks:
            return "\n".join(chunks).strip()
        raise RuntimeError("OpenAI API response did not contain text output.")

    def _request_with_retries(self, req: request.Request) -> dict:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with request.urlopen(req, timeout=self.timeout_sec) as resp:
                    body = resp.read().decode("utf-8")
                    return json.loads(body)
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                status = exc.code
                retryable = status in {408, 409, 429, 500, 502, 503, 504}
                last_error = RuntimeError(f"OpenAI API HTTPError: {status} {detail}")
                if not retryable or attempt >= self.max_retries:
                    raise last_error from exc
            except error.URLError as exc:
                last_error = RuntimeError(f"OpenAI API URLError: {exc.reason}")
                if attempt >= self.max_retries:
                    raise last_error from exc

            delay = self.retry_backoff_sec * (2**attempt)
            time.sleep(delay)

        raise RuntimeError(f"OpenAI API request failed: {last_error}")


def make_llm_adapter(backend: str) -> LLMAdapter:
    name = (backend or "mock").strip().lower()
    if name == "openai":
        return OpenAIResponsesAdapter()
    if name == "mock":
        return MockLLMAdapter()
    raise ValueError(f"Unsupported backend: {backend}. Use 'mock' or 'openai'.")
