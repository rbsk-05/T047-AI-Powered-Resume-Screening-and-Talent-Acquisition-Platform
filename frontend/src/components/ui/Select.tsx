import React from "react";

interface Option {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: Option[];
  error?: string;
  helperText?: string;
}

export const Select: React.FC<SelectProps> = ({
  label,
  options,
  error,
  helperText,
  id,
  style,
  className = "",
  ...props
}) => {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div style={{ marginBottom: "16px", width: "100%" }}>
      {label && (
        <label
          htmlFor={selectId}
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
      <select
        id={selectId}
        style={{
          width: "100%",
          backgroundColor: "var(--bg-input)",
          border: `1px solid ${error ? "var(--color-error)" : "var(--border-default)"}`,
          borderRadius: "var(--radius-md)",
          padding: "9px 14px",
          color: "var(--text-primary)",
          fontSize: "14px",
          transition: "border-color 0.15s ease",
          boxSizing: "border-box",
          cursor: "pointer",
          ...style,
        }}
        className={`ui-select ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} style={{ backgroundColor: "var(--bg-card)", color: "var(--text-primary)" }}>
            {opt.label}
          </option>
        ))}
      </select>
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
