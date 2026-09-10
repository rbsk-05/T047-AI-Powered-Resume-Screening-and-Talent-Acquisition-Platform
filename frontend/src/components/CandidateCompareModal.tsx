import React from "react";
import {
  Sparkles,
  Check,
  X,
  GitCompare,
  Briefcase,
  GraduationCap,
  Award,
} from "lucide-react";
import { CompareResponse } from "../api";
import { Modal } from "./ui/Modal";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { StatusBadge } from "./ui/StatusBadge";
import { ProgressRing } from "./ui/ProgressRing";
import { Card } from "./ui/Card";

interface CandidateCompareModalProps {
  data: CompareResponse;
  onClose: () => void;
  onUpdateStatus?: (applicationId: string, status: string) => void;
}

export const CandidateCompareModal: React.FC<CandidateCompareModalProps> = ({
  data,
  onClose,
  onUpdateStatus,
}) => {
  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Side-by-Side Candidate Comparison"
      subtitle={`Comparing ${data.candidates.length} candidates for: ${data.job_title}`}
      maxWidth="960px"
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        {/* AI Comparative Summary Banner */}
        <div
          style={{
            background: "linear-gradient(135deg, rgba(124, 58, 237, 0.12) 0%, rgba(99, 102, 241, 0.12) 100%)",
            border: "1px solid rgba(124, 58, 237, 0.3)",
            borderRadius: "var(--radius-lg)",
            padding: "18px 20px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <Sparkles size={18} color="var(--accent-secondary)" />
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#C084FC", margin: 0, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              AI Differentiator Summary
            </h4>
          </div>
          <p style={{ fontSize: "14px", color: "var(--text-primary)", lineHeight: 1.6, margin: 0 }}>
            {data.comparison_summary}
          </p>
        </div>

        {/* Candidate Overview Cards Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${data.candidates.length}, 1fr)`,
            gap: "16px",
          }}
        >
          {data.candidates.map((cand) => (
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
                <div><strong>Exp:</strong> {cand.experience || "Flexible"}</div>
                <div><strong>Edu:</strong> {cand.education?.length > 0 ? cand.education.join(", ") : "CS"}</div>
              </div>

              {onUpdateStatus && (
                <div style={{ display: "flex", gap: "6px", width: "100%", marginTop: "4px" }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    style={{ flex: 1, fontSize: "11px", padding: "4px 8px" }}
                    onClick={() => onUpdateStatus(cand.id, "SHORTLISTED")}
                  >
                    Shortlist
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    style={{ flex: 1, fontSize: "11px", padding: "4px 8px" }}
                    onClick={() => onUpdateStatus(cand.id, "REJECTED")}
                  >
                    Reject
                  </Button>
                </div>
              )}
            </Card>
          ))}
        </div>

        {/* Side-by-Side Skills Coverage Matrix Table */}
        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
            <GitCompare size={18} color="var(--accent-primary)" />
            <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              Skill & Requirement Coverage Matrix
            </h4>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border-default)", backgroundColor: "var(--bg-input)" }}>
                  <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>
                    Requirement / Skill
                  </th>
                  <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>
                    Type
                  </th>
                  {data.candidates.map((cand) => (
                    <th key={cand.id} style={{ padding: "12px 14px", color: "var(--text-primary)", fontWeight: 700, textAlign: "center" }}>
                      {cand.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.skills_matrix.map((item, idx) => (
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
                    {data.candidates.map((cand) => {
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
    </Modal>
  );
};
