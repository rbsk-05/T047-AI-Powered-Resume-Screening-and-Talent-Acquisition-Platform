import React, { useEffect, useState } from "react";
import {
  Briefcase,
  Clock,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Award,
  ArrowRight,
  Compass,
} from "lucide-react";
import { listJobs, StoredJob, StoredApplication } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { StatCard } from "../ui/StatCard";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { LoadingState } from "../ui/LoadingState";
import { SkillChip } from "../ui/SkillChip";
import { CandidateNavTab } from "../layout/Sidebar";

interface CandidateDashboardProps {
  onNavigate: (tab: CandidateNavTab) => void;
  onSelectJob: (job: StoredJob) => void;
}

export const CandidateDashboard: React.FC<CandidateDashboardProps> = ({
  onNavigate,
  onSelectJob,
}) => {
  const { user, token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedSkills, setExpandedSkills] = useState<Record<string, boolean>>({});

  const toggleSkillsExpand = (e: React.MouseEvent, jobId: string) => {
    e.stopPropagation();
    setExpandedSkills((prev) => ({ ...prev, [jobId]: !prev[jobId] }));
  };


  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        const [jobsData, appsData] = await Promise.all([
          listJobs(),
          token ? fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"}/applications`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then(r => r.ok ? r.json() : []) : Promise.resolve([]),
        ]);
        setJobs(jobsData);
        setApplications(appsData);
      } catch (err) {
        console.error("Failed to load candidate dashboard data:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Loading your talent intelligence dashboard..." rows={4} />;
  }

  const appliedCount = applications.length;
  const underReviewCount = applications.filter(a => (a.status || "").toUpperCase() === "UNDER_REVIEW").length;
  const shortlistedCount = applications.filter(a => (a.status || "").toUpperCase() === "SHORTLISTED").length;
  const selectedCount = applications.filter(a => (a.status || "").toUpperCase() === "SELECTED").length;

  // Best match application
  const topApplication = applications.length > 0
    ? [...applications].sort((a, b) => (b.match?.overall_match_score || 0) - (a.match?.overall_match_score || 0))[0]
    : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Welcome Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          borderRadius: "var(--radius-xl)",
          padding: "24px 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span style={{ fontSize: "12px", color: "#818CF8", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Candidate Intelligence
            </span>
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
            Welcome back, {user?.full_name} 👋
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
            Track your ATS scores, target skill gaps, and explore AI-matched career opportunities.
          </p>
        </div>

        <Button variant="primary" icon={Compass} onClick={() => onNavigate("browse_jobs")}>
          Explore Open Roles
        </Button>
      </div>

      {/* Shortlisted Celebration Banner */}
      {shortlistedCount > 0 && (
        <div
          className="animate-fade-in"
          style={{
            backgroundColor: "rgba(124, 58, 237, 0.12)",
            border: "1px solid rgba(124, 58, 237, 0.35)",
            borderRadius: "var(--radius-lg)",
            padding: "16px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                backgroundColor: "rgba(124, 58, 237, 0.25)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#C084FC",
              }}
            >
              <Sparkles size={22} />
            </div>
            <div>
              <h4 style={{ fontSize: "15px", fontWeight: 700, color: "#FFFFFF", margin: 0 }}>
                🎉 Great News! You have been Shortlisted!
              </h4>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "2px 0 0" }}>
                A recruiter has shortlisted your application based on your high ATS match score and skill profile.
              </p>
            </div>
          </div>

          <Button
            variant="ai"
            size="sm"
            onClick={() => onNavigate("my_applications")}
          >
            View Shortlisted Applications →
          </Button>
        </div>
      )}

      {/* KPI Stats Strip */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
        }}
      >
        <StatCard
          title="Applications"
          value={appliedCount}
          subtitle="Total submitted"
          icon={Briefcase}
          accentColor="var(--accent-primary)"
        />
        <StatCard
          title="Under Review"
          value={underReviewCount}
          subtitle="In recruiter pipeline"
          icon={Clock}
          accentColor="var(--color-warning)"
        />
        <StatCard
          title="Shortlisted"
          value={shortlistedCount}
          subtitle="High compatibility"
          icon={Sparkles}
          accentColor="var(--accent-secondary)"
        />
        <StatCard
          title="Selected / Offers"
          value={selectedCount}
          subtitle="Final stage"
          icon={CheckCircle2}
          accentColor="var(--color-success)"
        />
      </div>

      {/* Main Grid: Best Match + Recommended Roles */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "24px",
        }}
      >
        {/* Left: Top Match Overview */}
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)" }}>
              Top Match Performance
            </h3>
            {topApplication && (
              <Badge variant="success" size="sm">
                Active
              </Badge>
            )}
          </div>

          {topApplication ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
                <ProgressRing score={topApplication.match?.overall_match_score || 0} size={100} />
                <div>
                  <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
                    {topApplication.job_title || "Software Engineering Role"}
                  </h4>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "2px 0 6px" }}>
                    {topApplication.company_name}
                  </p>
                  <StatusBadge status={topApplication.status} size="sm" />
                </div>
              </div>

              {topApplication.evaluation?.summary && (
                <div
                  style={{
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: "var(--radius-md)",
                    padding: "12px",
                    fontSize: "13px",
                    color: "var(--text-secondary)",
                    lineHeight: 1.5,
                  }}
                >
                  <span style={{ fontWeight: 600, color: "var(--accent-primary)", display: "block", marginBottom: "2px" }}>
                    AI Evaluation Rationale:
                  </span>
                  {topApplication.evaluation.summary}
                </div>
              )}

              <Button
                variant="secondary"
                size="sm"
                icon={ArrowRight}
                iconPosition="right"
                onClick={() => onNavigate("my_applications")}
                style={{ width: "100%" }}
              >
                View Full Score Breakdown
              </Button>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "24px 0", color: "var(--text-muted)" }}>
              <p style={{ fontSize: "14px", marginBottom: "12px" }}>
                No active applications submitted yet.
              </p>
              <Button variant="primary" size="sm" onClick={() => onNavigate("browse_jobs")}>
                Apply to Your First Job
              </Button>
            </div>
          )}
        </Card>

        {/* Right: Recommended Jobs */}
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)" }}>
              Featured Opportunities
            </h3>
            <button
              type="button"
              onClick={() => onNavigate("browse_jobs")}
              style={{ background: "none", border: "none", color: "var(--accent-primary)", fontSize: "13px", fontWeight: 600, cursor: "pointer" }}
            >
              View all
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {jobs.slice(0, 3).map((job) => (
              <div
                key={job.id}
                onClick={() => onSelectJob(job)}
                style={{
                  padding: "14px",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "var(--bg-input)",
                  border: "1px solid var(--border-subtle)",
                  cursor: "pointer",
                  transition: "border-color 0.15s ease",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                  <div>
                    <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                      {job.title}
                    </h4>
                    <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "1px 0 0" }}>
                      {job.company_name || "Hiring Company"} · 📍 {job.location || "Remote"}
                    </p>
                  </div>
                  <Badge variant="primary" size="sm">
                    {job.employment_type || "Full-time"}
                  </Badge>
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "8px", alignItems: "center" }}>
                  {((expandedSkills[job.id] ? job.required_skills : job.required_skills?.slice(0, 3)) || []).map((skill, sIdx) => (
                    <SkillChip key={sIdx} skill={skill} size="sm" type="neutral" />
                  ))}
                  {(job.required_skills?.length || 0) > 3 && (
                    <button
                      type="button"
                      onClick={(e) => toggleSkillsExpand(e, job.id)}
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
                      {expandedSkills[job.id] ? "Show less" : `+${(job.required_skills?.length || 0) - 3} more`}
                    </button>
                  )}
                </div>

              </div>
            ))}

            {jobs.length === 0 && (
              <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center", padding: "16px 0" }}>
                No published job openings available at the moment.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
