import React, { useEffect, useState } from "react";
import { Alert } from "react-bootstrap";

import IntegrationDashboard from "../components/integration/Dashboard";
import { dashboardApi, healthApi } from "../utils/api";

function DashboardPage() {
  const [snapshot, setSnapshot] = useState(null);
  const [previousSnapshot, setPreviousSnapshot] = useState(null);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState("light");
  const [isLive, setIsLive] = useState(true);
  const [health, setHealth] = useState(null);

  const loadSnapshot = () => {
    dashboardApi
      .snapshot()
      .then((response) => {
        setPreviousSnapshot(snapshot);
        setSnapshot(response.data);
        setError("");
        setIsLive(true);
      })
      .catch(() => {
        setError("Backend is not reachable right now. Start the API and refresh.");
        setIsLive(false);
      });
  };

  const loadHealth = () => {
    healthApi
      .check()
      .then((response) => {
        setHealth(response.data);
        setIsLive(true);
      })
      .catch(() => {
        setHealth(null);
        setIsLive(false);
      });
  };

  useEffect(() => {
    loadSnapshot();
    loadHealth();
    const snapshotTimer = window.setInterval(loadSnapshot, 2000);
    const healthTimer = window.setInterval(loadHealth, 10000);
    return () => {
      window.clearInterval(snapshotTimer);
      window.clearInterval(healthTimer);
    };
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
          previousSnapshot={previousSnapshot}
          health={health}
          isLive={isLive}
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
