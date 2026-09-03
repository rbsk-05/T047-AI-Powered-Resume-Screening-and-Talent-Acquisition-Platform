from app.schemas.candidate import CandidateProfile
from app.schemas.gap import SkillGapRequest
from app.schemas.job import JobProfile
from app.services.skill_gap import SkillGapAnalyzer


def test_gap_analysis_prioritizes_required_skills() -> None:
    result = SkillGapAnalyzer().analyze(SkillGapRequest(
        job_profile=JobProfile(job_title="Backend Developer", required_skills=["Python", "Docker"], preferred_skills=["Kubernetes"], experience=None, education=[], responsibilities=[]),
        candidate_profile=CandidateProfile(name=None, email=None, phone=None, skills=["Python"], experience=None, education=[], projects=[], certifications=[]),
    ))
    assert result.matched_skills == ["Python"]
    assert [(gap.skill, gap.priority) for gap in result.gaps] == [("Docker", "critical"), ("Kubernetes", "important")]
