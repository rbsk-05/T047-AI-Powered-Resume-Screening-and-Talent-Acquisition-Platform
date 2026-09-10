import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  X,
  BrainCircuit,
  User,
  Mail,
  Briefcase,
  GraduationCap,
  Award,
  ArrowRight,
  Layers,
} from "lucide-react";
import { createApplication, createCandidate, StoredApplication, StoredJob, StoredCandidate, CandidateProfile } from "../api";
import { useAuth } from "../auth/AuthContext";
import { Modal } from "./ui/Modal";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { SkillChip } from "./ui/SkillChip";
import { Card } from "./ui/Card";

interface ApplyModalProps {
  job: StoredJob;
  onClose: () => void;
  onSuccess: (application: StoredApplication) => void;
}

export const ApplyModal: React.FC<ApplyModalProps> = ({ job, onClose, onSuccess }) => {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Workflow steps: 'upload' -> 'parsed_preview' -> 'evaluating' -> 'done'
  const [step, setStep] = useState<"upload" | "parsed_preview" | "evaluating">("upload");
  const [candidateRecord, setCandidateRecord] = useState<StoredCandidate | null>(null);
  const [parsedProfile, setParsedProfile] = useState<CandidateProfile | null>(null);

  const [isParsing, setIsParsing] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentStatus, setAgentStatus] = useState<string>("");

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.name.endsWith(".pdf") || dropped.name.endsWith(".docx")) {
        setFile(dropped);
        setError(null);
      } else {
        setError("Please upload a valid PDF or DOCX resume document.");
      }
    }
  };

  // STEP 1: Parse Resume with AI
  async function handleParseResume() {
    if (!token || !file) return;

    setIsParsing(true);
    setError(null);
    setAgentStatus("Parsing document & extracting structured candidate profile...");

    try {
      const stored = await createCandidate(token, file);
      setCandidateRecord(stored);
      setParsedProfile(stored.profile);
      setStep("parsed_preview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse resume document.");
    } finally {
      setIsParsing(false);
    }
  }

  // STEP 2: Submit Application & Run ATS Matching
  async function handleRunMatchingAndApply() {
    if (!token || !candidateRecord) return;

    setIsEvaluating(true);
    setStep("evaluating");
    setError(null);
    setAgentStatus("Matching skills & calculating deterministic ATS score...");

    try {
      setTimeout(() => {
        setAgentStatus("Generating match rationale, skill gaps & milestone learning roadmaps...");
      }, 900);

      const application = await createApplication(token, job.id, candidateRecord.id);
      onSuccess(application);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to complete ATS matching.");
      setIsEvaluating(false);
      setStep("parsed_preview");
    }
  }

  return (
    <Modal
      isOpen={true}
      onClose={isParsing || isEvaluating ? () => {} : onClose}
      title={`Apply for ${job.title}`}
      subtitle={job.company_name || "Enterprise Company"}
      maxWidth="680px"
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* Step Indicator */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: "var(--bg-input)",
            borderRadius: "var(--radius-md)",
            padding: "10px 16px",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                backgroundColor: step === "upload" ? "var(--accent-primary)" : "var(--color-success)",
                color: "#FFFFFF",
                fontSize: "12px",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              1
            </span>
            <span style={{ fontSize: "13px", fontWeight: 600, color: step === "upload" ? "var(--text-primary)" : "var(--text-muted)" }}>
              Upload & Parse Resume
            </span>
          </div>

          <span style={{ color: "var(--border-default)" }}>→</span>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                backgroundColor: step === "parsed_preview" || step === "evaluating" ? "var(--accent-secondary)" : "var(--bg-card)",
                color: step === "parsed_preview" || step === "evaluating" ? "#FFFFFF" : "var(--text-muted)",
                fontSize: "12px",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: step === "upload" ? "1px solid var(--border-default)" : "none",
              }}
            >
              2
            </span>
            <span style={{ fontSize: "13px", fontWeight: 600, color: step === "parsed_preview" || step === "evaluating" ? "var(--text-primary)" : "var(--text-muted)" }}>
              ATS Screening & Matching
            </span>
          </div>
        </div>

        {/* Error Alert */}
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

        {/* STEP 1 VIEW: Upload Resume Dropzone */}
        {step === "upload" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Select Resume Document (PDF or DOCX)
            </label>

            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              style={{ display: "none" }}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                  setError(null);
                }
              }}
            />

            {!file ? (
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleFileDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: `2px dashed ${dragOver ? "var(--accent-primary)" : "var(--border-default)"}`,
                  borderRadius: "var(--radius-lg)",
                  backgroundColor: dragOver ? "rgba(99, 102, 241, 0.08)" : "var(--bg-input)",
                  padding: "40px 20px",
                  textAlign: "center",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                <div
                  style={{
                    width: "50px",
                    height: "50px",
                    borderRadius: "50%",
                    backgroundColor: "var(--bg-card)",
                    border: "1px solid var(--border-subtle)",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "var(--accent-primary)",
                    marginBottom: "12px",
                  }}
                >
                  <UploadCloud size={26} />
                </div>
                <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Click to choose file or drag & drop resume here
                </p>
                <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>
                  Supports standard resumes in PDF or DOCX format (Max 10 MB)
                </p>
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "14px 18px",
                  backgroundColor: "var(--bg-input)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <FileText size={24} color="var(--accent-primary)" />
                  <div>
                    <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                      {file.name}
                    </p>
                    <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                      {(file.size / 1024 / 1024).toFixed(2)} MB · Ready for AI parsing
                    </p>
                  </div>
                </div>
                {!isParsing && (
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "4px" }}
                  >
                    <X size={18} />
                  </button>
                )}
              </div>
            )}

            {isParsing && (
              <div
                className="animate-fade-in"
                style={{
                  backgroundColor: "rgba(99, 102, 241, 0.12)",
                  border: "1px solid rgba(99, 102, 241, 0.3)",
                  borderRadius: "var(--radius-md)",
                  padding: "14px 16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span
                  className="animate-spin"
                  style={{
                    width: "18px",
                    height: "18px",
                    border: "2px solid var(--accent-primary)",
                    borderTopColor: "transparent",
                    borderRadius: "50%",
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: "13px", fontWeight: 600, color: "#818CF8" }}>
                  {agentStatus}
                </span>
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
              <Button variant="secondary" onClick={onClose} disabled={isParsing}>
                Cancel
              </Button>
              <Button
                variant="primary"
                icon={Sparkles}
                loading={isParsing}
                disabled={!file || isParsing}
                onClick={handleParseResume}
              >
                ✨ Step 1: Parse Resume with AI
              </Button>
            </div>
          </div>
        )}

        {/* STEP 2 VIEW: AI Extracted Details Preview */}
        {(step === "parsed_preview" || step === "evaluating") && parsedProfile && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Resume Parsing Success Header */}
            <div
              style={{
                backgroundColor: "rgba(16, 185, 129, 0.1)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                borderRadius: "var(--radius-md)",
                padding: "12px 16px",
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <CheckCircle2 size={20} color="var(--color-success)" />
              <div>
                <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-success)", display: "block" }}>
                  ✓ Resume Successfully Parsed & Structured!
                </span>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  Review the structured information extracted from your resume below:
                </span>
              </div>
            </div>

            {/* Extracted Details Card */}
            <Card elevated style={{ backgroundColor: "var(--bg-input)", padding: "18px" }}>
              {/* Personal Info & Extracted Role */}
              <div style={{ display: "grid", gridTemplateColumns: parsedProfile.role ? "1fr 1fr 1fr" : "1fr 1fr", gap: "12px", marginBottom: "14px", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "12px" }}>
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Candidate Name
                  </span>
                  <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", margin: "2px 0 0" }}>
                    {parsedProfile.name || "Candidate"}
                  </p>
                </div>
                {parsedProfile.role && (
                  <div>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                      Extracted Role / Title
                    </span>
                    <p style={{ fontSize: "14px", fontWeight: 600, color: "#818CF8", margin: "2px 0 0" }}>
                      {parsedProfile.role}
                    </p>
                  </div>
                )}
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Extracted Email
                  </span>
                  <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: "2px 0 0" }}>
                    {parsedProfile.email || "Extracted from document"}
                  </p>
                </div>
              </div>

              {/* Extracted Skills */}
              <div style={{ marginBottom: "14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                    Extracted Technical Skills ({parsedProfile.skills?.length || 0})
                  </span>
                  <Badge variant="primary" size="sm">
                    Verified Profile
                  </Badge>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", maxHeight: "120px", overflowY: "auto" }}>
                  {parsedProfile.skills && parsedProfile.skills.length > 0 ? (
                    parsedProfile.skills.map((skill, sIdx) => (
                      <SkillChip key={sIdx} skill={skill} type="matched" size="sm" />
                    ))
                  ) : (
                    <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>General profile skills parsed</span>
                  )}
                </div>
              </div>

              {/* Experience & Education */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", paddingTop: "12px", borderTop: "1px solid var(--border-subtle)" }}>
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Experience
                  </span>
                  <p style={{ fontSize: "13px", color: "var(--text-primary)", margin: "2px 0 0" }}>
                    {parsedProfile.experience || "Experience extracted"}
                  </p>
                </div>
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Education
                  </span>
                  <p style={{ fontSize: "13px", color: "var(--text-primary)", margin: "2px 0 0" }}>
                    {parsedProfile.education?.join(", ") || "Technical Education"}
                  </p>
                </div>
              </div>
            </Card>

            {/* Live Evaluating Banner */}
            {isEvaluating && (
              <div
                className="animate-fade-in"
                style={{
                  backgroundColor: "rgba(124, 58, 237, 0.12)",
                  border: "1px solid rgba(124, 58, 237, 0.3)",
                  borderRadius: "var(--radius-md)",
                  padding: "14px 16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span
                  className="animate-spin"
                  style={{
                    width: "18px",
                    height: "18px",
                    border: "2px solid var(--accent-secondary)",
                    borderTopColor: "transparent",
                    borderRadius: "50%",
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: "13px", fontWeight: 600, color: "#C084FC" }}>
                  {agentStatus}
                </span>
              </div>
            )}

            {/* Actions */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border-subtle)", paddingTop: "16px" }}>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setStep("upload")}
                disabled={isEvaluating}
              >
                ← Upload Different Resume
              </Button>

              <Button
                variant="ai"
                size="md"
                icon={Sparkles}
                loading={isEvaluating}
                disabled={isEvaluating}
                onClick={handleRunMatchingAndApply}
              >
                🚀 Submit Application & Run ATS Matching
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};