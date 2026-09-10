import React from "react";
import { LucideIcon } from "lucide-react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: LucideIcon;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon: Icon,
  id,
  style,
  className = "",
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div style={{ marginBottom: "16px", width: "100%" }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            display: "block",
            fontSize: "13px",
            fontWeight: 600,
            color: "var(--text-primary)",
            marginBottom: "6px",
          }}
        >
          {label}
        </label>
      )}
      <div style={{ position: "relative", width: "100%" }}>
        {Icon && (
          <div
            style={{
              position: "absolute",
              left: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--text-muted)",
              pointerEvents: "none",
              display: "flex",
              alignItems: "center",
            }}
          >
            <Icon size={16} />
          </div>
        )}
        <input
          id={inputId}
          style={{
            width: "100%",
            backgroundColor: "var(--bg-input)",
            border: `1px solid ${error ? "var(--color-error)" : "var(--border-default)"}`,
            borderRadius: "var(--radius-md)",
            padding: Icon ? "9px 14px 9px 38px" : "9px 14px",
            color: "var(--text-primary)",
            fontSize: "14px",
            transition: "border-color 0.15s ease, box-shadow 0.15s ease",
            boxSizing: "border-box",
            ...style,
          }}
          className={`ui-input ${className}`}
          {...props}
        />
      </div>
      {error && (
        <p style={{ color: "var(--color-error)", fontSize: "12px", marginTop: "4px", fontWeight: 500 }}>
          {error}
        </p>
      )}
      {helperText && !error && (
        <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "4px" }}>
          {helperText}
        </p>
      )}
    </div>
  );
};

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const TextArea: React.FC<TextAreaProps> = ({
  label,
  error,
  helperText,
  id,
  style,
  className = "",
  rows = 4,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div style={{ marginBottom: "16px", width: "100%" }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            display: "block",
            fontSize: "13px",
            fontWeight: 600,
            color: "var(--text-primary)",
            marginBottom: "6px",
          }}
        >
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        rows={rows}
        style={{
          width: "100%",
          backgroundColor: "var(--bg-input)",
          border: `1px solid ${error ? "var(--color-error)" : "var(--border-default)"}`,
          borderRadius: "var(--radius-md)",
          padding: "10px 14px",
          color: "var(--text-primary)",
          fontSize: "14px",
          lineHeight: 1.5,
          resize: "vertical",
          transition: "border-color 0.15s ease",
          boxSizing: "border-box",
          ...style,
        }}
        className={`ui-textarea ${className}`}
        {...props}
      />
      {error && (
        <p style={{ color: "var(--color-error)", fontSize: "12px", marginTop: "4px", fontWeight: 500 }}>
          {error}
        </p>
      )}
      {helperText && !error && (
        <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "4px" }}>
          {helperText}
        </p>
      )}
    </div>
  );
};
