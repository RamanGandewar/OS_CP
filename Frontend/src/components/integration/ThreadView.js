import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

function ThreadView({ snapshot }) {
  const threads = snapshot?.threads?.threads || [];
  const pool = snapshot?.threads?.thread_pool_utilization || {};

  return (
    <Row className="g-4">
      <Col lg={8}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Active Threads</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Runtime</th>
                    <th>CPU</th>
                    <th>Memory</th>
                  </tr>
                </thead>
                <tbody>
                  {threads.map((thread) => (
                    <tr key={thread.id}>
                      <td>{thread.thread_name}</td>
                      <td>{thread.thread_type}</td>
                      <td>{thread.status}</td>
                      <td>{thread.runtime_seconds}</td>
                      <td>{thread.cpu_time}</td>
                      <td>{thread.memory_used}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={4}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Thread Pool</h4>
            <div className="small">
              <div>Active workers: {pool.active_workers || 0}</div>
              <div>Max workers: {pool.max_workers || 0}</div>
              <div>Utilization: {pool.utilization_percent || 0}%</div>
              <div>Native threads: {snapshot?.threads?.native_threads || 0}</div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default ThreadView;
