import React from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export type ToastType = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: "20px",
        right: "20px",
        zIndex: 2000,
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        maxWidth: "380px",
        width: "100%",
      }}
    >
      {toasts.map((toast) => {
        const getStyles = () => {
          if (toast.type === "success") {
            return {
              bg: "var(--bg-card-elevated)",
              border: "1px solid var(--color-success-border)",
              icon: <CheckCircle2 size={18} color="var(--color-success)" />,
            };
          }
          if (toast.type === "error") {
            return {
              bg: "var(--bg-card-elevated)",
              border: "1px solid var(--color-error-border)",
              icon: <AlertCircle size={18} color="var(--color-error)" />,
            };
          }
          return {
            bg: "var(--bg-card-elevated)",
            border: "1px solid var(--color-info-border)",
            icon: <Info size={18} color="var(--color-info)" />,
          };
        };

        const config = getStyles();

        return (
          <div
            key={toast.id}
            className="animate-fade-in"
            style={{
              backgroundColor: config.bg,
              border: config.border,
              borderRadius: "var(--radius-md)",
              padding: "12px 16px",
              boxShadow: "var(--shadow-lg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              {config.icon}
              <span style={{ fontSize: "14px", color: "var(--text-primary)", fontWeight: 500 }}>
                {toast.message}
              </span>
            </div>
            <button
              type="button"
              onClick={() => onDismiss(toast.id)}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "2px",
                display: "flex",
              }}
            >
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
};
