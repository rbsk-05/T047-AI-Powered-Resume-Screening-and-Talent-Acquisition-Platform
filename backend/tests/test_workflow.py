from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile
from app.schemas.workflow import CandidateWorkflowRequest
from app.services.workflow import CandidateAnalysisWorkflow


def test_workflow_returns_all_analysis_outputs() -> None:
    result = CandidateAnalysisWorkflow().run(CandidateWorkflowRequest(
        job_profile=JobProfile(job_title="Backend Developer", required_skills=["Python", "Docker"], preferred_skills=[], experience=None, education=[], responsibilities=[]),
        candidate_profile=CandidateProfile(name="Candidate A", email=None, phone=None, skills=["Python"], experience=None, education=[], projects=[], certifications=[]),
    ))
    assert result.skill_gap.gaps[0].skill == "Docker"
    assert result.recommendations.recommendations[0].skill == "Docker"
