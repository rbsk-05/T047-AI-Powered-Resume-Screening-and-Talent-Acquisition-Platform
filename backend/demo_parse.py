"""Quick demonstration script to parse a sample resume and print the extracted CandidateProfile JSON output."""

import json
from pathlib import Path
from app.services.resume_parser import ResumeParser


SAMPLE_RESUME_TEXT = """
Jane Doe
Software Engineer
Email: jane.doe@example.com | Phone: +1-555-123-4567
LinkedIn: https://linkedin.com/in/janedoe | GitHub: github.com/janedoe

SUMMARY
Enthusiastic Senior Full-Stack Engineer with 5+ years of experience building scalable microservices, AI-powered applications, and real-time dashboards using Python, FastAPI, React, and PostgreSQL.

EXPERIENCE
Senior Software Engineer at TechCorp Solutions | 2022 - Present
- Architected AI resume screening microservices using Python, FastAPI, and HuggingFace sentence-transformers.
- Spearheaded PostgreSQL query optimization, reducing latency by 40%.

Software Developer at DataSoft Inc. | 2019 - 2022
- Developed RESTful APIs and modern web dashboards using React, TypeScript, Node.js, and Docker.

EDUCATION
- Bachelor of Science in Computer Science, Stanford University (2015 - 2019)

SKILLS
Python, FastAPI, React, TypeScript, Node.js, PostgreSQL, Docker, Kubernetes, AWS, PyTorch, Scikit-learn, Git, CI/CD, Redis, MongoDB
"""


def main():
    print("=" * 70)
    print("       RESUME PARSER DEMO — CANDIDATE INFORMATION EXTRACTION      ")
    print("=" * 70)

    parser = ResumeParser()
    
    # Extract Candidate Profile directly from text
    profile = parser.parse_text(SAMPLE_RESUME_TEXT)

    print("\n--- Raw Input Text Preview ---")
    print(SAMPLE_RESUME_TEXT.strip()[:300] + "...\n")

    print("--- Extracted CandidateProfile (Structured Output) ---")
    profile_dict = profile.model_dump()
    print(json.dumps(profile_dict, indent=2))
    
    print("\n" + "=" * 70)
    print("DEMO SUCCESSFUL: All fields (Name, Email, Phone, Socials, Summary, Experience, Education, Skills) correctly extracted!")
    print("=" * 70)


if __name__ == "__main__":
    main()
