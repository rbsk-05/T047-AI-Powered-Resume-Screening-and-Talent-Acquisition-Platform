import React from "react";
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  Award,
  BookOpen,
  User,
  Clock,
  GraduationCap,
  Layers,
} from "lucide-react";
import { StoredApplication } from "../../api";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { ProgressBar } from "../ui/ProgressBar";
import { SkillChip } from "../ui/SkillChip";
import { Card } from "../ui/Card";

interface CandidateEvaluationModalProps {
  application: StoredApplication | null;
  onClose: () => void;
  onUpdateStatus?: (appId: string, status: string) => void;
}

export const CandidateEvaluationModal: React.FC<CandidateEvaluationModalProps> = ({
  application,
  onClose,
  onUpdateStatus,
}) => {
  if (!application) return null;

  const match = application.match;
  const breakdown = (match as any)?.score_breakdown || match?.component_scores;
  const candidateName = application.company_name || "Applicant";

  return (
    <Modal
      isOpen={!!application}
      onClose={onClose}
      title={`ATS Evaluation: ${candidateName}`}
      subtitle={`Position: ${application.job_title || "Role"}`}
      maxWidth="840px"
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        {/* Top Header Card */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            backgroundColor: "var(--bg-input)",
            border: "1px solid var(--border-default)",
            borderRadius: "var(--radius-lg)",
            padding: "20px 24px",
            flexWrap: "wrap",
            gap: "16px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "50%",
                background: "var(--accent-gradient)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#FFFFFF",
                fontSize: "18px",
                fontWeight: 700,
              }}
            >
              {candidateName.charAt(0)}
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                {candidateName}
              </h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: "2px 0 6px" }}>
                Applied {new Date(application.created_at).toLocaleDateString()}
              </p>
              <StatusBadge status={application.status} />
            </div>
          </div>

          <ProgressRing score={match?.overall_match_score || 0} size={100} sublabel="Overall ATS" />
        </div>

        {/* 4-Pillar Score Breakdown */}
        {breakdown && (
          <Card>
            <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
              Component Score Breakdown
            </h4>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
              <ProgressBar
                label="Required Skills"
                weightLabel="35%"
                value={breakdown.required_skills ?? (breakdown.skill_match ? breakdown.skill_match * 100 : 0)}
              />
              <ProgressBar
                label="Experience Alignment"
                weightLabel="20%"
                value={breakdown.experience ?? (breakdown.experience_match ? breakdown.experience_match * 100 : 0)}
              />
              <ProgressBar
                label="Education Match"
                weightLabel="10%"
                value={breakdown.education ?? (breakdown.education_match ? breakdown.education_match * 100 : 0)}
              />
              <ProgressBar
                label="Semantic Similarity"
                weightLabel="15%"
                value={breakdown.semantic_similarity ?? (breakdown.semantic_similarity ? breakdown.semantic_similarity * 100 : 0)}
              />
            </div>
          </Card>
        )}

        {/* AI Evaluation Rationale from Agent 4 */}
        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
            <Sparkles size={18} color="var(--accent-primary)" />
            <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              AI Rationale & Screening Summary
            </h4>
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
            {application.evaluation?.summary || "Candidate profile scored and ranked via intelligent ATS evaluation."}
          </div>

          {/* 3-Level Match Breakdown Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "16px" }}>
            <div>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--color-success)", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                ✓ Exact Matched Skills
              </span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {(match?.exact_matched_skills || match?.matched_skills || []).map((s, idx) => (
                  <SkillChip key={idx} skill={s} type="matched" size="sm" />
                ))}
              </div>
            </div>

            <div>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "#a855f7", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                ⚡ Related / Transferable Skills
              </span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {match?.related_matched_skills && match.related_matched_skills.length > 0 ? (
                  match.related_matched_skills.map((s, idx) => (
                    <span
                      key={idx}
                      style={{
                        fontSize: "12px",
                        fontWeight: 500,
                        backgroundColor: "rgba(168, 85, 247, 0.12)",
                        color: "#c084fc",
                        border: "1px solid rgba(168, 85, 247, 0.25)",
                        padding: "3px 8px",
                        borderRadius: "6px",
                      }}
                    >
                      {s}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>None</span>
                )}
              </div>
            </div>

            <div>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--color-error)", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                ✗ Missing Required Skills
              </span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {match?.missing_required_skills && match.missing_required_skills.length > 0 ? (
                  match.missing_required_skills.map((s, idx) => (
                    <SkillChip key={idx} skill={s} type="missing-critical" size="sm" />
                  ))
                ) : (
                  <span style={{ fontSize: "12px", color: "var(--color-success)" }}>All required skills satisfied!</span>
                )}
              </div>
            </div>

            <div>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                ○ Missing Preferred Skills
              </span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {match?.missing_preferred_skills && match.missing_preferred_skills.length > 0 ? (
                  match.missing_preferred_skills.map((s, idx) => (
                    <SkillChip key={idx} skill={s} type="preferred" size="sm" />
                  ))
                ) : (
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>None missing</span>
                )}
              </div>
            </div>
          </div>

          {/* Detailed Evidence Audit Table */}
          {application.evaluation?.evidence && application.evaluation.evidence.length > 0 && (
            <div style={{ marginTop: "16px", borderTop: "1px solid var(--border-subtle)", paddingTop: "12px" }}>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", display: "block", marginBottom: "8px" }}>
                Evidence & Rationale Audit
              </span>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: "160px", overflowY: "auto" }}>
                {application.evaluation.evidence.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: "12px",
                      padding: "6px 10px",
                      backgroundColor: "var(--bg-input)",
                      borderRadius: "4px",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{item.requirement}</span>
                    <span
                      style={{
                        color:
                          item.status === "exact" || item.status === "matched"
                            ? "var(--color-success)"
                            : item.status === "related"
                            ? "#c084fc"
                            : "var(--color-error)",
                        fontStyle: "italic",
                      }}
                    >
                      {item.evidence}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Recruiter Action Buttons */}
        {onUpdateStatus && (
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", borderTop: "1px solid var(--border-subtle)", paddingTop: "16px" }}>
            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                onUpdateStatus(application.id, "REJECTED");
                onClose();
              }}
            >
              Reject Candidate
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                onUpdateStatus(application.id, "UNDER_REVIEW");
                onClose();
              }}
            >
              Mark Under Review
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Sparkles}
              onClick={() => {
                onUpdateStatus(application.id, "SHORTLISTED");
                onClose();
              }}
            >
              Shortlist Candidate
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};
