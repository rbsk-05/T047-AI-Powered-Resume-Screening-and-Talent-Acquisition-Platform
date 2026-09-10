import React from "react";

interface ProgressBarProps {
  label?: string;
  value: number; // 0 to 100 or float 0 to 1
  max?: number;
  weightLabel?: string;
  color?: string;
  showValue?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  label,
  value,
  max = 100,
  weightLabel,
  color,
  showValue = true,
}) => {
  // Normalize percentage
  const percentage = Math.min(100, Math.max(0, max === 1 ? value * 100 : value));
  
  const getColor = () => {
    if (color) return color;
    if (percentage >= 75) return "var(--color-success)";
    if (percentage >= 50) return "var(--color-warning)";
    return "var(--color-error)";
  };

  const barColor = getColor();

  return (
    <div style={{ marginBottom: "12px", width: "100%" }}>
      {(label || showValue) && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "5px", fontSize: "13px" }}>
          <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>
            {label} {weightLabel && <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>({weightLabel})</span>}
          </span>
          {showValue && (
            <span style={{ color: "var(--text-primary)", fontWeight: 600, fontFamily: "monospace" }}>
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div
        style={{
          width: "100%",
          height: "8px",
          backgroundColor: "var(--bg-input)",
          borderRadius: "var(--radius-full)",
          overflow: "hidden",
          border: "1px solid var(--border-subtle)",
        }}
      >
        <div
          style={{
            width: `${percentage}%`,
            height: "100%",
            backgroundColor: barColor,
            borderRadius: "var(--radius-full)",
            transition: "width 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
          }}
        />
      </div>
    </div>
  );
};
