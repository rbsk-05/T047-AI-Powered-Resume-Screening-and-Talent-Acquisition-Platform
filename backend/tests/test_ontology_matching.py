import pytest
from app.services.skill_ontology import SkillOntology, RelationshipType, SkillCategory
from app.schemas.job import JobProfile, JobRequirement, RequirementImportance, RequirementStatus, EvidenceType
from app.schemas.candidate import CandidateProfile, CandidateSkill, CandidateSkillEvidence
from app.schemas.match import MatchRequest, MatchLevel
from app.services.matching import CandidateMatcher
from app.services.job_analyzer import JobDescriptionAnalyzer
from app.services.evaluation import EvaluationService
from app.schemas.evaluation import EvaluationRequest


@pytest.fixture
def ontology():
    return SkillOntology()


@pytest.fixture
def matcher():
    return CandidateMatcher()


def test_ontology_canonical_normalization(ontology):
    assert ontology.normalize("C#") == "c#"
    assert ontology.normalize("c sharp") == "c#"
    assert ontology.normalize("golang") == "go"
    assert ontology.normalize("node.js") == "node.js"
    assert ontology.normalize("nodejs") == "node.js"
    assert ontology.normalize("ReactJS") == "react"
    assert ontology.normalize(".NET Core") == ".net"
    assert ontology.normalize("dotnet") == ".net"


def test_scenario_1_dotnet_stack(ontology, matcher):
    """Scenario 1: .NET, C#, ASP.NET Core, SQL stack."""
    rel_cs_net = ontology.get_relationship("c#", ".net")
    assert rel_cs_net.rel_type in (RelationshipType.ECOSYSTEM, RelationshipType.RELATED)

    rel_asp_net = ontology.get_relationship("asp.net core", ".net")
    assert rel_asp_net.rel_type in (RelationshipType.ECOSYSTEM, RelationshipType.CHILD, RelationshipType.RELATED)

    job = JobProfile(
        job_title="Senior .NET Engineer",
        required_skills=["C#", ".NET Core", "ASP.NET Core", "SQL"],
        preferred_skills=["Azure", "Docker"],
        experience="5+ years",
        education=["Computer Science"],
        responsibilities=["Build enterprise cloud microservices in .NET Core"],
        technology_specified=True,
    )
    candidate = CandidateProfile(
        name="Dotnet Dev",
        skills=["C#", ".NET Core", "ASP.NET Core", "SQL Server", "Docker"],
        experience="6 years",
        education=["B.S. in Computer Science"],
        projects=["Built enterprise ASP.NET Core microservices with Docker"],
        certifications=["Microsoft Certified: Azure Developer Associate"],
    )
    result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))
    
    assert "C#" in result.exact_matched_skills
    assert ".NET Core" in result.exact_matched_skills
    assert "ASP.NET Core" in result.exact_matched_skills
    # SQL Server matches SQL as child/related or alias
    assert any("sql" in s.lower() for s in result.exact_matched_skills + result.related_matched_skills)
    assert result.overall_match_score >= 80.0
    assert result.score_breakdown.required_skills >= 85.0


def test_scenario_2_angular_vs_react_non_equivalence(ontology, matcher):
    """Scenario 2: React != Angular non-equivalence guarantee."""
    # React and Angular are related frontend frameworks, but NEVER exact matches
    rel = ontology.get_relationship("angular", "react")
    assert rel.rel_type == RelationshipType.RELATED
    assert rel.rel_type != RelationshipType.EXACT
    assert rel.similarity_weight < 0.7  # typically 0.5

    job = JobProfile(
        job_title="Angular Developer",
        required_skills=["Angular", "TypeScript"],
        technology_specified=True,
    )
    # Candidate only knows React, not Angular
    candidate = CandidateProfile(
        name="React Dev",
        skills=["React", "TypeScript"],
    )
    result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    # Angular should be in related_matched_skills, NOT exact_matched_skills
    assert "Angular" not in result.exact_matched_skills
    assert any("Angular" in s for s in result.related_matched_skills)
    assert "TypeScript" in result.exact_matched_skills

    # Match detail explanation should explicitly describe the related match
    angular_detail = next(d for d in result.match_details if d.skill_name == "Angular")
    assert angular_detail.match_level == MatchLevel.RELATED
    assert "React" in angular_detail.matched_candidate_skill or "react" in angular_detail.matched_candidate_skill
    assert "frontend framework" in angular_detail.explanation.lower() or "related" in angular_detail.explanation.lower()


