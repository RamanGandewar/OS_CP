import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import CustomersPage from "./pages/CustomersPage";
import DashboardPage from "./pages/DashboardPage";
import EnquiriesPage from "./pages/EnquiriesPage";
import InvoicesPage from "./pages/InvoicesPage";
import OrdersPage from "./pages/OrdersPage";
import ProcessMonitorPage from "./pages/ProcessMonitorPage";
import QuotationsPage from "./pages/QuotationsPage";
import ReportsPage from "./pages/ReportsPage";
import SchedulerDashboardPage from "./pages/SchedulerDashboardPage";
import ThreadMonitorPage from "./pages/ThreadMonitorPage";
import DeadlockMonitorPage from "./pages/DeadlockMonitorPage";
import MemoryMonitorPage from "./pages/MemoryMonitorPage";
import DiskSchedulerMonitorPage from "./pages/DiskSchedulerMonitorPage";
import SyncMonitorPage from "./pages/SyncMonitorPage";

function App() {
  const user = { username: "Demo User", role: "admin" };

  return (
    <Routes>
      <Route path="/" element={<Layout user={user} />}>
        <Route index element={<DashboardPage />} />
        <Route path="customers" element={<CustomersPage />} />
        <Route path="enquiries" element={<EnquiriesPage />} />
        <Route path="quotations" element={<QuotationsPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="invoices" element={<InvoicesPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="process-monitor" element={<ProcessMonitorPage user={user} />} />
        <Route path="scheduler" element={<SchedulerDashboardPage />} />
        <Route path="thread-monitor" element={<ThreadMonitorPage />} />
        <Route path="sync-monitor" element={<SyncMonitorPage />} />
        <Route path="deadlock-monitor" element={<DeadlockMonitorPage />} />
        <Route path="memory-monitor" element={<MemoryMonitorPage />} />
        <Route path="io-monitor" element={<DiskSchedulerMonitorPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
