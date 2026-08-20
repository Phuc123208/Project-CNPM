import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";

const CAN_MANAGE = ["admin", "researcher"];

export default function DatasetDetailPage() {
  const { datasetId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const canManage = CAN_MANAGE.includes(user?.role);

  const [dataset, setDataset] = useState(null);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeVersion, setActiveVersion] = useState(null);
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const [dsRes, vRes] = await Promise.all([
        client.get(`/datasets/${datasetId}`),
        client.get(`/datasets/${datasetId}/versions`),
      ]);
      setDataset(dsRes.data.data);
      setVersions(vRes.data.data);
      if (vRes.data.data.length) setActiveVersion(vRes.data.data[0]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [datasetId]);

  const openPreview = async (v) => {
    setActiveVersion(v);
    setPreview(null);
    const res = await client.get(`/datasets/versions/${v.version_id}/preview`, { params: { limit: 20 } });
    setPreview(res.data.data);
  };

  const revalidate = async (v) => {
    setBusy(true); setMsg("");
    try {
      await client.post(`/datasets/versions/${v.version_id}/validate`);
      setMsg("Validation re-run successfully.");
      load();
    } finally { setBusy(false); }
  };

  const doStatusAction = async (action) => {
    setBusy(true);
    try {
      await client.post(`/datasets/${datasetId}/${action}`);
      load();
    } finally { setBusy(false); }
  };

  const doDelete = async () => {
    if (!window.confirm("Delete this dataset? This can be undone (soft delete) unless permanent.")) return;
    await client.delete(`/datasets/${datasetId}`);
    navigate("/datasets");
  };

  if (loading) return <Loading label="Loading dataset…" />;
  if (!dataset) return <div className="empty-state">Dataset not found.</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Dataset #{dataset.dataset_id}</span>
          <h1>{dataset.name}</h1>
          <p className="subtitle">{dataset.description || "No description provided."}</p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <StatusBadge status={dataset.status} />
          {canManage && (
            <>
              {dataset.status !== "archived" ? (
                <button className="btn btn-secondary btn-sm" disabled={busy} onClick={() => doStatusAction("archive")}>Archive</button>
              ) : (
                <button className="btn btn-secondary btn-sm" disabled={busy} onClick={() => doStatusAction("restore")}>Restore</button>
              )}
              <button className="btn btn-danger btn-sm" disabled={busy} onClick={doDelete}>Delete</button>
            </>
          )}
        </div>
      </div>

      {msg && <div className="alert alert-success">{msg}</div>}

      <div className="grid" style={{ gridTemplateColumns: "280px 1fr", gap: 16, alignItems: "start" }}>
        <div className="card">
          <h3>Versions</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
            {versions.map((v) => (
              <button key={v.version_id}
                      onClick={() => openPreview(v)}
                      className="btn-ghost"
                      style={{
                        textAlign: "left", padding: "8px 10px", borderRadius: 8, cursor: "pointer",
                        background: activeVersion?.version_id === v.version_id ? "var(--surface-alt)" : "transparent",
                        border: "1px solid " + (activeVersion?.version_id === v.version_id ? "var(--border-strong)" : "transparent"),
                      }}>
                <div className="mono" style={{ fontWeight: 600, fontSize: 13 }}>{v.version_number}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{v.row_count} rows</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          {activeVersion && (
            <div className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3>Validation report — {activeVersion.version_number}</h3>
                {canManage && (
                  <button className="btn btn-secondary btn-sm" disabled={busy} onClick={() => revalidate(activeVersion)}>
                    Re-run validation
                  </button>
                )}
              </div>
              {activeVersion.validation_report ? (
                <div className="grid grid-3" style={{ marginTop: 12 }}>
                  <MiniStat label="Rows" value={activeVersion.validation_report.row_count} />
                  <MiniStat label="Vehicles" value={activeVersion.validation_report.vehicles} />
                  <MiniStat label="Segments" value={activeVersion.validation_report.segments?.length} />
                  <MiniStat label="Missing values" value={Object.values(activeVersion.validation_report.missing_values || {}).reduce((a, b) => a + b, 0)} />
                  <MiniStat label="Duplicates" value={activeVersion.validation_report.duplicated_records} />
                  <MiniStat label="Invalid coords" value={activeVersion.validation_report.invalid_coordinates} />
                  <MiniStat label="Invalid timestamps" value={activeVersion.validation_report.invalid_timestamps} />
                  <MiniStat label="Invalid speed" value={activeVersion.validation_report.invalid_speed} />
                  <MiniStat label="Overall" value={activeVersion.validation_report.is_valid ? "Valid ✓" : "Issues found"} />
                </div>
              ) : <p className="subtitle">No validation report yet.</p>}

              <div style={{ marginTop: 16, display: "flex", gap: 10 }}>
                <Link className="btn btn-primary btn-sm" to={`/analysis?version_id=${activeVersion.version_id}`}>
                  Run traffic pattern analysis →
                </Link>
              </div>
            </div>
          )}

          {activeVersion && (
            <div className="card">
              <h3>Data preview</h3>
              {!preview ? <Loading label="Loading preview…" /> : (
                <div style={{ overflowX: "auto" }}>
                  <table>
                    <thead>
                      <tr>{preview.columns.map((c) => <th key={c}>{c}</th>)}</tr>
                    </thead>
                    <tbody>
                      {preview.rows.map((r, i) => (
                        <tr key={i}>{preview.columns.map((c) => <td key={c} className="mono">{String(r[c])}</td>)}</tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="subtitle" style={{ marginTop: 8 }}>Showing {preview.rows.length} of {preview.total_rows} rows</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div style={{ padding: "10px 12px", background: "var(--surface-alt)", borderRadius: 8 }}>
      <div className="mono" style={{ fontSize: 10, textTransform: "uppercase", color: "var(--text-faint)" }}>{label}</div>
      <div className="mono" style={{ fontSize: 18, fontWeight: 600, marginTop: 2 }}>{value ?? "—"}</div>
    </div>
  );
}
