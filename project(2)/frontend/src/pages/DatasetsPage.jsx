import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/useAuth";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";

const CAN_MANAGE = ["admin", "researcher"];

export default function DatasetsPage() {
  const { user } = useAuth();
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const canManage = CAN_MANAGE.includes(user?.role);

  const load = async (q) => {
    setLoading(true);
    try {
      const res = await client.get("/datasets", { params: q ? { search: q } : {} });
      setDatasets(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    client.get("/datasets").then((res) => {
      if (active) setDatasets(res.data.data);
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) { setError("Please choose a CSV trajectory file"); return; }
    setError(""); setUploading(true);
    try {
      const fd = new FormData();
      fd.append("name", form.name);
      fd.append("description", form.description);
      fd.append("file", file);
      await client.post("/datasets", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setShowUpload(false);
      setForm({ name: "", description: "" });
      setFile(null);
      load();
    } catch (err) {
      setError(err?.response?.data?.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Module 1</span>
          <h1>Dataset Management</h1>
          <p className="subtitle">Import, validate and version UAV trajectory datasets.</p>
        </div>
        {canManage && (
          <button className="btn btn-primary" onClick={() => setShowUpload((s) => !s)}>
            {showUpload ? "Cancel" : "+ Upload dataset"}
          </button>
        )}
      </div>

      {showUpload && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3>Upload trajectory dataset</h3>
          <p className="subtitle" style={{ marginBottom: 14 }}>
            Expected CSV columns: <span className="mono">vehicle_id, timestamp, segment_id, speed, lat, lon</span>
          </p>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleUpload}>
            <div className="grid grid-2">
              <div className="form-field">
                <label>Dataset name</label>
                <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="form-field">
                <label>CSV file</label>
                <input type="file" accept=".csv" required onChange={(e) => setFile(e.target.files[0])} />
              </div>
            </div>
            <div className="form-field">
              <label>Description</label>
              <textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <button className="btn btn-primary" disabled={uploading}>
              {uploading ? "Uploading…" : "Upload"}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
          <input placeholder="Search datasets…" value={search}
                 onChange={(e) => setSearch(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && load(search)}
                 style={{ flex: 1, padding: "9px 12px", border: "1px solid var(--border-strong)", borderRadius: 6 }} />
          <button className="btn btn-secondary" onClick={() => load(search)}>Search</button>
        </div>

        {loading ? <Loading /> : datasets.length === 0 ? (
          <div className="empty-state">No datasets found. {canManage ? "Upload one to get started." : ""}</div>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Description</th><th>Status</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.dataset_id}>
                  <td><Link to={`/datasets/${d.dataset_id}`}>{d.name}</Link></td>
                  <td style={{ color: "var(--text-muted)" }}>{d.description || "—"}</td>
                  <td><StatusBadge status={d.status} /></td>
                  <td className="mono" style={{ fontSize: 12 }}>{new Date(d.created_at).toLocaleDateString()}</td>
                  <td><Link to={`/datasets/${d.dataset_id}`} className="btn btn-ghost btn-sm">Open →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
