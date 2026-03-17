import React, { useEffect, useState } from "react";
import { Alert } from "react-bootstrap";

import IntegrationDashboard from "../components/integration/Dashboard";
import { dashboardApi } from "../utils/api";

function DashboardPage() {
  const [snapshot, setSnapshot] = useState(null);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState("light");

  const loadSnapshot = () => {
    dashboardApi
      .snapshot()
      .then((response) => {
        setSnapshot(response.data);
        setError("");
      })
      .catch(() => {
        setSnapshot(null);
        setError("Backend is not reachable right now. Start the API and refresh.");
      });
  };

  useEffect(() => {
    loadSnapshot();
    const timer = window.setInterval(loadSnapshot, 2000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    document.body.classList.toggle("theme-dark", theme === "dark");
    document.body.classList.toggle("theme-light", theme === "light");
    return () => {
      document.body.classList.remove("theme-dark");
      document.body.classList.remove("theme-light");
    };
  }, [theme]);

  const exportCsv = () => {
    window.open("http://127.0.0.1:5000/api/dashboard/export/csv", "_blank", "noopener,noreferrer");
  };

  const exportReport = () => {
    window.open("http://127.0.0.1:5000/api/dashboard/report", "_blank", "noopener,noreferrer");
  };

  return (
    <div>
      {error && <Alert variant="warning">{error}</Alert>}
      {snapshot && (
        <IntegrationDashboard
          snapshot={snapshot}
          theme={theme}
          onRefresh={loadSnapshot}
          onExportCsv={exportCsv}
          onExportReport={exportReport}
          onToggleTheme={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
        />
      )}
    </div>
  );
}

export default DashboardPage;
