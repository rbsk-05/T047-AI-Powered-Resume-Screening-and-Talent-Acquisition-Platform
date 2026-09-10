import React, { useEffect, useState } from "react";
import { Users, Mail, Briefcase, FileText, Calendar, Building2, Search, Filter } from "lucide-react";
import { API_URL, listMyJobs, StoredApplication, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { Select } from "../ui/Select";
import { Input } from "../ui/Input";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const RecruiterCandidatesPage: React.FC = () => {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("all");
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedSkills, setExpandedSkills] = useState<Record<string, boolean>>({});

  const toggleSkillsExpand = (e: React.MouseEvent, appId: string) => {
    e.stopPropagation();
    setExpandedSkills((prev) => ({ ...prev, [appId]: !prev[appId] }));
  };


  useEffect(() => {
    if (!token) return;
    setIsLoading(true);

    async function loadData() {
      try {
        const jobsData = await listMyJobs(token!);
        setJobs(jobsData);

        const appsPromises = jobsData.map((j) =>
          fetch(`${API_URL}/applications/job/${j.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then((r) => (r.ok ? r.json() : []))
        );
        const results = await Promise.all(appsPromises);
        setApplications(results.flat());
      } catch (err) {
        console.error("Failed to load candidate applications:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Loading candidates applied to your jobs..." rows={4} />;
  }

  const jobOptions = [
    { value: "all", label: `All Jobs (${jobs.length})` },
    ...jobs.map((j) => ({ value: j.id, label: `${j.title} (${applications.filter((a) => a.job_id === j.id).length} applicants)` })),
  ];

  const filteredApps = applications.filter((app) => {
    const matchesJob = selectedJobId === "all" || app.job_id === selectedJobId;
    const q = searchQuery.toLowerCase().trim();
    const candidateName = (app.candidate_name || app.candidate_profile?.name || app.company_name || "").toLowerCase();
    const jobTitle = (app.job_title || "").toLowerCase();
    const matchesSearch = !q || candidateName.includes(q) || jobTitle.includes(q);

    return matchesJob && matchesSearch;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Candidate Directory"
        subtitle="Review the candidates who have submitted applications for your job positions."
      />

      {/* Controls: Job Selector & Search */}
      <Card style={{ padding: "16px 20px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "minmax(240px, 1fr) minmax(280px, 2fr)", gap: "16px", alignItems: "center" }}>
          <Select
            label="Filter by Job Position"
            options={jobOptions}
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{ marginBottom: 0 }}
          />

          <Input
            label="Search Candidate"
            placeholder="Search candidate by name or target position..."
            icon={Search}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ marginBottom: 0 }}
          />
        </div>
      </Card>

      {/* Candidates Table / Cards */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
          Showing <strong style={{ color: "var(--text-primary)" }}>{filteredApps.length}</strong> candidate{filteredApps.length === 1 ? "" : "s"} applied
        </p>
      </div>

      {filteredApps.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {filteredApps.map((app) => {
            const name = app.candidate_name || app.candidate_profile?.name || app.company_name || "Applicant";
            const role = app.candidate_profile?.role;
            const email = app.candidate_profile?.email;
            const skills = app.candidate_profile?.skills || app.match?.matched_skills || [];

            return (
              <Card
                key={app.id}
                elevated
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "16px",
                  padding: "16px 20px",
                }}
              >
                {/* Candidate Info */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px", flex: "1 1 300px" }}>
                  <div
                    style={{
                      width: "44px",
                      height: "44px",
                      borderRadius: "50%",
                      background: "var(--accent-gradient)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#FFFFFF",
                      fontSize: "16px",
                      fontWeight: 700,
                      flexShrink: 0,
                    }}
                  >
                    {name.charAt(0)}
                  </div>

                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                      <h4 style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                        {name}
                      </h4>
                      {role && (
                        <Badge variant="primary" size="sm">
                          {role}
                        </Badge>
                      )}
                      <StatusBadge status={app.status} size="sm" />
                    </div>

                    <p style={{ fontSize: "13px", color: "var(--accent-primary)", fontWeight: 500, margin: "2px 0 0" }}>
                      Applied for: <strong>{app.job_title || "Role"}</strong>
                      {email && <span style={{ color: "var(--text-muted)", marginLeft: "8px" }}>· {email}</span>}
                    </p>

                    {skills.length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                        {((expandedSkills[app.id] ? skills : skills.slice(0, 5)) || []).map((s, sIdx) => (
                          <span
                            key={sIdx}
                            style={{
                              fontSize: "11px",
                              backgroundColor: "var(--bg-input)",
                              color: "var(--text-secondary)",
                              padding: "2px 8px",
                              borderRadius: "4px",
                              border: "1px solid var(--border-subtle)",
                            }}
                          >
                            {s}
                          </span>
                        ))}
                        {skills.length > 5 && (
                          <button
                            type="button"
                            onClick={(e) => toggleSkillsExpand(e, app.id)}
                            style={{
                              background: "var(--bg-card-hover, rgba(255, 255, 255, 0.08))",
                              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.15))",
                              borderRadius: "12px",
                              color: "var(--accent-primary, #6366f1)",
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "1px 6px",
                              cursor: "pointer",
                              transition: "all 0.2s ease",
                              outline: "none",
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(99, 102, 241, 0.15)")}
                            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-card-hover, rgba(255, 255, 255, 0.08))")}
                          >
                            {expandedSkills[app.id] ? "Show less" : `+${skills.length - 5} more`}
                          </button>
                        )}
                      </div>
                    )}

                    <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "4px 0 0", display: "flex", alignItems: "center", gap: "6px" }}>
                      <Calendar size={13} />
                      Applied on {new Date(app.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                    </p>
                  </div>
                </div>

                {/* Candidate Application Match & Badge */}
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <div style={{ textAlign: "right" }}>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>ATS Score</span>
                    <span style={{ fontSize: "16px", fontWeight: 800, color: (app.match?.overall_match_score || 0) >= 75 ? "var(--color-success)" : "var(--accent-primary)" }}>
                      {app.match?.overall_match_score || 0}%
                    </span>
                  </div>
                  <Badge variant="neutral" size="md">
                    Verified Applicant
                  </Badge>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No Candidates Found"
          description={
            applications.length === 0
              ? "No candidates have applied to your jobs yet."
              : "No candidates match the selected job filter or search query."
          }
        />
      )}
    </div>
  );
};
