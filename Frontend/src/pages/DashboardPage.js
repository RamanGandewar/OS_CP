import React, { useEffect, useState } from "react";
import { Alert, Toast, ToastContainer } from "react-bootstrap";

import IntegrationDashboard from "../components/integration/Dashboard";
import { dashboardApi, healthApi } from "../utils/api";

function DashboardPage({ theme, setTheme }) {
  const [snapshot, setSnapshot] = useState(null);
  const [previousSnapshot, setPreviousSnapshot] = useState(null);
  const [error, setError] = useState("");
  const [isLive, setIsLive] = useState(true);
  const [health, setHealth] = useState(null);
  const [notifications, setNotifications] = useState([]);

  const addNotification = (title, body, variant = "info") => {
    const id = `${Date.now()}-${Math.random()}`;
    setNotifications((current) => [...current, { id, title, body, variant }].slice(-4));
  };

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
        if (!isLive) {
          addNotification("Connection Restored", "Dashboard polling is live again.", "success");
        }
        setIsLive(true);
      })
      .catch(() => {
        setHealth(null);
        if (isLive) {
          addNotification("Backend Offline", "Health checks are failing. Showing offline state.", "danger");
        }
        setIsLive(false);
      });
  };

  useEffect(() => {
    if (!snapshot || !previousSnapshot) {
      return;
    }

    const previousOverview = previousSnapshot.overview || {};
    const currentOverview = snapshot.overview || {};

    if ((currentOverview.task_queue_size || 0) !== (previousOverview.task_queue_size || 0)) {
      addNotification(
        "Task Queue Updated",
        `Queue changed from ${previousOverview.task_queue_size || 0} to ${currentOverview.task_queue_size || 0}.`,
        "info"
      );
    }

    if (snapshot.deadlock?.visualization?.deadlock && !previousSnapshot.deadlock?.visualization?.deadlock) {
      addNotification("Deadlock Alert", "A deadlock has been detected in the current resource graph.", "danger");
    }

    if ((currentOverview.thread_count || 0) > (previousOverview.thread_count || 0)) {
      addNotification("Thread Activity", "New thread activity was detected.", "success");
    }
  }, [snapshot, previousSnapshot]);

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

  const exportCsv = () => {
    window.open("http://127.0.0.1:5000/api/dashboard/export/csv", "_blank", "noopener,noreferrer");
  };

  const exportReport = () => {
    window.open("http://127.0.0.1:5000/api/dashboard/report", "_blank", "noopener,noreferrer");
  };

  return (
    <div>
      {error && <Alert variant="warning">{error}</Alert>}
      <ToastContainer position="top-end" className="p-3">
        {notifications.map((notification) => (
          <Toast
            key={notification.id}
            bg={notification.variant}
            onClose={() => setNotifications((current) => current.filter((item) => item.id !== notification.id))}
            delay={3200}
            autohide
          >
            <Toast.Header closeButton>
              <strong className="me-auto">{notification.title}</strong>
            </Toast.Header>
            <Toast.Body className={notification.variant === "danger" ? "text-white" : ""}>{notification.body}</Toast.Body>
          </Toast>
        ))}
      </ToastContainer>
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
