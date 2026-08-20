import React, { useEffect, useState } from "react";
import client from "../api/client";
import Loading from "../components/Loading";

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/audit").then((res) => setLogs(res.data.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Admin</span>
          <h1>Audit Trail</h1>
          <p className="subtitle">System-wide log of dataset uploads, experiment runs, forecasts and user activity.</p>
        </div>
      </div>
      <div className="card">
        {loading ? <Loading /> : logs.length === 0 ? (
          <div className="empty-state">No activity recorded yet.</div>
        ) : (
          <table>
            <thead><tr><th>Time</th><th>User</th><th>Action</th><th>Resource</th><th>Details</th></tr></thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.log_id}>
                  <td className="mono" style={{ fontSize: 12 }}>{new Date(l.created_at).toLocaleString()}</td>
                  <td className="mono">{l.user_id ?? "—"}</td>
                  <td><span className="badge badge-teal">{l.action}</span></td>
                  <td className="mono" style={{ fontSize: 12 }}>{l.resource_type ? `${l.resource_type}#${l.resource_id}` : "—"}</td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)", maxWidth: 320, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {l.details && Object.keys(l.details).length ? JSON.stringify(l.details) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
