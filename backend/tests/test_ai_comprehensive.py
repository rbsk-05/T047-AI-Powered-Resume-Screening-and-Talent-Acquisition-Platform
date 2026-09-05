import pytest

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
from app.explanation import EvaluationService
from app.workflows import CandidateAnalysisWorkflow


def test_perfect_candidate_vs_perfect_job():
    """Test 1: Perfect candidate meeting 100% of job requirements across all criteria."""
    candidate = CandidateProfile(
        name="Perfect Dev",
        email="perfect@example.com",
        phone="1234567890",
        skills=["Python", "FastAPI", "AWS", "Docker", "Kubernetes"],
        experience="5 years",
        education=["B.S. in Computer Science"],
        projects=["Built cloud backend API"],
        certifications=["AWS Certified Solutions Architect"]
    )
    job = JobProfile(
        job_title="Senior Backend Engineer",
        required_skills=["Python", "FastAPI", "AWS"],
        preferred_skills=["Docker", "Kubernetes"],
        experience="5 years",
        education=["Computer Science"],
        responsibilities=["Build scalable microservices"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.overall_match_score >= 95.0
    assert match_result.score_breakdown.required_skills == 100.0
    assert match_result.score_breakdown.experience == 100.0
    assert match_result.score_breakdown.education == 100.0
    assert match_result.score_breakdown.certifications == 100.0
    assert len(match_result.missing_required_skills) == 0
    assert len(match_result.missing_preferred_skills) == 0


def test_poor_candidate_vs_job():
    """Test 2: Unrelated candidate with no matching skills or experience."""
    candidate = CandidateProfile(
        name="Unrelated Candidate",
        skills=["Graphic Design", "Photoshop", "Illustrator"],
        experience="0 years",
        education=["B.A. in Fine Arts"],
        projects=[],
        certifications=[]
    )
    job = JobProfile(
        job_title="Python Developer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker"],
        experience="3 years",
        education=["Computer Science"],
        responsibilities=["Write server-side code"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.overall_match_score < 30.0
    assert match_result.score_breakdown.required_skills == 0.0
    assert match_result.score_breakdown.experience == 0.0
    assert len(match_result.matched_skills) == 0
    assert set(match_result.missing_required_skills) == {"Python", "FastAPI", "PostgreSQL"}


def test_partial_candidate_vs_job():
    """Test 3: Candidate meeting some required skills and half of experience requirement."""
    candidate = CandidateProfile(
        name="Partial Match Dev",
        skills=["Python"],
        experience="1 year",
        education=["Computer Science"],
        projects=["Django Website"],
        certifications=[]
    )
    job = JobProfile(
        job_title="Mid-Level Python Developer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        experience="2 years",
        education=["Computer Science"],
        responsibilities=["Maintain APIs"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.score_breakdown.required_skills == 50.0
    assert match_result.score_breakdown.experience == 50.0
    assert "Python" in match_result.matched_skills
    assert "FastAPI" in match_result.missing_required_skills


def test_backend_dev_ranks_above_graphic_designer():
    """Test 4: Backend developer ranks significantly higher than unrelated Graphic Designer for Python job."""
    job = JobProfile(
        job_title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "SQL"],
        experience="2 years"
    )
    backend_dev = CandidateProfile(
        name="Backend Dev",
        skills=["Python", "FastAPI", "SQL"],
        experience="3 years"
    )
    graphic_designer = CandidateProfile(
        name="Graphic Designer",
        skills=["Photoshop", "Figma", "UI Design"],
        experience="5 years"
    )

    ranker = RankingService()
    result = ranker.rank(RankingRequest(job_profile=job, candidates=[graphic_designer, backend_dev]))

    assert len(result.ranked_candidates) == 2
    assert result.ranked_candidates[0].candidate_name == "Backend Dev"
    assert result.ranked_candidates[0].rank == 1
    assert result.ranked_candidates[1].candidate_name == "Graphic Designer"
    assert result.ranked_candidates[1].rank == 2
    assert result.ranked_candidates[0].match.overall_match_score > result.ranked_candidates[1].match.overall_match_score


def test_multiple_candidate_ranking():
    """Test 5: Rank candidates with high, medium, and low qualification levels."""
    job = JobProfile(
        job_title="Full Stack Developer",
        required_skills=["React", "Node.js", "MongoDB"],
        experience="3 years"
    )
    cand_high = CandidateProfile(
        name="High Candidate",
        skills=["React", "Node.js", "MongoDB", "Express"],
        experience="4 years"
    )
    cand_mid = CandidateProfile(
        name="Mid Candidate",
        skills=["React", "Node.js"],
        experience="2 years"
    )
    cand_low = CandidateProfile(
        name="Low Candidate",
        skills=["HTML", "CSS"],
        experience="0 years"
    )

    ranker = RankingService()
    result = ranker.rank(RankingRequest(job_profile=job, candidates=[cand_mid, cand_low, cand_high]))

    assert len(result.ranked_candidates) == 3
    assert result.ranked_candidates[0].candidate_name == "High Candidate"
    assert result.ranked_candidates[0].rank == 1
    assert result.ranked_candidates[1].candidate_name == "Mid Candidate"
    assert result.ranked_candidates[1].rank == 2
    assert result.ranked_candidates[2].candidate_name == "Low Candidate"
    assert result.ranked_candidates[2].rank == 3


def test_ranking_independent_of_input_order():
    """Test 6: Verify candidate ranking and scores are identical regardless of input array ordering."""
    job = JobProfile(
        job_title="Data Scientist",
        required_skills=["Python", "Pandas", "Scikit-Learn"],
        experience="2 years"
    )
    cand_a = CandidateProfile(name="Alice", skills=["Python", "Pandas", "Scikit-Learn"], experience="3 years")
    cand_b = CandidateProfile(name="Bob", skills=["Python"], experience="1 year")
    cand_c = CandidateProfile(name="Charlie", skills=["Python", "Pandas"], experience="2 years")

    ranker = RankingService()

    order1 = ranker.rank(RankingRequest(job_profile=job, candidates=[cand_a, cand_b, cand_c]))
    order2 = ranker.rank(RankingRequest(job_profile=job, candidates=[cand_c, cand_a, cand_b]))

    names_order1 = [c.candidate_name for c in order1.ranked_candidates]
    names_order2 = [c.candidate_name for c in order2.ranked_candidates]

    assert names_order1 == ["Alice", "Charlie", "Bob"]
    assert names_order2 == ["Alice", "Charlie", "Bob"]

    scores1 = [c.match.overall_match_score for c in order1.ranked_candidates]
    scores2 = [c.match.overall_match_score for c in order2.ranked_candidates]
    assert scores1 == scores2


def test_ranking_determinism():
    """Test 7: Confirm multiple calls with identical input produce exact same ranking and scores."""
    job = JobProfile(
        job_title="DevOps Engineer",
        required_skills=["AWS", "Docker", "Kubernetes"],
        experience="3 years"
    )
    cand_1 = CandidateProfile(name="DevOps Pro", skills=["AWS", "Docker", "Kubernetes"], experience="4 years")
    cand_2 = CandidateProfile(name="DevOps Novice", skills=["Docker"], experience="1 year")

    ranker = RankingService()
    run_1 = ranker.rank(RankingRequest(job_profile=job, candidates=[cand_1, cand_2]))
    run_2 = ranker.rank(RankingRequest(job_profile=job, candidates=[cand_1, cand_2]))

    assert [c.rank for c in run_1.ranked_candidates] == [c.rank for c in run_2.ranked_candidates]
    assert [c.match.overall_match_score for c in run_1.ranked_candidates] == [c.match.overall_match_score for c in run_2.ranked_candidates]


def test_adding_relevant_skill_does_not_decrease_score():
    """Test 8: Adding a relevant required skill to a candidate must not decrease their score."""
    job = JobProfile(
        job_title="Backend Developer",
        required_skills=["Python", "FastAPI", "Docker"],
        experience="2 years"
    )
    candidate_base = CandidateProfile(
        name="Candidate Base",
        skills=["Python"],
        experience="2 years"
    )
    candidate_added = CandidateProfile(
        name="Candidate Added",
        skills=["Python", "FastAPI"],
        experience="2 years"
    )

    matcher = CandidateMatcher()
    score_base = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate_base)).overall_match_score
    score_added = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate_added)).overall_match_score

    assert score_added >= score_base


