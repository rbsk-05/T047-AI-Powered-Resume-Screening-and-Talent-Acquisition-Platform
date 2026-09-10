import React, { useEffect, useState } from "react";
import { Building2, Globe, Users, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { API_URL } from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Input, TextArea } from "../ui/Input";
import { Select } from "../ui/Select";
import { LoadingState } from "../ui/LoadingState";
import { PageHeader } from "../ui/PageHeader";

export const RecruiterCompanyProfile: React.FC = () => {
  const { token, user } = useAuth();
  const [name, setName] = useState(user?.company_name || "");
  const [website, setWebsite] = useState("");
  const [industry, setIndustry] = useState("Information Technology");
  const [size, setSize] = useState("50-200");
  const [description, setDescription] = useState(user?.company_description || "");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setIsLoading(true);
    fetch(`${API_URL}/companies/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((company) => {
        if (company) {
          setName(company.name || "");
          setWebsite(company.website || "");
          setIndustry(company.industry || "Information Technology");
          setSize(company.size || "50-200");
          setDescription(company.description || "");
        }
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setIsSaving(true);
    setError(null);
    setSuccessMsg(false);

    try {
      const res = await fetch(`${API_URL}/companies`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name,
          website,
          industry,
          size,
          description,
        }),
      });

      if (!res.ok) throw new Error("Failed to update company profile");
      setSuccessMsg(true);
      setTimeout(() => setSuccessMsg(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading company profile details..." rows={3} />;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <PageHeader
        title="Company Profile"
        subtitle="Manage your employer brand, enterprise details, and public job posting identity."
      />

      <Card elevated style={{ maxWidth: "760px" }}>
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
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

          {successMsg && (
            <div
              style={{
                backgroundColor: "var(--color-success-bg)",
                border: "1px solid var(--color-success-border)",
                color: "var(--color-success)",
                padding: "10px 14px",
                borderRadius: "var(--radius-md)",
                fontSize: "13px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <CheckCircle2 size={16} />
              <span>Company profile successfully updated!</span>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <Input
              label="Company Name"
              placeholder="e.g. Acme Technologies"
              icon={Building2}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <Input
              label="Company Website"
              placeholder="https://example.com"
              icon={Globe}
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <Select
              label="Industry"
              options={[
                { value: "Information Technology", label: "Information Technology" },
                { value: "Software & SaaS", label: "Software & SaaS" },
                { value: "Financial Services", label: "Financial Services / FinTech" },
                { value: "Healthcare", label: "Healthcare & Life Sciences" },
                { value: "E-Commerce", label: "E-Commerce & Retail" },
              ]}
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />
            <Select
              label="Company Size"
              options={[
                { value: "1-10", label: "1-10 employees" },
                { value: "11-50", label: "11-50 employees" },
                { value: "50-200", label: "50-200 employees" },
                { value: "201-1000", label: "201-1,000 employees" },
                { value: "1000+", label: "1,000+ enterprise" },
              ]}
              value={size}
              onChange={(e) => setSize(e.target.value)}
            />
          </div>

          <TextArea
            label="About the Company"
            placeholder="Describe your company culture, mission, and benefits..."
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <div style={{ display: "flex", justifyContent: "flex-end", borderTop: "1px solid var(--border-subtle)", paddingTop: "16px" }}>
            <Button type="submit" variant="primary" loading={isSaving}>
              Save Company Profile
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
