import { useEffect, useState } from "react";
import { API_URL, MatchResult, StoredApplication } from "../api";
import { useAuth } from "../auth/AuthContext";
import { ChipGroup } from "./ChipGroup";

export function MyApplications() {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<StoredApplication | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    // Add API call here
    fetch(`${API_URL}/applications`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setApplications)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  if (selectedApp) {
    const match = selectedApp.match;
    const scoreColor = match.overall_match_score >= 80 ? "var(--color-success)" : match.overall_match_score >= 60 ? "var(--color-warning)" : "var(--color-danger)";

    return (
      <div className="layout-row">
        <div className="main-content" style={{ maxWidth: "800px", margin: "0 auto" }}>
          <button className="ghost-button" onClick={() => setSelectedApp(null)} style={{ marginBottom: "1rem" }}>
            ← Back to Applications
          </button>
          
          <div className="panel">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
              <div>
                <h2>{selectedApp.job_title}</h2>
                <p className="eyebrow" style={{ fontSize: "1rem" }}>{selectedApp.company_name}</p>
                <div style={{ marginTop: "0.5rem" }}>
                   <span className="badge" style={{ background: "var(--color-primary-light)", color: "var(--color-primary)" }}>
                     Status: {selectedApp.status}
                   </span>
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
              {/* If we had structured milestones here, we'd render them, but recommendation contains it for now */}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>My Applications</h2>
      <p className="intro">Track your application status and review your ATS match scores.</p>
      
      {isLoading ? (
        <p>Loading applications...</p>
      ) : applications.length === 0 ? (
        <div className="empty-state">
          <p>You haven't applied to any jobs yet.</p>
        </div>
      ) : (
        <div className="job-list" style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1.5rem" }}>
          {applications.map((app) => {
            const scoreColor = app.match.overall_match_score >= 80 ? "var(--color-success)" : app.match.overall_match_score >= 60 ? "var(--color-warning)" : "var(--color-danger)";
            
            return (
              <div key={app.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <h3 style={{ marginBottom: "0.25rem" }}>{app.job_title}</h3>
                  <p className="eyebrow" style={{ fontSize: "0.875rem", marginBottom: "0.5rem" }}>{app.company_name}</p>
                  <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                    <span className="badge" style={{ background: "var(--color-primary-light)", color: "var(--color-primary)" }}>
                      {app.status}
                    </span>
                    <span style={{ fontSize: "0.875rem", color: "var(--color-text-secondary)" }}>
                      Applied {new Date(app.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                
                <div style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: scoreColor }}>
                      {app.match.overall_match_score}%
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", textTransform: "uppercase" }}>
                      Match
                    </div>
                  </div>
                  <button className="secondary-button" onClick={() => setSelectedApp(app)}>Review AI Feedback</button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}