import React, { useState, useRef, useEffect } from "react";
import { Bell, ChevronDown, User, Settings, LogOut, Menu } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { Badge } from "../ui/Badge";

interface HeaderProps {
  title: string;
  breadcrumb?: string;
  onMenuToggle?: () => void;
  onNavigateSettings?: () => void;
  onNavigateProfile?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  breadcrumb,
  onMenuToggle,
  onNavigateSettings,
  onNavigateProfile,
}) => {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header
      style={{
        height: "64px",
        backgroundColor: "var(--bg-secondary)",
        borderBottom: "1px solid var(--border-default)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        position: "sticky",
        top: 0,
        zIndex: 90,
        flexShrink: 0,
      }}
    >
      {/* Left: Breadcrumbs & Page Title */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {onMenuToggle && (
          <button
            type="button"
            onClick={onMenuToggle}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              padding: "4px",
            }}
          >
            <Menu size={20} />
          </button>
        )}
        <div>
          {breadcrumb && (
            <span style={{ fontSize: "12px", color: "var(--text-muted)", display: "block", marginBottom: "1px" }}>
              {breadcrumb}
            </span>
          )}
          <span style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)" }}>
            {title}
          </span>
        </div>
      </div>

      {/* Right: Notification & Profile dropdown */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {/* Notification Bell */}
        <button
          type="button"
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-default)",
            color: "var(--text-secondary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            position: "relative",
          }}
          title="Notifications"
        >
          <Bell size={16} />
          <span
            style={{
              position: "absolute",
              top: "8px",
              right: "8px",
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--accent-primary)",
            }}
          />
        </button>

        {/* Profile Dropdown */}
        <div style={{ position: "relative" }} ref={dropdownRef}>
          <button
            type="button"
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              background: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              padding: "5px 10px 5px 6px",
              borderRadius: "var(--radius-full)",
              cursor: "pointer",
            }}
          >
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: "var(--accent-gradient)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#FFFFFF",
                fontSize: "12px",
                fontWeight: 700,
              }}
            >
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              {user?.full_name}
            </span>
            <Badge variant={user?.role === "recruiter" ? "secondary" : "primary"} size="sm">
              {user?.role}
            </Badge>
            <ChevronDown size={14} color="var(--text-muted)" />
          </button>

          {/* Menu popup */}
          {dropdownOpen && (
            <div
              className="animate-fade-in"
              style={{
                position: "absolute",
                top: "calc(100% + 8px)",
                right: 0,
                width: "200px",
                backgroundColor: "var(--bg-card-elevated)",
                border: "1px solid var(--border-default)",
                borderRadius: "var(--radius-md)",
                boxShadow: "var(--shadow-lg)",
                padding: "6px",
                zIndex: 200,
              }}
            >
              <div style={{ padding: "8px 12px", borderBottom: "1px solid var(--border-subtle)", marginBottom: "4px" }}>
                <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
                  {user?.full_name}
                </p>
                <p style={{ fontSize: "11px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                  {user?.email}
                </p>
              </div>

              {onNavigateProfile && (
                <button
                  type="button"
                  onClick={() => {
                    setDropdownOpen(false);
                    onNavigateProfile();
                  }}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 12px",
                    fontSize: "13px",
                    color: "var(--text-secondary)",
                    background: "none",
                    border: "none",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <User size={14} />
                  <span>Profile</span>
                </button>
              )}

              {onNavigateSettings && (
                <button
                  type="button"
                  onClick={() => {
                    setDropdownOpen(false);
                    onNavigateSettings();
                  }}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 12px",
                    fontSize: "13px",
                    color: "var(--text-secondary)",
                    background: "none",
                    border: "none",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <Settings size={14} />
                  <span>Settings</span>
                </button>
              )}

              <div style={{ height: "1px", backgroundColor: "var(--border-subtle)", margin: "4px 0" }} />

              <button
                type="button"
                onClick={logout}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 12px",
                  fontSize: "13px",
                  color: "var(--color-error)",
                  background: "none",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <LogOut size={14} />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
