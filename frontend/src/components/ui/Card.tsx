import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  elevated?: boolean;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  elevated = false,
  className = "",
  style,
  ...props
}) => {
  return (
    <div
      style={{
        backgroundColor: elevated ? "var(--bg-card-elevated)" : "var(--bg-card)",
        border: "1px solid var(--border-default)",
        borderRadius: "var(--radius-lg)",
        padding: "20px 24px",
        boxShadow: elevated ? "var(--shadow-lg)" : "var(--shadow-md)",
        transition: "border-color 0.15s ease, transform 0.15s ease",
        ...style,
      }}
      className={`ui-card ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
