import { FormEvent, useState } from "react";
import { Role } from "../api";
import { useAuth } from "../auth/AuthContext";

export function AuthScreen() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<Role>("candidate");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password, fullName, role, role === "recruiter" ? companyName : undefined);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <p className="eyebrow">TalentLens AI</p>
        <h1 className="auth-title">{mode === "login" ? "Sign in to your account" : "Create your account"}</h1>
        <p className="intro">{mode === "login" ? "Recruiters and candidates sign in here." : "Choose the account type that matches how you'll use TalentLens AI."}</p>

        <form onSubmit={submit}>
          {mode === "register" && (
            <>
              <label htmlFor="full-name">Full name</label>
              <input id="full-name" value={fullName} onChange={(event) => setFullName(event.target.value)} minLength={2} required />

              <label>Account type</label>
              <div className="role-toggle">
                <button type="button" className={role === "candidate" ? "role-option active" : "role-option"} onClick={() => setRole("candidate")}>
                  Candidate
                </button>
                <button type="button" className={role === "recruiter" ? "role-option active" : "role-option"} onClick={() => setRole("recruiter")}>
                  Recruiter
                </button>
              </div>

              {role === "recruiter" && (
                <>
                  <label htmlFor="company-name">Company name</label>
                  <input id="company-name" value={companyName} onChange={(event) => setCompanyName(event.target.value)} minLength={2} required />
                </>
              )}
            </>
          )}

          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />

          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required />

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
        </form>

        <p className="auth-switch">
          {mode === "login" ? (
            <>
              Don't have an account?{" "}
              <button type="button" className="link-button" onClick={() => setMode("register")}>
                Create one
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button type="button" className="link-button" onClick={() => setMode("login")}>
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </main>
  );
}
