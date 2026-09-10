import React, { useState } from "react";
import {
  Search,
  Building2,
  MapPin,
  Briefcase,
  Clock,
  Filter,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { StoredJob } from "../../api";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { Badge } from "../ui/Badge";
import { SkillChip } from "../ui/SkillChip";
import { EmptyState } from "../ui/EmptyState";
import { PageHeader } from "../ui/PageHeader";

interface CandidateBrowseJobsProps {
  jobs: StoredJob[];
  onSelectJob: (job: StoredJob) => void;
  onApplyJob: (job: StoredJob) => void;
}

export const CandidateBrowseJobs: React.FC<CandidateBrowseJobsProps> = ({
  jobs,
  onSelectJob,
  onApplyJob,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [experienceFilter, setExperienceFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");

  const [expandedSkills, setExpandedSkills] = useState<Record<string, boolean>>({});

  const toggleSkillsExpand = (e: React.MouseEvent, jobId: string) => {
    e.stopPropagation();
    setExpandedSkills((prev) => ({ ...prev, [jobId]: !prev[jobId] }));
  };

  const filteredJobs = jobs.filter((job) => {

    // Only published jobs should appear for candidates
    if (job.status && job.status.toUpperCase() === "DRAFT") return false;

    const q = searchQuery.toLowerCase().trim();
    const titleMatch = job.title.toLowerCase().includes(q);
    const companyMatch = (job.company_name || "").toLowerCase().includes(q);
    const locationMatch = (job.location || "").toLowerCase().includes(q);
    const skillMatch = (job.required_skills || []).some((s) => s.toLowerCase().includes(q));

    const matchesQuery = !q || titleMatch || companyMatch || locationMatch || skillMatch;

    const matchesType =
      typeFilter === "all" ||
      (job.employment_type || "").toLowerCase().includes(typeFilter.toLowerCase());

    return matchesQuery && matchesType;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Browse Job Opportunities"
        subtitle="Discover verified roles matched with AI-driven screening and transparent requirements."
      />

      {/* Search & Filter Bar */}
      <Card style={{ padding: "16px 20px" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "16px",
            alignItems: "center",
          }}
        >
          {/* Main Keyword Search */}
          <div style={{ gridColumn: "span 2" }}>
            <Input
              placeholder="Search by job title, company name, skill, or keyword..."
              icon={Search}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ marginBottom: 0 }}
            />
          </div>

          {/* Job Type Filter */}
          <Select
            options={[
              { value: "all", label: "All Employment Types" },
              { value: "full-time", label: "Full-time" },
              { value: "contract", label: "Contract" },
              { value: "part-time", label: "Part-time" },
              { value: "remote", label: "Remote" },
            ]}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{ marginBottom: 0 }}
          />
        </div>
      </Card>

      {/* Results Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
          Showing <strong style={{ color: "var(--text-primary)" }}>{filteredJobs.length}</strong> active position{filteredJobs.length === 1 ? "" : "s"}
        </p>
      </div>

      {/* Jobs Grid */}
      {filteredJobs.length > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: "20px",
          }}
        >
          {filteredJobs.map((job) => (
            <Card
              key={job.id}
              elevated
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                height: "100%",
              }}
            >
              <div>
                {/* Header: Company & Employment Type */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div
                      style={{
                        width: "40px",
                        height: "40px",
                        borderRadius: "var(--radius-md)",
                        backgroundColor: "var(--bg-input)",
                        border: "1px solid var(--border-subtle)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "var(--accent-primary)",
                        fontWeight: 700,
                        fontSize: "15px",
                      }}
                    >
                      {job.company_name?.charAt(0) || <Building2 size={20} />}
                    </div>
                    <div>
                      <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                        {job.title}
                      </h3>
                      <p style={{ fontSize: "13px", color: "var(--accent-primary)", fontWeight: 600, margin: "2px 0 0" }}>
                        {job.company_name || "Enterprise Company"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Job Metadata Badges */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", margin: "12px 0 16px" }}>
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

                {/* Short snippet */}
                <p
                  style={{
                    fontSize: "13px",
                    color: "var(--text-secondary)",
                    lineHeight: 1.5,
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                    marginBottom: "16px",
                  }}
                >
                  {job.description}
                </p>

                {/* Required Skills */}
                <div style={{ marginBottom: "16px" }}>
                  <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "6px" }}>
                    Required Skills
                  </span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
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
                          padding: "2px 8px",
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

              </div>

              {/* Actions Footer */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "10px",
                  borderTop: "1px solid var(--border-subtle)",
                  paddingTop: "14px",
                  marginTop: "8px",
                }}
              >
                <Button variant="secondary" size="sm" onClick={() => onSelectJob(job)}>
                  View Details
                </Button>
                <Button variant="primary" size="sm" icon={Sparkles} onClick={() => onApplyJob(job)}>
                  Apply Now
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Matching Jobs Found"
          description="Try adjusting your search keywords or clearing your active filters to view more positions."
          actionText="Clear Filters"
          onAction={() => {
            setSearchQuery("");
            setTypeFilter("all");
            setExperienceFilter("all");
          }}
        />
      )}
    </div>
  );
};
