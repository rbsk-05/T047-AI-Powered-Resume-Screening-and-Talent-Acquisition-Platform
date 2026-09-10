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

export type JobRequirement = {
  name: string;
  normalized_name: string;
  category?: string | null;
  importance: "REQUIRED" | "PREFERRED";
  evidence_type: "EXPLICIT" | "INFERRED";
  status: "KNOWN" | "NEEDS_VERIFICATION";
  explanation: string;
};

export type JobProfile = {
  job_title: string;
  job_family?: string | null;
  technology_specified?: boolean;
  requirements?: JobRequirement[];
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
  role?: string | null;
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

export type SkillMatchDetail = {
  skill_name: string;
  match_level: "EXACT" | "RELATED" | "MISSING";
  matched_candidate_skill?: string | null;
  relationship_type: string;
  score_weight: number;
  explanation: string;
};

export type MatchResult = {
  overall_match_score: number;
  score_breakdown?: {
    required_skills: number;
    experience: number;
    education: number;
    projects: number;
    semantic_similarity: number;
    certifications: number;
  };
  component_scores?: {
    skill_match: number;
    experience_match: number;
    education_match: number;
    semantic_similarity: number;
  };
  matched_skills: string[];
  exact_matched_skills?: string[];
  related_matched_skills?: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  match_details?: SkillMatchDetail[];
  confidence_level?: string;
  evidence_coverage_pct?: number;
};

export type EvidenceItem = {
  requirement: string;
  status: string;
  evidence: string;
};

export type CandidateEvaluation = {
  summary: string;
  recommendation: string;
  strengths: string[];
  gaps: string[];
  evidence?: EvidenceItem[];
};

export function analyzeJobDescription(token: string, jobTitle: string, jobDescription: string): Promise<JobProfile> {
  return unwrap(
    fetch(`${API_URL}/jobs/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ job_title: jobTitle, job_description: jobDescription }),
    })
  );
}

export type SkillGap = {
  skill: string;
  priority: "critical" | "important" | "high" | "medium";
  reason: string;
};

export type SkillGapResult = {
  matched_skills: string[];
  gaps: SkillGap[];
};

export type LearningRecommendation = {
  skill: string;
  priority: string;
  reason: string;
  learning_path: string[];
};

export type RecommendationResult = {
  recommendations: LearningRecommendation[];
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
  candidate_name?: string;
  candidate_profile?: CandidateProfile | null;
  skill_gap?: SkillGapResult | null;
  recommendations?: RecommendationResult | null;
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

export type SkillCoverageItem = {
  skill: string;
  is_required: boolean;
  coverage: Record<string, boolean>;
};

export type CompareCandidateItem = {
  id: string;
  name: string;
  overall_match_score: number;
  experience: string | null;
  education: string[];
  status: string;
  matched_skills: string[];
  missing_skills: string[];
  summary: string;
};

export type CompareResponse = {
  job_title: string;
  skills_matrix: SkillCoverageItem[];
  candidates: CompareCandidateItem[];
  comparison_summary: string;
};

export function compareApplications(token: string, applicationIds: string[]): Promise<CompareResponse> {
  return unwrap(
    fetch(`${API_URL}/applications/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ application_ids: applicationIds }),
    })
  );
}

