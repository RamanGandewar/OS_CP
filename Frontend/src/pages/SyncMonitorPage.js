import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Row, Table } from "react-bootstrap";

import { syncApi } from "../utils/api";

function SyncMonitorPage() {
  const [monitor, setMonitor] = useState({ active_locks: [], lock_queue: [], contention_counts: {} });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [raceDemo, setRaceDemo] = useState(null);

  const loadMonitor = () => {
    syncApi
      .monitor()
      .then((response) => {
        setMonitor(response.data);
        setError("");
      })
      .catch(() => {
        setMonitor({ active_locks: [], lock_queue: [], contention_counts: {} });
        setError("Synchronization monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    loadMonitor();
    const timer = window.setInterval(loadMonitor, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const runMutexScenario = async () => {
    try {
      const response = await syncApi.quotationEdit({ quotation_id: 123, user_id: 1, data: { amendment: "price change" } });
      setMessage(response.data.message);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Mutex scenario failed.");
    }
  };

  const runSemaphoreScenario = async () => {
    try {
      const response = await syncApi.reserveInventory({ product_id: "PRODUCT_X", user_id: 2, units: 1 });
      setMessage(response.data.message || `Remaining stock: ${response.data.remaining_stock}`);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Semaphore scenario failed.");
    }
  };

  const runReaderWriterScenario = async () => {
    try {
      const reader = await syncApi.readReport({ user_id: 10, report_id: "monthly-sales" });
      const writer = await syncApi.writeReport({ user_id: 99, report_id: "monthly-sales" });
      setMessage(`Reader: ${reader.data.mode}, Writer: ${writer.data.mode}`);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Reader-writer scenario failed.");
    }
  };

  const runProducerConsumerScenario = async () => {
    try {
      await syncApi.produce({ enquiry: `Enquiry-${Date.now()}` });
      const response = await syncApi.consume();
      setMessage(response.data.success ? `Consumed ${response.data.enquiry}` : response.data.message);
    } catch (err) {
      setError(err.response?.data?.error || "Producer-consumer scenario failed.");
    }
  };

  const runRaceDemo = async () => {
    try {
      const response = await syncApi.raceDemo();
      setRaceDemo(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "Race condition demo failed.");
    }
  };

  return (
    <div className="monitor-page">
      <div className="monitor-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Synchronization Monitor</h1>
          <p className="text-muted mb-0">Mutex, semaphore, reader-writer, producer-consumer, and race-condition visibility in one dashboard.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <Button variant="primary" onClick={runMutexScenario}>Run Mutex</Button>
          <Button variant="outline-primary" onClick={runSemaphoreScenario}>Run Semaphore</Button>
          <Button variant="outline-secondary" onClick={runReaderWriterScenario}>Run Reader/Writer</Button>
          <Button variant="outline-dark" onClick={runProducerConsumerScenario}>Run Producer/Consumer</Button>
          <Button variant="success" onClick={runRaceDemo}>Run Race Demo</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col lg={7}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Active Locks</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Resource</th>
                      <th>Resource ID</th>
                      <th>Holder User</th>
                      <th>Process</th>
                      <th>Lock Type</th>
                      <th>Acquired</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.active_locks.map((lock) => (
                      <tr key={`${lock.resource_type}-${lock.id}`}>
                        <td>{lock.resource_type}</td>
                        <td>{lock.resource_id}</td>
                        <td>{lock.holder_user_id ?? "-"}</td>
                        <td>{lock.holder_process_id ?? "-"}</td>
                        <td>{lock.lock_type}</td>
                        <td>{lock.acquired_at}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={5}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Lock Wait Queue</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Resource</th>
                      <th>Resource ID</th>
                      <th>User</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.lock_queue.map((entry) => (
                      <tr key={entry.id}>
                        <td>{entry.resource_type}</td>
                        <td>{entry.resource_id}</td>
                        <td>{entry.waiting_user_id ?? "-"}</td>
                        <td>{entry.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        <Col lg={6}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Contention Analysis</h4>
              <div className="small text-muted">
                {Object.entries(monitor.contention_counts || {}).map(([resource, count]) => (
                  <div key={resource}>{resource}: {count}</div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Race Condition Demo</h4>
              {raceDemo ? (
                <div className="small">
                  <div>Before Fix: expected {raceDemo.before_fix.expected}, actual {raceDemo.before_fix.actual}</div>
                  <div>After Fix: expected {raceDemo.after_fix.expected}, actual {raceDemo.after_fix.actual}</div>
                </div>
              ) : (
                <p className="text-muted mb-0">Run the race demo to compare unsynchronized vs synchronized access.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default SyncMonitorPage;
