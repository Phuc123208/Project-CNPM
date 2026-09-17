import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, Legend, Cell,
} from "recharts";
import client from "../api/client";
import { useAuth } from "../context/useAuth";
import KpiCard from "../components/KpiCard";
import Loading from "../components/Loading";

const CAN_COMPUTE = ["admin", "researcher", "analyst"];

export default function AnalysisPage() {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const canCompute = CAN_COMPUTE.includes(user?.role);

  const [datasets, setDatasets] = useState([]);
  const [versions, setVersions] = useState([]);
  const [datasetId, setDatasetId] = useState("");
  const [versionId, setVersionId] = useState(params.get("version_id") || "");
  const [interval, setInterval_] = useState(1);
  const [segmentFilter, setSegmentFilter] = useState("");

  const [kpis, setKpis] = useState(null);
  const [trend, setTrend] = useState([]);
  const [heatmap, setHeatmap] = useState([]);
  const [speedDist, setSpeedDist] = useState([]);
  const [peakHours, setPeakHours] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [computing, setComputing] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [msg, setMsg] = useState("");
  const [reportMsg, setReportMsg] = useState("");

  const generateReport = async (format) => {
    setReportMsg("Generating…");
    try {
      const res = await client.post(`/reports/traffic/${versionId}`, { format });
      setReportMsg(`Report ready: ${res.data.data.report_name} — see the Reports page to download.`);
    } catch (err) {
      setReportMsg(err?.response?.data?.message || "Report generation failed");
    }
  };

  useEffect(() => {
    client.get("/datasets").then((res) => setDatasets(res.data.data));
  }, []);

  useEffect(() => {
    if (!datasetId) return;
    client.get(`/datasets/${datasetId}/versions`).then((res) => {
      setVersions(res.data.data);
      if (!versionId && res.data.data.length) {
        const nextVersionId = String(res.data.data[0].version_id);
        setVersionId(nextVersionId);
        setParams({ version_id: nextVersionId });
      }
    });
    // eslint-disable-next-line
  }, [datasetId]);

  // If a version_id came from URL query, find its parent dataset for the dropdown
  useEffect(() => {
    if (versionId && datasets.length && !datasetId) {
      client.get(`/datasets/versions/${versionId}/preview`).catch(() => {});
    }
  }, [versionId, datasets, datasetId]);

  const loadAll = async (vId, segId) => {
    setLoadingData(true);
    try {
      const seg = segId ? { segment_id: segId } : {};
      const [k, t, h, s, p, hs] = await Promise.all([
        client.get(`/analysis/versions/${vId}/kpis`),
        client.get(`/analysis/versions/${vId}/trend`, { params: seg }),
        client.get(`/analysis/versions/${vId}/heatmap`),
        client.get(`/analysis/versions/${vId}/speed-distribution`),
        client.get(`/analysis/versions/${vId}/peak-hours`),
        client.get(`/analysis/versions/${vId}/hotspots`),
      ]);
      setKpis(k.data.data);
      setTrend(t.data.data);
      setHeatmap(h.data.data);
      setSpeedDist(s.data.data);
      setPeakHours(p.data.data);
      setHotspots(hs.data.data);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    if (versionId) {
      Promise.resolve().then(() => loadAll(versionId, segmentFilter));
    }
    // eslint-disable-next-line
  }, [versionId]);

  const compute = async () => {
    if (!versionId) return;
    setComputing(true); setMsg("");
    try {
      const res = await client.post(`/analysis/versions/${versionId}/compute`, { interval_minutes: Number(interval) });
      setMsg(`Generated ${res.data.data.points_generated} data points across ${res.data.data.segments.length} segment(s).`);
      loadAll(versionId, segmentFilter);
    } catch (err) {
      setMsg(err?.response?.data?.message || "Computation failed");
    } finally {
      setComputing(false);
    }
  };

  const trendChartData = useMemo(() => trend.map((t) => ({
    time: new Date(t.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    density: t.traffic_density,
    speed: t.avg_speed,
    vehicles: t.vehicle_count,
  })), [trend]);

  const heatmapSegments = useMemo(() => [...new Set(heatmap.map((h) => h.segment_id))], [heatmap]);
  const heatmapHours = useMemo(() => [...Array(24).keys()], []);
  const heatmapLookup = useMemo(() => {
    const m = {};
    heatmap.forEach((h) => { m[`${h.segment_id}_${h.hour}`] = h.traffic_density; });
    return m;
  }, [heatmap]);
  const maxDensity = useMemo(() => Math.max(1, ...heatmap.map((h) => h.traffic_density || 0)), [heatmap]);

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Module 2 &amp; 4</span>
          <h1>Traffic Pattern Analysis</h1>
          <p className="subtitle">Vehicle count, speed, density, peak-hour and hotspot analytics.</p>
        </div>
      </div>

      <div className="card">
        <div className="grid grid-4">
          <div className="form-field" style={{ marginBottom: 0 }}>
            <label>Dataset</label>
            <select value={datasetId} onChange={(e) => {
              setDatasetId(e.target.value);
              setVersionId("");
              setParams({});
            }}>
              <option value="">Select dataset…</option>
              {datasets.map((d) => <option key={d.dataset_id} value={d.dataset_id}>{d.name}</option>)}
            </select>
          </div>
          <div className="form-field" style={{ marginBottom: 0 }}>
            <label>Version</label>
            <select value={versionId} onChange={(e) => {
              setVersionId(e.target.value);
              setParams(e.target.value ? { version_id: e.target.value } : {});
            }} disabled={!versions.length}>
              <option value="">Select version…</option>
              {versions.map((v) => <option key={v.version_id} value={v.version_id}>{v.version_number} ({v.row_count} rows)</option>)}
            </select>
          </div>
          {canCompute && (
            <div className="form-field" style={{ marginBottom: 0 }}>
              <label>Aggregation interval (min)</label>
              <select value={interval} onChange={(e) => setInterval_(e.target.value)}>
                <option value={1}>1</option>
                <option value={5}>5</option>
                <option value={15}>15</option>
                <option value={30}>30</option>
                <option value={60}>60</option>
              </select>
            </div>
          )}
          {canCompute && (
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <button className="btn btn-primary" disabled={!versionId || computing} onClick={compute}>
                {computing ? "Computing…" : "Compute features"}
              </button>
            </div>
          )}
        </div>
        {msg && <div className="alert alert-success" style={{ marginTop: 14 }}>{msg}</div>}
      </div>

      {!versionId ? (
        <div className="empty-state">Select a dataset version above to view analytics.</div>
      ) : loadingData ? (
        <Loading label="Loading analytics…" />
      ) : (
        <>
          <div className="grid grid-4" style={{ marginTop: 16 }}>
            <KpiCard label="Total Vehicle Count" value={kpis?.vehicle_count_total ?? 0} />
            <KpiCard label="Avg Speed" value={kpis?.avg_speed ?? 0} unit="km/h" />
            <KpiCard label="Avg Density" value={kpis?.avg_density ?? 0} unit="veh/km" />
            <KpiCard label="Peak Data Points" value={kpis?.peak_points ?? 0} />
          </div>

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <h3>Traffic density trend</h3>
              <select value={segmentFilter} onChange={(e) => { setSegmentFilter(e.target.value); loadAll(versionId, e.target.value); }}>
                <option value="">All segments</option>
                {heatmapSegments.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            {trendChartData.length === 0 ? <p className="subtitle">No data — run "Compute features" first.</p> : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={trendChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e1e7ed" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="density" name="Density (veh/km)" stroke="#0f766e" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="speed" name="Avg speed (km/h)" stroke="#d97706" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="grid grid-2">
            <div className="card">
              <h3>Speed distribution</h3>
              {speedDist.length === 0 ? <p className="subtitle">No data.</p> : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={speedDist}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e1e7ed" />
                    <XAxis dataKey="range" tick={{ fontSize: 9 }} interval={0} angle={-30} textAnchor="end" height={60} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0f766e" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="card">
              <h3>Peak-hour detection</h3>
              {peakHours.length === 0 ? <p className="subtitle">No data.</p> : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={peakHours}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e1e7ed" />
                    <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="avg_vehicle_count" radius={[4, 4, 0, 0]}>
                      {peakHours.map((p, i) => (
                        <Cell key={i} fill={p.is_peak ? "#d97706" : "#0f766e"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="card">
            <h3>Congestion heatmap (segment × hour of day)</h3>
            {heatmap.length === 0 ? <p className="subtitle">No data.</p> : (
              <div style={{ overflowX: "auto" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Segment</th>
                      {heatmapHours.map((h) => <th key={h} style={{ textAlign: "center" }}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {heatmapSegments.map((seg) => (
                      <tr key={seg}>
                        <td className="mono">{seg}</td>
                        {heatmapHours.map((h) => {
                          const v = heatmapLookup[`${seg}_${h}`];
                          const intensity = v ? Math.min(1, v / maxDensity) : 0;
                          return (
                            <td key={h} style={{
                              background: v ? `rgba(15,118,110,${0.15 + intensity * 0.75})` : "transparent",
                              color: intensity > 0.6 ? "#fff" : "var(--text)",
                              textAlign: "center", fontSize: 11, padding: "6px 4px",
                            }}>
                              {v ? v.toFixed(1) : ""}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3>Export traffic analysis report</h3>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-secondary btn-sm" onClick={() => generateReport("pdf")}>PDF</button>
                <button className="btn btn-secondary btn-sm" onClick={() => generateReport("excel")}>Excel</button>
              </div>
            </div>
            {reportMsg && <div className="alert alert-success" style={{ marginTop: 10 }}>{reportMsg}</div>}
          </div>

          <div className="card">
            <h3>Congestion hotspots</h3>
            {hotspots.length === 0 ? <p className="subtitle">No data.</p> : (
              <table>
                <thead><tr><th>Segment</th><th>Avg Density</th><th>Avg Speed</th><th>Total Vehicles</th></tr></thead>
                <tbody>
                  {hotspots.map((h) => (
                    <tr key={h.segment_id}>
                      <td><span className="segment-tag">{h.segment_id}</span></td>
                      <td className="mono">{h.avg_density?.toFixed(2)}</td>
                      <td className="mono">{h.avg_speed?.toFixed(2)}</td>
                      <td className="mono">{h.total_vehicle_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
