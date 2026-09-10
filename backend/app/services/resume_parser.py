import io

import fitz
from docx import Document

from app.schemas.candidate import CandidateProfile
from app.services.llm_provider import LLMProvider, get_llm_provider


class ResumeParser:
    """Extract candidate profile from resume text using AI Agent (LLM)."""

    ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()

    @staticmethod
    def _is_list_of_str(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    def extract_text(self, filename: str, content: bytes) -> str:
        """Extract raw text from PDF, DOCX, or text file with resilient fallback."""
        if not content:
            raise ValueError("The uploaded resume file is empty.")

        suffix = filename.lower().rsplit(".", maxsplit=1)
        suffix = f".{suffix[-1]}" if len(suffix) == 2 else ""

        if suffix == ".pdf":
            try:
                document = fitz.open(stream=content, filetype="pdf")
                try:
                    text = "\n".join(page.get_text() for page in document)
                    if text.strip():
                        return text
                finally:
                    document.close()
            except Exception:
                pass

        if suffix == ".docx":
            try:
                document = Document(io.BytesIO(content))
                text = "\n".join(paragraph.text for paragraph in document.paragraphs)
                if text.strip():
                    return text
            except Exception:
                pass

        # Text file or resilient byte decoding fallback
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                decoded = content.decode(encoding)
                if decoded.strip():
                    return decoded
            except UnicodeDecodeError:
                continue

        raise ValueError("Could not extract readable text from the uploaded document. Please check the file format.")

    def parse_text(self, text: str) -> CandidateProfile:
        """Parse resume text using AI Agent and Skill Ontology."""
        if not text or len(text.strip()) < 10:
            raise ValueError("The uploaded document is empty or unreadable.")

        from app.schemas.candidate import CandidateSkill, CandidateSkillEvidence
        from app.services.skill_ontology import get_skill_ontology

        ontology = get_skill_ontology()

        # Delegate parsing directly to AI Agent
        extracted = self.llm_provider.extract_candidate_profile(text)
        if extracted:
            raw_skills = extracted.get("skills") if self._is_list_of_str(extracted.get("skills")) else []
            norm_skills: list[str] = []
            structured_skills: list[CandidateSkill] = []

            for s in raw_skills:
                canonical, _ = ontology.normalize_skill(s)
                c_name = canonical if canonical else s
                if c_name not in norm_skills:
                    norm_skills.append(c_name)

            raw_struct = extracted.get("structured_skills")
            if isinstance(raw_struct, list):
                for item in raw_struct:
                    if isinstance(item, dict) and item.get("skill_name"):
                        s_name = str(item.get("skill_name"))
                        canonical, _ = ontology.normalize_skill(s_name)
                        structured_skills.append(
                            CandidateSkill(
                                skill_name=s_name,
                                normalized_name=canonical if canonical else s_name,
                                evidence_text=str(item.get("evidence_text", "")),
                                evidence_type=CandidateSkillEvidence.EXPLICIT if str(item.get("evidence_type", "")).upper() == "EXPLICIT" else CandidateSkillEvidence.INFERRED,
                                confidence=str(item.get("confidence", "HIGH")),
                            )
                        )

            # Fallback structured skills if LLM didn't return structured_skills list
            if not structured_skills and norm_skills:
                for s in norm_skills:
                    structured_skills.append(
                        CandidateSkill(
                            skill_name=s,
                            normalized_name=s,
                            evidence_text=f"Demonstrated in resume: {s}",
                            evidence_type=CandidateSkillEvidence.EXPLICIT,
                            confidence="HIGH",
                        )
                    )

            return CandidateProfile(
                name=extracted.get("name") if isinstance(extracted.get("name"), str) else None,
                role=extracted.get("role") if isinstance(extracted.get("role"), str) else None,
                email=extracted.get("email") if isinstance(extracted.get("email"), str) else None,
                phone=extracted.get("phone") if isinstance(extracted.get("phone"), str) else None,
                skills=norm_skills,
                structured_skills=structured_skills,
                experience=extracted.get("experience") if isinstance(extracted.get("experience"), str) else None,
                education=extracted.get("education") if self._is_list_of_str(extracted.get("education")) else [],
                projects=extracted.get("projects") if self._is_list_of_str(extracted.get("projects")) else [],
                certifications=extracted.get("certifications") if self._is_list_of_str(extracted.get("certifications")) else [],
                domain_knowledge=extracted.get("domain_knowledge") if self._is_list_of_str(extracted.get("domain_knowledge")) else [],
            )

        # Fallback for offline/test environments without active API connection
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        email = None
        skills = []
        for line in lines:
            if "@" in line and "." in line and not email:
                for token in line.split():
                    if "@" in token and "." in token:
                        email = token.strip("<>(),;:")
            lower = line.lower()
            if any(k in lower for k in ["skills:", "technical skills:", "technologies:", "tools:"]):
                parts = line.split(":", 1)[1] if ":" in line else line
                for s in parts.replace("•", ",").replace("|", ",").split(","):
                    item = s.strip()
                    if item and len(item) < 30:
                        canonical, _ = ontology.normalize_skill(item)
                        skills.append(canonical if canonical else item)

        struct_fallback = [
            CandidateSkill(skill_name=s, normalized_name=s, evidence_text=s, evidence_type=CandidateSkillEvidence.EXPLICIT, confidence="HIGH")
            for s in skills
        ]

        return CandidateProfile(
            name=lines[0] if lines else None,
            email=email,
            skills=skills,
            structured_skills=struct_fallback,
            education=[],
            projects=[],
            certifications=[],
            domain_knowledge=[],
        )

    def parse(self, filename: str, content: bytes) -> CandidateProfile:
        return self.parse_text(self.extract_text(filename, content))



