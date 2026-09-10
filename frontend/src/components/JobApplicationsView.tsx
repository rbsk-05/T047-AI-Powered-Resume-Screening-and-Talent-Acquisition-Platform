import React, { useEffect, useState } from "react";
import {
  ArrowLeft,
  Users,
  Sparkles,
  GitCompare,
  CheckCircle2,
  XCircle,
  Eye,
  Clock,
  Filter,
  SlidersHorizontal,
} from "lucide-react";
import { API_URL, compareApplications, CompareResponse, StoredApplication, StoredJob } from "../api";
import { useAuth } from "../auth/AuthContext";
import { Card } from "./ui/Card";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { StatusBadge } from "./ui/StatusBadge";
import { ProgressRing } from "./ui/ProgressRing";
import { SkillChip } from "./ui/SkillChip";
import { EmptyState } from "./ui/EmptyState";
import { LoadingState } from "./ui/LoadingState";
import { PageHeader } from "./ui/PageHeader";
import { CandidateEvaluationModal } from "./recruiter/CandidateEvaluationModal";
import { CandidateCompareModal } from "./CandidateCompareModal";

interface JobApplicationsViewProps {
  job: StoredJob;
  onBack: () => void;
}

export const JobApplicationsView: React.FC<JobApplicationsViewProps> = ({ job, onBack }) => {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inspectApp, setInspectApp] = useState<StoredApplication | null>(null);

  // Filter state
  const [statusFilter, setStatusFilter] = useState("all");
  const [minScoreFilter, setMinScoreFilter] = useState(0);

  // Comparison state
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [compareData, setCompareData] = useState<CompareResponse | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    fetch(`${API_URL}/applications/job/${job.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : []))
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
        body: JSON.stringify({ status }),
      });
      // Update local state
      setApplications((apps) =>
        apps.map((app) => (app.id === appId ? { ...app, status } : app))
      );
      if (inspectApp && inspectApp.id === appId) {
        setInspectApp({ ...inspectApp, status });
      }
    } catch (err) {
      console.error("Failed to update status", err);
    }
  }

  function toggleCandidateSelection(appId: string) {
    setSelectedForCompare((prev) =>
      prev.includes(appId) ? prev.filter((id) => id !== appId) : [...prev, appId]
    );
  }

  async function handleCompare() {
    if (!token || selectedForCompare.length < 2) return;
    setIsComparing(true);
    setCompareError(null);
    try {
      const res = await compareApplications(token, selectedForCompare);
      setCompareData(res);
    } catch (err) {
      setCompareError(err instanceof Error ? err.message : "Failed to compare candidates");
    } finally {
      setIsComparing(false);
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading and ranking candidate pool..." rows={4} />;
  }

  // Sort candidates by match score descending (Ranking logic)
  const rankedApps = [...applications].sort(
    (a, b) => (b.match?.overall_match_score || 0) - (a.match?.overall_match_score || 0)
  );

  const filteredApps = rankedApps.filter((app) => {
    const score = app.match?.overall_match_score || 0;
    if (score < minScoreFilter) return false;

    if (statusFilter === "all") return true;
    return (app.status || "").toUpperCase() === statusFilter.toUpperCase();
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Top Breadcrumb Header */}
      <div>
        <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={onBack}>
          Back to Jobs List
        </Button>
      </div>

      <PageHeader
        title={`Applicants: ${job.title}`}
        subtitle={`Screened and ranked candidate pool for ${job.company_name || "Enterprise Company"}`}
        action={
          selectedForCompare.length >= 2 ? (
            <Button
              variant="ai"
              icon={GitCompare}
              loading={isComparing}
              onClick={handleCompare}
            >
              Compare Selected ({selectedForCompare.length})
            </Button>
          ) : (
            <Badge variant="neutral" size="md">
              Select 2+ candidates to compare
            </Badge>
          )
        }
      />

      {/* Filter and Score Slider Bar */}
      <Card style={{ padding: "14px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          {/* Status Tabs */}
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            {[
              { id: "all", label: `All (${applications.length})` },
              { id: "applied", label: `Applied (${applications.filter((a) => (a.status || "").toUpperCase() === "APPLIED").length})` },
              { id: "under_review", label: `Under Review (${applications.filter((a) => (a.status || "").toUpperCase() === "UNDER_REVIEW").length})` },
              { id: "shortlisted", label: `Shortlisted (${applications.filter((a) => (a.status || "").toUpperCase() === "SHORTLISTED").length})` },
              { id: "selected", label: `Selected (${applications.filter((a) => (a.status || "").toUpperCase() === "SELECTED").length})` },
              { id: "rejected", label: `Rejected (${applications.filter((a) => (a.status || "").toUpperCase() === "REJECTED").length})` },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setStatusFilter(tab.id)}
                style={{
                  padding: "5px 12px",
                  borderRadius: "var(--radius-full)",
                  fontSize: "12px",
                  fontWeight: 600,
                  backgroundColor: statusFilter === tab.id ? "rgba(99, 102, 241, 0.15)" : "transparent",
                  color: statusFilter === tab.id ? "#818CF8" : "var(--text-secondary)",
                  border: statusFilter === tab.id ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
                  cursor: "pointer",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Score Threshold Filter */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <SlidersHorizontal size={16} color="var(--text-muted)" />
            <span style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: 500 }}>
              Min Score: <strong style={{ color: "var(--text-primary)" }}>{minScoreFilter}%</strong>
            </span>
            <input
              type="range"
              min="0"
              max="90"
              step="10"
              value={minScoreFilter}
              onChange={(e) => setMinScoreFilter(Number(e.target.value))}
              style={{ width: "100px", accentColor: "var(--accent-primary)", cursor: "pointer", margin: 0 }}
            />
          </div>
        </div>
      </Card>

      {/* Ranked Candidate List */}
      {filteredApps.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {filteredApps.map((app, idx) => {
            const isSelected = selectedForCompare.includes(app.id);
            const score = Math.round(app.match?.overall_match_score || 0);
            const candidateName = app.company_name || `Candidate #${idx + 1}`;

            return (
              <Card
                key={app.id}
                elevated={isSelected}
                style={{
                  border: isSelected ? "1px solid var(--accent-primary)" : "1px solid var(--border-default)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "16px",
                  padding: "16px 20px",
                }}
              >
                {/* Left: Checkbox + Rank Badge + Name */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleCandidateSelection(app.id)}
                    style={{ width: "18px", height: "18px", accentColor: "var(--accent-primary)", cursor: "pointer" }}
                    title="Select to compare"
                  />

                  <span
                    style={{
                      width: "28px",
                      height: "28px",
                      borderRadius: "50%",
                      backgroundColor: idx === 0 ? "rgba(245, 158, 11, 0.2)" : "var(--bg-input)",
                      color: idx === 0 ? "#FBBF24" : "var(--text-muted)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    #{idx + 1}
                  </span>

                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <h4 style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                        {candidateName}
                      </h4>
                      <StatusBadge status={app.status} size="sm" />
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "6px" }}>
                      {app.match?.matched_skills?.slice(0, 3).map((s, sIdx) => (
                        <SkillChip key={sIdx} skill={s} type="matched" size="sm" />
                      ))}
                      {(app.match?.matched_skills?.length || 0) > 3 && (
                        <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>
                          +{(app.match?.matched_skills?.length || 0) - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: Score Ring + Actions */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <ProgressRing score={score} size={60} strokeWidth={6} />

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={Eye}
                      onClick={() => setInspectApp(app)}
                    >
                      View Report
                    </Button>

                    <Button
                      variant="primary"
                      size="sm"
                      icon={Sparkles}
                      disabled={app.status === "SHORTLISTED"}
                      onClick={() => updateStatus(app.id, "SHORTLISTED")}
                    >
                      Shortlist
                    </Button>
                  </div>
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
              ? "No candidate applications have been submitted for this position yet."
              : "No candidates match your active status or score filters."
          }
          actionText={applications.length > 0 ? "Reset Filters" : undefined}
          onAction={() => {
            setStatusFilter("all");
            setMinScoreFilter(0);
          }}
        />
      )}

      {/* Candidate Evaluation Modal */}
      {inspectApp && (
        <CandidateEvaluationModal
          application={inspectApp}
          onClose={() => setInspectApp(null)}
          onUpdateStatus={updateStatus}
        />
      )}

      {/* Candidate Comparison Modal */}
      {compareData && (
        <CandidateCompareModal
          data={compareData}
          onClose={() => setCompareData(null)}
          onUpdateStatus={updateStatus}
        />
      )}
    </div>
  );
};