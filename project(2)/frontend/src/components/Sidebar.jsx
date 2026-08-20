import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ICONS = {
  dashboard: "◱",
  datasets: "▤",
  analysis: "◈",
  experiments: "⇅",
  reports: "▣",
  users: "◍",
  audit: "≡",
  profile: "●",
};

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: "dashboard", roles: ["admin", "researcher", "analyst", "student"] },
  { to: "/datasets", label: "Datasets", icon: "datasets", roles: ["admin", "researcher", "analyst", "student"] },
  { to: "/analysis", label: "Traffic Analysis", icon: "analysis", roles: ["admin", "researcher", "analyst", "student"] },
  { to: "/experiments", label: "Forecasting", icon: "experiments", roles: ["admin", "researcher", "analyst", "student"] },
  { to: "/reports", label: "Reports", icon: "reports", roles: ["admin", "researcher", "analyst", "student"] },
  { to: "/users", label: "User Management", icon: "users", roles: ["admin"] },
  { to: "/audit", label: "Audit Trail", icon: "audit", roles: ["admin"] },
];

export default function Sidebar() {
  const { user } = useAuth();
  const role = user?.role || "student";

  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>
        <div style={styles.brandMark}>UTA</div>
        <div>
          <div style={styles.brandTitle}>Urban Traffic</div>
          <div style={styles.brandSub}>Analytics Platform</div>
        </div>
      </div>

      <nav style={styles.nav}>
        {LINKS.filter((l) => l.roles.includes(role)).map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            style={({ isActive }) => ({
              ...styles.link,
              ...(isActive ? styles.linkActive : {}),
            })}
          >
            <span style={styles.icon}>{ICONS[l.icon]}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>

      <div style={styles.footer}>
        <NavLink to="/profile" style={({ isActive }) => ({ ...styles.link, ...(isActive ? styles.linkActive : {}) })}>
          <span style={styles.icon}>{ICONS.profile}</span>
          {user?.full_name || "Profile"}
        </NavLink>
        <div style={styles.roleTag}>{role}</div>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: 240,
    background: "var(--sidebar-bg)",
    color: "var(--sidebar-text)",
    display: "flex",
    flexDirection: "column",
    padding: "22px 16px",
    flexShrink: 0,
  },
  brand: { display: "flex", alignItems: "center", gap: 10, padding: "0 8px 24px" },
  brandMark: {
    width: 36, height: 36, borderRadius: 8, background: "var(--primary)",
    color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
    fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: 12,
  },
  brandTitle: { fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 14, color: "#fff" },
  brandSub: { fontSize: 10.5, color: "var(--sidebar-text-dim)", letterSpacing: "0.04em" },
  nav: { display: "flex", flexDirection: "column", gap: 2, flex: 1 },
  link: {
    display: "flex", alignItems: "center", gap: 10, padding: "9px 10px",
    borderRadius: 8, color: "var(--sidebar-text)", fontSize: 13, fontWeight: 500,
  },
  linkActive: { background: "rgba(255,255,255,0.08)", color: "#fff" },
  icon: { width: 18, textAlign: "center", opacity: 0.85 },
  footer: { borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 14, marginTop: 10 },
  roleTag: {
    fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase",
    letterSpacing: "0.08em", color: "var(--sidebar-text-dim)", padding: "4px 10px",
  },
};
