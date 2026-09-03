import { useEffect, useState } from "react";
import { API_URL, MatchResult, StoredApplication, StoredJob } from "../api";
import { useAuth } from "../auth/AuthContext";
import { ChipGroup } from "./ChipGroup";

type JobApplicationsViewProps = {
  job: StoredJob;
  onBack: () => void;
};

export function JobApplicationsView({ job, onBack }: JobApplicationsViewProps) {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<StoredApplication | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    fetch(`${API_URL}/applications/job/${job.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setApplications)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token, job.id]);

  async function updateStatus(appId: string, status: string) {
    if (!token) return;
    try {
      await fetch(`${API_URL}/applications/${appId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status })
      });
      // Update local state
      setApplications(apps => apps.map(app => app.id === appId ? { ...app, status } : app));
      if (selectedApp && selectedApp.id === appId) {
        setSelectedApp({ ...selectedApp, status });
      }
    } catch (err) {
      console.error("Failed to update status", err);
    }
  }

  if (selectedApp) {
    const match = selectedApp.match;
    const scoreColor = match.overall_match_score >= 80 ? "var(--color-success)" : match.overall_match_score >= 60 ? "var(--color-warning)" : "var(--color-danger)";

    return (
      <div className="panel">
        <button className="ghost-button" onClick={() => setSelectedApp(null)} style={{ marginBottom: "1rem" }}>
          ← Back to Applicants
        </button>
        
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
          <div>
            <h2>{selectedApp.company_name /* Candidate name hack */}</h2>
            <p className="eyebrow" style={{ fontSize: "1rem" }}>Applied for {job.title}</p>
            <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
               <button 
                 onClick={() => updateStatus(selectedApp.id, "shortlisted")} 
                 disabled={selectedApp.status === "shortlisted"}
                 className={selectedApp.status === "shortlisted" ? "secondary-button" : ""}
               >
                 Shortlist
               </button>
               <button 
                 onClick={() => updateStatus(selectedApp.id, "rejected")} 
                 disabled={selectedApp.status === "rejected"}
                 className={selectedApp.status === "rejected" ? "secondary-button" : ""}
               >
                 Reject
               </button>
               <button 
                 onClick={() => updateStatus(selectedApp.id, "hired")} 
                 disabled={selectedApp.status === "hired"}
                 style={{ background: "var(--color-success)", color: "white" }}
               >
                 Hire
               </button>
            </div>
          </div>
          
          <div style={{ textAlign: "center", padding: "1rem", background: "var(--color-bg)", borderRadius: "8px", border: `2px solid ${scoreColor}` }}>
            <div style={{ fontSize: "2rem", fontWeight: "bold", color: scoreColor }}>
              {match.overall_match_score}%
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "1px" }}>
              ATS Score
            </div>
          </div>
        </div>

        <div style={{ marginBottom: "2rem" }}>
          <h3>AI Evaluation Summary</h3>
          <p style={{ marginTop: "0.5rem", lineHeight: 1.6 }}>{selectedApp.evaluation.summary}</p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
          <div style={{ background: "var(--color-bg)", padding: "1.5rem", borderRadius: "8px" }}>
            <h3 style={{ color: "var(--color-success)", marginBottom: "1rem" }}>Strengths (Matched)</h3>
            <ul style={{ paddingLeft: "1.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {selectedApp.evaluation.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          
          <div style={{ background: "var(--color-bg)", padding: "1.5rem", borderRadius: "8px" }}>
            <h3 style={{ color: "var(--color-warning)", marginBottom: "1rem" }}>Skill Gaps (Missing)</h3>
            <ul style={{ paddingLeft: "1.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {selectedApp.evaluation.gaps.map((g, i) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          </div>
        </div>

        <div style={{ background: "var(--color-primary-light)", padding: "1.5rem", borderRadius: "8px", borderLeft: "4px solid var(--color-primary)" }}>
          <h3>Recommendation & Learning Path</h3>
          <p style={{ marginTop: "0.5rem", lineHeight: 1.6 }}>{selectedApp.evaluation.recommendation}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel">
      <button className="ghost-button" onClick={onBack} style={{ marginBottom: "1rem" }}>
        ← Back to Jobs
      </button>
      <h2>Applicants for {job.title}</h2>
      <p className="intro">Candidates are ranked by their AI match score.</p>
      
      {isLoading ? (
        <p>Loading applicants...</p>
      ) : applications.length === 0 ? (
        <div className="empty-state">
          <p>No one has applied to this job yet.</p>
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1.5rem", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--color-border)" }}>
              <th style={{ padding: "1rem 0" }}>Candidate</th>
              <th style={{ padding: "1rem 0" }}>ATS Score</th>
              <th style={{ padding: "1rem 0" }}>Status</th>
              <th style={{ padding: "1rem 0" }}>Applied On</th>
              <th style={{ padding: "1rem 0" }}></th>
            </tr>
          </thead>
          <tbody>
            {applications.map((app) => {
              const scoreColor = app.match.overall_match_score >= 80 ? "var(--color-success)" : app.match.overall_match_score >= 60 ? "var(--color-warning)" : "var(--color-danger)";
              
              return (
                <tr key={app.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "1rem 0", fontWeight: "bold" }}>{app.company_name /* Hack for candidate name */}</td>
                  <td style={{ padding: "1rem 0", color: scoreColor, fontWeight: "bold" }}>{app.match.overall_match_score}%</td>
                  <td style={{ padding: "1rem 0" }}>
                    <span className="badge" style={{ background: "var(--color-primary-light)", color: "var(--color-primary)" }}>
                      {app.status}
                    </span>
                  </td>
                  <td style={{ padding: "1rem 0", color: "var(--color-text-secondary)" }}>
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ padding: "1rem 0", textAlign: "right" }}>
                    <button className="secondary-button" onClick={() => setSelectedApp(app)}>Review Details</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}