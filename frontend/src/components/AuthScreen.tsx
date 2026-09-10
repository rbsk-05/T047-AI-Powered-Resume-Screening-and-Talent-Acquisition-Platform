import React, { FormEvent, useState } from "react";
import { BrainCircuit, Mail, Lock, User as UserIcon, Building2, ArrowRight } from "lucide-react";
import { Role } from "../api";
import { useAuth } from "../auth/AuthContext";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";

interface AuthScreenProps {
  onBackToLanding?: () => void;
}

export const AuthScreen: React.FC<AuthScreenProps> = ({ onBackToLanding }) => {
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
        await register(
          email,
          password,
          fullName,
          role,
          role === "recruiter" ? companyName : undefined
        );
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "var(--bg-primary)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          marginBottom: "32px",
          cursor: onBackToLanding ? "pointer" : "default",
        }}
        onClick={onBackToLanding}
      >
        <div
          style={{
            width: "42px",
            height: "42px",
            borderRadius: "var(--radius-md)",
            background: "var(--accent-gradient)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#FFFFFF",
            boxShadow: "var(--shadow-glow)",
          }}
        >
          <BrainCircuit size={26} />
        </div>
        <div>
          <span style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", display: "block" }}>
            TalentLens AI
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Intelligent Hiring. Better Talent Decisions.
          </span>
        </div>
      </div>

      {/* Auth Card */}
      <div
        className="animate-fade-in"
        style={{
          width: "100%",
          maxWidth: "460px",
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border-default)",
          borderRadius: "var(--radius-xl)",
          boxShadow: "var(--shadow-lg)",
          padding: "32px",
        }}
      >
        {/* Toggle Mode Tabs */}
        <div
          style={{
            display: "flex",
            backgroundColor: "var(--bg-input)",
            borderRadius: "var(--radius-md)",
            padding: "4px",
            marginBottom: "24px",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <button
            type="button"
            onClick={() => { setMode("login"); setError(null); }}
            style={{
              flex: 1,
              padding: "8px",
              fontSize: "13px",
              fontWeight: 600,
              borderRadius: "var(--radius-sm)",
              backgroundColor: mode === "login" ? "var(--bg-card-elevated)" : "transparent",
              color: mode === "login" ? "var(--text-primary)" : "var(--text-muted)",
              border: mode === "login" ? "1px solid var(--border-default)" : "none",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setMode("register"); setError(null); }}
            style={{
              flex: 1,
              padding: "8px",
              fontSize: "13px",
              fontWeight: 600,
              borderRadius: "var(--radius-sm)",
              backgroundColor: mode === "register" ? "var(--bg-card-elevated)" : "transparent",
              color: mode === "register" ? "var(--text-primary)" : "var(--text-muted)",
              border: mode === "register" ? "1px solid var(--border-default)" : "none",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            Create Account
          </button>
        </div>

        <h2 style={{ fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "6px" }}>
          {mode === "login" ? "Welcome back" : "Get started with TalentLens"}
        </h2>
        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "20px" }}>
          {mode === "login"
            ? "Sign in to access your recruitment or job application portal."
            : "Select your role and create an account to begin."}
        </p>

        {error && (
          <div
            style={{
              backgroundColor: "var(--color-error-bg)",
              border: "1px solid var(--color-error-border)",
              color: "var(--color-error)",
              padding: "10px 14px",
              borderRadius: "var(--radius-md)",
              fontSize: "13px",
              marginBottom: "18px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={submit}>
          {mode === "register" && (
            <>
              {/* Role Selection Tabs */}
              <div style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                  I am a:
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <button
                    type="button"
                    onClick={() => setRole("candidate")}
                    style={{
                      padding: "12px",
                      borderRadius: "var(--radius-md)",
                      backgroundColor: role === "candidate" ? "rgba(99, 102, 241, 0.15)" : "var(--bg-input)",
                      border: `1px solid ${role === "candidate" ? "var(--accent-primary)" : "var(--border-default)"}`,
                      color: role === "candidate" ? "#818CF8" : "var(--text-secondary)",
                      fontSize: "13px",
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "6px",
                    }}
                  >
                    <UserIcon size={16} />
                    <span>Candidate</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole("recruiter")}
                    style={{
                      padding: "12px",
                      borderRadius: "var(--radius-md)",
                      backgroundColor: role === "recruiter" ? "rgba(124, 58, 237, 0.15)" : "var(--bg-input)",
                      border: `1px solid ${role === "recruiter" ? "var(--accent-secondary)" : "var(--border-default)"}`,
                      color: role === "recruiter" ? "#C084FC" : "var(--text-secondary)",
                      fontSize: "13px",
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "6px",
                    }}
                  >
                    <Building2 size={16} />
                    <span>Recruiter</span>
                  </button>
                </div>
              </div>

              <Input
                label="Full Name"
                placeholder="e.g. Alex Johnson"
                icon={UserIcon}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                minLength={2}
              />

              {role === "recruiter" && (
                <Input
                  label="Company Name"
                  placeholder="e.g. Acme Technologies"
                  icon={Building2}
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required
                  minLength={2}
                />
              )}
            </>
          )}

          <Input
            label="Email Address"
            type="email"
            placeholder="you@example.com"
            icon={Mail}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            icon={Lock}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            helperText={mode === "register" ? "Must be at least 8 characters" : undefined}
          />

          <Button
            type="submit"
            variant="primary"
            size="md"
            loading={isSubmitting}
            icon={ArrowRight}
            iconPosition="right"
            style={{ width: "100%", marginTop: "8px" }}
          >
            {mode === "login" ? "Sign In" : "Create Account"}
          </Button>
        </form>

        <div style={{ marginTop: "20px", textAlign: "center" }}>
          {mode === "login" ? (
            <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => { setMode("register"); setError(null); }}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--accent-primary)",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Sign up
              </button>
            </p>
          ) : (
            <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
              Already registered?{" "}
              <button
                type="button"
                onClick={() => { setMode("login"); setError(null); }}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--accent-primary)",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Sign in
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
