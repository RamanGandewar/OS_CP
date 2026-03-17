import React, { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Row, Table } from "react-bootstrap";

import { processApi, reportsApi } from "../utils/api";

function buildPieGradient(stateCounts) {
  const palette = {
    NEW: "#0d6efd",
    READY: "#20c997",
    RUNNING: "#fd7e14",
    WAITING: "#ffc107",
    TERMINATED: "#6c757d"
  };
  const entries = Object.entries(stateCounts);
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  if (!total) {
    return "conic-gradient(#dee2e6 0deg 360deg)";
  }

  let angle = 0;
  const stops = entries.map(([state, count]) => {
    const slice = (count / total) * 360;
    const start = angle;
    angle += slice;
    return `${palette[state] || "#adb5bd"} ${start}deg ${angle}deg`;
  });
  return `conic-gradient(${stops.join(", ")})`;
}

function ProcessMonitorPage({ user }) {
  const [monitor, setMonitor] = useState({ processes: [], logs: [], state_counts: {}, active_count: 0, total_count: 0 });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadMonitor = () => {
    processApi
      .monitor()
      .then((response) => {
        setMonitor(response.data);
        setError("");
      })
      .catch(() => {
        setMonitor({ processes: [], logs: [], state_counts: {}, active_count: 0, total_count: 0 });
        setError("Process monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    loadMonitor();
    const timer = window.setInterval(loadMonitor, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const pieStyle = useMemo(
    () => ({
      background: buildPieGradient(monitor.state_counts || {}),
    }),
    [monitor.state_counts]
  );

  const triggerReportProcess = async () => {
    const response = await reportsApi.generate({
      report_type: "phase-2-process-report",
      scope: "dashboard",
      duration: 3,
      wait: false
    });
    setMessage(`Report process created with PID ${response.data.pid}`);
    loadMonitor();
  };

  const triggerEmailProcess = async () => {
    const response = await processApi.createBackgroundTask({
      task_type: "email",
      operation: "manual-email-notification",
      duration: 2,
      priority: 4
    });
    setMessage(`Email child process created with PID ${response.data.pid}`);
    loadMonitor();
  };

  return (
    <div>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Process Monitor</h1>
          <p className="text-muted mb-0">Live OS process tracking for the CRM. Current user: {user?.username}</p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="primary" onClick={triggerReportProcess}>Run Report Process</Button>
          <Button variant="outline-primary" onClick={triggerEmailProcess}>Fork Email Process</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col md={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <p className="text-muted mb-2">Active Processes</p>
              <h2>{monitor.active_count}</h2>
              <small>Total tracked: {monitor.total_count}</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <p className="text-muted mb-2">Your Session PID</p>
              <h2>{monitor.processes.find((item) => item.username === user?.username && item.task_type === "session" && item.state !== "TERMINATED")?.pid || "N/A"}</h2>
              <small>One login creates one session process.</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex align-items-center justify-content-between gap-3">
              <div>
                <p className="text-muted mb-2">State Pie Chart</p>
                <div className="small text-muted">
                  {Object.entries(monitor.state_counts || {}).map(([state, count]) => (
                    <div key={state}>{state}: {count}</div>
                  ))}
                </div>
              </div>
              <div className="process-pie" style={pieStyle} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        <Col xl={8}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Tracked Processes</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>PID</th>
                      <th>User</th>
                      <th>Type</th>
                      <th>State</th>
                      <th>Priority</th>
                      <th>CPU Time</th>
                      <th>Parent PID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.processes.map((process) => (
                      <tr key={`${process.pid}-${process.created_at}`}>
                        <td>{process.pid}</td>
                        <td>{process.username}</td>
                        <td>{process.task_type}</td>
                        <td>{process.state}</td>
                        <td>{process.priority}</td>
                        <td>{process.cpu_time}s</td>
                        <td>{process.parent_pid || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col xl={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">State Transition Log</h4>
              <div className="process-log-list">
                {monitor.logs.map((log) => (
                  <div key={log.id} className="process-log-item">
                    <strong>PID {log.pid}</strong>
                    <div>{log.previous_state || "START"} to {log.new_state}</div>
                    <small>{log.message}</small>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ProcessMonitorPage;
