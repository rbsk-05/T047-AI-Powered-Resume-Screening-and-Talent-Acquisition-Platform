"""Adapter converting rich internal ResumeData into the shared CandidateProfile."""

from app.schemas.candidate import CandidateProfile, ExperienceEntry
from app.resume.schemas import ResumeData


class CandidateProfileAdapter:
    """Integration boundary adapter for CandidateProfile."""

    @staticmethod
    def to_candidate_profile(data: ResumeData) -> CandidateProfile:
        """Convert ResumeData into canonical CandidateProfile expected by AI Core."""
        # Convert total experience years to string format expected by ComponentScorer
        if data.total_experience_years > 0:
            # Format cleanly as "X.X years" or "X years"
            years_val = int(data.total_experience_years) if data.total_experience_years.is_integer() else data.total_experience_years
            exp_str = f"{years_val} years"
        else:
            exp_str = "0 years"

        # Form ExperienceEntry list for experience_entries
        entries: list[ExperienceEntry] = []
        for w in data.work_experience:
            duration = w.duration_text
            if not duration and w.start_date:
                end = w.end_date or "Present"
                duration = f"{w.start_date} - {end}"
            desc_text = " ".join(w.description) if w.description else None
            entries.append(
                ExperienceEntry(
                    company=w.company,
                    title=w.role,
                    duration=duration,
                    description=desc_text,
                )
            )

        # Form education strings
        edu_strings: list[str] = []
        for e in data.education:
            parts = [p for p in (e.degree, e.field_of_study, e.institution, e.graduation_year) if p]
            if parts:
                edu_strings.append(" - ".join(parts))
            elif e.degree:
                edu_strings.append(e.degree)

        # Form project strings
        proj_strings: list[str] = []
        for p in data.projects:
            if p.name:
                tech = f" ({', '.join(p.technologies)})" if p.technologies else ""
                desc = f": {p.description}" if p.description else ""
                proj_strings.append(f"{p.name}{tech}{desc}")

        return CandidateProfile(
            name=data.name,
            email=data.email,
            phone=data.phone,
            linkedin=data.linkedin,
            github=data.github,
            summary=data.summary,
            skills=data.skills,
            experience=exp_str,
            experience_entries=entries,
            education=edu_strings,
            projects=proj_strings,
            certifications=data.certifications,
        )