def test_required_skill_weight_behavior():
    """Test 9: Verify required skills component contributes 35% to overall match score."""
    matcher = CandidateMatcher()
    assert matcher.WEIGHTS["required_skills"] == 0.35

    job = JobProfile(required_skills=["Python", "FastAPI"])
    candidate_full = CandidateProfile(skills=["Python", "FastAPI"])
    candidate_none = CandidateProfile(skills=[])

    res_full = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate_full))
    res_none = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate_none))

    assert res_full.score_breakdown.required_skills == 100.0
    assert res_none.score_breakdown.required_skills == 0.0


def test_skill_gap_classification():
    """Test 10: Check required skills become critical gaps while preferred skills become important gaps."""
    candidate = CandidateProfile(skills=["Python"])
    job = JobProfile(
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker", "Redis"]
    )

    analyzer = SkillGapAnalyzer()
    gap_result = analyzer.analyze(SkillGapRequest(job_profile=job, candidate_profile=candidate))

    critical_skills = [g.skill for g in gap_result.gaps if g.priority == "critical"]
    important_skills = [g.skill for g in gap_result.gaps if g.priority == "important"]

    assert set(critical_skills) == {"FastAPI", "SQL"}
    assert set(important_skills) == {"Docker", "Redis"}


def test_recommendation_generation_known_and_custom_skills():
    """Test 11: Verify recommendation paths for standard pre-configured skills vs custom skills."""
    candidate = CandidateProfile(skills=["Python"])
    job = JobProfile(
        required_skills=["Python", "Docker", "Rust"]
    )
    analyzer = SkillGapAnalyzer()
    gap_result = analyzer.analyze(SkillGapRequest(job_profile=job, candidate_profile=candidate))

    recommender = LearningRecommendationService()
    rec_result = recommender.generate(RecommendationRequest(skill_gap_result=gap_result))

    rec_dict = {r.skill: r for r in rec_result.recommendations}
    
    assert "Docker" in rec_dict
    assert "Docker fundamentals" in rec_dict["Docker"].learning_path

    assert "Rust" in rec_dict
    assert "Learn Rust fundamentals" in rec_dict["Rust"].learning_path


