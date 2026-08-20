import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";
import KpiCard from "../components/KpiCard";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";

const ROLE_INTRO = {
  admin: "Manage users, oversee platform data, and review the audit trail.",
  researcher: "Manage datasets, run analysis, build and compare forecasting models.",
  analyst: "Monitor KPIs, explore visualizations, and run congestion forecasts.",
  student: "Explore sample datasets, learn through visualizations, and practice experiments.",
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [sumRes, dsRes, expRes] = await Promise.all([
          client.get("/dashboard/summary"),
          client.get("/datasets"),
          client.get("/experiments"),
        ]);
        setSummary(sumRes.data.data);
        setDatasets(dsRes.data.data.slice(0, 5));
        setExperiments(expRes.data.data.slice(0, 5));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <Loading label="Loading dashboard…" />;

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Console / Overview</span>
          <h1>Welcome back, {user?.full_name?.split(" ")[0] || "there"}</h1>
          <p className="subtitle">{ROLE_INTRO[user?.role] || ""}</p>
        </div>
      </div>

      <div className="grid grid-4">
        <KpiCard label="Total Datasets" value={summary?.total_datasets ?? 0} />
        <KpiCard label="Total Experiments" value={summary?.total_experiments ?? 0} />
        <KpiCard label="Completed Forecasts" value={summary?.completed_experiments ?? 0} />
        <KpiCard label="Your Role" value={user?.role} />
      </div>

      <div className="grid grid-2" style={{ marginTop: 20 }}>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <h3>Recent Datasets</h3>
            <Link to="/datasets" className="mono" style={{ fontSize: 12 }}>View all →</Link>
          </div>
          {datasets.length === 0 ? (
            <p className="subtitle">No datasets yet.</p>
          ) : (
            <table>
              <thead><tr><th>Name</th><th>Status</th></tr></thead>
              <tbody>
                {datasets.map((d) => (
                  <tr key={d.dataset_id}>
                    <td><Link to={`/datasets/${d.dataset_id}`}>{d.name}</Link></td>
                    <td><StatusBadge status={d.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <h3>Recent Experiments</h3>
            <Link to="/experiments" className="mono" style={{ fontSize: 12 }}>View all →</Link>
          </div>
          {experiments.length === 0 ? (
            <p className="subtitle">No experiments yet.</p>
          ) : (
            <table>
              <thead><tr><th>Name</th><th>Model</th><th>Status</th></tr></thead>
              <tbody>
                {experiments.map((e) => (
                  <tr key={e.experiment_id}>
                    <td><Link to={`/experiments/${e.experiment_id}`}>{e.name}</Link></td>
                    <td className="mono">{e.model_type}</td>
                    <td><StatusBadge status={e.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
