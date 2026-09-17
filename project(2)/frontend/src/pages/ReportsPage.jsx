import React, { useEffect, useState } from "react";
import client from "../api/client";
import Loading from "../components/Loading";

const API_ORIGIN = (import.meta.env.VITE_API_URL || "http://localhost:9999/api").replace(/\/api$/, "");

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    client.get("/reports").then((res) => {
      if (active) setReports(res.data.data);
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, []);

  const download = async (report) => {
    const token = localStorage.getItem("utap_token");
    const res = await fetch(`${API_ORIGIN}${report.download_url}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${report.report_name}.${report.format === "excel" ? "xlsx" : "pdf"}`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Module 6</span>
          <h1>Reports</h1>
          <p className="subtitle">Traffic analysis, forecast and experiment reports (PDF / Excel).</p>
        </div>
      </div>

      <div className="card">
        {loading ? <Loading /> : reports.length === 0 ? (
          <div className="empty-state">
            No reports yet. Generate one from a dataset's Analysis page or an Experiment's detail page.
          </div>
        ) : (
          <table>
            <thead><tr><th>Report</th><th>Format</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.report_id}>
                  <td>{r.report_name}</td>
                  <td><span className="badge badge-grey">{r.format.toUpperCase()}</span></td>
                  <td className="mono" style={{ fontSize: 12 }}>{new Date(r.created_at).toLocaleString()}</td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => download(r)}>Download</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
