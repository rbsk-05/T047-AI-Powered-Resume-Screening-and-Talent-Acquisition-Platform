import { FormEvent, useEffect, useState } from "react";
import { createJob, listJobs, JobProfile, StoredJob } from "../api";
import { useAuth } from "../auth/AuthContext";
import { ChipGroup } from "./ChipGroup";

const EXAMPLE_DESCRIPTION = `Develop REST API services using Python, FastAPI, SQL and AWS.
Candidates need 3+ years of experience and a Computer Science degree.
Docker and Kubernetes are preferred.`;

export function JobAnalysisPanel() {
  const { token } = useAuth();
  const [title, setTitle] = useState("Backend Developer");
  const [description, setDescription] = useState(EXAMPLE_DESCRIPTION);
  const [profile, setProfile] = useState<JobProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedJobs, setSavedJobs] = useState<StoredJob[]>([]);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);

  async function refreshSavedJobs() {
    setIsLoadingSaved(true);
    try {
      setSavedJobs(await listJobs());
    } catch {
      // Non-fatal: the saved-jobs list is a convenience, not the main flow.
    } finally {
      setIsLoadingSaved(false);
    }
  }

  useEffect(() => {
    refreshSavedJobs();
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    setError(null);
    setProfile(null);
    setIsLoading(true);
    try {
      const stored = await createJob(token, {
        job_title: title,
        job_description: description,
        company_name: "",
        location: "",
        employment_type: "Full-time",
        experience_required: "",
        required_skills: [],
        preferred_skills: [],
        education: [],
      });
      setProfile(stored.profile);
      await refreshSavedJobs();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not save this job.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <header>
        <p className="eyebrow">TalentLens AI</p>
        <h1>Publish a job and extract its requirements.</h1>
        <p className="intro">Enter a vacancy below. TalentLens AI identifies the essential skills and requirements, then saves it for candidates to apply against.</p>
      </header>
      <div className="workspace">
        <form onSubmit={submit}>
          <label htmlFor="job-title">Job title</label>
          <input id="job-title" value={title} onChange={(event) => setTitle(event.target.value)} minLength={2} required />
          <label htmlFor="job-description">Job description</label>
          <textarea id="job-description" value={description} onChange={(event) => setDescription(event.target.value)} minLength={30} required rows={10} />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Publishing…" : "Publish job"}
          </button>
          {error && (
            <p className="error" role="alert">
              {error} Confirm that the backend is running on port 8000.
            </p>
          )}
        </form>
        <section className="result" aria-live="polite">
          <div className="result-heading">
            <h2>Structured job profile</h2>
            {profile && <span className="ready">Saved</span>}
          </div>
          {profile ? (
            <>
              <ChipGroup label="Required skills" items={profile.required_skills} />
              <ChipGroup label="Preferred skills" items={profile.preferred_skills} tone="preferred" />
              <ChipGroup label="Education" items={profile.education} />
              <div className="profile-group">
                <h3>Experience</h3>
                <p>{profile.experience ?? "Not detected"}</p>
              </div>
              <div className="profile-group">
                <h3>Responsibilities</h3>
                <ul>
                  {profile.responsibilities.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="empty result-placeholder">Publish a job description to see the extracted profile.</p>
          )}
        </section>
      </div>
      <section className="saved-list">
        <div className="result-heading">
          <h2>Published jobs</h2>
          <span className="muted">{isLoadingSaved ? "Loading…" : `${savedJobs.length} published`}</span>
        </div>
        {savedJobs.length ? (
          <ul className="record-list">
            {savedJobs.map((job) => (
              <li key={job.id}>
                <strong>{job.profile.job_title}</strong>
                <span className="muted"> · {new Date(job.created_at).toLocaleString()}</span>
                <div className="chips">
                  {job.profile.required_skills.slice(0, 6).map((skill) => (
                    <span className="chip" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty">No jobs published yet.</p>
        )}
      </section>
    </>
  );
}
