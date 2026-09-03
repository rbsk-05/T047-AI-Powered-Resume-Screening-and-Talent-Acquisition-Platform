import { FormEvent, useEffect, useState } from "react";
import { createJob, listMyJobs, StoredJob } from "../api";
import { useAuth } from "../auth/AuthContext";
import { ChipGroup } from "./ChipGroup";
import { JobApplicationsView } from "./JobApplicationsView";

export function RecruiterDashboard() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<"jobs" | "create">("jobs");
  const [myJobs, setMyJobs] = useState<StoredJob[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [selectedJob, setSelectedJob] = useState<StoredJob | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState(user?.company_name || "");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("Full-time");
  const [experience, setExperience] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || activeTab !== "jobs") return;
    setIsLoadingJobs(true);
    listMyJobs(token)
      .then(setMyJobs)
      .catch((err) => console.error(err))
      .finally(() => setIsLoadingJobs(false));
  }, [token, activeTab]);

  async function handlePublish(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await createJob(token, {
        job_title: title,
        job_description: description,
        company_name: company,
        location,
        employment_type: employmentType,
        experience_required: experience,
        required_skills: [], // AI will fill this
        preferred_skills: [], // AI will fill this
        education: [], // AI will fill this
      });
      // Reset form and switch tab
      setTitle("");
      setLocation("");
      setExperience("");
      setDescription("");
      setActiveTab("jobs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to publish job");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="layout-row">
      <div className="sidebar">
        <h2 className="eyebrow">Recruiter Dashboard</h2>
        <nav className="nav-menu">
          <button
            className={`nav-item ${activeTab === "jobs" ? "active" : ""}`}
            onClick={() => setActiveTab("jobs")}
          >
            My Published Jobs
          </button>
          <button
            className={`nav-item ${activeTab === "create" ? "active" : ""}`}
            onClick={() => setActiveTab("create")}
          >
            Create New Job
          </button>
        </nav>
      </div>

      <div className="main-content">
        {selectedJob ? (
          <JobApplicationsView job={selectedJob} onBack={() => setSelectedJob(null)} />
        ) : activeTab === "jobs" ? (
          <div className="panel">
            <h2>My Published Jobs</h2>
            {isLoadingJobs ? (
              <p>Loading jobs...</p>
            ) : myJobs.length === 0 ? (
              <div className="empty-state">
                <p>You haven't published any jobs yet.</p>
                <button onClick={() => setActiveTab("create")} style={{ marginTop: "1rem" }}>
                  Create your first job
                </button>
              </div>
            ) : (
              <div className="job-list" style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
                {myJobs.map((job) => (
                  <div key={job.id} className="card">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <h3>{job.title}</h3>
                        <p style={{ color: "var(--color-text-secondary)", fontSize: "0.875rem", marginBottom: "1rem" }}>
                          {job.company_name} • {job.location || "Remote"} • {job.employment_type || "Full-time"}
                        </p>
                      </div>
                      <span className="badge" style={{ background: "var(--color-primary-light)", color: "var(--color-primary)" }}>
                        {job.status}
                      </span>
                    </div>
                    <div style={{ marginBottom: "1rem" }}>
                      <ChipGroup label="Required Skills" items={job.required_skills} />
                    </div>
                    <button className="secondary-button" onClick={() => setSelectedJob(job)}>
                      View Applications
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : activeTab === "create" ? (
          <div className="panel">
            <h2>Create New Job</h2>
            <p className="intro">
              Enter the details below. Our AI will automatically analyze the description to extract requirements, skills, and experience levels.
            </p>
            <form onSubmit={handlePublish} style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1.5rem" }}>
              <div className="form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div>
                  <label htmlFor="title">Job Title *</label>
                  <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="e.g. Senior Backend Developer" />
                </div>
                <div>
                  <label htmlFor="company">Company Name *</label>
                  <input id="company" value={company} onChange={(e) => setCompany(e.target.value)} required />
                </div>
              </div>

              <div className="form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
                <div>
                  <label htmlFor="location">Location</label>
                  <input id="location" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Remote, New York" />
                </div>
                <div>
                  <label htmlFor="employmentType">Employment Type</label>
                  <select id="employmentType" value={employmentType} onChange={(e) => setEmploymentType(e.target.value)}>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Freelance">Freelance</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="experience">Experience</label>
                  <input id="experience" value={experience} onChange={(e) => setExperience(e.target.value)} placeholder="e.g. 3+ years" />
                </div>
              </div>

              <div>
                <label htmlFor="description">Job Description *</label>
                <textarea 
                  id="description" 
                  value={description} 
                  onChange={(e) => setDescription(e.target.value)} 
                  required 
                  minLength={30}
                  rows={8}
                  placeholder="Describe the role, responsibilities, and requirements..."
                />
              </div>

              {error && <div className="error-message">{error}</div>}

              <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
                <button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Publishing & Analyzing..." : "Publish Job"}
                </button>
                <button type="button" className="ghost-button" onClick={() => setActiveTab("jobs")}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        ) : null}
      </div>
    </div>
  );
}
