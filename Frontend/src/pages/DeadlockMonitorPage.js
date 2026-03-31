import React, { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Row, Table } from "react-bootstrap";

import { deadlockApi } from "../utils/api";

function DeadlockMonitorPage() {
  const [state, setState] = useState({ resources: [], allocations: [], events: [], visualization: { deadlock: false, processes: [], resources: [] } });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [bankerResult, setBankerResult] = useState(null);
  const [graphVersion, setGraphVersion] = useState(Date.now());

  const loadState = () => {
    deadlockApi
      .state()
      .then((response) => {
        setState(response.data);
        setError("");
      })
      .catch(() => {
        setState({ resources: [], allocations: [], events: [], visualization: { deadlock: false, processes: [], resources: [] } });
        setError("Deadlock monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    deadlockApi.initResources().finally(loadState);
    const timer = window.setInterval(loadState, 4000);
    return () => window.clearInterval(timer);
  }, []);

  const allocationSummary = useMemo(
    () =>
      state.allocations.reduce((accumulator, item) => {
        accumulator[item.process_id] = accumulator[item.process_id] || [];
        accumulator[item.process_id].push(`${item.resource_name} (A:${item.allocated_count}, R:${item.requested_count})`);
        return accumulator;
      }, {}),
    [state.allocations]
  );

  const runScenario = async () => {
    try {
      const response = await deadlockApi.createScenario();
      setMessage(response.data.message);
      setBankerResult(null);
      setGraphVersion(Date.now());
      loadState();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to create the deadlock scenario.");
    }
  };

  const runDetection = async () => {
    try {
      const response = await deadlockApi.detect();
      setState((current) => ({ ...current, visualization: response.data }));
      setMessage(response.data.deadlock ? `Deadlock detected involving ${response.data.processes.join(", ")}` : "No deadlock detected.");
      setGraphVersion(Date.now());
    } catch (err) {
      setError(err.response?.data?.error || "Deadlock detection failed.");
    }
  };

  const runBanker = async () => {
    try {
      const response = await deadlockApi.bankerCheck({
        process_id: "P3",
        request: { R1_DB: 1, R4_PDF: 1 },
      });
      setBankerResult(response.data);
      setMessage(response.data.granted ? "Banker's algorithm approved the request." : response.data.reason);
    } catch (err) {
      setError(err.response?.data?.error || "Banker's algorithm check failed.");
    }
  };

  const runRecovery = async () => {
    try {
      const response = await deadlockApi.recover({
        processes: state.visualization?.processes || [],
      });
      setMessage(response.data.recovered ? `Recovered by rolling back ${response.data.result.victim_process}` : response.data.message);
      setGraphVersion(Date.now());
      loadState();
    } catch (err) {
      setError(err.response?.data?.error || "Deadlock recovery failed.");
    }
  };

  const resetDemo = async () => {
    try {
      await deadlockApi.reset();
      setBankerResult(null);
      setMessage("Deadlock state reset successfully.");
      setGraphVersion(Date.now());
      loadState();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to reset deadlock state.");
    }
  };

  return (
    <div className="monitor-page">
      <div className="monitor-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Deadlock Monitor</h1>
          <p className="text-muted mb-0">Resource allocation graph, cycle detection, Banker&apos;s safety checks, and recovery actions for CRM resources.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <Button variant="primary" onClick={runScenario}>Create Deadlock</Button>
          <Button variant="outline-primary" onClick={runDetection}>Detect</Button>
          <Button variant="outline-secondary" onClick={runBanker}>Run Banker</Button>
          <Button variant="outline-danger" onClick={runRecovery}>Recover</Button>
          <Button variant="dark" onClick={resetDemo}>Reset</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <h4 className="mb-3">Detection Status</h4>
              <div className="display-6">{state.visualization?.deadlock ? "DEADLOCK" : "SAFE"}</div>
              <div className="small text-muted mt-2">Processes: {(state.visualization?.processes || []).join(", ") || "-"}</div>
              <div className="small text-muted">Resources: {(state.visualization?.resources || []).join(", ") || "-"}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <h4 className="mb-3">Available Resources</h4>
              <div className="small">
                {state.resources.map((resource) => (
                  <div key={resource.id}>
                    {resource.resource_name}: {resource.available_instances} / {resource.total_instances}
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <h4 className="mb-3">Banker&apos;s Result</h4>
              {bankerResult ? (
                <div className="small">
                  <div>Granted: {bankerResult.granted ? "Yes" : "No"}</div>
                  <div>Safe State: {bankerResult.current_safe_state ? "Yes" : "No"}</div>
                  <div>Safe Sequence: {(bankerResult.safe_sequence || bankerResult.current_safe_sequence || []).join(" -> ") || "-"}</div>
                </div>
              ) : (
                <p className="text-muted mb-0">Run Banker&apos;s algorithm to evaluate whether a resource request is safe.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={7}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Resource Allocation State</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Process</th>
                      <th>Allocations / Requests</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(allocationSummary).map(([processId, resources]) => (
                      <tr key={processId}>
                        <td>{processId}</td>
                        <td>{resources.join(", ")}</td>
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
              <h4 className="mb-3">Resource Allocation Graph</h4>
              <img
                alt="Resource allocation graph"
                className="img-fluid rounded border"
                src={deadlockApi.graphUrl(graphVersion)}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm monitor-panel-card">
        <Card.Body>
          <h4 className="mb-3">Deadlock Events</h4>
          <div className="table-responsive">
            <Table striped bordered hover>
              <thead className="table-dark">
                <tr>
                  <th>Detected At</th>
                  <th>Processes</th>
                  <th>Resources</th>
                  <th>Resolution</th>
                  <th>Resolved At</th>
                </tr>
              </thead>
              <tbody>
                {state.events.map((event) => (
                  <tr key={event.id}>
                    <td>{event.detected_at}</td>
                    <td>{event.processes_involved}</td>
                    <td>{event.resources_involved}</td>
                    <td>{event.resolution_action || "Pending"}</td>
                    <td>{event.resolved_at || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
}

export default DeadlockMonitorPage;
