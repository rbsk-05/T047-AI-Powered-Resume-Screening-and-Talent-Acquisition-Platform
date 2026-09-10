import React, { useEffect, useState } from "react";
import { Award, CheckCircle2, AlertTriangle, XCircle, Sparkles } from "lucide-react";
import { API_URL, StoredApplication } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { SkillChip } from "../ui/SkillChip";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const CandidateSkillAnalysis: React.FC = () => {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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
    return <LoadingState message="Aggregating your skill intelligence analysis..." rows={4} />;
  }

  // Aggregate matched skills vs gaps across applications
  const allMatchedSkills = new Set<string>();
  const criticalGaps = new Map<string, string>();
  const niceToHaveGaps = new Map<string, string>();

  applications.forEach((app) => {
    app.match?.matched_skills?.forEach((s) => allMatchedSkills.add(s));
    app.skill_gap?.gaps?.forEach((gap) => {
      if (gap.priority === "critical" || gap.priority === "high") {
        criticalGaps.set(gap.skill, gap.reason);
      } else {
        niceToHaveGaps.set(gap.skill, gap.reason);
      }
    });
  });

  const strongList = Array.from(allMatchedSkills);
  const criticalList = Array.from(criticalGaps.entries());
  const niceList = Array.from(niceToHaveGaps.entries());

  if (applications.length === 0) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        <PageHeader
          title="Skill Gap Intelligence"
          subtitle="Comprehensive breakdown of your demonstrated technical proficiencies and target gap priorities."
        />
        <EmptyState
          title="No Skill Data Available"
          description="Apply to a job to let AI analyze your resume and extract your skill coverage matrix."
        />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Skill Gap Intelligence"
        subtitle="AI-synthesized analysis of verified candidate strengths versus missing role requirements."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
        {/* Strong Verified Skills */}
        <Card elevated>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "var(--color-success-bg)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--color-success)",
              }}
            >
              <CheckCircle2 size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                Strong & Verified Skills
              </h3>
              <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>
                Demonstrated in your resume and verified by ATS matching
              </p>
            </div>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {strongList.length > 0 ? (
              strongList.map((skill, idx) => (
                <SkillChip key={idx} skill={skill} type="matched" />
              ))
            ) : (
              <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>No verified skills extracted yet.</p>
            )}
          </div>
        </Card>

        {/* Needs Improvement / Medium Priority */}
        <Card elevated>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "var(--color-warning-bg)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--color-warning)",
              }}
            >
              <AlertTriangle size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                Skills to Improve (Nice to Have)
              </h3>
              <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>
                Preferred qualifications that will increase your match score
              </p>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {niceList.length > 0 ? (
              niceList.map(([skill, reason], idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: "rgba(245, 158, 11, 0.08)",
                    border: "1px solid rgba(245, 158, 11, 0.2)",
                    borderRadius: "var(--radius-md)",
                    padding: "10px 14px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", fontWeight: 700, color: "#FBBF24" }}>
                      {skill}
                    </span>
                    <Badge variant="warning" size="sm">
                      Medium Priority
                    </Badge>
                  </div>
                  <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: "4px 0 0" }}>
                    {reason}
                  </p>
                </div>
              ))
            ) : (
              <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>No secondary skill gaps detected.</p>
            )}
          </div>
        </Card>
      </div>

      {/* Critical Missing Skills Section */}
      <Card elevated>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "var(--color-error-bg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-error)",
            }}
          >
            <XCircle size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              High Priority / Critical Skill Gaps
            </h3>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>
              Essential core skills required by target roles but not present in your current profile
            </p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "12px" }}>
          {criticalList.length > 0 ? (
            criticalList.map(([skill, reason], idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.08)",
                  border: "1px solid rgba(239, 68, 68, 0.25)",
                  borderRadius: "var(--radius-md)",
                  padding: "12px 16px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "#F87171" }}>
                    {skill}
                  </span>
                  <Badge variant="danger" size="sm">
                    High Priority
                  </Badge>
                </div>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px", margin: "4px 0 0" }}>
                  {reason}
                </p>
              </div>
            ))
          ) : (
            <p style={{ fontSize: "13px", color: "var(--color-success)" }}>No critical skill gaps identified across target positions!</p>
          )}
        </div>
      </Card>
    </div>
  );
};
