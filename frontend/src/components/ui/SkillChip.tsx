import React from "react";
import { Check, X, AlertTriangle } from "lucide-react";

interface SkillChipProps {
  skill: string;
  type?: "matched" | "missing-critical" | "missing-nice" | "neutral" | "preferred";
  size?: "sm" | "md";
  onRemove?: () => void;
}

export const SkillChip: React.FC<SkillChipProps> = ({
  skill,
  type = "neutral",
  size = "md",
  onRemove,
}) => {
  const getStyles = () => {
    switch (type) {
      case "matched":
        return {
          bg: "rgba(16, 185, 129, 0.12)",
          color: "#34D399",
          border: "rgba(16, 185, 129, 0.3)",
          icon: Check,
        };
      case "missing-critical":
        return {
          bg: "rgba(239, 68, 68, 0.12)",
          color: "#F87171",
          border: "rgba(239, 68, 68, 0.3)",
          icon: X,
        };
      case "missing-nice":
        return {
          bg: "rgba(245, 158, 11, 0.12)",
          color: "#FBBF24",
          border: "rgba(245, 158, 11, 0.3)",
          icon: AlertTriangle,
        };
      case "preferred":
        return {
          bg: "rgba(124, 58, 237, 0.12)",
          color: "#A78BFA",
          border: "rgba(124, 58, 237, 0.3)",
          icon: null,
        };
      case "neutral":
      default:
        return {
          bg: "var(--bg-input)",
          color: "var(--text-secondary)",
          border: "var(--border-default)",
          icon: null,
        };
    }
  };

  const styleConfig = getStyles();
  const IconComponent = styleConfig.icon;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: size === "sm" ? "2px 8px" : "4px 10px",
        fontSize: size === "sm" ? "12px" : "13px",
        fontWeight: 500,
        borderRadius: "var(--radius-md)",
        backgroundColor: styleConfig.bg,
        color: styleConfig.color,
        border: `1px solid ${styleConfig.border}`,
        lineHeight: 1.2,
      }}
    >
      {IconComponent && <IconComponent size={size === "sm" ? 11 : 13} />}
      <span>{skill}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          style={{
            background: "none",
            border: "none",
            color: "inherit",
            cursor: "pointer",
            padding: "0 2px",
            display: "flex",
            alignItems: "center",
            opacity: 0.7,
          }}
        >
          <X size={12} />
        </button>
      )}
    </span>
  );
};
