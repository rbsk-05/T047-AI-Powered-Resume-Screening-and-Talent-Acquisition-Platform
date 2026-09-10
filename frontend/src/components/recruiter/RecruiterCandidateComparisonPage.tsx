import React, { useEffect, useState } from "react";
import { GitCompare, Sparkles, Check, X, Users, Award, Briefcase } from "lucide-react";
import { API_URL, compareApplications, CompareResponse, listMyJobs, StoredApplication, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { Select } from "../ui/Select";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const RecruiterCandidateComparisonPage: React.FC = () => {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [selectedAppIds, setSelectedAppIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Comparison result state
  const [compareResult, setCompareResult] = useState<CompareResponse | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);

    async function loadData() {
      try {
        const jobsData = await listMyJobs(token!);
        setJobs(jobsData);
        if (jobsData.length > 0 && !selectedJobId) {
          setSelectedJobId(jobsData[0].id);
        }

        const appsPromises = jobsData.map((j) =>
          fetch(`${API_URL}/applications/job/${j.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then((r) => (r.ok ? r.json() : []))
        );
        const results = await Promise.all(appsPromises);
        setApplications(results.flat());
      } catch (err) {
        console.error("Failed to load comparison data:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [token]);

  const activeJob = jobs.find((j) => j.id === selectedJobId) || jobs[0];
  const jobApps = applications.filter((a) => a.job_id === (activeJob?.id || selectedJobId));

  // Reset comparison when job changes
  useEffect(() => {
    setSelectedAppIds([]);
    setCompareResult(null);
  }, [selectedJobId]);

  const toggleAppSelection = (id: string) => {
    setSelectedAppIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleRunComparison = async () => {
    if (!token || selectedAppIds.length < 2) return;
    setIsComparing(true);
    setCompareError(null);

    try {
      const res = await compareApplications(token, selectedAppIds);
      setCompareResult(res);
    } catch (err) {
      setCompareError(err instanceof Error ? err.message : "Failed to generate comparison analysis.");
    } finally {
      setIsComparing(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading candidate comparison workspace..." rows={4} />;
  }

  const jobOptions = jobs.map((j) => ({
    value: j.id,
    label: `${j.title} (${applications.filter((a) => a.job_id === j.id).length} applicants)`,
  }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Candidate Comparison Tool"
        subtitle="Side-by-side criteria evaluation with AI-generated reasoning explaining candidate differentiators."
      />

      {/* Step 1: Select Job & Candidates */}
      <Card elevated>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
            <div style={{ minWidth: "280px" }}>
              <Select
                label="Select Job Position"
                options={jobOptions}
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                style={{ marginBottom: 0 }}
              />
            </div>

            <Button
              variant="ai"
              icon={GitCompare}
              loading={isComparing}
              disabled={selectedAppIds.length < 2 || isComparing}
              onClick={handleRunComparison}
            >
              Generate Comparison with AI ({selectedAppIds.length} Selected)
            </Button>
          </div>

          {/* Candidate Selection Checkbox Grid */}
          <div>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", display: "block", marginBottom: "8px" }}>
              Select 2 or more candidates to compare:
            </span>

            {jobApps.length > 0 ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "10px" }}>
                {jobApps.map((app) => {
                  const isChecked = selectedAppIds.includes(app.id);
                  const candName = app.candidate_name || app.candidate_profile?.name || (app.company_name !== activeJob?.company_name ? app.company_name : null) || "Applicant";
                  const candRole = app.candidate_profile?.role;
                  const score = Math.round(app.match?.overall_match_score || 0);

                  return (
                    <div
                      key={app.id}
                      onClick={() => toggleAppSelection(app.id)}
                      style={{
                        padding: "10px 14px",
                        backgroundColor: isChecked ? "rgba(99, 102, 241, 0.15)" : "var(--bg-input)",
                        border: isChecked ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                        borderRadius: "var(--radius-md)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}} // Handled by parent div
                          style={{ width: "16px", height: "16px", accentColor: "var(--accent-primary)", cursor: "pointer" }}
                        />
                        <div>
                          <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", display: "block" }}>
                            {candName}
                          </span>
                          {candRole && (
                            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                              {candRole}
                            </span>
                          )}
                        </div>
                      </div>
                      <Badge variant={score >= 75 ? "success" : "warning"} size="sm">
                        {score}%
                      </Badge>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
                No applicants available for this job yet.
              </p>
            )}
          </div>
        </div>
      </Card>

      {/* Comparison Results Section */}
      {compareResult && (
        <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* AI Reason & Rationale Card */}
          <div
            style={{
              background: "linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)",
              border: "1px solid rgba(124, 58, 237, 0.35)",
              borderRadius: "var(--radius-lg)",
              padding: "20px 24px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <Sparkles size={20} color="var(--accent-secondary)" />
              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#C084FC", margin: 0, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                AI Comparative Reason & Differentiator Analysis
              </h3>
            </div>
            <p style={{ fontSize: "14px", color: "var(--text-primary)", lineHeight: 1.6, margin: 0 }}>
              {compareResult.comparison_summary}
            </p>
          </div>

          {/* Candidate Cards Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `repeat(${compareResult.candidates.length}, 1fr)`,
              gap: "16px",
            }}
          >
            {compareResult.candidates.map((cand) => (
              <Card
                key={cand.id}
                elevated
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  textAlign: "center",
                  gap: "12px",
                  padding: "20px 16px",
                }}
              >
                <ProgressRing score={cand.overall_match_score} size={84} strokeWidth={8} />

                <div>
                  <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                    {cand.name}
                  </h4>
                  <div style={{ marginTop: "4px" }}>
                    <StatusBadge status={cand.status} size="sm" />
                  </div>
                </div>

                <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px", width: "100%" }}>
                  <div><strong>Experience:</strong> {cand.experience || "Flexible"}</div>
                  <div><strong>Education:</strong> {cand.education?.length > 0 ? cand.education.join(", ") : "CS Degree"}</div>
                  <div><strong>Matched Skills:</strong> {cand.matched_skills?.length || 0} skills</div>
                </div>
              </Card>
            ))}
          </div>

          {/* Side-by-Side Skills Coverage Matrix Table */}
          <Card>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
              <GitCompare size={18} color="var(--accent-primary)" />
              <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                Side-by-Side Requirement Coverage
              </h4>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13px" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-default)", backgroundColor: "var(--bg-input)" }}>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>
                      Skill Requirement
                    </th>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>
                      Priority
                    </th>
                    {compareResult.candidates.map((cand) => (
                      <th key={cand.id} style={{ padding: "12px 14px", color: "var(--text-primary)", fontWeight: 700, textAlign: "center" }}>
                        {cand.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {compareResult.skills_matrix.map((item, idx) => (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: "1px solid var(--border-subtle)",
                        backgroundColor: idx % 2 === 0 ? "transparent" : "rgba(255, 255, 255, 0.01)",
                      }}
                    >
                      <td style={{ padding: "12px 14px", fontWeight: 600, color: "var(--text-primary)" }}>
                        {item.skill}
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        <Badge variant={item.is_required ? "primary" : "neutral"} size="sm">
                          {item.is_required ? "Required" : "Preferred"}
                        </Badge>
                      </td>
                      {compareResult.candidates.map((cand) => {
                        const covered = item.coverage[cand.name];
                        return (
                          <td key={cand.id} style={{ padding: "12px 14px", textAlign: "center" }}>
                            {covered ? (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  width: "24px",
                                  height: "24px",
                                  borderRadius: "50%",
                                  backgroundColor: "var(--color-success-bg)",
                                  color: "var(--color-success)",
                                }}
                              >
                                <Check size={14} />
                              </span>
                            ) : (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  width: "24px",
                                  height: "24px",
                                  borderRadius: "50%",
                                  backgroundColor: "var(--color-error-bg)",
                                  color: "var(--color-error)",
                                }}
                              >
                                <X size={14} />
                              </span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
