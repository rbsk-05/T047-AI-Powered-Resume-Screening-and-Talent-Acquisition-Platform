# TalentLens AI - AI-Powered Resume Screening and Talent Acquisition Platform

An explainable, AI-assisted resume-screening platform built with FastAPI, PyTorch / SentenceTransformers, PostgreSQL, and React.

---

## Architecture & Project Structure

The project is modularized into distinct ownership areas to maintain clean separation of concerns:

```text
backend/
└── app/
    ├── api/                  # FastAPI router endpoints
    │   ├── applications.py
    │   ├── auth.py
    │   ├── evaluations.py
    │   ├── jobs.py
    │   ├── matches.py
    │   ├── rankings.py
    │   ├── recommendations.py
    │   ├── resumes.py
    │   ├── skill_gaps.py
    │   └── workflows.py
    │
    ├── matching/             # [AI/ML Owner] Semantic matching & 6-component scoring
    │   ├── embeddings.py     # SentenceTransformer embeddings & fallback provider
    │   ├── matcher.py        # CandidateMatcher service
    │   └── scorer.py        # Transparent component scoring logic
    │
    ├── ranking/              # [AI/ML Owner] Candidate ranking & multi-candidate comparison
    │   └── ranker.py         # RankingService & Comparison matrix
    │
    ├── skill_gap/            # [AI/ML Owner] Critical vs Important skill gap analysis
    │   └── analyzer.py       # SkillGapAnalyzer
    │
    ├── recommendations/      # [AI/ML Owner] Targeted upskilling roadmaps
    │   └── recommender.py    # LearningRecommendationService
    │
    ├── explanation/          # [AI/ML Owner] Explainable AI & evidence generation
    │   └── explainer.py      # EvaluationService / ExplainableAI
    │
    ├── workflows/            # [AI/ML Owner] End-to-end pipeline orchestration
    │   └── candidate_analysis.py  # CandidateAnalysisWorkflow
    │
    ├── services/             # Backwards-compatibility bridge (re-exports AI modules)
    ├── core/                 # App configuration & settings
    ├── db/                   # Database session & models
    └── main.py               # FastAPI application entry point
```

> **Note on Compatibility**: The files under `backend/app/services/` (`matching.py`, `ranking.py`, `skill_gap.py`, `recommendations.py`, `evaluation.py`, `workflow.py`) serve as a compatibility forwarding layer re-exporting classes from the feature owner folders (`app/matching/`, `app/ranking/`, etc.). The feature subdirectories are the primary logic owners.

---

## Data Flow & Processing Pipeline

```text
Resume PDF / Document
    ↓
Resume Parser
    ↓
CandidateProfile
                     ┐
                     │
                     ▼
                AI Candidate
                Analysis Layer
                     ▲
                     │
                     ┘
Job Description Text
    ↓
JD Parser / Analyzer
    ↓
JobProfile

CandidateProfile + JobProfile
    ↓
Matching (CandidateMatcher)
    ↓
Ranking (RankingService)
    ↓
Skill Gap Analysis (SkillGapAnalyzer)
    ↓
Learning Recommendations (LearningRecommendationService)
    ↓
Explainability (EvaluationService)
    ↓
Final Candidate Analysis Workflow
```

The AI Candidate Analysis Layer consumes standardized `CandidateProfile` and `JobProfile` schemas as inputs and produces stable JSON output contracts (`MatchResult`, `RankingResult`, `SkillGapResult`, `RecommendationResult`, `CandidateEvaluation`, `CandidateWorkflowResult`).

---

## Current Development Status

