import React from "react";

export default function Loading({ label = "Loading…" }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "40px 0", color: "var(--text-muted)" }}>
      <div className="spinner" />
      <span className="mono" style={{ fontSize: 12 }}>{label}</span>
    </div>
  );
}
