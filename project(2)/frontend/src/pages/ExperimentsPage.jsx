import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/useAuth";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";

const CAN_MANAGE = ["admin", "researcher", "analyst"];

export default function ExperimentsPage() {
  const { user } = useAuth();
  const canManage = CAN_MANAGE.includes(user?.role);

  const [experiments, setExperiments] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ dataset_id: "", version_id: "", name: "", model_type: "arima" });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [compareIds, setCompareIds] = useState(["", ""]);
  const [comparison, setComparison] = useState(null);
  const [compareBusy, setCompareBusy] = useState(false);
  const [compareError, setCompareError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const res = await client.get("/experiments");
      setExperiments(res.data.data);
    } finally { setLoading(false); }
  };

  useEffect(() => {
    let active = true;
    client.get("/experiments").then((res) => {
      if (active) setExperiments(res.data.data);
    }).finally(() => {
      if (active) setLoading(false);
    });
    client.get("/datasets").then((res) => {
      if (active) setDatasets(res.data.data);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (form.dataset_id) {
      client.get(`/datasets/${form.dataset_id}/versions`).then((res) => setVersions(res.data.data));
    }
  }, [form.dataset_id]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError(""); setCreating(true);
    try {
      await client.post("/experiments", {
        version_id: Number(form.version_id), name: form.name, model_type: form.model_type,
      });
      setShowCreate(false);
      setForm({ dataset_id: "", version_id: "", name: "", model_type: "arima" });
      load();
    } catch (err) {
      setError(err?.response?.data?.message || "Could not create experiment");
    } finally {
      setCreating(false);
    }
  };

  const compare = async (e) => {
    e.preventDefault();
    if (!compareIds[0] || !compareIds[1] || compareIds[0] === compareIds[1]) {
      setCompareError("Select two different experiments.");
      return;
    }
    setCompareBusy(true);
    setCompareError("");
    try {
      const res = await client.get(`/experiments/compare?ids=${compareIds.join(",")}`);
      setComparison(res.data.data);
    } catch (err) {
      setCompareError(err?.response?.data?.message || "Could not compare experiments");
    } finally {
      setCompareBusy(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Module 3 &amp; 5</span>
          <h1>Forecasting &amp; Experiments</h1>
          <p className="subtitle">ARIMA / Prophet short-term congestion forecasting with reproducible experiment tracking.</p>
        </div>
        {canManage && (
          <button className="btn btn-primary" onClick={() => setShowCreate((s) => !s)}>
            {showCreate ? "Cancel" : "+ New experiment"}
          </button>
        )}
      </div>

      {showCreate && (
        <div className="card">
          <h3>Create experiment</h3>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleCreate}>
            <div className="grid grid-3">
              <div className="form-field">
                <label>Dataset</label>
                <select required value={form.dataset_id} onChange={(e) => {
                  setForm({ ...form, dataset_id: e.target.value, version_id: "" });
                  setVersions([]);
                }}>
                  <option value="">Select…</option>
                  {datasets.map((d) => <option key={d.dataset_id} value={d.dataset_id}>{d.name}</option>)}
                </select>
              </div>

              <div className="card" style={{ marginTop: 20 }}>
                <h3>Compare experiments</h3>
                <p className="subtitle">Compare completed ARIMA and Prophet runs on the same dataset version.</p>
                {compareError && <div className="alert alert-error">{compareError}</div>}
                <form onSubmit={compare} className="grid grid-3">
                  {[0, 1].map((index) => (
                    <div className="form-field" key={index}>
                      <label>Experiment {index + 1}</label>
                      <select
                        value={compareIds[index]}
                        onChange={(e) => {
                          const next = [...compareIds];
                          next[index] = e.target.value;
                          setCompareIds(next);
                        }}
                      >
                        <option value="">Select completed experiment…</option>
                        {experiments.filter((item) => item.status === "completed").map((item) => (
                          <option key={item.experiment_id} value={item.experiment_id}>
                            {item.model_type.toUpperCase()} — {item.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                  <div style={{ display: "flex", alignItems: "flex-end" }}>
                    <button className="btn btn-secondary" disabled={compareBusy}>
                      {compareBusy ? "Comparing…" : "Compare"}
                    </button>
                  </div>
                </form>
                {comparison && (
                  <table style={{ marginTop: 16 }}>
                    <thead><tr><th>Experiment</th><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>R²</th></tr></thead>
                    <tbody>
                      {comparison.map((item) => (
                        <tr key={item.experiment_id}>
                          <td>{item.name}</td>
                          <td className="mono">{item.model_type.toUpperCase()}</td>
                          <td>{item.evaluation_metrics?.MAE ?? "—"}</td>
                          <td>{item.evaluation_metrics?.RMSE ?? "—"}</td>
                          <td>{item.evaluation_metrics?.MAPE ?? "—"}</td>
                          <td>{item.evaluation_metrics?.R2 ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              <div className="form-field">
                <label>Dataset version</label>
                <select required value={form.version_id} onChange={(e) => setForm({ ...form, version_id: e.target.value })} disabled={!versions.length}>
                  <option value="">Select…</option>
                  {versions.map((v) => <option key={v.version_id} value={v.version_id}>{v.version_number}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label>Forecasting model</label>
                <select value={form.model_type} onChange={(e) => setForm({ ...form, model_type: e.target.value })}>
                  <option value="arima">ARIMA</option>
                  <option value="prophet">Prophet</option>
                </select>
              </div>
            </div>
            <div className="form-field">
              <label>Experiment name</label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                     placeholder="e.g. ARIMA baseline — 15min interval" />
            </div>
            <button className="btn btn-primary" disabled={creating}>{creating ? "Creating…" : "Create experiment"}</button>
          </form>
        </div>
      )}

      <div className="card">
        {loading ? <Loading /> : experiments.length === 0 ? (
          <div className="empty-state">No experiments yet.</div>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Model</th><th>Status</th><th>Metrics (MAE / RMSE)</th><th></th></tr></thead>
            <tbody>
              {experiments.map((e) => (
                <tr key={e.experiment_id}>
                  <td><Link to={`/experiments/${e.experiment_id}`}>{e.name}</Link></td>
                  <td className="mono">{e.model_type}</td>
                  <td><StatusBadge status={e.status} /></td>
                  <td className="mono" style={{ fontSize: 12 }}>
                    {e.evaluation_metrics?.MAE !== undefined
                      ? `${e.evaluation_metrics.MAE} / ${e.evaluation_metrics.RMSE}`
                      : "—"}
                  </td>
                  <td><Link to={`/experiments/${e.experiment_id}`} className="btn btn-ghost btn-sm">Open →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