def test_explainability_output_structure():
    """Test 12: Verify evaluation service creates recruiter-friendly evidence and decision recommendation."""
    candidate = CandidateProfile(
        name="Candidate One",
        skills=["Python", "FastAPI"],
        experience="3 years",
        education=["Computer Science"],
        projects=["FastAPI Web Service"],
        certifications=["Python Certification"]
    )
    job_matched = JobProfile(
        job_title="Python Developer",
        required_skills=["Python", "FastAPI"],
        experience="2 years"
    )
    job_unmatched = JobProfile(
        job_title="Senior Lead",
        required_skills=["Python", "Kubernetes", "C++"],
        experience="8 years"
    )

    matcher = CandidateMatcher()
    evaluator = EvaluationService(matcher=matcher)

    # High match evaluation (score >= 80% threshold -> Recommended for technical interview)
    eval_high = evaluator.evaluate(EvaluationRequest(match_request=MatchRequest(job_profile=job_matched, candidate_profile=candidate)))
    assert eval_high.match.overall_match_score >= 80.0
    assert eval_high.recommendation == "Recommended for technical interview"
    assert any("Demonstrates Python" in s for s in eval_high.strengths)
    assert any(e.requirement == "Python" and e.status == "matched" for e in eval_high.evidence)

    # Skill gap evaluation
    eval_low = evaluator.evaluate(EvaluationRequest(match_request=MatchRequest(job_profile=job_unmatched, candidate_profile=candidate)))
    assert eval_low.recommendation == "Review required skill gaps before progressing"
    assert any(e.requirement == "Kubernetes" and e.status == "missing" for e in eval_low.evidence)


def test_full_candidate_analysis_workflow_integration():
    """Test 13: Integrated CandidateAnalysisWorkflow output structure."""
    candidate = CandidateProfile(
        name="Full Pipeline Candidate",
        skills=["Python", "FastAPI", "SQL"],
        experience="3 years",
        education=["Computer Science"],
        projects=["Backend REST Service"],
        certifications=["AWS Developer"]
    )
    job = JobProfile(
        job_title="Backend Developer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        experience="2 years"
    )

    workflow = CandidateAnalysisWorkflow()
    result = workflow.run(CandidateWorkflowRequest(job_profile=job, candidate_profile=candidate))

    assert result.match.overall_match_score >= 80.0
    assert result.evaluation.recommendation == "Recommended for technical interview"
    assert "Docker" in [g.skill for g in result.skill_gap.gaps]
    assert len(result.recommendations.recommendations) > 0


