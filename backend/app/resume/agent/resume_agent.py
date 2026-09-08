"""Resume Analysis Agent coordinator."""

from typing import Any

from app.resume.agent.providers import BaseResumeProvider, GeminiProvider
from app.resume.experience import ExperienceCalculator
from app.resume.normalizer import Normalizer
from app.resume.regex_extractor import RegexExtractor
from app.resume.schemas import EducationEntry, ProjectEntry, ResumeData, WorkExperience


class ResumeAnalysisAgent:
    """Coordinator that executes deterministic + AI extraction, controlled merge, and normalization."""

    def __init__(self, provider: BaseResumeProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    def analyze(self, text: str) -> ResumeData:
        """Run full hybrid resume analysis pipeline."""
        # 1. Deterministic Extraction Layer
        det_context = RegexExtractor.extract_all(text)

        # 2. AI Extraction Layer (or Fallback)
        raw_ai, method = self.provider.extract(text, det_context)
        ai_data = raw_ai or {}

        # 3. Controlled Merge Strategy
        # Contact & URLs: Prefer deterministic regex when valid
        email = det_context.get("email") or ai_data.get("email")
        phone = det_context.get("phone") or ai_data.get("phone")
        linkedin = det_context.get("linkedin") or ai_data.get("linkedin")
        github = det_context.get("github") or ai_data.get("github")

        # Name: AI or deterministic fallback
        name = ai_data.get("name") or det_context.get("name")
        summary = ai_data.get("summary") or det_context.get("summary")
        location = ai_data.get("location")

        # Skills: Combine AI + deterministic, normalize & deduplicate
        combined_skills = list(ai_data.get("skills", [])) + det_context.get("skills", [])
        normalized_skills = Normalizer.normalize_skills(combined_skills)

        # Work Experience
        raw_work = ai_data.get("work_experience", [])
        work_entries: list[WorkExperience] = []
        if isinstance(raw_work, list):
            for item in raw_work:
                if isinstance(item, dict):
                    desc = item.get("description", [])
                    if isinstance(desc, str):
                        desc = [desc]
                    work_entries.append(
                        WorkExperience(
                            company=item.get("company"),
                            role=item.get("role") or item.get("title"),
                            start_date=item.get("start_date"),
                            end_date=item.get("end_date"),
                            duration_text=item.get("duration_text") or item.get("duration"),
                            description=desc if isinstance(desc, list) else [],
                        )
                    )

        # Calculate unique non-overlapping experience
        total_exp_years = ExperienceCalculator.calculate_total_experience_years(work_entries)

        # Education
        raw_edu = ai_data.get("education", [])
        edu_entries: list[EducationEntry] = []
        if isinstance(raw_edu, list):
            for item in raw_edu:
                if isinstance(item, dict):
                    edu_entries.append(
                        EducationEntry(
                            institution=item.get("institution"),
                            degree=item.get("degree"),
                            field_of_study=item.get("field_of_study"),
                            graduation_year=item.get("graduation_year"),
                            cgpa_or_grade=item.get("cgpa_or_grade"),
                        )
                    )
        if not edu_entries and det_context.get("raw_education"):
            edu_entries = [EducationEntry(degree=line) for line in det_context["raw_education"]]

        # Projects
        raw_proj = ai_data.get("projects", [])
        proj_entries: list[ProjectEntry] = []
        if isinstance(raw_proj, list):
            for item in raw_proj:
                if isinstance(item, dict):
                    techs = item.get("technologies", [])
                    proj_entries.append(
                        ProjectEntry(
                            name=item.get("name"),
                            description=item.get("description"),
                            technologies=Normalizer.normalize_skills(techs) if isinstance(techs, list) else [],
                        )
                    )
        if not proj_entries and det_context.get("raw_projects"):
            proj_entries = [ProjectEntry(name=line) for line in det_context["raw_projects"]]

        # Certifications
        certs = ai_data.get("certifications") or det_context.get("raw_certifications", [])
        if not isinstance(certs, list):
            certs = [str(certs)]

        return ResumeData(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
            summary=summary,
            skills=normalized_skills,
            work_experience=work_entries,
            total_experience_years=total_exp_years,
            education=edu_entries,
            projects=proj_entries,
            certifications=[str(c) for c in certs if c],
            analysis_method="hybrid" if method == "hybrid" else "deterministic_fallback",
        )
