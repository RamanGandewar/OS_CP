import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

function ProcessMonitor({ snapshot }) {
  const processes = snapshot?.processes?.processes || [];
  const logs = snapshot?.processes?.logs || [];
  const stateCounts = snapshot?.processes?.state_counts || {};

  return (
    <Row className="g-4">
      <Col lg={8}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Active Processes</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>PID</th>
                    <th>User</th>
                    <th>State</th>
                    <th>Priority</th>
                    <th>CPU Time</th>
                    <th>Parent</th>
                  </tr>
                </thead>
                <tbody>
                  {processes.map((process) => (
                    <tr key={process.pid}>
                      <td>{process.pid}</td>
                      <td>{process.username}</td>
                      <td>{process.state}</td>
                      <td>{process.priority}</td>
                      <td>{process.cpu_time}</td>
                      <td>{process.parent_pid ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={4}>
        <Card className="shadow-sm border-0 mb-4">
          <Card.Body>
            <h4 className="mb-3">Process States</h4>
            <div className="small">
              {Object.entries(stateCounts).map(([state, count]) => (
                <div key={state}>{state}: {count}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Timeline</h4>
            <div className="small dashboard-scroll">
              {logs.map((log) => (
                <div key={log.id}>{log.logged_at}: PID {log.pid} {log.previous_state || "START"} -> {log.new_state}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default ProcessMonitor;
