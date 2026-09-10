from app.schemas.job import (
    ConfidenceLevel,
    EvidenceType,
    JobDescriptionAnalysisRequest,
    JobProfile,
    JobRequirement,
    RequirementImportance,
    RequirementStatus,
)
from app.services.llm_provider import LLMProvider, get_llm_provider
from app.services.skill_ontology import SkillOntology, get_skill_ontology


class JobDescriptionAnalyzer:
    """Extracts a structured job profile from a job description using AI Agent (LLM) and Skill Ontology."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        ontology: SkillOntology | None = None,
    ) -> None:
        self.llm_provider = llm_provider or get_llm_provider()
        self.ontology = ontology or get_skill_ontology()

    @staticmethod
    def _is_list_of_str(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    def analyze(self, request: JobDescriptionAnalysisRequest) -> JobProfile:
        job_title = request.job_title.strip() if request.job_title else "Job Role"
        description = request.job_description.strip()

        # 1. Delegate parsing directly to AI Agent
        extracted = self.llm_provider.extract_job_requirements(job_title, description)
        if extracted:
            extracted_title = extracted.get("job_title") if isinstance(extracted.get("job_title"), str) and extracted.get("job_title").strip() else None
            final_title = extracted_title if (job_title in ("Job Role", "", "Software Engineer") and extracted_title) else job_title

            raw_req_skills = extracted.get("required_skills") if self._is_list_of_str(extracted.get("required_skills")) else []
            raw_pref_skills = extracted.get("preferred_skills") if self._is_list_of_str(extracted.get("preferred_skills")) else []
            
            # Normalize skills and build structured requirements
            norm_required: list[str] = []
            structured_reqs: list[JobRequirement] = []

            for raw_s in raw_req_skills:
                norm_name, is_known = self.ontology.normalize_skill(raw_s)
                canonical = norm_name if norm_name else raw_s
                if canonical not in norm_required:
                    norm_required.append(canonical)
                
                skill_def = self.ontology.get_skill(canonical)
                cat = skill_def.category.value if skill_def else "Technology"
                status = RequirementStatus.KNOWN if is_known else RequirementStatus.NEEDS_VERIFICATION

                structured_reqs.append(
                    JobRequirement(
                        name=raw_s,
                        normalized_name=canonical,
                        category=cat,
                        importance=RequirementImportance.REQUIRED,
                        evidence_type=EvidenceType.EXPLICIT,
                        evidence_text=f"Explicitly required: {raw_s}",
                        confidence=ConfidenceLevel.HIGH,
                        status=status,
                    )
                )

            norm_preferred: list[str] = []
            for raw_s in raw_pref_skills:
                norm_name, is_known = self.ontology.normalize_skill(raw_s)
                canonical = norm_name if norm_name else raw_s
                if canonical not in norm_preferred and canonical not in norm_required:
                    norm_preferred.append(canonical)

                skill_def = self.ontology.get_skill(canonical)
                cat = skill_def.category.value if skill_def else "Technology"
                status = RequirementStatus.KNOWN if is_known else RequirementStatus.NEEDS_VERIFICATION

                structured_reqs.append(
                    JobRequirement(
                        name=raw_s,
                        normalized_name=canonical,
                        category=cat,
                        importance=RequirementImportance.PREFERRED,
                        evidence_type=EvidenceType.EXPLICIT,
                        evidence_text=f"Preferred: {raw_s}",
                        confidence=ConfidenceLevel.HIGH,
                        status=status,
                    )
                )

            # Inferred requirements if parsed by LLM
            llm_reqs = extracted.get("requirements")
            if isinstance(llm_reqs, list):
                for r in llm_reqs:
                    if isinstance(r, dict) and r.get("name"):
                        r_name = str(r.get("name"))
                        norm_n, is_k = self.ontology.normalize_skill(r_name)
                        canonical = norm_n if norm_n else r_name
                        ev_type = EvidenceType.INFERRED if str(r.get("evidence_type", "")).upper() == "INFERRED" else EvidenceType.EXPLICIT
                        imp = RequirementImportance.PREFERRED if str(r.get("importance", "")).upper() == "PREFERRED" else RequirementImportance.REQUIRED
                        conf = ConfidenceLevel.MEDIUM if str(r.get("confidence", "")).upper() == "MEDIUM" else ConfidenceLevel.HIGH

                        if not any(sr.normalized_name.lower() == canonical.lower() for sr in structured_reqs):
                            structured_reqs.append(
                                JobRequirement(
                                    name=r_name,
                                    normalized_name=canonical,
                                    category=str(r.get("category", "General")),
                                    importance=imp,
                                    evidence_type=ev_type,
                                    evidence_text=str(r.get("evidence_text", "")),
                                    confidence=conf,
                                    status=RequirementStatus.KNOWN if is_k else RequirementStatus.NEEDS_VERIFICATION,
                                )
                            )

            job_family = str(extracted.get("job_family")) if extracted.get("job_family") else "General Engineering"
            tech_specified = bool(extracted.get("technology_specified", True))
            if not norm_required and not norm_preferred:
                tech_specified = False

            return JobProfile(
                job_title=final_title,
                job_family=job_family,
                technology_specified=tech_specified,
                required_skills=norm_required,
                preferred_skills=norm_preferred,
                experience=extracted.get("experience") if isinstance(extracted.get("experience"), str) else None,
                education=extracted.get("education") if self._is_list_of_str(extracted.get("education")) else [],
                responsibilities=extracted.get("responsibilities") if self._is_list_of_str(extracted.get("responsibilities")) else [],
                requirements=structured_reqs,
                soft_skills=extracted.get("soft_skills") if self._is_list_of_str(extracted.get("soft_skills")) else [],
                domain_knowledge=extracted.get("domain_knowledge") if self._is_list_of_str(extracted.get("domain_knowledge")) else [],
            )

        # Baseline fallback for offline / test environments
        norm_title, _ = self.ontology.normalize_skill(job_title)
        return JobProfile(
            job_title=job_title,
            job_family="General Engineering",
            technology_specified=False,
            required_skills=[],
            preferred_skills=[],
            experience=None,
            education=[],
            responsibilities=[],
            requirements=[],
            soft_skills=[],
            domain_knowledge=[],
        )



