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

    def _complete(self, prompt: str, max_tokens: int = 4000) -> str | None:
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


    @staticmethod
    def _extract_json(raw: str | None) -> dict | list | None:
        if not raw:
            return None
        text = raw.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strip code fences
        if "```" in text:
            start_idx = text.find("```")
            end_idx = text.rfind("```")
            if end_idx > start_idx:
                block = text[start_idx:end_idx].strip()
                if "\n" in block:
                    block = block.split("\n", 1)[1]
                try:
                    return json.loads(block.strip())
                except json.JSONDecodeError:
                    pass

        # Substring search for outermost object { ... } or list [ ... ]
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            candidate_json = text[first_brace:last_brace + 1]
            try:
                return json.loads(candidate_json)
            except json.JSONDecodeError:
                # Remove trailing commas before } or ]
                cleaned_json = candidate_json.replace(",\n}", "\n}").replace(",}", "}").replace(",\n]", "\n]").replace(",]", "]")
                try:
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    pass

        first_sq = text.find("[")
        last_sq = text.rfind("]")
        if first_sq != -1 and last_sq > first_sq:
            try:
                return json.loads(text[first_sq:last_sq + 1])
            except json.JSONDecodeError:
                pass

        return None

    def extract_job_requirements(self, job_title: str, job_description: str) -> dict | None:
        """Ask the LLM to extract structured requirements from a JD with context awareness and zero-hallucination."""
        clean_desc = (
            job_description.replace("\u2011", "-")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
            .replace("\u2022", "*")
        )
        title_hint = f"Role/Title context: {job_title}\n" if job_title and job_title != "Job Role" else ""
        prompt = f"""You are an expert technical recruiter and talent acquisition AI agent.
Analyze the following job description text (which may be written in paragraphs, prose, bullet points, or freeform text) and extract the exact structured hiring requirements.

{title_hint}Job Description Content:
\"\"\"
{clean_desc}
\"\"\"

CRITICAL EXTRACTION RULES:
1. EXPLICIT vs INFERRED REQUIREMENTS:
   - If a technology/skill is explicitly named (e.g. "React", "TypeScript", "C#", "SQL Server"), mark evidence_type as "EXPLICIT".
   - If the JD describes generic responsibilities (e.g. "develop responsive web applications", "design microservices") without naming specific tools, mark the domain requirement as "INFERRED".
   - NEVER invent or assume mandatory technologies that are not stated in the JD. For example, if JD says "develop responsive web applications", do NOT invent React or Angular!
2. TECHNOLOGY SPECIFICATION:
   - If specific programming languages/frameworks are explicitly required, set "technology_specified": true.
   - If only general responsibilities are given without naming specific technologies, set "technology_specified": false.
3. REQUIRED vs PREFERRED:
   - "required_skills": Mandatory must-have technical skills, tools, languages, and competencies.
   - "preferred_skills": Nice-to-have, bonus, or secondary skills explicitly mentioned as preferred.
4. JOB FAMILY: Identify the primary role family (e.g. "Frontend Development", "Backend Development", "Full Stack Development", "Cloud & DevOps", "Data Science & AI", "UI/UX Design", "QA & Testing", "Mobile Development").

Respond with ONLY a valid JSON object matching this structure:
{{
  "job_title": "string",
  "job_family": "string",
  "technology_specified": true,
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "requirements": [
    {{
      "name": "string",
      "category": "string",
      "importance": "REQUIRED" or "PREFERRED",
      "evidence_type": "EXPLICIT" or "INFERRED",
      "evidence_text": "short quote from JD",
      "confidence": "HIGH" or "MEDIUM" or "LOW"
    }}
  ],
  "experience": "string or null (e.g. '3+ years')",
  "education": ["string"],
  "responsibilities": ["string (3-6 bullet points)"],
  "soft_skills": ["string"],
  "domain_knowledge": ["string"]
}}
"""
        raw = self._complete(prompt, max_tokens=3500)
        data = self._extract_json(raw)
        if not isinstance(data, dict):
            return None
        expected_keys = {"required_skills", "preferred_skills", "experience", "education", "responsibilities"}
        if not expected_keys.issubset(data.keys()):
            return None
        return data

    def extract_candidate_profile(self, resume_text: str) -> dict | None:
        """Ask the LLM to extract structured candidate profile from resume text with evidence tracing."""
        clean_text = (
            resume_text.replace("\u2011", "-")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
            .replace("\u2022", "*")
        )
        prompt = f"""Extract structured candidate information from this resume text.
CRITICAL INSTRUCTION FOR SKILLS:
- Extract ONLY the skills and technologies explicitly supported by the resume text.
- Do NOT assume a candidate knows a technology just because they know a related one (e.g., if candidate has React, do NOT invent Angular).
- For each skill, identify the supporting evidence text from the resume.

Resume Text:
{clean_text[:4500]}

Respond with ONLY a JSON object with exactly these keys:
- "name": string or null (Candidate full name)
- "role": string or null (Target job title or primary profession stated in the resume)
- "email": string or null
- "phone": string or null
- "skills": list of strings (clean individual skill names, e.g. ["Python", "FastAPI", "SQL", "Docker"])
- "structured_skills": [
    {{
      "skill_name": "string",
      "evidence_text": "short snippet or quote demonstrating this skill",
      "evidence_type": "EXPLICIT" or "INFERRED",
      "confidence": "HIGH" or "MEDIUM"
    }}
  ]
- "experience": string or null (e.g. "3 years", "Fresher / 1 year", or total years of experience)
- "education": list of strings (e.g. ["B.E. in Computer Science - XYZ University"])
- "projects": list of strings (key project titles from the resume)
- "certifications": list of strings (certifications and licenses)
- "domain_knowledge": list of strings
"""
        raw = self._complete(prompt, max_tokens=4000)
        data = self._extract_json(raw)
        if not isinstance(data, dict):
            return None
        expected_keys = {"name", "skills", "experience", "education"}
        if not expected_keys.issubset(data.keys()):
            return None
        return data


    def generate_summary(
        self,
        candidate_name: str,
        overall_score: float,
        matched_skills: list[str],
        missing_required_skills: list[str],
        missing_preferred_skills: list[str],
        job_title: str | None = None,
        experience: str | None = None,
        recommendation: str | None = None,
    ) -> str | None:
        """Ask the AI Evaluation Agent to phrase a rich, comprehensive evaluation summary.

        The LLM is provided the computed score and skill lists as ground truth.
        """
        job_ctx = f"Target Role: {job_title}\n" if job_title else ""
        exp_ctx = f"Experience: {experience}\n" if experience else ""
        rec_ctx = f"Recommendation: {recommendation}\n" if recommendation else ""

        prompt = f"""You are the AI Evaluation Agent for an advanced talent acquisition platform.
Generate a clear, professional, and comprehensive evaluation summary (3-4 complete sentences) for the candidate application below.

{job_ctx}Candidate: {candidate_name}
Overall ATS Match Score: {overall_score}%
{exp_ctx}{rec_ctx}Exact & Related Matched Skills: {', '.join(matched_skills) or 'None demonstrated'}
Missing Required Skills: {', '.join(missing_required_skills) or 'None (All satisfied)'}
Missing Preferred Skills: {', '.join(missing_preferred_skills) or 'None'}

INSTRUCTIONS:
1. State the candidate's overall ATS match score and role fit clearly.
2. Highlight their verified skill matches and experience alignment where applicable.
3. Identify the key technical gaps or required competencies they need to develop.
4. Conclude with an objective hiring recommendation.
5. Do NOT cut off mid-sentence. Write complete, well-formed, professional sentences.

Respond with ONLY the evaluation summary text, no preamble, no markdown formatting.
"""
        raw = self._complete(prompt, max_tokens=600)
        if not raw:
            return None
        text = raw.strip()
        if len(text) < 30 or text.endswith((" an", " a", " the", " with", " and", " for")):
            return None
        return text

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
"""
        raw = self._complete(prompt, max_tokens=300)
        data = self._extract_json(raw)
        if isinstance(data, list) and all(isinstance(s, str) for s in data):
            return data
        return None

    def generate_comparison_summary(
        self,
        job_title: str,
        candidates_data: list[dict],
    ) -> str | None:
        """Ask the LLM to generate an objective, concise recruiter-facing comparison between candidates."""
        candidates_text = ""
        for c in candidates_data:
            candidates_text += f"\n- {c['name']} (ATS Score: {c['score']}%): Matched: {', '.join(c['matched_skills']) or 'None'}, Missing: {', '.join(c['missing_skills']) or 'None'}, Experience: {c.get('experience', 'N/A')}"

        prompt = f"""You are a technical recruitment advisor. Compare the following candidates for the '{job_title}' position.
Provide a concise 3-4 sentence comparison summarizing their relative strengths and key differentiators.
Do NOT invent facts, skills, or experience outside the data provided.

Candidates:{candidates_text}

Respond with ONLY the summary text, no preamble, no markdown.
"""
        raw = self._complete(prompt, max_tokens=300)
        return raw.strip() if raw else None


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Process-wide singleton, cheap to call repeatedly from route handlers."""
    settings = get_settings()
    return LLMProvider(api_key=settings.groq_api_key, model=settings.llm_model, enabled=settings.enable_llm_extraction)
