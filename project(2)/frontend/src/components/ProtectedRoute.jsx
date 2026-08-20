import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Layout from "./Layout";

export default function ProtectedRoute({ children, roles }) {
  const { user, token } = useAuth();
  if (!token || !user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) {
    return (
      <Layout>
        <div className="empty-state">
          <h2>403 — Access restricted</h2>
          <p>Your role ({user.role}) does not have permission to view this page.</p>
        </div>
      </Layout>
    );
  }
  return <Layout>{children}</Layout>;
}
