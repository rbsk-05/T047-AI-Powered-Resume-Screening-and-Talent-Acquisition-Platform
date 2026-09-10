import React from "react";
import { BrainCircuit, Sparkles, FileText, Award, BarChart3, CheckCircle2, ArrowRight } from "lucide-react";
import { Button } from "./ui/Button";

interface LandingPageProps {
  onGetStarted: () => void;
  onLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onLogin }) => {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-primary)", display: "flex", flexDirection: "column" }}>
      {/* Top Navbar */}
      <nav
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "20px 48px",
          borderBottom: "1px solid var(--border-subtle)",
          backgroundColor: "rgba(11, 17, 32, 0.8)",
          backdropFilter: "blur(8px)",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "var(--radius-md)",
              background: "var(--accent-gradient)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              boxShadow: "var(--shadow-glow)",
            }}
          >
            <BrainCircuit size={22} />
          </div>
          <span style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)" }}>
            TalentLens AI
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Button variant="ghost" onClick={onLogin}>
            Sign In
          </Button>
          <Button variant="primary" onClick={onGetStarted}>
            Get Started
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "80px 24px 60px",
          maxWidth: "1000px",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "6px 14px",
            borderRadius: "var(--radius-full)",
            backgroundColor: "rgba(99, 102, 241, 0.12)",
            border: "1px solid rgba(99, 102, 241, 0.3)",
            color: "#818CF8",
            fontSize: "13px",
            fontWeight: 600,
            marginBottom: "24px",
          }}
        >
          <Sparkles size={14} />
          <span>Next-Generation AI Recruitment & ATS Intelligence</span>
        </div>

        <h1
          style={{
            fontSize: "clamp(2.5rem, 5vw, 4rem)",
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            color: "var(--text-primary)",
            marginBottom: "20px",
          }}
        >
          Intelligent Hiring. <br />
          <span
            style={{
              background: "linear-gradient(135deg, #818CF8 0%, #C084FC 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Better Talent Decisions.
          </span>
        </h1>

        <p
          style={{
            fontSize: "18px",
            color: "var(--text-secondary)",
            maxWidth: "680px",
            lineHeight: 1.6,
            marginBottom: "36px",
          }}
        >
          End-to-end recruitment platform powered by advanced AI. Instant resume screening, transparent ATS scoring, prioritized skill-gap analysis, and milestone upskilling roadmaps.
        </p>

        <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", justifyContent: "center" }}>
          <Button variant="primary" size="lg" icon={ArrowRight} iconPosition="right" onClick={onGetStarted}>
            Start Free as Recruiter / Candidate
          </Button>
          <Button variant="secondary" size="lg" onClick={onLogin}>
            Sign In to Account
          </Button>
        </div>

        {/* Feature Cards Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "20px",
            width: "100%",
            marginTop: "64px",
            textAlign: "left",
          }}
        >
          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-lg)",
              padding: "24px",
            }}
          >
            <div style={{ color: "var(--accent-primary)", marginBottom: "12px" }}>
              <FileText size={24} />
            </div>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
              AI Resume & JD Parsing
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
              Extract structured profiles from PDF/DOCX and job descriptions with intelligent parsing.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-lg)",
              padding: "24px",
            }}
          >
            <div style={{ color: "var(--accent-secondary)", marginBottom: "12px" }}>
              <BarChart3 size={24} />
            </div>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
              Explainable ATS Scoring
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
              4-pillar scoring (Skills 35%, Experience 20%, Education 10%, Semantic 15%) with clear AI rationale.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-lg)",
              padding: "24px",
            }}
          >
            <div style={{ color: "var(--color-warning)", marginBottom: "12px" }}>
              <Award size={24} />
            </div>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
              Prioritized Skill Gaps
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
              Identifies Critical vs. Nice-to-Have missing skills so candidates know exactly what to target.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-lg)",
              padding: "24px",
            }}
          >
            <div style={{ color: "var(--color-success)", marginBottom: "12px" }}>
              <Sparkles size={24} />
            </div>
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
              Upskilling Roadmaps
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
              Personalized, step-by-step milestone learning sequences and practical projects for candidate growth.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: "1px solid var(--border-subtle)",
          padding: "24px",
          textAlign: "center",
          color: "var(--text-muted)",
          fontSize: "13px",
        }}
      >
        © {new Date().getFullYear()} TalentLens AI. Intelligent Hiring. Better Talent Decisions.
      </footer>
    </div>
  );
};
