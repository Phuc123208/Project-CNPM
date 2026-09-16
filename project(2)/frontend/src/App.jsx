import React, { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Loading from "./components/Loading";

const AuthPage = lazy(() => import("./pages/AuthPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const DatasetsPage = lazy(() => import("./pages/DatasetsPage"));
const DatasetDetailPage = lazy(() => import("./pages/DatasetDetailPage"));
const AnalysisPage = lazy(() => import("./pages/AnalysisPage"));
const ExperimentsPage = lazy(() => import("./pages/ExperimentsPage"));
const ExperimentDetailPage = lazy(() => import("./pages/ExperimentDetailPage"));
const ReportsPage = lazy(() => import("./pages/ReportsPage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));
const AuditPage = lazy(() => import("./pages/AuditPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));

export default function App() {
  return (
    <Suspense fallback={<Loading />}>
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
    </Suspense>
  );
}
