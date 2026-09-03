import { useEffect, useState } from "react";
import { listJobs, StoredJob } from "../api";
import { ChipGroup } from "./ChipGroup";
import { ApplyModal } from "./ApplyModal";
import { MyApplications } from "./MyApplications";

export function CandidatePortal() {
  const [activeTab, setActiveTab] = useState<"browse" | "applications">("browse");
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<StoredJob | null>(null);
  const [showApplyModal, setShowApplyModal] = useState(false);

  useEffect(() => {
    if (activeTab !== "browse") return;
    setIsLoading(true);
    listJobs()
      .then(setJobs)
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, [activeTab]);

  if (selectedJob && activeTab === "browse") {
    return (
      <div className="layout-row">
        <div className="main-content" style={{ maxWidth: "800px", margin: "0 auto" }}>
          <button className="ghost-button" onClick={() => setSelectedJob(null)} style={{ marginBottom: "1rem" }}>
            ← Back to Jobs
          </button>
          
          <div className="panel">
            <h2 style={{ marginBottom: "0.25rem" }}>{selectedJob.title}</h2>
            <p className="eyebrow" style={{ fontSize: "1rem" }}>{selectedJob.company_name}</p>
            
            <div style={{ display: "flex", gap: "1rem", color: "var(--color-text-secondary)", marginTop: "1rem", marginBottom: "2rem" }}>
              <span>📍 {selectedJob.location || "Remote"}</span>
              <span>💼 {selectedJob.experience_required || "Not specified"}</span>
              <span>⏱️ {selectedJob.employment_type || "Full-time"}</span>
            </div>

            <div style={{ marginBottom: "2rem" }}>
              <button onClick={() => setShowApplyModal(true)}>Apply Now</button>
            </div>

            <div style={{ marginBottom: "2rem" }}>
              <h3>Job Description</h3>
              <p style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{selectedJob.description}</p>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", background: "var(--color-bg)", padding: "1.5rem", borderRadius: "8px" }}>
              <h3>Requirements</h3>
              
              <ChipGroup label="Required Skills (Must have)" items={selectedJob.required_skills} />
              
              {selectedJob.preferred_skills.length > 0 && (
                <ChipGroup label="Preferred Skills (Nice to have)" items={selectedJob.preferred_skills} />
              )}
              
              {selectedJob.education.length > 0 && (
                <ChipGroup label="Education" items={selectedJob.education} />
              )}
            </div>
          </div>
        </div>
        
        {showApplyModal && (
          <ApplyModal 
            job={selectedJob} 
            onClose={() => setShowApplyModal(false)} 
            onSuccess={(app) => {
              setShowApplyModal(false);
              setSelectedJob(null);
              setActiveTab("applications");
            }} 
          />
        )}
      </div>
    );
  }

  return (
    <div className="layout-row">
      <div className="sidebar">
        <h2 className="eyebrow">Candidate Portal</h2>
        <nav className="nav-menu">
          <button 
            className={`nav-item ${activeTab === "browse" ? "active" : ""}`}
            onClick={() => setActiveTab("browse")}
          >
            Browse Jobs
          </button>
          <button 
            className={`nav-item ${activeTab === "applications" ? "active" : ""}`}
            onClick={() => setActiveTab("applications")}
          >
            My Applications
          </button>
        </nav>
      </div>

      <div className="main-content">
        {activeTab === "browse" ? (
          <div className="panel">
            <h2>Available Jobs</h2>
            <p className="intro">Find your next role. Our AI matches your resume directly to these requirements.</p>
            
            {isLoading ? (
              <p>Loading jobs...</p>
            ) : jobs.length === 0 ? (
              <div className="empty-state">
                <p>No jobs available right now.</p>
              </div>
            ) : (
              <div className="job-list" style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginTop: "2rem" }}>
                {jobs.map((job) => (
                  <div key={job.id} className="card">
                    <h3 style={{ marginBottom: "0.25rem" }}>{job.title}</h3>
                    <p className="eyebrow" style={{ fontSize: "0.875rem", marginBottom: "1rem" }}>{job.company_name}</p>
                    
                    <div style={{ display: "flex", gap: "1rem", color: "var(--color-text-secondary)", fontSize: "0.875rem", marginBottom: "1rem" }}>
                      <span>📍 {job.location || "Remote"}</span>
                      <span>💼 {job.experience_required || "Not specified"}</span>
                    </div>

                    <div style={{ marginBottom: "1.5rem" }}>
                      <ChipGroup label="Key Skills" items={job.required_skills.slice(0, 5)} />
                      {job.required_skills.length > 5 && (
                        <span style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
                          +{job.required_skills.length - 5} more
                        </span>
                      )}
                    </div>

                    <div style={{ display: "flex", gap: "1rem" }}>
                      <button className="secondary-button" onClick={() => setSelectedJob(job)}>View Details</button>
                      <button onClick={() => { setSelectedJob(job); setShowApplyModal(true); }}>Apply Now</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <MyApplications />
        )}
      </div>
      
      {showApplyModal && selectedJob && (
        <ApplyModal 
          job={selectedJob} 
          onClose={() => setShowApplyModal(false)} 
          onSuccess={(app) => {
            setShowApplyModal(false);
            setSelectedJob(null);
            setActiveTab("applications");
          }} 
        />
      )}
    </div>
  );
}