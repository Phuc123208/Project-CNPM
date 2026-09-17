import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import client from "../api/client";
import { useAuth } from "../context/useAuth";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";
import KpiCard from "../components/KpiCard";

const CAN_RUN = ["admin", "researcher", "analyst"];

function storedResult(experiment, forecasts) {
  const metrics = experiment.evaluation_metrics || {};
  return {
    test_actual: metrics._test_actual || [],
    test_predicted: metrics._test_predicted || [],
    test_index: metrics._test_index || [],
    forecast: forecasts.map((r) => ({
      timestamp: r.forecast_time, predicted_density: r.predicted_density,
      lower_bound: r.lower_bound, upper_bound: r.upper_bound,
    })),
    metrics,
  };
}

export default function ExperimentDetailPage() {
  const { experimentId } = useParams();
  const { user } = useAuth();
  const canRun = CAN_RUN.includes(user?.role);

  const [experiment, setExperiment] = useState(null);
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ segment_id: "", horizon: 4, test_size: 4 });
  const [result, setResult] = useState(null);
  const [reportBusy, setReportBusy] = useState(false);
  const [reportMsg, setReportMsg] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const res = await client.get(`/experiments/${experimentId}`);
      setExperiment(res.data.data);
      const hs = await client.get(`/analysis/versions/${res.data.data.version_id}/hotspots`, { params: { top_n: 50 } });
      const segs = hs.data.data.map((h) => h.segment_id);
      setSegments(segs);
      if (segs.length) setForm((f) => ({ ...f, segment_id: segs[0] }));

      const resultsRes = await client.get(`/experiments/${experimentId}/results`);
      if (resultsRes.data.data.length) {
        setResult(storedResult(res.data.data, resultsRes.data.data));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    const fetchExperiment = async () => {
      const res = await client.get(`/experiments/${experimentId}`);
      if (!active) return;
      setExperiment(res.data.data);
      const hs = await client.get(`/analysis/versions/${res.data.data.version_id}/hotspots`, { params: { top_n: 50 } });
      if (!active) return;
      const segs = hs.data.data.map((h) => h.segment_id);
      setSegments(segs);
      if (segs.length) setForm((f) => ({ ...f, segment_id: segs[0] }));
      const resultsRes = await client.get(`/experiments/${experimentId}/results`);
      if (!active) return;
      if (resultsRes.data.data.length) {
        setResult(storedResult(res.data.data, resultsRes.data.data));
      }
    };
    fetchExperiment().finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [experimentId]);

  const runForecast = async (e) => {
    e.preventDefault();
    setError(""); setRunning(true);
    try {
      const res = await client.post(`/experiments/${experimentId}/run`, {
        segment_id: form.segment_id, horizon: Number(form.horizon), test_size: Number(form.test_size),
      });
      setResult(res.data.data);
      load();
    } catch (err) {
      setError(err?.response?.data?.message || "Forecast run failed");
    } finally {
      setRunning(false);
    }
  };

  const generateReport = async (format) => {
    setReportBusy(true); setReportMsg("");
    try {
      const res = await client.post(`/reports/forecast/${experimentId}`, { format });
      setReportMsg(`Report ready: ${res.data.data.report_name}`);
    } finally { setReportBusy(false); }
  };

  if (loading) return <Loading label="Loading experiment…" />;
  if (!experiment) return <div className="empty-state">Experiment not found.</div>;

  const chartData = result ? [
    ...(result.test_index || []).map((t, i) => ({
      time: new Date(t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      actual: result.test_actual[i], predicted: result.test_predicted[i],
    })),
    ...(result.forecast || []).map((f) => ({
      time: new Date(f.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      forecast: f.predicted_density, lower: f.lower_bound, upper: f.upper_bound,
      band: [f.lower_bound, f.upper_bound],
    })),
  ] : [];

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Experiment #{experiment.experiment_id}</span>
          <h1>{experiment.name}</h1>
          <p className="subtitle">Model: <span className="mono">{experiment.model_type.toUpperCase()}</span> · Dataset version #{experiment.version_id}</p>
        </div>
        <StatusBadge status={experiment.status} />
      </div>

      {canRun && (
        <div className="card">
          <h3>Run forecast</h3>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={runForecast}>
            <div className="grid grid-3">
              <div className="form-field">
                <label>Road segment</label>
                <select value={form.segment_id} onChange={(e) => setForm({ ...form, segment_id: e.target.value })}>
                  {segments.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label>Forecast horizon (steps ahead)</label>
                <input type="number" min={1} max={50} value={form.horizon}
                       onChange={(e) => setForm({ ...form, horizon: e.target.value })} />
              </div>
              <div className="form-field">
                <label>Test window size</label>
                <input type="number" min={2} max={50} value={form.test_size}
                       onChange={(e) => setForm({ ...form, test_size: e.target.value })} />
              </div>
            </div>
            <button className="btn btn-primary" disabled={running || !segments.length}>
              {running ? "Running…" : "Run forecast"}
            </button>
            {!segments.length && <p className="subtitle" style={{ marginTop: 8 }}>
              No traffic features found for this dataset version yet — run "Compute features" on the Analysis page first.
            </p>}
          </form>
        </div>
      )}

      {result && (
        <>
          <div className="grid grid-4">
            <KpiCard label="MAE" value={result.metrics?.MAE ?? "—"} />
            <KpiCard label="RMSE" value={result.metrics?.RMSE ?? "—"} />
            <KpiCard label="MAPE" value={result.metrics?.MAPE ?? "—"} unit="%" />
            <KpiCard label="R²" value={result.metrics?.R2 ?? "—"} />
          </div>

          <div className="card">
            <h3>Actual vs. Predicted &amp; Short-term Forecast</h3>
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e1e7ed" />
                <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Area dataKey="band" name="Confidence interval" fill="#fde68a" stroke="none" opacity={0.5} />
                <Line type="monotone" dataKey="actual" name="Actual density" stroke="#0f766e" strokeWidth={2} dot />
                <Line type="monotone" dataKey="predicted" name="Test prediction" stroke="#2563eb" strokeWidth={2} strokeDasharray="4 3" dot />
                <Line type="monotone" dataKey="forecast" name="Future forecast" stroke="#d97706" strokeWidth={2} dot />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3>Export report</h3>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-secondary btn-sm" disabled={reportBusy} onClick={() => generateReport("pdf")}>PDF</button>
                <button className="btn btn-secondary btn-sm" disabled={reportBusy} onClick={() => generateReport("excel")}>Excel</button>
              </div>
            </div>
            {reportMsg && <div className="alert alert-success" style={{ marginTop: 10 }}>{reportMsg} — see the Reports page to download.</div>}
          </div>
        </>
      )}
    </div>
  );
}
