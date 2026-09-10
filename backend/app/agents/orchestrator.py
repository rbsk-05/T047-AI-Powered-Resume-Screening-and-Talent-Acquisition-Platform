from typing import Any, TypedDict

from app.agents.explanation_agent import ExplanationAgent
from app.agents.jd_agent import JDAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.skill_agent import SkillAgent
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateEvaluation
from app.schemas.gap import SkillGapResult
from app.schemas.job import JobProfile
from app.schemas.match import MatchRequest, MatchResult
from app.schemas.recommendation import RecommendationResult
from app.schemas.workflow import CandidateWorkflowRequest, CandidateWorkflowResult
from app.services.matching import CandidateMatcher


class AgentWorkflowState(TypedDict, total=False):
    job_profile: JobProfile
    candidate_profile: CandidateProfile
    match_result: MatchResult
    evaluation_result: CandidateEvaluation
    skill_gap_result: SkillGapResult
    recommendations_result: RecommendationResult


class MultiAgentOrchestrator:
    """LangGraph-compatible Multi-Agent Orchestration Layer.
    
    Coordinates:
    - Agent 1: Resume Agent
    - Agent 2: JD Agent
    - Agent 3: Skill Agent
    - Agent 4: Explanation Agent
    - Agent 5: Recommendation Agent
    - ML Semantic Engine + Deterministic ATS Math Engine
    """

    def __init__(self) -> None:
        self.resume_agent = ResumeAgent()
        self.jd_agent = JDAgent()
        self.skill_agent = SkillAgent()
        self.matcher = CandidateMatcher()
        self.explanation_agent = ExplanationAgent()
        self.recommendation_agent = RecommendationAgent()

    def run_candidate_pipeline(self, request: CandidateWorkflowRequest) -> CandidateWorkflowResult:
        """Executes the multi-agent evaluation pipeline."""
        # 1. Matching Engine (SentenceTransformers Embeddings + Deterministic Scoring)
        match_req = MatchRequest(job_profile=request.job_profile, candidate_profile=request.candidate_profile)
        match = self.matcher.score(match_req)

        # 2. Agent 4: Explanation Agent
        evaluation = self.explanation_agent.explain_evaluation(match_req)

        # 3. Agent 3: Skill Agent
        skill_gap = self.skill_agent.process(request.job_profile, request.candidate_profile)

        # 4. Agent 5: Recommendation Agent
        recommendations = self.recommendation_agent.process(skill_gap)

        return CandidateWorkflowResult(
            match=match,
            evaluation=evaluation,
            skill_gap=skill_gap,
            recommendations=recommendations,
        )
