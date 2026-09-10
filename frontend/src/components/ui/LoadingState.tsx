import React from "react";

interface LoadingStateProps {
  message?: string;
  rows?: number;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading...",
  rows = 3,
}) => {
  return (
    <div style={{ width: "100%", padding: "24px 0" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px", color: "var(--text-secondary)" }}>
        <span
          className="animate-spin"
          style={{
            width: "18px",
            height: "18px",
            border: "2px solid var(--accent-primary)",
            borderTopColor: "transparent",
            borderRadius: "50%",
            display: "inline-block",
          }}
        />
        <span style={{ fontSize: "14px", fontWeight: 500 }}>{message}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {Array.from({ length: rows }).map((_, idx) => (
          <div
            key={idx}
            style={{
              height: idx === 0 ? "70px" : "55px",
              width: "100%",
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              opacity: 0.6 - idx * 0.15,
            }}
          />
        ))}
      </div>
    </div>
  );
};