def test_scenario_3_generic_responsive_web_fairness(matcher):
    """Scenario 3: Generic prose JD without specific technologies should not penalize candidate."""
    # Job has general web frontend requirements, but technology_specified is False
    job = JobProfile(
        job_title="Web Developer",
        required_skills=["HTML", "CSS", "Responsive Web Design"],
        preferred_skills=[],
        technology_specified=False,
    )
    candidate = CandidateProfile(
        name="Modern Web Dev",
        skills=["HTML", "CSS", "React", "Tailwind CSS"],
    )
    result = matcher.score(MatchRequest(job_profile=job, candidate_profile=candidate))

    # Candidate should not be penalized with missing required skills
    assert len(result.missing_required_skills) == 0
    assert result.score_breakdown.required_skills >= 70.0


def test_scenario_4_required_vs_preferred_weighting(matcher):
    """Scenario 4: Required vs Preferred skill differentiation."""
    job = JobProfile(
        job_title="Backend Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Kubernetes", "GraphQL", "Redis"],
    )
    # Candidate has all required skills, but none of the preferred skills
    cand_all_required = CandidateProfile(
        name="Core Dev",
        skills=["Python", "FastAPI", "PostgreSQL"],
    )
    # Candidate has only preferred skills, but missing all required skills
    cand_only_preferred = CandidateProfile(
        name="Preferred Only Dev",
        skills=["Kubernetes", "GraphQL", "Redis"],
    )

    res_required = matcher.score(MatchRequest(job_profile=job, candidate_profile=cand_all_required))
    res_preferred = matcher.score(MatchRequest(job_profile=job, candidate_profile=cand_only_preferred))

    assert res_required.score_breakdown.required_skills == 100.0
    assert res_preferred.score_breakdown.required_skills == 0.0
    assert res_required.overall_match_score > res_preferred.overall_match_score
    assert len(res_required.missing_required_skills) == 0
    assert len(res_required.missing_preferred_skills) == 3
    assert len(res_preferred.missing_required_skills) == 3


def test_scenario_5_unknown_technology_handling(ontology, matcher):
    """Scenario 5: Unknown/Emerging technology should be handled gracefully."""
    unknown_tech = "QuantumFluxDB"
    is_known = ontology.is_known_skill(unknown_tech)
    assert not is_known

    job = JobProfile(
        job_title="Quantum Systems Engineer",
        required_skills=["Python", unknown_tech],
        requirements=[
            JobRequirement(
                name=unknown_tech,
                normalized_name=unknown_tech,
                importance=RequirementImportance.REQUIRED,
                evidence_type=EvidenceType.EXPLICIT,
                status=RequirementStatus.NEEDS_VERIFICATION,
                explanation="Novel or proprietary technology detected",
            )
        ]
    )
    # Candidate who has the exact unknown tech
    cand_with_unknown = CandidateProfile(
        name="Quantum Dev",
        skills=["Python", "QuantumFluxDB"],
    )
    res_with = matcher.score(MatchRequest(job_profile=job, candidate_profile=cand_with_unknown))
    assert unknown_tech in res_with.exact_matched_skills

    # Candidate without unknown tech
    cand_without_unknown = CandidateProfile(
        name="Regular Dev",
        skills=["Python", "PostgreSQL"],
    )
    res_without = matcher.score(MatchRequest(job_profile=job, candidate_profile=cand_without_unknown))
    assert unknown_tech in res_without.missing_required_skills


def test_evaluation_service_with_ontology_evidence():
    eval_svc = EvaluationService()
    job = JobProfile(
        job_title="Frontend Lead",
        required_skills=["Angular", "TypeScript"],
        preferred_skills=["Docker"],
    )
    candidate = CandidateProfile(
        name="Jane Doe",
        skills=["React", "TypeScript"],
    )
    eval_res = eval_svc.evaluate(EvaluationRequest(match_request=MatchRequest(job_profile=job, candidate_profile=candidate)))
    
    assert any("TypeScript" in s for s in eval_res.strengths)
    assert any("Angular" in g or "Docker" in g for g in eval_res.gaps)
    # Check evidence items
    angular_evidence = next(e for e in eval_res.evidence if e.requirement == "Angular")
    assert angular_evidence.status in ("related", "missing")
