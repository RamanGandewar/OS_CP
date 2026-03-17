import React from "react";
import { Alert, Card, Col, Row, Table } from "react-bootstrap";

function DeadlockView({ snapshot }) {
  const deadlock = snapshot?.deadlock || {};
  const viz = deadlock.visualization || {};

  return (
    <Row className="g-4">
      <Col lg={6}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Deadlock Status</h4>
            {viz.deadlock ? (
              <Alert variant="danger">Deadlock detected involving {viz.processes?.join(", ")}</Alert>
            ) : (
              <Alert variant="success">No deadlock detected.</Alert>
            )}
            <div className="small">
              <div>Processes: {viz.processes?.join(", ") || "-"}</div>
              <div>Resources: {viz.resources?.join(", ") || "-"}</div>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={6}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Safe Sequence Context</h4>
            <div className="small">
              {deadlock.resources?.map((resource) => (
                <div key={resource.id}>{resource.resource_name}: {resource.available_instances}/{resource.total_instances}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={12}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Recovery Actions Log</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Detected</th>
                    <th>Processes</th>
                    <th>Resources</th>
                    <th>Resolution</th>
                    <th>Resolved</th>
                  </tr>
                </thead>
                <tbody>
                  {(deadlock.events || []).map((event) => (
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
      </Col>
    </Row>
  );
}

export default DeadlockView;
