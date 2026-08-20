import React, { useEffect, useState } from "react";
import client from "../api/client";
import Loading from "../components/Loading";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "student" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await client.get("/users");
      setUsers(res.data.data);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const createUser = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await client.post("/users", form);
      setShowCreate(false);
      setForm({ full_name: "", email: "", password: "", role: "student" });
      load();
    } catch (err) {
      setError(err?.response?.data?.message || "Could not create user");
    } finally { setBusy(false); }
  };

  const changeRole = async (userId, role) => {
    await client.patch(`/users/${userId}/role`, { role });
    load();
  };

  const removeUser = async (userId) => {
    if (!window.confirm("Delete this user account?")) return;
    await client.delete(`/users/${userId}`);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Admin</span>
          <h1>User Management</h1>
          <p className="subtitle">Create accounts and manage role-based access control.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate((s) => !s)}>
          {showCreate ? "Cancel" : "+ New user"}
        </button>
      </div>

      {showCreate && (
        <div className="card">
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={createUser}>
            <div className="grid grid-4">
              <div className="form-field">
                <label>Full name</label>
                <input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
              </div>
              <div className="form-field">
                <label>Email</label>
                <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="form-field">
                <label>Password</label>
                <input type="password" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              </div>
              <div className="form-field">
                <label>Role</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  <option value="student">Student</option>
                  <option value="analyst">Analyst</option>
                  <option value="researcher">Researcher</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
            </div>
            <button className="btn btn-primary" disabled={busy}>{busy ? "Creating…" : "Create user"}</button>
          </form>
        </div>
      )}

      <div className="card">
        {loading ? <Loading /> : (
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th></th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.user_id}>
                  <td>{u.full_name}</td>
                  <td className="mono">{u.email}</td>
                  <td>
                    <select value={u.role} onChange={(e) => changeRole(u.user_id, e.target.value)}>
                      <option value="student">student</option>
                      <option value="analyst">analyst</option>
                      <option value="researcher">researcher</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td className="mono" style={{ fontSize: 12 }}>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td><button className="btn btn-danger btn-sm" onClick={() => removeUser(u.user_id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
