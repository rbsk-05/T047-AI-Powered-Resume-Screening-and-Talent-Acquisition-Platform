"""Provider abstraction for Resume Analysis Agent (Gemini & Fallback)."""

from abc import ABC, abstractmethod
import json
import logging
import re
from typing import Any

import httpx

from app.core.config import get_settings
from app.resume.agent.prompts import RESUME_AGENT_SYSTEM_PROMPT, RESUME_AGENT_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class BaseResumeProvider(ABC):
    """Abstract Base Provider for Resume Analysis."""

    @abstractmethod
    def extract(self, resume_text: str, deterministic_context: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        """Extract structured resume dictionary.

        Returns (extracted_dict, analysis_method).
        """
        pass


class FallbackProvider(BaseResumeProvider):
    """Deterministic regex & heuristic fallback provider when LLM is unavailable or fails."""

    def extract(self, resume_text: str, deterministic_context: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        # Form basic work experience entries from raw experience lines
        raw_exp = deterministic_context.get("raw_experience", [])
        work_exp = []
        for line in raw_exp:
            if re.search(r"\b(19|20)\d{2}\b", line):
                work_exp.append({"duration_text": line})
            elif len(line) > 5:
                work_exp.append({"company": line})

        # Form basic education entries
        raw_edu = deterministic_context.get("raw_education", [])
        education = [{"degree": line} for line in raw_edu] if raw_edu else []

        # Form basic projects
        raw_proj = deterministic_context.get("raw_projects", [])
        projects = [{"name": line} for line in raw_proj] if raw_proj else []

        # Form basic certifications
        raw_certs = deterministic_context.get("raw_certifications", [])

        fallback_dict = {
            "name": deterministic_context.get("name"),
            "email": deterministic_context.get("email"),
            "phone": deterministic_context.get("phone"),
            "location": None,
            "linkedin": deterministic_context.get("linkedin"),
            "github": deterministic_context.get("github"),
            "summary": deterministic_context.get("summary"),
            "skills": deterministic_context.get("skills", []),
            "work_experience": work_exp,
            "education": education,
            "projects": projects,
            "certifications": raw_certs,
        }
        return fallback_dict, "deterministic_fallback"


class GeminiProvider(BaseResumeProvider):
    """Gemini AI Provider for Resume Analysis."""

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-1.5-flash") -> None:
        settings = get_settings()
        self.api_key = api_key or getattr(settings, "gemini_api_key", None)
        self.model_name = getattr(settings, "gemini_model", model_name)
        self.fallback = FallbackProvider()

    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def extract(self, resume_text: str, deterministic_context: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        if not self.is_available:
            logger.info("GEMINI_API_KEY is not configured. Falling back to deterministic extraction.")
            return self.fallback.extract(resume_text, deterministic_context)

        prompt = RESUME_AGENT_USER_PROMPT_TEMPLATE.format(
            resume_text=resume_text,
            deterministic_json=json.dumps(deterministic_context, indent=2, default=str),
        )

        try:
            extracted_json = self._call_gemini_api(prompt)
            if extracted_json:
                return extracted_json, "hybrid"
        except Exception as exc:
            logger.warning(f"Gemini API request failed: {exc}. Falling back to deterministic mode.")

        return self.fallback.extract(resume_text, deterministic_context)

    def _call_gemini_api(self, prompt: str) -> dict[str, Any] | None:
        """Execute HTTP request to Gemini REST API with JSON response constraints."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{RESUME_AGENT_SYSTEM_PROMPT}\n\n{prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return None

        text_out = parts[0].get("text", "").strip()
        # Clean any potential backticks
        if text_out.startswith("```json"):
            text_out = text_out[7:]
        if text_out.startswith("```"):
            text_out = text_out[3:]
        if text_out.endswith("```"):
            text_out = text_out[:-3]

        return json.loads(text_out.strip())
