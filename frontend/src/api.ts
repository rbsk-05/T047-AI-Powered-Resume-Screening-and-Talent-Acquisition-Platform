export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export type Role = "recruiter" | "candidate";

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  company_name: string | null;
  company_description: string | null;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type JobProfile = {
  job_title: string;
  required_skills: string[];
  preferred_skills: string[];
  experience: string | null;
  education: string[];
  responsibilities: string[];
};

export type StoredJob = {
  id: string;
  title: string;
  description: string;
  company_name: string | null;
  location: string | null;
  employment_type: string | null;
  experience_required: string | null;
  required_skills: string[];
  preferred_skills: string[];
  education: string[];
  status: string;
  profile: JobProfile;
  created_at: string;
};

export type CandidateProfile = {
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: string[];
  experience: string | null;
  education: string[];
  projects: string[];
  certifications: string[];
};

export type StoredCandidate = {
  id: string;
  profile: CandidateProfile;
  resume_filename: string | null;
  created_at: string;
};

async function unwrap<T>(responsePromise: Promise<Response>): Promise<T> {
  const response = await responsePromise;
  if (!response.ok) {
    let detail = `The API returned ${response.status}.`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // response wasn't JSON; keep the generic message
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

// --- Auth ---

export function register(
  email: string,
  password: string,
  full_name: string,
  role: Role,
  company_name?: string,
  company_description?: string,
): Promise<AuthResponse> {
  return unwrap(
    fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name, role, company_name, company_description }),
    })
  );
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return unwrap(
    fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
  );
}

export function fetchCurrentUser(token: string): Promise<User> {
  return unwrap(fetch(`${API_URL}/auth/me`, { headers: authHeaders(token) }));
}

// --- Jobs (recruiter: create/list mine; candidate: browse all) ---

export type CreateJobPayload = {
  job_title: string;
  job_description: string;
  company_name: string;
  location: string;
  employment_type: string;
  experience_required: string;
  required_skills: string[];
  preferred_skills: string[];
  education: string[];
};

export function createJob(token: string, payload: CreateJobPayload): Promise<StoredJob> {
  return unwrap(
    fetch(`${API_URL}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify(payload),
    })
  );
}

export function listJobs(): Promise<StoredJob[]> {
  return unwrap(fetch(`${API_URL}/jobs`));
}

export function listMyJobs(token: string): Promise<StoredJob[]> {
  return unwrap(fetch(`${API_URL}/jobs/mine`, { headers: authHeaders(token) }));
}

export function getJob(id: string): Promise<StoredJob> {
  return unwrap(fetch(`${API_URL}/jobs/${id}`));
}

// --- Resume upload and parsing (candidate) ---

export function createCandidate(token: string, file: File): Promise<StoredCandidate> {
  const body = new FormData();
  body.append("file", file);
  return unwrap(fetch(`${API_URL}/resumes`, { method: "POST", headers: authHeaders(token), body }));
}

export function listCandidates(token: string): Promise<StoredCandidate[]> {
  return unwrap(fetch(`${API_URL}/resumes`, { headers: authHeaders(token) }));
}

// --- Applications (applying and reviewing) ---

export type MatchResult = {
  overall_match_score: number;
  component_scores: {
    skill_match: number;
    experience_match: number;
    education_match: number;
    semantic_similarity: number;
  };
  matched_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
};

export type CandidateEvaluation = {
  summary: string;
  recommendation: string;
  strengths: string[];
  gaps: string[];
};

export type StoredApplication = {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  match: MatchResult;
  evaluation: CandidateEvaluation;
  created_at: string;
  job_title?: string;
  company_name?: string;
};

export function createApplication(token: string, job_id: string, candidate_id: string): Promise<StoredApplication> {
  return unwrap(
    fetch(`${API_URL}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ job_id, candidate_id }),
    })
  );
}
