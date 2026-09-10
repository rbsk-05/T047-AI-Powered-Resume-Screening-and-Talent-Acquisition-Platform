import React, { useEffect, useState } from "react";
import { Award, Sparkles, TrendingUp, Eye, SlidersHorizontal, ArrowUpRight } from "lucide-react";
import { API_URL, listMyJobs, StoredApplication, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { ProgressBar } from "../ui/ProgressBar";
import { SkillChip } from "../ui/SkillChip";
import { Select } from "../ui/Select";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";
import { CandidateEvaluationModal } from "./CandidateEvaluationModal";

export const RecruiterCandidateRankingPage: React.FC = () => {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inspectApp, setInspectApp] = useState<StoredApplication | null>(null);
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
        console.error("Failed to load ranking data:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Calculating candidate ATS rankings and analysis..." rows={4} />;
  }

  const jobOptions = jobs.map((j) => ({
    value: j.id,
    label: `${j.title} (${applications.filter((a) => a.job_id === j.id).length} applicants)`,
  }));

  const activeJob = jobs.find((j) => j.id === selectedJobId) || jobs[0];

  const jobApps = applications
    .filter((a) => a.job_id === (activeJob?.id || selectedJobId))
    .sort((a, b) => (b.match?.overall_match_score || 0) - (a.match?.overall_match_score || 0));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Candidate Ranking & ATS Analysis"
        subtitle="Objective, algorithmically ranked candidate leaderboard based on multi-pillar ATS evaluation."
      />

      {/* Job Selector Card */}
      {jobs.length > 0 && (
        <Card style={{ padding: "16px 20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
            <div style={{ minWidth: "280px" }}>
              <Select
                label="Select Job Position for Ranking Analysis"
                options={jobOptions}
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                style={{ marginBottom: 0 }}
              />
            </div>

            {activeJob && (
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <Badge variant="primary" size="md">
                  {jobApps.length} Screened Applicants
                </Badge>
                <Badge variant="success" size="md">
                  Top Score: {jobApps.length > 0 ? Math.round(jobApps[0].match?.overall_match_score || 0) : 0}%
                </Badge>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Ranked Candidate Leaderboard */}
      {jobApps.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {jobApps.map((app, idx) => {
            const score = Math.round(app.match?.overall_match_score || 0);
            const breakdown = (app.match as any)?.score_breakdown || app.match?.component_scores;
            const candidateName = app.candidate_name || app.candidate_profile?.name || (app.company_name !== activeJob?.company_name ? app.company_name : null) || `Candidate #${idx + 1}`;
            const candidateRole = app.candidate_profile?.role;

            // Ranking tier determination
            let tierBadge = <Badge variant="success" size="sm">Tier 1: High Fit (≥75%)</Badge>;
            if (score < 50) {
              tierBadge = <Badge variant="danger" size="sm">Tier 3: Low Match (&lt;50%)</Badge>;
            } else if (score < 75) {
              tierBadge = <Badge variant="warning" size="sm">Tier 2: Moderate Match (50-74%)</Badge>;
            }

            return (
              <Card
                key={app.id}
                elevated={idx < 3}
                style={{
                  border: idx === 0 ? "1px solid rgba(245, 158, 11, 0.4)" : "1px solid var(--border-default)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "16px",
                  padding: "20px 24px",
                }}
              >
                {/* Top Row: Rank, Name, Tier, Score Ring */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <div
                      style={{
                        width: "36px",
                        height: "36px",
                        borderRadius: "50%",
                        backgroundColor: idx === 0 ? "rgba(245, 158, 11, 0.25)" : idx === 1 ? "rgba(148, 163, 184, 0.2)" : "var(--bg-input)",
                        color: idx === 0 ? "#FBBF24" : idx === 1 ? "#CBD5E1" : "var(--text-muted)",
                        border: idx === 0 ? "1px solid rgba(245, 158, 11, 0.4)" : "1px solid var(--border-subtle)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "15px",
                        fontWeight: 800,
                      }}
                    >
                      #{idx + 1}
                    </div>

                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                          {candidateName}
                        </h3>
                        {tierBadge}
                        <StatusBadge status={app.status} size="sm" />
                      </div>
                      <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                        Target Role: <strong style={{ color: "var(--text-secondary)" }}>{app.job_title}</strong>
                      </p>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <ProgressRing score={score} size={64} strokeWidth={6} />
                    <Button variant="secondary" size="sm" icon={Eye} onClick={() => setInspectApp(app)}>
                      View Full Analysis
                    </Button>
                  </div>
                </div>

                {/* Score Breakdown Analysis Strip */}
                {breakdown && (
                  <div
                    style={{
                      backgroundColor: "var(--bg-input)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "var(--radius-md)",
                      padding: "14px 18px",
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                      gap: "12px",
                    }}
                  >
                    <div>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Skills Match (35%)
                      </span>
                      <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", margin: "2px 0 0" }}>
                        {Math.round(breakdown.required_skills ?? (breakdown.skill_match ? breakdown.skill_match * 100 : 0))}%
                      </p>
                    </div>

                    <div>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Experience (20%)
                      </span>
                      <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", margin: "2px 0 0" }}>
                        {Math.round(breakdown.experience ?? (breakdown.experience_match ? breakdown.experience_match * 100 : 0))}%
                      </p>
                    </div>

                    <div>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Education (10%)
                      </span>
                      <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", margin: "2px 0 0" }}>
                        {Math.round(breakdown.education ?? (breakdown.education_match ? breakdown.education_match * 100 : 0))}%
                      </p>
                    </div>

                    <div>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Semantic Similarity (15%)
                      </span>
                      <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", margin: "2px 0 0" }}>
                        {Math.round(breakdown.semantic_similarity ?? (breakdown.semantic_similarity ? breakdown.semantic_similarity * 100 : 0))}%
                      </p>
                    </div>
                  </div>
                )}

                {/* Matched & Related Skills Preview */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>
                      Matched Skills ({(app.match?.exact_matched_skills || app.match?.matched_skills || []).length} exact, {(app.match?.related_matched_skills || []).length} related)
                    </span>
                    {app.match?.confidence_level && (
                      <span
                        style={{
                          fontSize: "10px",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          backgroundColor:
                            app.match.confidence_level === "HIGH"
                              ? "rgba(16, 185, 129, 0.15)"
                              : app.match.confidence_level === "MEDIUM"
                              ? "rgba(245, 158, 11, 0.15)"
                              : "rgba(239, 68, 68, 0.15)",
                          color:
                            app.match.confidence_level === "HIGH"
                              ? "#34d399"
                              : app.match.confidence_level === "MEDIUM"
                              ? "#fbbf24"
                              : "#f87171",
                        }}
                      >
                        {app.match.confidence_level} CONFIDENCE
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                    {(app.match?.exact_matched_skills || app.match?.matched_skills || []).map((s, sIdx) => (
                      <SkillChip key={sIdx} skill={s} type="matched" size="sm" />
                    ))}
                    {(app.match?.related_matched_skills || []).map((s, rIdx) => (
                      <span
                        key={`rel-${rIdx}`}
                        style={{
                          fontSize: "11px",
                          fontWeight: 500,
                          backgroundColor: "rgba(168, 85, 247, 0.12)",
                          color: "#c084fc",
                          border: "1px solid rgba(168, 85, 247, 0.25)",
                          padding: "2px 7px",
                          borderRadius: "6px",
                        }}
                      >
                        ⚡ {s}
                      </span>
                    ))}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No Ranked Applicants"
          description="No candidates have applied to the selected job position yet. As applications arrive, they will be algorithmically ranked."
        />
      )}

      {inspectApp && (
        <CandidateEvaluationModal
          application={inspectApp}
          onClose={() => setInspectApp(null)}
        />
      )}
    </div>
  );
};
