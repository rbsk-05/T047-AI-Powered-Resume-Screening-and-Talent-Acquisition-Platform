"""Optional LLM assistance for Module 1 (extraction) and Module 4 (explanation).

Every method here degrades to `None` on any failure -- missing API key,
network error, malformed response -- so callers always have a deterministic
baseline to fall back to. The LLM is never the only path to a response.

Design choice: the LLM is asked to extract facts or phrase an explanation of
facts we already computed deterministically (matched/missing skills, scores).
It is not asked to invent a score or decide who's a good candidate on its
own -- that keeps the scoring transparent and auditable, matching the
project's "explainable AI" goal instead of quietly becoming a black box.
"""

import json
from functools import lru_cache

from app.core.config import get_settings


class LLMProvider:
    """Thin wrapper around the Groq Chat Completions API."""

    def __init__(self, api_key: str | None, model: str, enabled: bool = True):
        self.api_key = api_key
        self.model = model
        self.enabled = enabled
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.enabled and self.api_key)

    def _get_client(self):
        if self._client is None:
            from groq import Groq

            self._client = Groq(api_key=self.api_key)
        return self._client

    def _complete(self, prompt: str, max_tokens: int = 1000) -> str | None:
        if not self.available:
            return None
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception:
            return None


    def extract_job_requirements(self, job_title: str, job_description: str) -> dict | None:
        """Ask the LLM to extract structured requirements from a JD.

        Returns a dict with the same keys as JobProfile (minus job_title) on
        success, or None if the call failed or the response wasn't valid
        JSON -- the caller should fall back to the regex baseline.
        """
        prompt = f"""Extract structured hiring requirements from this job description.

Job title: {job_title}
Job description:
{job_description}

Respond with ONLY a JSON object (no prose, no markdown fences) with exactly these keys:
- "required_skills": list of strings, must-have technical skills
- "preferred_skills": list of strings, nice-to-have skills
- "experience": string or null, e.g. "3+ years"
- "education": list of strings, e.g. ["Computer Science"]
- "responsibilities": list of strings, up to 6 short responsibility statements
"""
        raw = self._complete(prompt)
        if raw is None:
            return None
        try:
            data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
        except json.JSONDecodeError:
            return None
        expected_keys = {"required_skills", "preferred_skills", "experience", "education", "responsibilities"}
        if not isinstance(data, dict) or not expected_keys.issubset(data.keys()):
            return None
        return data

    def extract_candidate_profile(self, resume_text: str) -> dict | None:
        """Ask the LLM to extract structured candidate profile from resume text."""
        prompt = f"""Extract structured candidate information from this resume text.
If the text does NOT look like a resume or CV, or has no relevant technical candidate information, return empty lists/null.

Resume Text:
{resume_text[:4000]}

Respond with ONLY a JSON object (no prose, no markdown fences) with exactly these keys:
- "name": string or null
- "email": string or null
- "phone": string or null
- "skills": list of strings (e.g. ["Python", "FastAPI", "Docker", "SQL"])
- "experience": string or null (e.g. "3 years", "2.5 years")
- "education": list of strings (e.g. ["B.Tech in Computer Science"])
- "projects": list of strings (e.g. ["Built an e-commerce platform using React and Node.js"])
- "certifications": list of strings (e.g. ["AWS Certified Solutions Architect"])
"""
        raw = self._complete(prompt)
        if raw is None:
            return None
        try:
            data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
        except json.JSONDecodeError:
            return None
        expected_keys = {"name", "email", "phone", "skills", "experience", "education", "projects", "certifications"}
        if not isinstance(data, dict) or not expected_keys.issubset(data.keys()):
            return None
        return data

    def generate_summary(
        self,
        candidate_name: str,
        overall_score: float,
        matched_skills: list[str],
        missing_required_skills: list[str],
        missing_preferred_skills: list[str],
    ) -> str | None:
        """Ask the LLM to phrase a recruiter-facing summary of facts we already know.

        The LLM only rephrases; it is given the computed score and skill
        lists as ground truth rather than being asked to judge fit itself.
        """
        prompt = f"""Write a single, concise (2-3 sentence) recruiter-facing summary for a candidate,
using ONLY the facts below. Do not invent skills, scores, or experience not listed here.

Candidate: {candidate_name}
Overall match score: {overall_score}%
Matched skills: {', '.join(matched_skills) or 'none'}
Missing required skills: {', '.join(missing_required_skills) or 'none'}
Missing preferred skills: {', '.join(missing_preferred_skills) or 'none'}

Respond with ONLY the summary text, no preamble, no markdown.
"""
        raw = self._complete(prompt, max_tokens=200)
        return raw.strip() if raw else None

    def analyze_skill_gap(
        self,
        candidate_name: str,
        missing_required: list[str],
        missing_preferred: list[str],
    ) -> str | None:
        """Ask the LLM to provide plain-language skill gap feedback for a candidate.

        Returns 2-3 sentences of constructive feedback, or None on failure.
        """
        prompt = f"""You are a career coach. Based on the missing skills below,
write 2-3 sentences of constructive, encouraging feedback for the candidate on what to focus on next.
Do NOT invent any details. Be specific to the skills listed.

Candidate: {candidate_name}
Missing required skills: {', '.join(missing_required) or 'none'}
Missing preferred skills: {', '.join(missing_preferred) or 'none'}

Respond with ONLY the feedback text, no preamble, no markdown.
"""
        raw = self._complete(prompt, max_tokens=250)
        return raw.strip() if raw else None

    def generate_learning_path(self, skill: str) -> list[str] | None:
        """Ask the LLM to suggest a short ordered learning path for a skill.

        Returns a list of milestone strings (3-5 items), or None on failure.
        """
        prompt = f"""Suggest a concise, ordered learning path (3-5 milestones) for someone learning '{skill}' from scratch.
Respond with ONLY a JSON array of short milestone strings, e.g. ["Step 1", "Step 2"].
No prose, no markdown fences.
"""
        raw = self._complete(prompt, max_tokens=300)
        if raw is None:
            return None
        try:
            data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
            if isinstance(data, list) and all(isinstance(s, str) for s in data):
                return data
        except json.JSONDecodeError:
            pass
        return None


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Process-wide singleton, cheap to call repeatedly from route handlers."""
    settings = get_settings()
    return LLMProvider(api_key=settings.groq_api_key, model=settings.llm_model, enabled=settings.enable_llm_extraction)
