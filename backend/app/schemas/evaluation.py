from pydantic import BaseModel

from app.schemas.match import MatchRequest, MatchResult


class EvaluationRequest(BaseModel):
    match_request: MatchRequest


class EvidenceItem(BaseModel):
    requirement: str
    status: str
    evidence: str


class CandidateEvaluation(BaseModel):
    match: MatchResult
    recommendation: str
    summary: str
    strengths: list[str]
    gaps: list[str]
    evidence: list[EvidenceItem]