def test_semantic_similarity_behavior():
    """Test 14: Test component scorer semantic similarity with related vs unrelated texts."""
    scorer = ComponentScorer()
    
    related_skills = ["Python", "FastAPI", "REST API", "Backend web development"]
    job_skills = ["Python", "FastAPI", "Web APIs"]

    tokens_related = scorer.extract_tokens(related_skills)
    tokens_job = scorer.extract_tokens(job_skills)

    overlap = len(tokens_related & tokens_job)
    assert overlap > 0


def test_sentence_transformer_fallback_behavior():
    """Test 15: SentenceTransformer fallback behavior when embedding provider is disabled."""
    disabled_embeddings = EmbeddingProvider(model_name="all-MiniLM-L6-v2", enabled=False)
    matcher = CandidateMatcher(embedding_provider=disabled_embeddings)

    candidate = CandidateProfile(
        name="Fallback Candidate",
        skills=["Python", "FastAPI"],
        projects=["Built backend API using Python FastAPI"]
    )
    job = JobProfile(
        job_title="Python Engineer",
        required_skills=["Python", "FastAPI"],
        responsibilities=["Develop FastAPI REST endpoints"]
    )

    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.score_breakdown.semantic_similarity >= 0.0
    assert match_result.overall_match_score > 0.0


def test_missing_and_empty_fields():
    """Test 16: Ensure system gracefully handles empty/None profile fields without crashing."""
    candidate_empty = CandidateProfile()
    job_empty = JobProfile()

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job_empty, candidate_profile=candidate_empty))

    assert match_result.overall_match_score >= 0.0

    analyzer = SkillGapAnalyzer()
    gap_result = analyzer.analyze(SkillGapRequest(job_profile=job_empty, candidate_profile=candidate_empty))
    assert len(gap_result.gaps) == 0


def test_invalid_inputs_and_edge_cases():
    """Test 17: Handle non-standard experience strings and whitespace lists."""
    candidate = CandidateProfile(
        skills=["  Python  ", "  ", ""],
        experience="Senior level (around 4.5 years)"
    )
    job = JobProfile(
        required_skills=["Python"],
        experience="3+ years"
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.score_breakdown.experience == 100.0
    assert "Python" in match_result.matched_skills


def test_duplicate_skills_with_different_casing():
    """Test 18: Ensure duplicate skills with different casing are deduplicated cleanly in matched_skills."""
    candidate = CandidateProfile(
        skills=["Python", "python", "PYTHON", "FastAPI"]
    )
    job = JobProfile(
        required_skills=["Python", "Python", "FastAPI"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.score_breakdown.required_skills == 100.0
    assert match_result.matched_skills == ["Python", "FastAPI"]


def test_whitespace_normalization():
    """Test 19: Test whitespace trimming and normalization for skill matching."""
    candidate = CandidateProfile(
        skills=["  Python  ", "FastAPI\t", "\nAWS  "]
    )
    job = JobProfile(
        required_skills=["Python", "FastAPI", "AWS"]
    )

    matcher = CandidateMatcher()
    match_result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    assert match_result.score_breakdown.required_skills == 100.0
    assert match_result.matched_skills == ["Python", "FastAPI", "AWS"]


def test_synonymous_related_wording_support():
    """Test 20: Test token-based lexical matching for related skill and responsibility terms."""
    candidate = CandidateProfile(
        skills=["Python", "PostgreSQL"],
        projects=["Developed web REST microservices using Python and Postgres"]
    )
    job = JobProfile(
        required_skills=["Python", "PostgreSQL"],
        responsibilities=["Build backend REST APIs and microservices"]
    )

    scorer = ComponentScorer()
    job_tokens = scorer.extract_tokens(job.required_skills + job.responsibilities)
    cand_tokens = scorer.extract_tokens(candidate.skills + candidate.projects)

    assert "microservices" in job_tokens & cand_tokens
    assert "rest" in job_tokens & cand_tokens
