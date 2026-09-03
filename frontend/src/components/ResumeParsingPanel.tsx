import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { createCandidate, listCandidates, CandidateProfile, StoredCandidate } from "../api";
import { useAuth } from "../auth/AuthContext";
import { ChipGroup } from "./ChipGroup";

export function ResumeParsingPanel() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedCandidates, setSavedCandidates] = useState<StoredCandidate[]>([]);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);

  async function refreshSavedCandidates() {
    if (!token) return;
    setIsLoadingSaved(true);
    try {
      setSavedCandidates(await listCandidates(token));
    } catch {
      // Non-fatal: the saved-candidates list is a convenience, not the main flow.
    } finally {
      setIsLoadingSaved(false);
    }
  }

  useEffect(() => {
    refreshSavedCandidates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || !token) {
      setError("Choose a PDF or DOCX resume first.");
      return;
    }
    setError(null);
    setProfile(null);
    setIsLoading(true);
    try {
      const stored = await createCandidate(token, file);
      setProfile(stored.profile);
      await refreshSavedCandidates();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not save this resume.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <header>
        <p className="eyebrow">TalentLens AI</p>
        <h1>Upload your resume to build your profile.</h1>
        <p className="intro">Upload a PDF or DOCX resume. TalentLens AI extracts your skills, education, experience, projects and certifications, and saves your profile for job matching.</p>
      </header>
      <div className="workspace">
        <form onSubmit={submit}>
          <label htmlFor="resume-file">Resume file (PDF or DOCX, max 10 MB)</label>
          <input id="resume-file" type="file" accept=".pdf,.docx" onChange={onFileChange} required />
          {file && <p className="muted file-name">Selected: {file.name}</p>}
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Saving…" : "Save my resume"}
          </button>
          {error && (
            <p className="error" role="alert">
              {error} Confirm that the backend is running on port 8000.
            </p>
          )}
        </form>
        <section className="result" aria-live="polite">
          <div className="result-heading">
            <h2>Structured candidate profile</h2>
            {profile && <span className="ready">Saved</span>}
          </div>
          {profile ? (
            <>
              <div className="profile-group">
                <h3>Name</h3>
                <p>{profile.name ?? "Not detected"}</p>
              </div>
              <div className="profile-group">
                <h3>Contact</h3>
                <p>
                  {profile.email ?? "No email detected"}
                  {profile.phone ? ` · ${profile.phone}` : ""}
                </p>
              </div>
              <ChipGroup label="Skills" items={profile.skills} />
              <div className="profile-group">
                <h3>Experience</h3>
                <p>{profile.experience ?? "Not detected"}</p>
              </div>
              <ChipGroup label="Education" items={profile.education} />
              <div className="profile-group">
                <h3>Projects</h3>
                {profile.projects.length ? (
                  <ul>
                    {profile.projects.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">None detected</p>
                )}
              </div>
              <ChipGroup label="Certifications" items={profile.certifications} />
            </>
          ) : (
            <p className="empty result-placeholder">Upload a resume to see your extracted profile.</p>
          )}
        </section>
      </div>
      <section className="saved-list">
        <div className="result-heading">
          <h2>Your saved resumes</h2>
          <span className="muted">{isLoadingSaved ? "Loading…" : `${savedCandidates.length} saved`}</span>
        </div>
        {savedCandidates.length ? (
          <ul className="record-list">
            {savedCandidates.map((candidate) => (
              <li key={candidate.id}>
                <strong>{candidate.profile.name ?? candidate.resume_filename ?? "Unnamed candidate"}</strong>
                <span className="muted"> · {new Date(candidate.created_at).toLocaleString()}</span>
                <div className="chips">
                  {candidate.profile.skills.slice(0, 6).map((skill) => (
                    <span className="chip" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty">No resumes saved yet.</p>
        )}
      </section>
    </>
  );
}
