from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest
from app.schemas.ranking import RankingRequest
from app.schemas.gap import SkillGapRequest
from app.schemas.recommendation import RecommendationRequest
from app.schemas.evaluation import EvaluationRequest
from app.schemas.workflow import CandidateWorkflowRequest

from app.matching import CandidateMatcher, ComponentScorer, EmbeddingProvider
from app.ranking import RankingService
from app.skill_gap import SkillGapAnalyzer
from app.recommendations import LearningRecommendationService
from app.explanation import EvaluationService, ExplainableAI
from app.workflows import CandidateAnalysisWorkflow


def test_matching_pipeline():
    candidate = CandidateProfile(
        name="John Doe",
        skills=["Python", "FastAPI", "AWS"],
        experience="3 years",
        education=["B.S. Computer Science"],
        projects=["Backend REST API"],
        certifications=["AWS Certified Developer"]
    )
    job = JobProfile(
        job_title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "AWS"],
        preferred_skills=["Docker", "Kubernetes"],
        experience="2 years",
        education=["Computer Science"],
        responsibilities=["Develop FastAPI microservices"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.overall_match_score >= 70.0
    assert "Python" in match_result.matched_skills
    assert "FastAPI" in match_result.matched_skills
    assert "AWS" in match_result.matched_skills
    assert "Docker" in match_result.missing_preferred_skills
    assert match_result.score_breakdown.required_skills == 100.0


def test_ranking_pipeline():
    job = JobProfile(
        job_title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "AWS"],
        preferred_skills=["Docker"],
        experience="2 years"
    )
    candidate_1 = CandidateProfile(
        name="Strong Candidate",
        skills=["Python", "FastAPI", "AWS", "Docker"],
        experience="4 years"
    )
    candidate_2 = CandidateProfile(
        name="Junior Candidate",
        skills=["Python"],
        experience="1 year"
    )

    ranker = RankingService()
    result = ranker.rank(RankingRequest(job_profile=job, candidates=[candidate_2, candidate_1]))

    assert len(result.ranked_candidates) == 2
    assert result.ranked_candidates[0].candidate_name == "Strong Candidate"
    assert result.ranked_candidates[0].rank == 1
    assert result.ranked_candidates[1].candidate_name == "Junior Candidate"


def test_skill_gap_pipeline():
    candidate = CandidateProfile(
        skills=["Python", "FastAPI"]
    )
    job = JobProfile(
        required_skills=["Python", "FastAPI", "AWS"],
        preferred_skills=["Docker"]
    )

    analyzer = SkillGapAnalyzer()
    gap_result = analyzer.analyze(SkillGapRequest(job_profile=job, candidate_profile=candidate))

    assert "Python" in gap_result.matched_skills
    gaps_by_skill = {gap.skill: gap for gap in gap_result.gaps}
    assert "AWS" in gaps_by_skill
    assert gaps_by_skill["AWS"].priority == "critical"
    assert "Docker" in gaps_by_skill
    assert gaps_by_skill["Docker"].priority == "important"


def test_recommendation_pipeline():
    candidate = CandidateProfile(skills=["Python"])
    job = JobProfile(required_skills=["Python", "Docker"])
    gap_analyzer = SkillGapAnalyzer()
    gap_result = gap_analyzer.analyze(SkillGapRequest(job_profile=job, candidate_profile=candidate))

    recommender = LearningRecommendationService()
    rec_result = recommender.generate(RecommendationRequest(skill_gap_result=gap_result))

    assert len(rec_result.recommendations) >= 1
    rec_docker = [r for r in rec_result.recommendations if r.skill.lower() == "docker"][0]
    assert len(rec_docker.learning_path) > 0


def test_explanation_pipeline():
    candidate = CandidateProfile(
        name="Jane Smith",
        skills=["Python", "FastAPI"],
        experience="3 years"
    )
    job = JobProfile(
        required_skills=["Python", "FastAPI", "Docker"],
        experience="2 years"
    )
    matcher = CandidateMatcher()
    evaluator = EvaluationService(matcher=matcher)
    match_req = MatchRequest(job_profile=job, candidate_profile=candidate)
    
    evaluation = evaluator.evaluate(EvaluationRequest(match_request=match_req))

    assert evaluation.match.overall_match_score > 0
    assert len(evaluation.strengths) > 0
    assert len(evaluation.gaps) > 0
    assert len(evaluation.evidence) > 0
    assert evaluation.summary is not None


def test_candidate_analysis_workflow():
    candidate = CandidateProfile(
        name="Alex River",
        skills=["Python", "FastAPI", "AWS"],
        experience="2 years"
    )
    job = JobProfile(
        job_title="Backend Engineer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Kubernetes"]
    )
    workflow = CandidateAnalysisWorkflow()
    result = workflow.run(CandidateWorkflowRequest(job_profile=job, candidate_profile=candidate))

    assert result.match.overall_match_score >= 60.0
    assert result.evaluation.summary is not None
    assert result.skill_gap is not None
    assert result.recommendations is not None
