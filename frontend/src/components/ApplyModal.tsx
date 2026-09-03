import { useState } from "react";
import { createApplication, createCandidate, StoredApplication, StoredJob } from "../api";
import { useAuth } from "../auth/AuthContext";

type ApplyModalProps = {
  job: StoredJob;
  onClose: () => void;
  onSuccess: (application: StoredApplication) => void;
};

export function ApplyModal({ job, onClose, onSuccess }: ApplyModalProps) {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressText, setProgressText] = useState("");

  async function handleApply() {
    if (!token || !file) return;

    setIsSubmitting(true);
    setError(null);

    try {
      // Step 1: Upload and parse resume
      setProgressText("Uploading and parsing resume with AI...");
      const candidate = await createCandidate(token, file);

      // Step 2: Create application (triggers matching & evaluation)
      setProgressText("Evaluating match against job requirements...");
      const application = await createApplication(token, job.id, candidate.id);

      setProgressText("Application submitted!");
      onSuccess(application);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to apply");
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" style={backdropStyle}>
      <div className="modal-content" style={contentStyle}>
        <h2>Apply for {job.title}</h2>
        <p className="eyebrow" style={{ marginBottom: "1.5rem" }}>{job.company_name}</p>

        <div style={{ marginBottom: "2rem" }}>
          <label htmlFor="resume-upload" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
            Upload your Resume (PDF or DOCX)
          </label>
          <input
            id="resume-upload"
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            disabled={isSubmitting}
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>

        {error && <div className="error-message" style={{ marginBottom: "1rem" }}>{error}</div>}
        {isSubmitting && <div style={{ color: "var(--color-primary)", marginBottom: "1rem" }}>{progressText}</div>}

        <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
          <button type="button" className="ghost-button" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button type="button" onClick={handleApply} disabled={!file || isSubmitting}>
            {isSubmitting ? "Applying..." : "Submit Application"}
          </button>
        </div>
      </div>
    </div>
  );
}

const backdropStyle: React.CSSProperties = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
};

const contentStyle: React.CSSProperties = {
  background: "var(--color-bg)",
  padding: "2rem",
  borderRadius: "12px",
  width: "100%",
  maxWidth: "500px",
  boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
};