import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import DatasetsPage from "./pages/DatasetsPage";
import DatasetDetailPage from "./pages/DatasetDetailPage";
import AnalysisPage from "./pages/AnalysisPage";
import ExperimentsPage from "./pages/ExperimentsPage";
import ExperimentDetailPage from "./pages/ExperimentDetailPage";
import ReportsPage from "./pages/ReportsPage";
import UsersPage from "./pages/UsersPage";
import AuditPage from "./pages/AuditPage";
import ProfilePage from "./pages/ProfilePage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />

      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />

      <Route path="/datasets" element={<ProtectedRoute><DatasetsPage /></ProtectedRoute>} />
      <Route path="/datasets/:datasetId" element={<ProtectedRoute><DatasetDetailPage /></ProtectedRoute>} />

      <Route path="/analysis" element={<ProtectedRoute><AnalysisPage /></ProtectedRoute>} />

      <Route path="/experiments" element={<ProtectedRoute><ExperimentsPage /></ProtectedRoute>} />
      <Route path="/experiments/:experimentId" element={<ProtectedRoute><ExperimentDetailPage /></ProtectedRoute>} />

      <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />

      <Route path="/users" element={<ProtectedRoute roles={["admin"]}><UsersPage /></ProtectedRoute>} />
      <Route path="/audit" element={<ProtectedRoute roles={["admin"]}><AuditPage /></ProtectedRoute>} />

      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
