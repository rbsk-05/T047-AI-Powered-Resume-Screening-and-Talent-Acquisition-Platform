import React from "react";
import { LucideIcon } from "lucide-react";
import { Card } from "./Card";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    positive?: boolean;
  };
  accentColor?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = "var(--accent-primary)",
}) => {
  return (
    <Card style={{ position: "relative", overflow: "hidden" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            {title}
          </p>
          <p style={{ color: "var(--text-primary)", fontSize: "32px", fontWeight: 700, margin: "6px 0 2px", lineHeight: 1.1 }}>
            {value}
          </p>
          {subtitle && (
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", margin: 0 }}>
              {subtitle}
            </p>
          )}
          {trend && (
            <p style={{ fontSize: "12px", marginTop: "4px", color: trend.positive ? "var(--color-success)" : "var(--color-error)", fontWeight: 600 }}>
              {trend.positive ? "↑" : "↓"} {trend.value}
            </p>
          )}
        </div>
        {Icon && (
          <div
            style={{
              padding: "10px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "var(--bg-input)",
              border: "1px solid var(--border-subtle)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: accentColor,
            }}
          >
            <Icon size={22} />
          </div>
        )}
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: "3px",
          backgroundColor: accentColor,
          opacity: 0.8,
        }}
      />
    </Card>
  );
};
