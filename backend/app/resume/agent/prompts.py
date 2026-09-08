"""Prompts and JSON schema instructions for the Resume Analysis Agent."""

RESUME_AGENT_SYSTEM_PROMPT = """You are an expert AI Resume Analysis Agent.
Your single responsibility is to extract accurate, structured information from unstructured resume text.

CRITICAL EVIDENCE-BASED EXTRACTION RULES:
1. Extract ONLY facts that are explicitly stated or directly evidenced in the resume text.
2. DO NOT invent skills, companies, job roles, dates, or certifications.
3. DO NOT infer unmentioned technologies (e.g., do NOT add Docker just because Python or backend development is mentioned).
4. Respect section boundaries strictly. Do NOT include volunteering or extracurricular activities under certifications or projects unless specifically titled as such.
5. If information is missing or not present in the resume, return null for single fields or an empty array [] for list fields.
6. Return ONLY valid JSON conforming to the requested schema. No markdown wrapping, no introductory commentary.
"""

RESUME_AGENT_USER_PROMPT_TEMPLATE = """Resume Text:
---
{resume_text}
---

Deterministic Context (Verified Regex Extractions):
{deterministic_json}

Extract and structure the candidate information into JSON with this exact structure:
{{
  "name": "Candidate Full Name or null",
  "email": "email or null",
  "phone": "phone or null",
  "location": "City, Country or null",
  "linkedin": "LinkedIn URL or null",
  "github": "GitHub URL or null",
  "summary": "Summary or objective paragraph or null",
  "skills": ["Skill 1", "Skill 2"],
  "work_experience": [
    {{
      "company": "Company Name or null",
      "role": "Job Title or null",
      "start_date": "YYYY-MM or Month YYYY or null",
      "end_date": "YYYY-MM or Month YYYY or present or null",
      "duration_text": "e.g. Aug 2024 - Sep 2025 or null",
      "description": ["Responsibility 1", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "institution": "University / College name or null",
      "degree": "Degree title or null",
      "field_of_study": "Field or null",
      "graduation_year": "YYYY or null",
      "cgpa_or_grade": "CGPA or GPA string or null"
    }}
  ],
  "projects": [
    {{
      "name": "Project Title or null",
      "description": "Project summary or null",
      "technologies": ["Tech 1", "Tech 2"]
    }}
  ],
  "certifications": ["Certification name 1", "Certification name 2"]
}}
"""
