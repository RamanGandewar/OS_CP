import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/customers", label: "Customers" },
  { to: "/enquiries", label: "Enquiries" },
  { to: "/quotations", label: "Quotations" },
  { to: "/orders", label: "Sales Orders" },
  { to: "/invoices", label: "Invoices" },
  { to: "/reports", label: "Reports" },
  { to: "/process-monitor", label: "Process Monitor" },
  { to: "/scheduler", label: "CPU Scheduler" },
  { to: "/thread-monitor", label: "Thread Monitor" },
  { to: "/sync-monitor", label: "Sync Monitor" },
  { to: "/deadlock-monitor", label: "Deadlock Monitor" },
  { to: "/memory-monitor", label: "Memory Monitor" },
  { to: "/io-monitor", label: "I/O Monitor" },
];

function Layout({ user }) {
  return (
    <div className="app-shell">
      <Navbar expand="xl" className="crm-navbar shadow-sm">
        <Container fluid className="crm-navbar-container">
          <Navbar.Brand className="crm-brand" as={NavLink} to="/">
            <span className="crm-brand-mark">SC</span>
            <span className="crm-brand-copy">
              <span className="crm-brand-title">SalesCRM</span>
              <span className="crm-brand-subtitle">Operating Systems Enabled CRM</span>
            </span>
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="main-nav" />
          <Navbar.Collapse id="main-nav">
            <Nav className="crm-nav-links me-auto">
              {navItems.map((item) => (
                <Nav.Link
                  key={item.to}
                  as={NavLink}
                  to={item.to}
                  end={item.to === "/"}
                  className="crm-nav-link"
                >
                  {item.label}
                </Nav.Link>
              ))}
            </Nav>
            <div className="crm-user-chip">
              <span className="crm-user-label">Signed in as</span>
              <span className="crm-user-name">{user?.username}</span>
            </div>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container fluid className="py-4">
        <Outlet />
      </Container>
    </div>
  );
}

export default Layout;
