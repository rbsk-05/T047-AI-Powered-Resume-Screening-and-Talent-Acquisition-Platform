import React from "react";
import { LucideIcon } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "success" | "ghost" | "ai";
  size?: "sm" | "md" | "lg";
  icon?: LucideIcon;
  iconPosition?: "left" | "right";
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  iconPosition = "left",
  loading = false,
  disabled,
  style,
  className = "",
  ...props
}) => {
  const getStyles = (): React.CSSProperties => {
    let bg = "var(--accent-primary)";
    let color = "#FFFFFF";
    let border = "1px solid transparent";

    if (variant === "secondary") {
      bg = "var(--bg-card-elevated)";
      color = "var(--text-primary)";
      border = "1px solid var(--border-default)";
    } else if (variant === "ghost") {
      bg = "transparent";
      color = "var(--text-secondary)";
      border = "1px solid transparent";
    } else if (variant === "danger") {
      bg = "var(--color-error)";
      color = "#FFFFFF";
    } else if (variant === "success") {
      bg = "var(--color-success)";
      color = "#FFFFFF";
    } else if (variant === "ai") {
      bg = "var(--accent-gradient)";
      color = "#FFFFFF";
      border = "1px solid rgba(124, 58, 237, 0.4)";
    }

    const padding =
      size === "sm"
        ? "6px 12px"
        : size === "lg"
        ? "12px 24px"
        : "9px 18px";

    const fontSize =
      size === "sm" ? "13px" : size === "lg" ? "16px" : "14px";

    return {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "8px",
      padding,
      fontSize,
      fontWeight: 600,
      borderRadius: "var(--radius-md)",
      background: bg,
      color,
      border,
      cursor: disabled || loading ? "not-allowed" : "pointer",
      opacity: disabled || loading ? 0.6 : 1,
      transition: "all 0.15s ease",
      lineHeight: 1.2,
      ...style,
    };
  };

  return (
    <button
      disabled={disabled || loading}
      style={getStyles()}
      className={`ui-button ${className}`}
      {...props}
    >
      {loading && (
        <span
          className="animate-spin"
          style={{
            width: "14px",
            height: "14px",
            border: "2px solid currentColor",
            borderTopColor: "transparent",
            borderRadius: "50%",
            display: "inline-block",
          }}
        />
      )}
      {!loading && Icon && iconPosition === "left" && <Icon size={size === "sm" ? 14 : 16} />}
      <span>{children}</span>
      {!loading && Icon && iconPosition === "right" && <Icon size={size === "sm" ? 14 : 16} />}
    </button>
  );
};
