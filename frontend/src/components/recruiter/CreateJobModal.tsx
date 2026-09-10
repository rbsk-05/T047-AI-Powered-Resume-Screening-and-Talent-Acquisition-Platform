import React, { useState } from "react";
import { Sparkles, Briefcase, Building2, MapPin, Clock, Plus, CheckCircle2, AlertCircle } from "lucide-react";
import { createJob, API_URL, StoredJob } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Input, TextArea } from "../ui/Input";
import { Select } from "../ui/Select";
import { SkillChip } from "../ui/SkillChip";
import { Badge } from "../ui/Badge";

interface CreateJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (job: StoredJob) => void;
}

export const CreateJobModal: React.FC<CreateJobModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { token, user } = useAuth();

  // Form State
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState(user?.company_name || "");
  const [location, setLocation] = useState("Remote");
  const [employmentType, setEmploymentType] = useState("Full-time");
  const [experience, setExperience] = useState("3+ years");
  const [description, setDescription] = useState("");

  // Extracted Requirements State
  const [jobFamily, setJobFamily] = useState<string | null>(null);
  const [techSpecified, setTechSpecified] = useState<boolean | null>(null);
  const [requirementsList, setRequirementsList] = useState<any[]>([]);
  const [requiredSkills, setRequiredSkills] = useState<string[]>([]);
  const [preferredSkills, setPreferredSkills] = useState<string[]>([]);
  const [education, setEducation] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");

  // UI state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [analysisDone, setAnalysisDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Trigger AI Job Analysis via JDAgent on raw text / paragraphs
  const handleAnalyzeJD = async () => {
    if (!description.trim()) {
      setError("Please enter a job description to analyze with AI.");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/jobs/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: title || "Software Engineer",
          job_description: description,
        }),
      });

      if (!res.ok) throw new Error("Failed to analyze job description");
      const profile = await res.json();

      if (profile.job_title && (!title || title === "Software Engineer")) {
        setTitle(profile.job_title);
      }
      setJobFamily(profile.job_family || null);
      setTechSpecified(profile.technology_specified !== undefined ? profile.technology_specified : true);
      setRequirementsList(profile.requirements || []);
      setRequiredSkills(profile.required_skills || []);
      setPreferredSkills(profile.preferred_skills || []);
      if (profile.education && profile.education.length > 0) {
        setEducation(profile.education);
      }
      if (profile.experience) {
        setExperience(profile.experience);
      }
      setAnalysisDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run AI JD analysis");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAddSkill = (type: "required" | "preferred") => {
    if (!newSkill.trim()) return;
    const skillName = newSkill.trim();
    if (type === "required") {
      if (!requiredSkills.includes(skillName)) setRequiredSkills([...requiredSkills, skillName]);
      setRequirementsList([
        ...requirementsList,
        {
          name: skillName,
          normalized_name: skillName.toLowerCase(),
          importance: "REQUIRED",
          evidence_type: "EXPLICIT",
          status: "KNOWN",
          explanation: "Manually added by recruiter as required.",
        },
      ]);
    } else {
      if (!preferredSkills.includes(skillName)) setPreferredSkills([...preferredSkills, skillName]);
      setRequirementsList([
        ...requirementsList,
        {
          name: skillName,
          normalized_name: skillName.toLowerCase(),
          importance: "PREFERRED",
          evidence_type: "EXPLICIT",
          status: "KNOWN",
          explanation: "Manually added by recruiter as preferred.",
        },
      ]);
    }
    setNewSkill("");
  };

  const toggleRequirementImportance = (index: number) => {
    const updated = [...requirementsList];
    const item = updated[index];
    if (item.importance === "REQUIRED") {
      item.importance = "PREFERRED";
      setRequiredSkills(requiredSkills.filter((s) => s.toLowerCase() !== item.name.toLowerCase()));
      if (!preferredSkills.some((s) => s.toLowerCase() === item.name.toLowerCase())) {
        setPreferredSkills([...preferredSkills, item.name]);
      }
    } else {
      item.importance = "REQUIRED";
      setPreferredSkills(preferredSkills.filter((s) => s.toLowerCase() !== item.name.toLowerCase()));
      if (!requiredSkills.some((s) => s.toLowerCase() === item.name.toLowerCase())) {
        setRequiredSkills([...requiredSkills, item.name]);
      }
    }
    setRequirementsList(updated);
  };

  const removeRequirementItem = (index: number) => {
    const item = requirementsList[index];
    setRequirementsList(requirementsList.filter((_, i) => i !== index));
    setRequiredSkills(requiredSkills.filter((s) => s.toLowerCase() !== item.name.toLowerCase()));
    setPreferredSkills(preferredSkills.filter((s) => s.toLowerCase() !== item.name.toLowerCase()));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    if (!title.trim() || !description.trim()) {
      setError("Job title and description are required.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const job = await createJob(token, {
        job_title: title,
        job_description: description,
        company_name: company || user?.company_name || "Enterprise Company",
        location,
        employment_type: employmentType,
        experience_required: experience,
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        education,
      });

      onSuccess(job);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to publish job");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Job Posting" subtitle="Configure role details and leverage AI to extract and validate structured qualifications." maxWidth="840px">
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {error && (
          <div
            style={{
              backgroundColor: "var(--color-error-bg)",
              border: "1px solid var(--color-error-border)",
              color: "var(--color-error)",
              padding: "10px 14px",
              borderRadius: "var(--radius-md)",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Section 1: Basic Information */}
        <div>
          <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "12px" }}>
            1. Role & Company Information
          </span>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <Input
              label="Job Title"
              placeholder="e.g. Senior Backend Engineer"
              icon={Briefcase}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <Input
              label="Company Name"
              placeholder="e.g. Acme Inc"
              icon={Building2}
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
            <Input
              label="Location"
              placeholder="e.g. Remote / New York"
              icon={MapPin}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
            <Select
              label="Employment Type"
              options={[
                { value: "Full-time", label: "Full-time" },
                { value: "Contract", label: "Contract" },
                { value: "Part-time", label: "Part-time" },
                { value: "Remote", label: "Remote" },
              ]}
              value={employmentType}
              onChange={(e) => setEmploymentType(e.target.value)}
            />
            <Input
              label="Experience Required"
              placeholder="e.g. 3+ years"
              icon={Clock}
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            />
          </div>
        </div>

        {/* Section 2: Job Description & AI Analysis Trigger */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              2. Job Description (Text / Paragraphs)
            </span>
            <Button
              type="button"
              variant="ai"
              size="sm"
              icon={Sparkles}
              loading={isAnalyzing}
              onClick={handleAnalyzeJD}
            >
              ✨ Extract & Validate with AI
            </Button>
          </div>

          <TextArea
            placeholder="Paste your job description here in paragraph format, bullet points, or freeform text..."
            rows={6}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            helperText="AI will read the text/paragraphs, identify the job family, extract explicit & inferred skills, and map against the skill ontology."
          />
        </div>

        {/* Section 3: Recruiter Requirement Validation UI */}
        {(analysisDone || requiredSkills.length > 0) && (
          <div
            className="animate-fade-in"
            style={{
              backgroundColor: "var(--bg-input)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-lg)",
              padding: "18px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <CheckCircle2 size={18} color="var(--color-success)" />
                <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  AI Requirement Validation & Classification
                </h4>
              </div>
              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                {jobFamily && (
                  <span
                    style={{
                      fontSize: "11px",
                      fontWeight: 600,
                      backgroundColor: "rgba(99, 102, 241, 0.15)",
                      color: "#818cf8",
                      padding: "3px 8px",
                      borderRadius: "6px",
                      border: "1px solid rgba(99, 102, 241, 0.3)",
                    }}
                  >
                    Family: {jobFamily}
                  </span>
                )}
                {techSpecified !== null && (
                  <span
                    style={{
                      fontSize: "11px",
                      fontWeight: 600,
                      backgroundColor: techSpecified ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                      color: techSpecified ? "#34d399" : "#fbbf24",
                      padding: "3px 8px",
                      borderRadius: "6px",
                      border: `1px solid ${techSpecified ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
                    }}
                  >
                    {techSpecified ? "Specific Technologies" : "Generic Role / Fair Scoring"}
                  </span>
                )}
              </div>
            </div>

            {/* Detailed Requirements Cards if available */}
            {requirementsList.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "14px", maxHeight: "240px", overflowY: "auto" }}>
                {requirementsList.map((req, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      backgroundColor: "var(--bg-card)",
                      padding: "8px 12px",
                      borderRadius: "var(--radius-md)",
                      border: "1px solid var(--border-subtle)",
                      fontSize: "13px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", flex: 1 }}>
                      <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{req.name}</span>
                      <button
                        type="button"
                        onClick={() => toggleRequirementImportance(idx)}
                        style={{
                          fontSize: "10px",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          border: "none",
                          cursor: "pointer",
                          backgroundColor: req.importance === "REQUIRED" ? "rgba(239, 68, 68, 0.15)" : "rgba(59, 130, 246, 0.15)",
                          color: req.importance === "REQUIRED" ? "#f87171" : "#60a5fa",
                        }}
                        title="Click to toggle Required / Preferred"
                      >
                        {req.importance}
                      </button>
                      <span
                        style={{
                          fontSize: "10px",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          backgroundColor: "rgba(148, 163, 184, 0.15)",
                          color: "#94a3b8",
                        }}
                      >
                        {req.evidence_type}
                      </span>
                      {req.status === "NEEDS_VERIFICATION" && (
                        <span
                          style={{
                            fontSize: "10px",
                            fontWeight: 600,
                            padding: "2px 6px",
                            borderRadius: "4px",
                            backgroundColor: "rgba(245, 158, 11, 0.15)",
                            color: "#fbbf24",
                            border: "1px solid rgba(245, 158, 11, 0.3)",
                          }}
                        >
                          Verify: Unknown Skill
                        </span>
                      )}
                      {req.explanation && (
                        <span style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic", marginLeft: "6px" }}>
                          — {req.explanation}
                        </span>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeRequirementItem(idx)}
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--text-muted)",
                        cursor: "pointer",
                        fontSize: "14px",
                        padding: "0 4px",
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <>
                {/* Fallback chip view if requirementsList is empty */}
                <div style={{ marginBottom: "12px" }}>
                  <span style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500, display: "block", marginBottom: "6px" }}>
                    Required Skills (Essential):
                  </span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {requiredSkills.map((skill, idx) => (
                      <SkillChip
                        key={idx}
                        skill={skill}
                        type="neutral"
                        onRemove={() => setRequiredSkills(requiredSkills.filter((_, i) => i !== idx))}
                      />
                    ))}
                  </div>
                </div>

                {preferredSkills.length > 0 && (
                  <div style={{ marginBottom: "12px" }}>
                    <span style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500, display: "block", marginBottom: "6px" }}>
                      Preferred Skills (Nice to Have):
                    </span>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                      {preferredSkills.map((skill, idx) => (
                        <SkillChip
                          key={idx}
                          skill={skill}
                          type="preferred"
                          onRemove={() => setPreferredSkills(preferredSkills.filter((_, i) => i !== idx))}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Quick add custom skill */}
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "10px" }}>
              <input
                placeholder="Add requirement (e.g. Docker, PostgreSQL)..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                style={{
                  backgroundColor: "var(--bg-card)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "var(--radius-sm)",
                  padding: "6px 10px",
                  color: "var(--text-primary)",
                  fontSize: "13px",
                  flex: 1,
                  margin: 0,
                }}
              />
              <Button type="button" variant="secondary" size="sm" onClick={() => handleAddSkill("required")}>
                + Add Required
              </Button>
              <Button type="button" variant="ghost" size="sm" onClick={() => handleAddSkill("preferred")}>
                + Add Preferred
              </Button>
            </div>
          </div>
        )}

        {/* Modal Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", borderTop: "1px solid var(--border-subtle)", paddingTop: "16px" }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting}>
            Publish Job Listing
          </Button>
        </div>
      </form>
    </Modal>
  );
};
