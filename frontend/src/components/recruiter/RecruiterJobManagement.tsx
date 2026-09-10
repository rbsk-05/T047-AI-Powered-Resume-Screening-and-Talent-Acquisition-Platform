import React, { useEffect, useState } from "react";
import {
  Briefcase,
  Plus,
  Users,
  Building2,
  MapPin,
  Clock,
  Eye,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { listMyJobs, StoredJob, API_URL } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";
import { SkillChip } from "../ui/SkillChip";
import { EmptyState } from "../ui/EmptyState";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

interface RecruiterJobManagementProps {
  onCreateJob: () => void;
  onSelectJob: (job: StoredJob) => void;
}

export const RecruiterJobManagement: React.FC<RecruiterJobManagementProps> = ({
  onCreateJob,
  onSelectJob,
}) => {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [expandedSkills, setExpandedSkills] = useState<Record<string, boolean>>({});

  const toggleSkillsExpand = (e: React.MouseEvent, jobId: string) => {
    e.stopPropagation();
    setExpandedSkills((prev) => ({ ...prev, [jobId]: !prev[jobId] }));
  };


  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    listMyJobs(token)
      .then(setJobs)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  if (isLoading) {
    return <LoadingState message="Loading your job listings..." rows={4} />;
  }

  const filteredJobs = jobs.filter((job) => {
    if (statusFilter === "all") return true;
    return (job.status || "PUBLISHED").toUpperCase() === statusFilter.toUpperCase();
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Job Management"
        subtitle="Manage your company job postings, review ATS screened applicant pools, and configure requirements."
        action={
          <Button variant="primary" icon={Plus} onClick={onCreateJob}>
            Create New Job
          </Button>
        }
      />

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "12px" }}>
        {[
          { id: "all", label: `All Jobs (${jobs.length})` },
          { id: "published", label: `Published (${jobs.filter((j) => (j.status || "PUBLISHED").toUpperCase() === "PUBLISHED").length})` },
          { id: "draft", label: `Drafts (${jobs.filter((j) => (j.status || "").toUpperCase() === "DRAFT").length})` },
          { id: "closed", label: `Closed (${jobs.filter((j) => (j.status || "").toUpperCase() === "CLOSED").length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setStatusFilter(tab.id)}
            style={{
              padding: "6px 14px",
              borderRadius: "var(--radius-full)",
              fontSize: "13px",
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

      {/* Jobs Cards Grid */}
      {filteredJobs.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {filteredJobs.map((job) => (
            <Card
              key={job.id}
              elevated
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "16px",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxWidth: "600px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                    {job.title}
                  </h3>
                  <StatusBadge status={job.status || "PUBLISHED"} size="sm" />
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", margin: "4px 0" }}>
                  <Badge variant="neutral" size="sm" icon={MapPin}>
                    {job.location || "Remote"}
                  </Badge>
                  <Badge variant="neutral" size="sm" icon={Briefcase}>
                    {job.experience_required || "Experience Flexible"}
                  </Badge>
                  <Badge variant="primary" size="sm" icon={Clock}>
                    {job.employment_type || "Full-time"}
                  </Badge>
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "4px", alignItems: "center" }}>
                  {((expandedSkills[job.id] ? job.required_skills : job.required_skills?.slice(0, 4)) || []).map((skill, sIdx) => (
                    <SkillChip key={sIdx} skill={skill} size="sm" type="neutral" />
                  ))}
                  {(job.required_skills?.length || 0) > 4 && (
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
                      {expandedSkills[job.id] ? "Show less" : `+${(job.required_skills?.length || 0) - 4} more`}
                    </button>
                  )}
                </div>

              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <Button variant="primary" size="sm" icon={Users} onClick={() => onSelectJob(job)}>
                  View Applicants
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Jobs Found"
          description="Create a new job posting with AI-assisted requirements extraction to start receiving candidate applications."
          actionText="Create Job"
          onAction={onCreateJob}
        />
      )}
    </div>
  );
};
