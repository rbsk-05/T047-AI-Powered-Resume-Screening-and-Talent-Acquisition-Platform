import React from "react";
import { Check, Clock, X, Circle } from "lucide-react";

interface Step {
  id: string;
  label: string;
  status: "complete" | "current" | "upcoming" | "rejected";
  date?: string;
}

interface TimelineProps {
  currentStatus: string;
}

export const Timeline: React.FC<TimelineProps> = ({ currentStatus }) => {
  const norm = (currentStatus || "").toUpperCase();

  const getSteps = (): Step[] => {
    if (norm === "REJECTED" || norm === "CLOSED") {
      return [
        { id: "applied", label: "Applied", status: "complete" },
        { id: "review", label: "Under Review", status: "complete" },
        { id: "decision", label: "Rejected", status: "rejected" },
      ];
    }

    if (norm === "SELECTED" || norm === "HIRED") {
      return [
        { id: "applied", label: "Applied", status: "complete" },
        { id: "review", label: "Under Review", status: "complete" },
        { id: "shortlist", label: "Shortlisted", status: "complete" },
        { id: "selected", label: "Selected", status: "complete" },
      ];
    }

    if (norm === "SHORTLISTED") {
      return [
        { id: "applied", label: "Applied", status: "complete" },
        { id: "review", label: "Under Review", status: "complete" },
        { id: "shortlist", label: "Shortlisted", status: "current" },
        { id: "selected", label: "Decision", status: "upcoming" },
      ];
    }

    if (norm === "UNDER_REVIEW" || norm === "UNDER REVIEW") {
      return [
        { id: "applied", label: "Applied", status: "complete" },
        { id: "review", label: "Under Review", status: "current" },
        { id: "shortlist", label: "Shortlisted", status: "upcoming" },
        { id: "selected", label: "Decision", status: "upcoming" },
      ];
    }

    // Default: Applied
    return [
      { id: "applied", label: "Applied", status: "current" },
      { id: "review", label: "Under Review", status: "upcoming" },
      { id: "shortlist", label: "Shortlisted", status: "upcoming" },
      { id: "selected", label: "Decision", status: "upcoming" },
    ];
  };

  const steps = getSteps();

  return (
    <div style={{ display: "flex", alignItems: "center", width: "100%", padding: "12px 0" }}>
      {steps.map((step, idx) => {
        const isLast = idx === steps.length - 1;

        const getIcon = () => {
          if (step.status === "complete") return <Check size={14} color="#FFFFFF" />;
          if (step.status === "rejected") return <X size={14} color="#FFFFFF" />;
          if (step.status === "current") return <Clock size={14} color="#FFFFFF" />;
          return <Circle size={10} color="var(--text-muted)" />;
        };

        const getNodeColor = () => {
          if (step.status === "complete") return "var(--color-success)";
          if (step.status === "rejected") return "var(--color-error)";
          if (step.status === "current") return "var(--accent-primary)";
          return "var(--bg-input)";
        };

        return (
          <React.Fragment key={step.id}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "relative", zIndex: 2 }}>
              <div
                style={{
                  width: "28px",
                  height: "28px",
                  borderRadius: "50%",
                  backgroundColor: getNodeColor(),
                  border: step.status === "upcoming" ? "2px solid var(--border-default)" : "none",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: step.status === "current" ? "0 0 12px rgba(99, 102, 241, 0.4)" : "none",
                }}
              >
                {getIcon()}
              </div>
              <span
                style={{
                  fontSize: "12px",
                  fontWeight: step.status === "current" ? 700 : 500,
                  color: step.status === "upcoming" ? "var(--text-muted)" : "var(--text-primary)",
                  marginTop: "6px",
                  whiteSpace: "nowrap",
                }}
              >
                {step.label}
              </span>
            </div>

            {!isLast && (
              <div
                style={{
                  flex: 1,
                  height: "2px",
                  backgroundColor: step.status === "complete" ? "var(--color-success)" : "var(--border-default)",
                  margin: "-20px 8px 0",
                  zIndex: 1,
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
