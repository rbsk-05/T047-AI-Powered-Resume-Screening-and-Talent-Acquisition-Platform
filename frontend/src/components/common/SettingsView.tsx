import React, { useState } from "react";
import { Settings, Shield, Bell, Moon, Key } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Badge } from "../ui/Badge";
import { PageHeader } from "../ui/PageHeader";

export const SettingsView: React.FC = () => {
  const { user } = useAuth();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [aiAnalysisFeedback, setAiAnalysisFeedback] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Settings & Preferences"
        subtitle="Manage your platform preferences, account security, and notification settings."
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px" }}>
        {/* Account Details */}
        <Card elevated>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <Shield size={20} color="var(--accent-primary)" />
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              Account Information
            </h3>
          </div>

          <form onSubmit={handleSave}>
            <Input label="Full Name" value={user?.full_name || ""} disabled helperText="Managed by account owner" />
            <Input label="Email Address" value={user?.email || ""} disabled helperText="Primary login email" />
            <div style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Account Role
              </label>
              <Badge variant={user?.role === "recruiter" ? "secondary" : "primary"}>
                {user?.role?.toUpperCase()}
              </Badge>
            </div>
          </form>
        </Card>

        {/* AI & Notification Preferences */}
        <Card elevated>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <Bell size={20} color="var(--accent-secondary)" />
            <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>
              Platform Preferences
            </h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <label style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}>
              <div>
                <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", display: "block" }}>
                  Real-time ATS Notifications
                </span>
                <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  Receive instant alerts when new match evaluations or status updates occur
                </span>
              </div>
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
                style={{ width: "18px", height: "18px", accentColor: "var(--accent-primary)" }}
              />
            </label>

            <label style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}>
              <div>
                <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", display: "block" }}>
                  AI Explainability Insights
                </span>
                <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  Include detailed rationale and milestone recommendations with score reports
                </span>
              </div>
              <input
                type="checkbox"
                checked={aiAnalysisFeedback}
                onChange={(e) => setAiAnalysisFeedback(e.target.checked)}
                style={{ width: "18px", height: "18px", accentColor: "var(--accent-primary)" }}
              />
            </label>

            <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "16px", marginTop: "8px" }}>
              <Button variant="primary" size="sm" onClick={handleSave}>
                Save Preferences
              </Button>
              {savedSuccess && (
                <span style={{ marginLeft: "12px", fontSize: "13px", color: "var(--color-success)", fontWeight: 600 }}>
                  ✓ Preferences updated
                </span>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
