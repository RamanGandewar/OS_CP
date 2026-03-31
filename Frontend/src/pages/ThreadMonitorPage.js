import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Row, Table } from "react-bootstrap";

import { threadApi } from "../utils/api";

function ThreadMonitorPage() {
  const [monitor, setMonitor] = useState({ threads: [], status_counts: {}, thread_pool_utilization: {} });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadMonitor = () => {
    threadApi
      .monitor()
      .then((response) => {
        setMonitor(response.data);
        setError("");
      })
      .catch(() => {
        setMonitor({ threads: [], status_counts: {}, thread_pool_utilization: {} });
        setError("Thread monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    loadMonitor();
    const timer = window.setInterval(loadMonitor, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const runReportThread = async () => {
    try {
      const response = await threadApi.reportJob({ duration: 3, report: "thread-demo" });
      setMessage(`Report worker thread created: ${response.data.thread_name}`);
      setError("");
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Report thread could not be started.");
    }
  };

  const runValidationThread = async () => {
    try {
      const response = await threadApi.validationJob({ source: "manual-validation" });
      setMessage(`Validation worker thread created: ${response.data.thread_name}`);
      setError("");
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Validation thread could not be started.");
    }
  };

  const runSyncThread = async () => {
    try {
      const response = await threadApi.syncJob({ source: "manual-sync" });
      setMessage(`Sync worker thread created: ${response.data.thread_name}`);
      setError("");
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Sync thread could not be started.");
    }
  };

  return (
    <div className="monitor-page">
      <div className="monitor-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Thread Monitor</h1>
          <p className="text-muted mb-0">Tracks daemon, worker, timer, and application threads with thread-safe monitoring.</p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="primary" onClick={runReportThread}>Start Report Thread</Button>
          <Button variant="outline-primary" onClick={runValidationThread}>Start Validation Thread</Button>
          <Button variant="outline-secondary" onClick={runSyncThread}>Start Sync Thread</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col md={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <p className="text-muted mb-2">Active Threads</p>
              <h2>{monitor.active_count || 0}</h2>
              <small>Total tracked: {monitor.total_count || 0}</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <p className="text-muted mb-2">Native Thread Count</p>
              <h2>{monitor.native_threads || 0}</h2>
              <small>Main + worker + daemon activity inside the backend process.</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <p className="text-muted mb-2">Thread Pool Utilization</p>
              <h2>{monitor.thread_pool_utilization?.utilization_percent || 0}%</h2>
              <small>
                {monitor.thread_pool_utilization?.active_workers || 0} / {monitor.thread_pool_utilization?.max_workers || 10} workers active
              </small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        <Col xl={8}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Active Threads List</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Thread ID</th>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Runtime</th>
                      <th>CPU Time</th>
                      <th>Memory Used</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.threads.map((thread) => (
                      <tr key={`${thread.thread_id}-${thread.created_at}`}>
                        <td>{thread.thread_id}</td>
                        <td>{thread.thread_name}</td>
                        <td>{thread.thread_type}</td>
                        <td>{thread.status}</td>
                        <td>{thread.runtime_seconds}s</td>
                        <td>{thread.cpu_time}s</td>
                        <td>{thread.memory_used} MB</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col xl={4}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Status Distribution</h4>
              <div className="small text-muted">
                {Object.entries(monitor.status_counts || {}).map(([status, count]) => (
                  <div key={status}>{status}: {count}</div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ThreadMonitorPage;
