import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

function SyncView({ snapshot }) {
  const locks = snapshot?.synchronization?.active_locks || [];
  const queue = snapshot?.synchronization?.lock_queue || [];
  const contention = snapshot?.synchronization?.contention_counts || {};

  return (
    <Row className="g-4">
      <Col lg={7}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Active Locks</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Resource</th>
                    <th>ID</th>
                    <th>Holder</th>
                    <th>Type</th>
                    <th>Acquired</th>
                  </tr>
                </thead>
                <tbody>
                  {locks.map((lock) => (
                    <tr key={lock.id}>
                      <td>{lock.resource_type}</td>
                      <td>{lock.resource_id}</td>
                      <td>{lock.holder_user_id ?? "-"}</td>
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
        <Card className="shadow-sm border-0 mb-4">
          <Card.Body>
            <h4 className="mb-3">Lock Wait Queue</h4>
            <div className="small dashboard-scroll">
              {queue.map((entry) => (
                <div key={entry.id}>{entry.resource_type}:{entry.resource_id} waiting user {entry.waiting_user_id}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Contention Heatmap</h4>
            <div className="small">
              {Object.entries(contention).map(([resource, count]) => (
                <div key={resource}>{resource}: {count}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default SyncView;
