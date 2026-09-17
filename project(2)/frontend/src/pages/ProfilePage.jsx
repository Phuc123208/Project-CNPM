import React, { useState } from "react";
import { useAuth } from "../context/useAuth";
import client from "../api/client";

export default function ProfilePage() {
  const { user, refreshProfile, logout } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [msg, setMsg] = useState("");
  const [pw, setPw] = useState({ old_password: "", new_password: "" });
  const [pwMsg, setPwMsg] = useState("");

  const saveProfile = async (e) => {
    e.preventDefault();
    await client.put(`/users/${user.user_id}`, { full_name: fullName });
    await refreshProfile();
    setMsg("Profile updated.");
  };

  const changePassword = async (e) => {
    e.preventDefault();
    setPwMsg("");
    try {
      await client.post("/auth/change-password", pw);
      setPwMsg("Password changed successfully.");
      setPw({ old_password: "", new_password: "" });
    } catch (err) {
      setPwMsg(err?.response?.data?.message || "Could not change password");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="eyebrow">Account</span>
          <h1>My Profile</h1>
        </div>
        <button className="btn btn-secondary" onClick={logout}>Sign out</button>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>Profile information</h3>
          {msg && <div className="alert alert-success">{msg}</div>}
          <form onSubmit={saveProfile}>
            <div className="form-field">
              <label>Full name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="form-field">
              <label>Email</label>
              <input value={user?.email} disabled />
            </div>
            <div className="form-field">
              <label>Role</label>
              <input value={user?.role} disabled className="mono" />
            </div>
            <button className="btn btn-primary">Save changes</button>
          </form>
        </div>

        <div className="card">
          <h3>Change password</h3>
          {pwMsg && <div className={`alert ${pwMsg.includes("success") ? "alert-success" : "alert-error"}`}>{pwMsg}</div>}
          <form onSubmit={changePassword}>
            <div className="form-field">
              <label>Current password</label>
              <input type="password" required value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} />
            </div>
            <div className="form-field">
              <label>New password</label>
              <input type="password" required minLength={6} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
            </div>
            <button className="btn btn-primary">Update password</button>
          </form>
        </div>
      </div>
    </div>
  );
}
