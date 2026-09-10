import React, { useEffect, useState } from "react";
import {
  Briefcase,
  Calendar,
  Building2,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  ArrowLeft,
  Sparkles,
  Award,
  Layers,
} from "lucide-react";
import { API_URL, StoredApplication } from "../api";
import { useAuth } from "../auth/AuthContext";
import { Card } from "./ui/Card";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { StatusBadge } from "./ui/StatusBadge";
import { ProgressRing } from "./ui/ProgressRing";
import { ProgressBar } from "./ui/ProgressBar";
import { SkillChip } from "./ui/SkillChip";
import { Timeline } from "./ui/Timeline";
import { EmptyState } from "./ui/EmptyState";
import { LoadingState } from "./ui/LoadingState";
import { PageHeader } from "./ui/PageHeader";

interface MyApplicationsProps {
  onBrowseJobs?: () => void;
  onNavigate?: (tab: "skill_analysis" | "recommendations" | "browse_jobs") => void;
}

export const MyApplications: React.FC<MyApplicationsProps> = ({ onBrowseJobs, onNavigate }) => {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<StoredApplication | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    fetch(`${API_URL}/applications`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : []))
      .then(setApplications)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Loading your applications and ATS evaluations..." rows={4} />;
  }

  // Selected Application Focused View: Progress & AI Evaluation Rationale
  if (selectedApp) {
    const match = selectedApp.match;
    const breakdown = (match as any)?.score_breakdown || match?.component_scores;

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        {/* Back Button */}
        <div>
          <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => setSelectedApp(null)}>
            Back to Applications
          </Button>
        </div>

        {/* Header Banner & Application Progress Timeline */}
        <Card elevated>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "20px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                  {selectedApp.job_title || "Position Evaluation"}
                </h2>
                <StatusBadge status={selectedApp.status} />
              </div>
              <p style={{ fontSize: "14px", color: "var(--accent-primary)", fontWeight: 600, margin: 0 }}>
                {selectedApp.company_name || "Enterprise Company"}
              </p>
              <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                Applied on {new Date(selectedApp.created_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })}
              </p>
            </div>

            <ProgressRing score={match?.overall_match_score || 0} size={110} sublabel="ATS Score" />
          </div>

          {/* Application Status Timeline */}
          <div style={{ marginTop: "24px", paddingTop: "20px", borderTop: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "12px" }}>
              Application Progress Timeline
            </span>
            <Timeline currentStatus={selectedApp.status} />
          </div>
        </Card>

        {/* 4-Pillar Score Breakdown */}
        {breakdown && (
          <Card>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
              ATS Component Score Breakdown
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
              <ProgressBar
                label="Required Skills"
                weightLabel="35% weight"
                value={breakdown.required_skills ?? (breakdown.skill_match ? breakdown.skill_match * 100 : 0)}
              />
              <ProgressBar
                label="Experience Alignment"
                weightLabel="20% weight"
                value={breakdown.experience ?? (breakdown.experience_match ? breakdown.experience_match * 100 : 0)}
              />
              <ProgressBar
                label="Education Relevance"
                weightLabel="10% weight"
                value={breakdown.education ?? (breakdown.education_match ? breakdown.education_match * 100 : 0)}
              />
              <ProgressBar
                label="Semantic Similarity"
                weightLabel="15% weight"
                value={breakdown.semantic_similarity ?? (breakdown.semantic_similarity ? breakdown.semantic_similarity * 100 : 0)}
              />
            </div>
          </Card>
        )}

        {/* AI Evaluation Rationale */}
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Sparkles size={18} color="var(--accent-primary)" />
              <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                AI Evaluation Rationale
              </h3>
            </div>
            {selectedApp.evaluation?.recommendation && (
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "4px 12px",
                  borderRadius: "9999px",
                  backgroundColor: selectedApp.evaluation.recommendation.includes("Recommended for")
                    ? "rgba(16, 185, 129, 0.15)"
                    : selectedApp.evaluation.recommendation.includes("gaps")
                    ? "rgba(245, 158, 11, 0.15)"
                    : "rgba(99, 102, 241, 0.15)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: selectedApp.evaluation.recommendation.includes("Recommended for")
                    ? "var(--color-success)"
                    : selectedApp.evaluation.recommendation.includes("gaps")
                    ? "#FBBF24"
                    : "var(--accent-primary)",
                }}
              >
                <span>🎯 {selectedApp.evaluation.recommendation}</span>
              </div>
            )}
          </div>
          <div
            style={{
              backgroundColor: "var(--bg-input)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              padding: "16px",
              fontSize: "14px",
              color: "var(--text-primary)",
              lineHeight: 1.6,
            }}
          >
            {(() => {
              const raw = selectedApp.evaluation?.summary;
              if (raw && raw.trim().length >= 30 && !raw.trim().endsWith(" an") && !raw.trim().endsWith(" a") && !raw.trim().endsWith(" the")) {
                return raw;
              }
              const score = selectedApp.match?.overall_match_score || 0;
              const exact = selectedApp.match?.exact_matched_skills || selectedApp.match?.matched_skills || [];
              const related = selectedApp.match?.related_matched_skills || [];
              const missing = selectedApp.match?.missing_required_skills || [];
              const parts: string[] = [];
              if (exact.length > 0) parts.push(`demonstrates verified core competencies in ${exact.join(", ")}`);
              if (related.length > 0) parts.push(`possesses transferable foundations in ${related.join(", ")}`);
              if (missing.length > 0) parts.push(`has critical skill gaps in ${missing.slice(0, 5).join(", ")}`);
              else if (exact.length === 0 && related.length === 0) parts.push(`does not currently list direct technical keywords for the primary required stack`);
              const detail = parts.join("; ") || "profile evaluated against job criteria";
              const rec = selectedApp.evaluation?.recommendation || (missing.length > 0 ? "Review required skill gaps before progressing" : score >= 80 ? "Recommended for technical interview" : "Consider for recruiter review");
              return `Candidate holds an overall ATS match score of ${score}% for the ${selectedApp.job_title || "target"} role. The applicant ${detail}. Recommendation: ${rec}.`;
            })()}
          </div>

          {/* Dedicated Tab Action Prompts */}
          {onNavigate && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "20px" }}>
              <div
                style={{
                  backgroundColor: "rgba(99, 102, 241, 0.08)",
                  border: "1px solid rgba(99, 102, 241, 0.25)",
                  borderRadius: "var(--radius-md)",
                  padding: "14px 16px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "10px",
                }}
              >
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: 700, color: "var(--accent-primary)", margin: "0 0 4px" }}>
                    🔍 Skill Gap Intelligence
                  </h4>
                  <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                    Inspect your full matched skill matrix, critical gaps, and priority ratings.
                  </p>
                </div>
                <Button variant="secondary" size="sm" onClick={() => onNavigate("skill_analysis")}>
                  Open Skill Analysis Tab →
                </Button>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(124, 58, 237, 0.08)",
                  border: "1px solid rgba(124, 58, 237, 0.25)",
                  borderRadius: "var(--radius-md)",
                  padding: "14px 16px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "10px",
                }}
              >
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#C084FC", margin: "0 0 4px" }}>
                    📚 Milestone Learning Paths
                  </h4>
                  <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                    Follow step-by-step learning sequences and practical projects to close your gaps.
                  </p>
                </div>
                <Button variant="secondary" size="sm" onClick={() => onNavigate("recommendations")}>
                  Open Recommendations Tab →
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    );
  }

  // Applications Overview List
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="My Applications"
        subtitle="Review your submitted applications, real-time status tracking, and AI match scores."
      />

      {applications.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {applications.map((app) => (
            <Card
              key={app.id}
              elevated
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "16px",
                cursor: "pointer",
                transition: "border-color 0.15s ease",
              }}
              onClick={() => setSelectedApp(app)}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "16px", minWidth: "260px" }}>
                <ProgressRing score={app.match?.overall_match_score || 0} size={64} strokeWidth={6} />
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                      {app.job_title || "Application"}
                    </h3>
                    <StatusBadge status={app.status} size="sm" />
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--accent-primary)", fontWeight: 600, margin: "2px 0 0" }}>
                    {app.company_name}
                  </p>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "4px 0 0" }}>
                    Applied {new Date(app.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <Button variant="secondary" size="sm" onClick={() => setSelectedApp(app)}>
                  View Full Evaluation & Gaps →
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Applications Submitted Yet"
          description="Browse available job positions and upload your resume to receive immediate ATS screening and personalized upskilling roadmaps."
          actionText="Browse Open Jobs"
          onAction={onBrowseJobs}
        />
      )}
    </div>
  );
};