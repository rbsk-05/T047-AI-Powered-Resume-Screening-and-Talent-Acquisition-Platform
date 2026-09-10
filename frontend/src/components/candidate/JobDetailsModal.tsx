import React from "react";
import {
  Building2,
  MapPin,
  Briefcase,
  Clock,
  GraduationCap,
  Sparkles,
  CheckCircle2,
  X,
} from "lucide-react";
import { StoredJob } from "../../api";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { SkillChip } from "../ui/SkillChip";
import { Card } from "../ui/Card";

interface JobDetailsModalProps {
  job: StoredJob | null;
  onClose: () => void;
  onApply: (job: StoredJob) => void;
}

export const JobDetailsModal: React.FC<JobDetailsModalProps> = ({
  job,
  onClose,
  onApply,
}) => {
  if (!job) return null;

  return (
    <Modal isOpen={!!job} onClose={onClose} title={job.title} subtitle={job.company_name || "Enterprise Company"} maxWidth="840px">
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.8fr) minmax(260px, 1.2fr)",
          gap: "24px",
          alignItems: "start",
        }}
      >
        {/* Left Column: Job Description & Detailed Specs */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Metadata Badges */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            <Badge variant="neutral" icon={MapPin}>
              {job.location || "Remote"}
            </Badge>
            <Badge variant="neutral" icon={Briefcase}>
              {job.experience_required || "Experience Flexible"}
            </Badge>
            <Badge variant="primary" icon={Clock}>
              {job.employment_type || "Full-time"}
            </Badge>
          </div>

          {/* Description */}
          <div>
            <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Role Overview & Description
            </h4>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
              {job.description}
            </p>
          </div>

          {/* Responsibilities if extracted */}
          {job.profile?.responsibilities && job.profile.responsibilities.length > 0 && (
            <div>
              <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
                Key Responsibilities
              </h4>
              <ul style={{ paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "6px", color: "var(--text-secondary)", fontSize: "13px" }}>
                {job.profile.responsibilities.map((resp, idx) => (
                  <li key={idx}>{resp}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Required Skills */}
          <div>
            <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Required Skills (Essential)
            </h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {job.required_skills?.map((skill, sIdx) => (
                <SkillChip key={sIdx} skill={skill} type="neutral" />
              ))}
            </div>
          </div>

          {/* Preferred Skills */}
          {job.preferred_skills && job.preferred_skills.length > 0 && (
            <div>
              <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
                Preferred Skills (Bonus)
              </h4>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {job.preferred_skills.map((skill, sIdx) => (
                  <SkillChip key={sIdx} skill={skill} type="preferred" />
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {job.education && job.education.length > 0 && (
            <div>
              <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
                Education Requirements
              </h4>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {job.education.map((edu, eIdx) => (
                  <Badge key={eIdx} variant="neutral" icon={GraduationCap}>
                    {edu}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Company Summary & Apply Card */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <Card elevated style={{ backgroundColor: "var(--bg-input)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "14px" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "var(--bg-card)",
                  border: "1px solid var(--border-default)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--accent-primary)",
                  fontWeight: 700,
                  fontSize: "18px",
                }}
              >
                {job.company_name?.charAt(0) || <Building2 size={24} />}
              </div>
              <div>
                <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  {job.company_name || "Enterprise Company"}
                </h4>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                  Verified Recruiter
                </p>
              </div>
            </div>

            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: "20px" }}>
              This role uses TalentLens AI for transparent ATS matching, structured skill evaluation, and real-time candidate feedback.
            </p>

            <Button
              variant="primary"
              size="lg"
              icon={Sparkles}
              onClick={() => {
                onClose();
                onApply(job);
              }}
              style={{ width: "100%" }}
            >
              Apply to Position
            </Button>
          </Card>

          <div
            style={{
              padding: "16px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "rgba(99, 102, 241, 0.08)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <CheckCircle2 size={16} color="var(--accent-primary)" />
              <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                Instant AI Score
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
              Upon applying, you will receive an immediate ATS breakdown, skill-gap analysis, and customized milestone learning roadmaps.
            </p>
          </div>
        </div>
      </div>
    </Modal>
  );
};
