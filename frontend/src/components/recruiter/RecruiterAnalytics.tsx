import React, { useEffect, useState } from "react";
import { BarChart3, TrendingUp, Users, Award, Briefcase, CheckCircle2, Sparkles } from "lucide-react";
import { API_URL, listMyJobs, StoredApplication, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { StatCard } from "../ui/StatCard";
import { ProgressBar } from "../ui/ProgressBar";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const RecruiterAnalytics: React.FC = () => {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [applications, setApplications] = useState<StoredApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);

    async function loadAnalytics() {
      try {
        const jobsData = await listMyJobs(token!);
        setJobs(jobsData);

        const appsPromises = jobsData.map((j) =>
          fetch(`${API_URL}/applications/job/${j.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }).then((r) => (r.ok ? r.json() : []))
        );
        const results = await Promise.all(appsPromises);
        setApplications(results.flat());
      } catch (err) {
        console.error("Failed to load analytics data:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadAnalytics();
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Aggregating recruitment pipeline analytics..." rows={4} />;
  }

  const avgMatchScore =
    applications.length > 0
      ? Math.round(
          applications.reduce((acc, a) => acc + (a.match?.overall_match_score || 0), 0) /
            applications.length
        )
      : 0;

  const highMatchCount = applications.filter(
    (a) => (a.match?.overall_match_score || 0) >= 75
  ).length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Recruitment Analytics & Insights"
        subtitle="Quantitative metrics on candidate quality, ATS screening match distributions, and pipeline velocity."
      />

      {/* KPI Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
        <StatCard
          title="Average ATS Match"
          value={`${avgMatchScore}%`}
          subtitle="Across all applicants"
          icon={Award}
          accentColor="var(--accent-primary)"
        />
        <StatCard
          title="High Quality Matches"
          value={highMatchCount}
          subtitle="Match Score ≥ 75%"
          icon={Sparkles}
          accentColor="var(--color-success)"
        />
        <StatCard
          title="Active Openings"
          value={jobs.length}
          subtitle="Configured positions"
          icon={Briefcase}
          accentColor="var(--accent-secondary)"
        />
        <StatCard
          title="Total Screenings"
          value={applications.length}
          subtitle="Automated ATS Screenings"
          icon={Users}
          accentColor="var(--color-info)"
        />
      </div>

      {/* Analytics Breakdown Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
        {/* Candidate Pipeline Distribution */}
        <Card elevated>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
            Application Stage Distribution
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <ProgressBar
              label="Applied (Initial Intake)"
              value={applications.length > 0 ? (applications.filter((a) => (a.status || "").toUpperCase() === "APPLIED").length / applications.length) * 100 : 0}
              color="var(--color-info)"
            />
            <ProgressBar
              label="Under Review"
              value={applications.length > 0 ? (applications.filter((a) => (a.status || "").toUpperCase() === "UNDER_REVIEW").length / applications.length) * 100 : 0}
              color="var(--color-warning)"
            />
            <ProgressBar
              label="Shortlisted"
              value={applications.length > 0 ? (applications.filter((a) => (a.status || "").toUpperCase() === "SHORTLISTED").length / applications.length) * 100 : 0}
              color="var(--accent-primary)"
            />
            <ProgressBar
              label="Selected / Offers"
              value={applications.length > 0 ? (applications.filter((a) => (a.status || "").toUpperCase() === "SELECTED").length / applications.length) * 100 : 0}
              color="var(--color-success)"
            />
          </div>
        </Card>

        {/* Position Screening Volume */}
        <Card elevated>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
            Applicant Volume by Position
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {jobs.map((job) => {
              const jobApps = applications.filter((a) => a.job_id === job.id);
              const jobAvg =
                jobApps.length > 0
                  ? Math.round(
                      jobApps.reduce((acc, a) => acc + (a.match?.overall_match_score || 0), 0) /
                        jobApps.length
                    )
                  : 0;

              return (
                <div
                  key={job.id}
                  style={{
                    padding: "12px 14px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: "var(--radius-md)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                      {job.title}
                    </h4>
                    <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                      {jobApps.length} applicants · Avg Score: {jobAvg}%
                    </p>
                  </div>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--accent-primary)" }}>
                    {jobApps.length}
                  </span>
                </div>
              );
            })}

            {jobs.length === 0 && (
              <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center", padding: "16px 0" }}>
                No active positions found.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
