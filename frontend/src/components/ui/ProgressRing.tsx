import React from "react";

interface ProgressRingProps {
  score: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  score,
  size = 120,
  strokeWidth = 10,
  label,
  sublabel = "Match Score",
}) => {
  const normalizedScore = Math.min(100, Math.max(0, Math.round(score)));
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  const getColor = () => {
    if (normalizedScore >= 75) return "var(--color-success)";
    if (normalizedScore >= 50) return "var(--color-warning)";
    return "var(--color-error)";
  };

  const ringColor = getColor();

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "relative", width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="var(--bg-input)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={ringColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: "stroke-dashoffset 0.6s cubic-bezier(0.16, 1, 0.3, 1)" }}
          />
        </svg>
        {/* Center Text */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: size > 90 ? "26px" : "18px", fontWeight: 700, color: "var(--text-primary)", lineHeight: 1 }}>
            {normalizedScore}%
          </span>
          {sublabel && (
            <span style={{ fontSize: size > 90 ? "11px" : "9px", color: "var(--text-muted)", marginTop: "3px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              {sublabel}
            </span>
          )}
        </div>
      </div>
      {label && (
        <span style={{ marginTop: "8px", fontSize: "13px", fontWeight: 600, color: ringColor }}>
          {label}
        </span>
      )}
    </div>
  );
};
