import React, { useEffect, useState } from "react";
import { Users, Eye, Sparkles, Award, Filter, Search } from "lucide-react";
import { API_URL, listMyJobs, StoredApplication, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { SkillChip } from "../ui/SkillChip";
import { Input } from "../ui/Input";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";
import { CandidateEvaluationModal } from "./CandidateEvaluationModal";

export const RecruiterCandidatesList: React.FC = () => {
  const { token } = useAuth();
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [inspectApp, setInspectApp] = useState<StoredApplication | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);

    async function loadCandidates() {
      try {
        const jobs = await listMyJobs(token!);
        const appsPromises = jobs.map((j) =>
          fetch(`${API_URL}/applications/job/${j.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then((r) => (r.ok ? r.json() : []))
        );
        const results = await Promise.all(appsPromises);
        setApplications(results.flat());
      } catch (err) {
        console.error("Failed to load candidate pool:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadCandidates();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Aggregating global candidate intelligence pool..." rows={4} />;
  }

  const filtered = applications.filter((app) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    const nameMatch = (app.company_name || "").toLowerCase().includes(q);
    const jobMatch = (app.job_title || "").toLowerCase().includes(q);
    const skillMatch = (app.match?.matched_skills || []).some((s) => s.toLowerCase().includes(q));
    return nameMatch || jobMatch || skillMatch;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Candidate Pool"
        subtitle="Global directory of all candidates who have applied to your active and archived job positions."
      />

      {/* Search Input */}
      <Card style={{ padding: "14px 20px" }}>
        <Input
          placeholder="Search candidates by name, target role, or verified skill..."
          icon={Search}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ marginBottom: 0 }}
        />
      </Card>

      {/* Candidates List */}
      {filtered.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {filtered.map((app, idx) => (
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
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
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
                  }}
                >
                  {(app.company_name || "C").charAt(0)}
                </div>

                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <h4 style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                      {app.company_name || "Applicant"}
                    </h4>
                    <StatusBadge status={app.status} size="sm" />
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: "2px 0 6px" }}>
                    Applied for: <strong style={{ color: "var(--text-secondary)" }}>{app.job_title || "Position"}</strong>
                  </p>

                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                    {app.match?.matched_skills?.slice(0, 4).map((s, sIdx) => (
                      <SkillChip key={sIdx} skill={s} type="matched" size="sm" />
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <ProgressRing score={app.match?.overall_match_score || 0} size={56} strokeWidth={6} />
                <Button variant="secondary" size="sm" icon={Eye} onClick={() => setInspectApp(app)}>
                  View Report
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Candidates Found"
          description="When candidates submit applications, their verified profiles and ATS score cards will appear here."
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
