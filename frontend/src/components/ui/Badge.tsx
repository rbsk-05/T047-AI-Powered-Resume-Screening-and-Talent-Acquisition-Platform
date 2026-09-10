import React from "react";
import { LucideIcon } from "lucide-react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral";
  size?: "sm" | "md";
  icon?: LucideIcon;
  style?: React.CSSProperties;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  style,
  className = "",
}) => {
  const getColors = () => {
    switch (variant) {
      case "success":
        return { bg: "var(--color-success-bg)", text: "var(--color-success)", border: "var(--color-success-border)" };
      case "warning":
        return { bg: "var(--color-warning-bg)", text: "var(--color-warning)", border: "var(--color-warning-border)" };
      case "danger":
        return { bg: "var(--color-error-bg)", text: "var(--color-error)", border: "var(--color-error-border)" };
      case "info":
        return { bg: "var(--color-info-bg)", text: "var(--color-info)", border: "var(--color-info-border)" };
      case "secondary":
        return { bg: "rgba(124, 58, 237, 0.12)", text: "#A78BFA", border: "rgba(124, 58, 237, 0.25)" };
      case "neutral":
        return { bg: "rgba(100, 116, 139, 0.12)", text: "var(--text-secondary)", border: "var(--border-default)" };
      default:
        return { bg: "rgba(99, 102, 241, 0.12)", text: "#818CF8", border: "rgba(99, 102, 241, 0.25)" };
    }
  };

  const colors = getColors();

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        padding: size === "sm" ? "2px 8px" : "4px 10px",
        fontSize: size === "sm" ? "11px" : "12px",
        fontWeight: 600,
        borderRadius: "var(--radius-full)",
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        lineHeight: 1.2,
        ...style,
      }}
      className={`ui-badge ${className}`}
    >
      {Icon && <Icon size={size === "sm" ? 11 : 13} />}
      {children}
    </span>
  );
};
