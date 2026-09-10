import React, { useEffect, useState } from "react";
import {
  Briefcase,
  Users,
  CheckCircle2,
  Sparkles,
  Award,
  Plus,
  ArrowRight,
  Building2,
  Clock,
} from "lucide-react";
import { listMyJobs, StoredJob, StoredApplication, API_URL } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { StatCard } from "../ui/StatCard";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { ProgressRing } from "../ui/ProgressRing";
import { LoadingState } from "../ui/LoadingState";
import { RecruiterNavTab } from "../layout/Sidebar";

interface RecruiterDashboardProps {
  onNavigate: (tab: RecruiterNavTab) => void;
  onCreateJob: () => void;
  onSelectJob: (job: StoredJob) => void;
}

export const RecruiterDashboard: React.FC<RecruiterDashboardProps> = ({
  onNavigate,
  onCreateJob,
  onSelectJob,
}) => {
  const { token, user } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);

    async function loadData() {
      try {
        const jobsData = await listMyJobs(token!);
        setJobs(jobsData);

        // Fetch applications for all jobs
        const appsPromises = jobsData.map((j) =>
          fetch(`${API_URL}/applications/job/${j.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then((r) => (r.ok ? r.json() : []))
        );
        const appsResults = await Promise.all(appsPromises);
        const allApps = appsResults.flat();
        setApplications(allApps);
      } catch (err) {
        console.error("Failed to load recruiter dashboard:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Loading your recruitment talent pipeline..." rows={4} />;
  }

  const totalJobs = jobs.length;
  const publishedJobs = jobs.filter((j) => (j.status || "PUBLISHED").toUpperCase() === "PUBLISHED").length;
  const totalApplications = applications.length;
  const shortlistedCount = applications.filter((a) => (a.status || "").toUpperCase() === "SHORTLISTED").length;
  const selectedCount = applications.filter((a) => (a.status || "").toUpperCase() === "SELECTED").length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Welcome Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)",
          border: "1px solid rgba(124, 58, 237, 0.3)",
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
            <span style={{ fontSize: "12px", color: "#C084FC", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Talent Acquisition Command Center
            </span>
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
            {user?.company_name ? `${user.company_name} Dashboard` : `Welcome, ${user?.full_name}`}
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
            Monitor AI-screened candidate rankings, compare top talent, and manage open positions.
          </p>
        </div>

        <Button variant="primary" icon={Plus} onClick={onCreateJob}>
          Create New Job
        </Button>
      </div>

      {/* KPI Stats Strip */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "16px",
        }}
      >
        <StatCard
          title="Total Positions"
          value={totalJobs}
          subtitle={`${publishedJobs} published`}
          icon={Briefcase}
          accentColor="var(--accent-primary)"
        />
        <StatCard
          title="Total Applicants"
          value={totalApplications}
          subtitle="Screened with ATS"
          icon={Users}
          accentColor="var(--color-info)"
        />
        <StatCard
          title="Shortlisted"
          value={shortlistedCount}
          subtitle="High match score"
          icon={Sparkles}
          accentColor="var(--accent-secondary)"
        />
        <StatCard
          title="Selected"
          value={selectedCount}
          subtitle="Offer stage"
          icon={CheckCircle2}
          accentColor="var(--color-success)"
        />
      </div>

      {/* Active Jobs & Recent Applications Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "24px" }}>
        {/* Active Jobs Overview */}
        <Card elevated>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              Active Job Listings
            </h3>
            <button
              type="button"
              onClick={() => onNavigate("jobs")}
              style={{ background: "none", border: "none", color: "var(--accent-primary)", fontSize: "13px", fontWeight: 600, cursor: "pointer" }}
            >
              Manage all →
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {jobs.slice(0, 4).map((job) => (
              <div
                key={job.id}
                onClick={() => onSelectJob(job)}
                style={{
                  padding: "14px 16px",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "var(--bg-input)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  cursor: "pointer",
                  transition: "border-color 0.15s ease",
                }}
              >
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                    {job.title}
                  </h4>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                    📍 {job.location || "Remote"} · {job.employment_type || "Full-time"}
                  </p>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <StatusBadge status={job.status || "PUBLISHED"} size="sm" />
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); onSelectJob(job); }}>
                    View Applicants
                  </Button>
                </div>
              </div>
            ))}

            {jobs.length === 0 && (
              <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center", padding: "16px 0" }}>
                No active jobs created yet. Click "Create New Job" to post your first position.
              </p>
            )}
          </div>
        </Card>

        {/* Top Ranked Applicants */}
        <Card elevated>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              Top Screened Candidates
            </h3>
            <button
              type="button"
              onClick={() => onNavigate("candidate_ranking")}
              style={{ background: "none", border: "none", color: "var(--accent-primary)", fontSize: "13px", fontWeight: 600, cursor: "pointer" }}
            >
              View Ranking →
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {applications
              .sort((a, b) => (b.match?.overall_match_score || 0) - (a.match?.overall_match_score || 0))
              .slice(0, 4)
              .map((app, idx) => (
                <div
                  key={app.id}
                  style={{
                    padding: "12px 14px",
                    borderRadius: "var(--radius-md)",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <span
                      style={{
                        width: "24px",
                        height: "24px",
                        borderRadius: "50%",
                        backgroundColor: idx === 0 ? "rgba(245, 158, 11, 0.2)" : "var(--bg-card)",
                        color: idx === 0 ? "#FBBF24" : "var(--text-muted)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "12px",
                        fontWeight: 700,
                      }}
                    >
                      #{idx + 1}
                    </span>
                    <div>
                      <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                        {app.company_name || "Applicant"}
                      </h4>
                      <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "1px 0 0" }}>
                        Role: {app.job_title || "Engineering"}
                      </p>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <Badge variant={app.match?.overall_match_score >= 75 ? "success" : "warning"} size="sm">
                      {Math.round(app.match?.overall_match_score || 0)}% Match
                    </Badge>
                    <StatusBadge status={app.status} size="sm" />
                  </div>
                </div>
              ))}

            {applications.length === 0 && (
              <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center", padding: "16px 0" }}>
                No candidate applications received yet.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
