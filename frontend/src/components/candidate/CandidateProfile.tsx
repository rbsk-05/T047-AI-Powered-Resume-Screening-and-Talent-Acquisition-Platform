import React, { useEffect, useState, useRef } from "react";
import {
  User,
  Mail,
  FileText,
  Award,
  GraduationCap,
  Briefcase,
  UploadCloud,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  X,
} from "lucide-react";
import { createCandidate, listCandidates, StoredCandidate, CandidateProfile as CandidateProfileType } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { SkillChip } from "../ui/SkillChip";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const CandidateProfile: React.FC = () => {
  const { user, token } = useAuth();
  const [candidates, setCandidates] = useState<StoredCandidate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Resume Upload & Agent 1 testing
  const [file, setFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);
  const [parseSuccess, setParseSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    listCandidates(token)
      .then(setCandidates)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  const handleParseNewResume = async () => {
    if (!token || !file) return;

    setIsParsing(true);
    setParseError(null);
    setParseSuccess(false);

    try {
      const stored = await createCandidate(token, file);
      setCandidates([stored, ...candidates]);
      setParseSuccess(true);
      setFile(null);
      setTimeout(() => setParseSuccess(false), 4000);
    } catch (err) {
      setParseError(err instanceof Error ? err.message : "Failed to parse resume with AI.");
    } finally {
      setIsParsing(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading your candidate profile..." rows={3} />;
  }

  const latestProfile = candidates.length > 0 ? candidates[0].profile : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Candidate Profile & AI Resume Intelligence"
        subtitle="Manage your personal credentials, upload resumes for automated parsing, and review verified skills."
      />

      {/* Account Info Card */}
      <Card elevated>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "var(--accent-gradient)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              fontSize: "22px",
              fontWeight: 700,
            }}
          >
            {user?.full_name?.charAt(0) || "C"}
          </div>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              {user?.full_name}
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "2px 0 0" }}>
              {user?.email}
            </p>
            <Badge variant="primary" size="sm" style={{ marginTop: "6px" }}>
              Candidate Account
            </Badge>
          </div>
        </div>
      </Card>

      {/* AI Resume Parser & Upload Card */}
      <Card elevated>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Sparkles size={18} color="var(--accent-primary)" />
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                Upload & Parse Resume with AI
              </h3>
            </div>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "4px 0 0" }}>
              Upload your resume to automatically parse, structure, and verify your skills and qualifications.
            </p>
          </div>
        </div>

        {parseError && (
          <div
            style={{
              backgroundColor: "var(--color-error-bg)",
              border: "1px solid var(--color-error-border)",
              color: "var(--color-error)",
              padding: "10px 14px",
              borderRadius: "var(--radius-md)",
              fontSize: "13px",
              marginBottom: "14px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <AlertCircle size={16} />
            <span>{parseError}</span>
          </div>
        )}

        {parseSuccess && (
          <div
            style={{
              backgroundColor: "var(--color-success-bg)",
              border: "1px solid var(--color-success-border)",
              color: "var(--color-success)",
              padding: "10px 14px",
              borderRadius: "var(--radius-md)",
              fontSize: "13px",
              marginBottom: "14px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <CheckCircle2 size={16} />
            <span>✓ Resume successfully parsed and profile updated!</span>
          </div>
        )}

        <input
          type="file"
          ref={fileInputRef}
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          style={{ display: "none" }}
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              setFile(e.target.files[0]);
              setParseError(null);
            }
          }}
        />

        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          {!file ? (
            <Button
              variant="secondary"
              icon={UploadCloud}
              onClick={() => fileInputRef.current?.click()}
            >
              Choose PDF / DOCX Resume
            </Button>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: "10px", backgroundColor: "var(--bg-input)", padding: "6px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-default)" }}>
              <FileText size={16} color="var(--accent-primary)" />
              <span style={{ fontSize: "13px", color: "var(--text-primary)", fontWeight: 500 }}>
                {file.name}
              </span>
              <button
                type="button"
                onClick={() => setFile(null)}
                style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "2px" }}
              >
                <X size={14} />
              </button>
            </div>
          )}

          {file && (
            <Button
              variant="primary"
              icon={Sparkles}
              loading={isParsing}
              onClick={handleParseNewResume}
            >
              Extract Details from Resume
            </Button>
          )}
        </div>
      </Card>

      {/* Extracted Profile Details */}
      {latestProfile ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
          {/* Extracted Skills */}
          <Card elevated>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Award size={18} color="var(--accent-primary)" />
                <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  Extracted Skills from Resume
                </h4>
              </div>
              <Badge variant="success" size="sm">
                {latestProfile.skills?.length || 0} Skills Parsed
              </Badge>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {latestProfile.skills?.map((skill, sIdx) => (
                <SkillChip key={sIdx} skill={skill} type="matched" size="sm" />
              ))}
            </div>
          </Card>

          {/* Education & Experience & Role */}
          <Card elevated>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
              <GraduationCap size={18} color="var(--accent-secondary)" />
              <h4 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                Role, Education & Experience
              </h4>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {latestProfile.role && (
                <div style={{ fontSize: "13px", color: "#818CF8", backgroundColor: "rgba(99, 102, 241, 0.1)", padding: "6px 10px", borderRadius: "var(--radius-sm)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
                  🎯 <strong>Target Role:</strong> {latestProfile.role}
                </div>
              )}
              {latestProfile.education?.map((edu, eIdx) => (
                <div key={eIdx} style={{ fontSize: "13px", color: "var(--text-primary)" }}>
                  🎓 {edu}
                </div>
              ))}
              {latestProfile.experience && (
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
                  💼 <strong>Experience:</strong> {latestProfile.experience}
                </div>
              )}
            </div>
          </Card>
        </div>
      ) : (
        <Card>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", textAlign: "center", padding: "16px 0", margin: 0 }}>
            No parsed resume on file. Upload a resume above to view your extracted structured profile.
          </p>
        </Card>
      )}
    </div>
  );
};