### Completed
- [x] Authentication & Authorization (JWT + bcrypt)
- [x] Resume upload endpoint & storage integration
- [x] **AI/ML Candidate Analysis Layer**
- [x] Candidate–Job semantic matching & 6-component scoring (Required Skills, Experience, Education, Projects, Semantic Similarity, Certifications)
- [x] Vector embeddings via SentenceTransformer (`all-MiniLM-L6-v2`) with automatic lexical fallback
- [x] Deterministic multi-candidate ranking & comparison matrix
- [x] Skill gap categorization (`critical` required gaps vs `important` preferred gaps)
- [x] Personalized learning & upskilling recommendations
- [x] Explainable AI output (recruiter summaries, positive factors, skill gaps, itemized evidence table)
- [x] End-to-end candidate analysis workflow orchestration
- [x] **Automated Test Suite**: **58/58 tests passing**

### In Progress
- [ ] Resume parser / information extraction refinements
- [ ] Job description parser / analyzer refinements
- [ ] Recruiter & Candidate frontend UI integration
- [ ] End-to-end system integration with real-world resumes & JDs

### Next Integration Milestone

The Resume Parser and JD Parser will be finalized to produce standardized `CandidateProfile` and `JobProfile` objects.

```text
Real Resume PDF + Real Job Description
                 ↓
        Production Extraction
                 ↓
    CandidateProfile + JobProfile
                 ↓
    AI Candidate Analysis Layer
                 ↓
Ranking + Skill Gaps + Recommendations + Explanation
```

---

## Known Current Limitations (Upstream Parser Work)

Real-data validation tests confirmed that the AI/ML Analysis Layer operates correctly (100% mathematical, scoring, and workflow accuracy). However, real-world end-to-end accuracy depends on upstream extraction quality:

### Resume Parser (Upstream Tracker)
- **Name Extraction**: Improve header parsing when contact details are formatted inline.
- **Phone Extraction**: Improve regex matching for international formats (e.g. `+91...`).
- **Experience Duration**: Add date range calculation (e.g. `"MAR 2026 - OCT 2026"`) in addition to explicit `"X years of experience"` text strings.
- **Skill Normalization**: Expand skill taxonomy matching for unpunctuated variants (`NodeJS` / `Node.js`, `ExpressJS` / `Express.js`, `ReactNative` / `React Native`).
- **Section Boundaries**: Ensure certification parsing cleanly stops at adjacent headers such as `VOLUNTEERING`.

### JD Parser (Upstream Tracker)
- **Section Priority**: Enhance sentence splitting to distinguish required vs preferred skill sections reliably when headings like `PREFERRED SKILLS` are used.
- **Responsibilities Extraction**: Parse bullet-pointed responsibility statements even when ending punctuation (`.!?`) is omitted.

---

## Ownership & Development Boundaries

```text
Resume Parser Module  → Person 2 (Resume / Extraction owner)
JD Parser / Analyzer  → Job / JD Analysis owner
AI/ML Analysis Layer  → AI/ML owner (Primary Ownership)
Recruiter Frontend    → Person 3 (Recruiter UI owner)
Candidate Frontend    → Person 4 (Candidate UI owner)
```

---

## API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/v1/jobs/analyze` | `POST` | Extract structured `JobProfile` from JD text |
| `/api/v1/resumes/parse` | `POST` | Parse uploaded PDF/DOCX resume into `CandidateProfile` |
| `/api/v1/matches/score` | `POST` | Calculate overall match score and 6-component breakdown |
| `/api/v1/evaluations/explain` | `POST` | Generate recruiter summary, strengths, gaps, and evidence table |
| `/api/v1/rankings/rank` | `POST` | Rank multiple candidate profiles for a target job |
| `/api/v1/rankings/compare` | `POST` | Generate side-by-side candidate comparison matrix |
| `/api/v1/skill-gaps/analyze` | `POST` | Classify missing skills into critical and important gaps |
| `/api/v1/recommendations/generate` | `POST` | Generate targeted upskilling learning roadmaps |
| `/api/v1/workflows/candidate-analysis` | `POST` | Execute full candidate analysis workflow end-to-end |

---

## Run Locally

### Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Run Tests
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```
