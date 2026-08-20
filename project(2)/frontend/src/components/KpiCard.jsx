import React from "react";

export default function KpiCard({ label, value, unit }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">
        {value}
        {unit && <span>{unit}</span>}
      </div>
    </div>
  );
}
