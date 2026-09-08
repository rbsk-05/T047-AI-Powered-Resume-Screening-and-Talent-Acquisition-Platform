"""Deterministic regex and heuristic extraction layer."""

import re
from app.resume.section_detector import SectionDetector

# Broad skill vocabulary for deterministic matching
_SKILLS: tuple[str, ...] = (
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "C",
    "Rust", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
    "MATLAB", "Bash", "Shell", "Perl", "Dart", "Elixir",
    # Frontend
    "React", "Angular", "Vue", "Next.js", "Nuxt.js", "Svelte",
    "HTML", "CSS", "SASS", "Bootstrap", "Tailwind", "VanillaJS",
    # Backend / frameworks
    "Node.js", "Express.js", "Nest.js", "FastAPI", "Django", "Flask",
    "Spring Boot", "Laravel", "Rails", ".NET", "ASP.NET",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Nginx", "Apache", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "ArgoCD", "Helm", "CI/CD", "Linux",
    # Data & databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "SQLite", "Oracle", "SQL Server",
    "Firebase", "Supabase", "Snowflake", "BigQuery", "Redshift",
    "Kafka", "RabbitMQ", "Celery", "Airflow", "dbt",
    # ML / AI
    "TensorFlow", "PyTorch", "scikit-learn", "Keras", "XGBoost",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV", "spaCy",
    "NLTK", "Hugging Face", "LangChain", "MLflow", "Spark", "Hadoop",
    # APIs & protocols
    "REST API", "GraphQL", "gRPC", "WebSockets", "OAuth", "JWT",
    # Practices / tools
    "Git", "GitHub", "SQL", "Microservices", "Agile", "Scrum", "TDD",
    "Prometheus", "Grafana", "Stripe", "Twilio", "SendGrid",
    "Postman", "Insomnia",
)


class RegexExtractor:
    """Deterministic, regex-based baseline extraction engine."""

    SKILLS = _SKILLS

    @classmethod
    def extract_all(cls, text: str) -> dict:
        """Run all deterministic regex extractors on raw text."""
        lines = SectionDetector.clean_lines(text)
        return {
            "name": cls.extract_name(lines),
            "email": cls.extract_email(text),
            "phone": cls.extract_phone(text),
            "linkedin": cls.extract_linkedin(text),
            "github": cls.extract_github(text),
            "summary": cls.extract_summary(lines),
            "skills": cls.extract_skills(text),
            "raw_education": cls.extract_education_lines(lines),
            "raw_projects": cls.extract_project_lines(lines),
            "raw_certifications": cls.extract_certification_lines(lines),
            "raw_experience": cls.extract_experience_lines(lines),
        }

    @staticmethod
    def extract_name(lines: list[str]) -> str | None:
        """Heuristic: first non-header/title line that looks like a person's name."""
        skip_titles = {
            "curriculum vitae", "resume", "cv", "profile", "summary",
            "full stack developer", "backend developer", "software engineer",
            "frontend developer", "web developer", "data scientist",
        }
        for line in lines[:5]:
            cleaned = line.strip()
            lowered = cleaned.lower()
            if lowered in skip_titles or "@" in cleaned or "http" in cleaned or re.search(r"\d{5,}", cleaned):
                continue
            if re.fullmatch(r"[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024F .'\-]{1,60}", cleaned):
                return cleaned
        return None

    @staticmethod
    def extract_email(text: str) -> str | None:
        match = re.search(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> str | None:
        """Capture international and Indian mobile formats cleanly."""
        # Check for Indian mobile number (+91 9361465734 or 9361465734)
        in_match = re.search(r"(?:\+91[\s\-]?)?[6-9]\d{9}\b", text)
        if in_match:
            return in_match.group(0).strip()

        match = re.search(
            r"(?<!\d)(?:\+?(\d{1,3})[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,5}[\s\-.]?\d{4,6}(?!\d)",
            text,
        )
        return match.group(0).strip() if match else None

    @staticmethod
    def extract_linkedin(text: str) -> str | None:
        match = re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9\-_%]+)",
            text,
            re.IGNORECASE,
        )
        return f"https://linkedin.com/in/{match.group(1)}" if match else None

    @staticmethod
    def extract_github(text: str) -> str | None:
        match = re.search(
            r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9\-_.]+)",
            text,
            re.IGNORECASE,
        )
        return f"https://github.com/{match.group(1)}" if match else None

    @staticmethod
    def extract_summary(lines: list[str]) -> str | None:
        section = SectionDetector.extract_section_lines(
            lines, ("summary", "professional summary", "objective", "profile", "about me", "about"), max_items=4
        )
        return " ".join(section).strip() if section else None

    @classmethod
    def extract_skills(cls, text: str) -> list[str]:
        found = [
            skill
            for skill in cls.SKILLS
            if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text, re.IGNORECASE)
        ]
        seen: set[str] = set()
        result: list[str] = []
        for skill in found:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                result.append(skill)
        return result

    @staticmethod
    def extract_education_lines(lines: list[str]) -> list[str]:
        section = SectionDetector.extract_section_lines(
            lines, ("education", "academic background", "qualifications", "academic history"), max_items=6
        )
        if section:
            return section
        edu_terms = ("b.e", "b.tech", "b.sc", "b.s", "b.a", "m.sc", "m.e", "m.tech", "mba", "phd", "bachelor", "master", "computer science")
        return [line for line in lines if any(term in line.lower() for term in edu_terms)][:6]

    @staticmethod
    def extract_project_lines(lines: list[str]) -> list[str]:
        return SectionDetector.extract_section_lines(
            lines, ("projects", "project experience", "key projects", "academic projects", "personal projects"), max_items=10
        )

    @staticmethod
    def extract_certification_lines(lines: list[str]) -> list[str]:
        return SectionDetector.extract_section_lines(
            lines, ("certifications", "certificates", "licenses"), max_items=8
        )

    @staticmethod
    def extract_experience_lines(lines: list[str]) -> list[str]:
        return SectionDetector.extract_section_lines(
            lines, ("experience", "work experience", "professional experience", "employment history", "career history"), max_items=30
        )
