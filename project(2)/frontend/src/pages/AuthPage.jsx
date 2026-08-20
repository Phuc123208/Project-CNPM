import React, { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = [
  { role: "admin", email: "admin@traffic.edu.vn", password: "Admin@123" },
  { role: "researcher", email: "researcher@traffic.edu.vn", password: "Research@123" },
  { role: "analyst", email: "analyst@traffic.edu.vn", password: "Analyst@123" },
  { role: "student", email: "student@traffic.edu.vn", password: "Student@123" },
];

export default function AuthPage() {
  const { login, register, token } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [regForm, setRegForm] = useState({ full_name: "", email: "", password: "", role: "student" });

  if (token) return <Navigate to="/dashboard" replace />;

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await login(loginForm.email, loginForm.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);
    try {
      await register(regForm);
      setSuccess("Account created. You can now log in.");
      setTab("login");
      setLoginForm({ email: regForm.email, password: "" });
    } catch (err) {
      setError(err?.response?.data?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (acc) => {
    setTab("login");
    setLoginForm({ email: acc.email, password: acc.password });
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-brand">Urban Traffic Analytics Platform</div>
        <h1>Sign in to the console</h1>
        <p className="subtitle" style={{ marginTop: 4, marginBottom: 20, color: "var(--text-muted)" }}>
          Traffic pattern analysis &amp; short-term congestion forecasting from UAV data
        </p>

        <div className="tabs">
          <div className={`tab ${tab === "login" ? "active" : ""}`} onClick={() => setTab("login")}>Login</div>
          <div className={`tab ${tab === "register" ? "active" : ""}`} onClick={() => setTab("register")}>Register</div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {tab === "login" ? (
          <form onSubmit={handleLogin}>
            <div className="form-field">
              <label>Email</label>
              <input type="email" required value={loginForm.email}
                     onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })} />
            </div>
            <div className="form-field">
              <label>Password</label>
              <input type="password" required value={loginForm.password}
                     onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} />
            </div>
            <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }} disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-field">
              <label>Full name</label>
              <input required value={regForm.full_name}
                     onChange={(e) => setRegForm({ ...regForm, full_name: e.target.value })} />
            </div>
            <div className="form-field">
              <label>Email</label>
              <input type="email" required value={regForm.email}
                     onChange={(e) => setRegForm({ ...regForm, email: e.target.value })} />
            </div>
            <div className="form-field">
              <label>Password</label>
              <input type="password" required minLength={6} value={regForm.password}
                     onChange={(e) => setRegForm({ ...regForm, password: e.target.value })} />
            </div>
            <div className="form-field">
              <label>Role</label>
              <select value={regForm.role} onChange={(e) => setRegForm({ ...regForm, role: e.target.value })}>
                <option value="student">Student</option>
                <option value="analyst">Analyst</option>
                <option value="researcher">Researcher</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
            <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }} disabled={loading}>
              {loading ? "Creating…" : "Create account"}
            </button>
          </form>
        )}

        <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
          <div className="mono" style={{ fontSize: 11, color: "var(--text-faint)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Demo accounts (one per role)
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {DEMO_ACCOUNTS.map((acc) => (
              <button key={acc.role} type="button" className="btn btn-secondary btn-sm"
                      onClick={() => fillDemo(acc)}>
                {acc.role}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
