import React from "react";
import {
  LayoutDashboard,
  Briefcase,
  FileCheck,
  User,
  GitCompare,
  Building2,
  Users,
  Award,
  Sparkles,
  BarChart3,
  Settings,
  BrainCircuit,
  LogOut,
  Compass,
} from "lucide-react";
import { useAuth } from "../../auth/AuthContext";

export type CandidateNavTab =
  | "dashboard"
  | "browse_jobs"
  | "my_applications"
  | "skill_analysis"
  | "recommendations"
  | "profile"
  | "settings";

export type RecruiterNavTab =
  | "dashboard"
  | "company_profile"
  | "jobs"
  | "applications"
  | "candidates"
  | "candidate_ranking"
  | "candidate_comparison"
  | "analytics"
  | "settings";

export type NavTab = CandidateNavTab | RecruiterNavTab;

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  isOpen = true,
  onClose,
}) => {
  const { user, logout } = useAuth();
  const isRecruiter = user?.role === "recruiter";

  const candidateNavItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "browse_jobs", label: "Browse Jobs", icon: Compass },
    { id: "my_applications", label: "My Applications", icon: FileCheck },
    { id: "skill_analysis", label: "Skill Analysis", icon: Award },
    { id: "recommendations", label: "Recommendations", icon: Sparkles },
    { id: "profile", label: "My Profile", icon: User },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const recruiterNavItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "company_profile", label: "Company Profile", icon: Building2 },
    { id: "jobs", label: "Jobs", icon: Briefcase },
    { id: "applications", label: "Applications", icon: FileCheck },
    { id: "candidates", label: "Candidates", icon: Users },
    { id: "candidate_ranking", label: "Candidate Ranking", icon: Award },
    { id: "candidate_comparison", label: "Candidate Comparison", icon: GitCompare },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const navItems = isRecruiter ? recruiterNavItems : candidateNavItems;

  return (
    <aside
      style={{
        width: "250px",
        height: "100vh",
        backgroundColor: "var(--bg-secondary)",
        borderRight: "1px solid var(--border-default)",
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        top: 0,
        zIndex: 100,
        flexShrink: 0,
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: "20px 24px",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          gap: "10px",
        }}
      >
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
        <div>
          <span style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.01em", display: "block" }}>
            TalentLens AI
          </span>
          <span style={{ fontSize: "11px", color: "var(--accent-primary)", fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase" }}>
            {isRecruiter ? "Recruiter Portal" : "Candidate Portal"}
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ flex: 1, padding: "16px 12px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "4px" }}>
        <p style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", padding: "0 12px 8px" }}>
          Menu
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                onTabChange(item.id as NavTab);
                if (onClose) onClose();
              }}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "10px 12px",
                borderRadius: "var(--radius-md)",
                backgroundColor: isActive ? "rgba(99, 102, 241, 0.15)" : "transparent",
                color: isActive ? "#818CF8" : "var(--text-secondary)",
                border: isActive ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
                fontSize: "14px",
                fontWeight: isActive ? 600 : 500,
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.15s ease",
              }}
            >
              <Icon size={18} color={isActive ? "var(--accent-primary)" : "var(--text-muted)"} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Footer & Signout */}
      <div
        style={{
          padding: "16px",
          borderTop: "1px solid var(--border-subtle)",
          backgroundColor: "var(--bg-primary)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "50%",
                backgroundColor: "var(--bg-card-elevated)",
                border: "1px solid var(--border-default)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--text-primary)",
                fontWeight: 600,
                fontSize: "13px",
                flexShrink: 0,
              }}
            >
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div style={{ minWidth: 0 }}>
              <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", margin: 0 }}>
                {user?.full_name}
              </p>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", margin: 0, textTransform: "capitalize" }}>
                {user?.role}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={logout}
            title="Sign out"
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "6px",
              display: "flex",
              alignItems: "center",
              borderRadius: "var(--radius-sm)",
            }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
