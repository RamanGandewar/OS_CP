import React from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", tag: "DB" },
  { to: "/customers", label: "Customers", tag: "CU" },
  { to: "/enquiries", label: "Enquiries", tag: "EN" },
  { to: "/quotations", label: "Quotations", tag: "QT" },
  { to: "/orders", label: "Sales Orders", tag: "SO" },
  { to: "/invoices", label: "Invoices", tag: "IN" },
  { to: "/reports", label: "Reports", tag: "RP" },
  { to: "/process-monitor", label: "Process Monitor", tag: "PM" },
  { to: "/scheduler", label: "CPU Scheduler", tag: "CS" },
  { to: "/thread-monitor", label: "Thread Monitor", tag: "TM" },
  { to: "/sync-monitor", label: "Sync Monitor", tag: "SM" },
  { to: "/deadlock-monitor", label: "Deadlock Monitor", tag: "DM" },
  { to: "/memory-monitor", label: "Memory Monitor", tag: "MM" },
  { to: "/io-monitor", label: "I/O Monitor", tag: "IO" },
];

function buildTitle(pathname) {
  const current = navItems.find((item) => item.to === pathname);
  return current?.label || "SalesCRM";
}

function Layout({ user }) {
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="crm-sidebar">
        <div className="crm-sidebar-top">
          <NavLink className="crm-brand" to="/">
            <span className="crm-brand-mark">SC</span>
            <span className="crm-brand-copy">
              <span className="crm-brand-title">SalesCRM</span>
              <span className="crm-brand-version">v1.0 | OS Edition</span>
              <span className="crm-brand-subtitle">OPERATING SYSTEMS ENABLED CRM</span>
            </span>
          </NavLink>
          <div className="crm-sidebar-divider" />
          <nav className="crm-side-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) => `crm-side-link ${isActive ? "active" : ""}`}
              >
                <span className="crm-side-link-tag">{item.tag}</span>
                <span className="crm-side-link-label">{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="crm-sidebar-foot">
          <div className="crm-user-chip">
            <span className="crm-user-label">Signed in as</span>
            <span className="crm-user-name">{user?.username}</span>
            <span className="crm-user-role">{user?.role}</span>
          </div>
        </div>
      </aside>

      <main className="crm-main-shell">
        <header className="crm-main-header">
          <div>
            <div className="crm-page-eyebrow">SalesCRM Workspace</div>
            <h1 className="crm-page-title">{buildTitle(location.pathname)}</h1>
          </div>
        </header>

        <section className="crm-content-panel">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default Layout;
