# TalentLens AI

An explainable, AI-assisted resume-screening platform. Development begins with a small, testable foundation and then adds each analysis module in order.

## Phase 0 status

- FastAPI backend with a health endpoint
- React + Vite frontend that verifies the API connection
- Environment-based PostgreSQL configuration
- Local development configuration without Docker

## Run locally

### Backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `DATABASE_URL` in `backend/.env` after PostgreSQL is installed and a database has been created. The health endpoint does not depend on the database yet.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the address Vite displays (normally `http://localhost:5173`).

## First API endpoint

`GET http://localhost:8000/api/v1/health`

## Module 1: Job Description Analysis

`POST http://localhost:8000/api/v1/jobs/analyze`

```json
{
  "job_title": "Backend Developer",
  "job_description": "Develop REST API services using Python and FastAPI. Candidates need 3+ years of experience. Docker is preferred."
}
```

Always computes a transparent rule-based baseline first. If `ENABLE_LLM_EXTRACTION=true` and `ANTHROPIC_API_KEY` is set, an LLM extraction pass runs on top and its output is used **field by field**, only where it's validly typed — any missing/malformed field, or any LLM failure, silently keeps the baseline value. The response shape never changes.

## Module 2: Resume Parsing

`POST http://localhost:8000/api/v1/resumes/parse`

Upload a PDF or DOCX resume as the `file` form field. The endpoint accepts files up to 10 MB and returns a structured candidate profile.

## Module 3: Candidate Matching and ATS Score

`POST http://localhost:8000/api/v1/matches/score`

Send a structured `job_profile` and `candidate_profile` to receive an overall ATS-style score, the six weighted component scores, and matched/missing skills. The scoring weights and logic are fully deterministic and auditable. The `semantic_similarity` component uses Sentence Transformers embeddings (`EMBEDDING_MODEL_NAME`, default `all-MiniLM-L6-v2`) when available, and automatically falls back to lexical (Jaccard) token overlap if the model can't be loaded — e.g. no internet access to fetch weights, or `ENABLE_EMBEDDINGS=false`.

## Module 4: Explainable Candidate Evaluation

`POST http://localhost:8000/api/v1/evaluations/explain`

Send the same matching input under `match_request`. The response adds a recruiter-facing summary, recommendation, strengths, gaps, and requirement-by-requirement evidence. The recommendation, strengths, gaps, and evidence are always computed deterministically from the match result. Only the free-text `summary` is optionally phrased by an LLM when `ENABLE_LLM_EXTRACTION=true` — the LLM is given the already-computed score and skill lists as ground truth and asked only to phrase them, not judge fit itself; any failure falls back to the templated summary.

## AI layer configuration

See `backend/.env.example` for `ENABLE_EMBEDDINGS`, `EMBEDDING_MODEL_NAME`, `ENABLE_LLM_EXTRACTION`, `ANTHROPIC_API_KEY`, and `LLM_MODEL`. Both the embedding provider and the LLM provider are designed to degrade to the deterministic baseline on any failure, so the API never breaks because a model or API key is unavailable.

## Module 5: Candidate Ranking and Comparison

`POST http://localhost:8000/api/v1/rankings/rank` ranks 2–200 candidate profiles for one job. `POST http://localhost:8000/api/v1/rankings/compare` returns their respective strengths and gaps for side-by-side presentation.

## Module 6: Skill Gap Analysis

`POST http://localhost:8000/api/v1/skill-gaps/analyze` classifies missing required skills as `critical` and missing preferred skills as `important`.

## Module 7: Personalized Skill Recommendations

`POST http://localhost:8000/api/v1/recommendations/generate` converts a skill-gap result into prioritized learning paths.

## Analysis Orchestration

`POST http://localhost:8000/api/v1/workflows/candidate-analysis` coordinates matching, explanation, skill-gap analysis, and learning recommendations for one structured job and candidate profile.

## PostgreSQL persistence

The backend now includes database models for `jobs`, `candidates`, and `applications`. Once local PostgreSQL is installed and `DATABASE_URL` is set in `backend/.env`, create the initial tables with:

```powershell
.venv\Scripts\python.exe -m app.db.initialize
```
