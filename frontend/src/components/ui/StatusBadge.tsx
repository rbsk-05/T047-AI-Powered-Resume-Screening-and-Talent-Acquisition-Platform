import React from "react";
import { CheckCircle2, Clock, XCircle, Sparkles, AlertCircle } from "lucide-react";
import { Badge } from "./Badge";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = "md" }) => {
  const normalized = (status || "").toUpperCase();

  switch (normalized) {
    case "PUBLISHED":
    case "SELECTED":
    case "HIRED":
      return (
        <Badge variant="success" size={size} icon={CheckCircle2}>
          {normalized === "PUBLISHED" ? "Published" : normalized === "SELECTED" ? "Selected" : "Hired"}
        </Badge>
      );
    case "SHORTLISTED":
      return (
        <Badge variant="secondary" size={size} icon={Sparkles}>
          Shortlisted
        </Badge>
      );
    case "UNDER_REVIEW":
    case "UNDER REVIEW":
    case "IN_REVIEW":
      return (
        <Badge variant="warning" size={size} icon={Clock}>
          Under Review
        </Badge>
      );
    case "APPLIED":
    case "SUBMITTED":
      return (
        <Badge variant="info" size={size} icon={Clock}>
          Applied
        </Badge>
      );
    case "REJECTED":
    case "CLOSED":
      return (
        <Badge variant="danger" size={size} icon={XCircle}>
          {normalized === "CLOSED" ? "Closed" : "Rejected"}
        </Badge>
      );
    case "DRAFT":
    default:
      return (
        <Badge variant="neutral" size={size} icon={AlertCircle}>
          {normalized || "Draft"}
        </Badge>
      );
  }
};
