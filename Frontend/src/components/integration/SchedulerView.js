import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

function SchedulerView({ snapshot }) {
  const queue = snapshot?.scheduler?.queue || [];
  const comparisons = snapshot?.scheduler?.comparison?.comparisons || {};

  return (
    <Row className="g-4">
      <Col lg={7}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Current Task Queue</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Task</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Burst</th>
                    <th>Algorithm</th>
                  </tr>
                </thead>
                <tbody>
                  {queue.map((task) => (
                    <tr key={task.task_id}>
                      <td>{task.task_id}</td>
                      <td>{task.task_type}</td>
                      <td>{task.status}</td>
                      <td>{task.priority}</td>
                      <td>{task.burst_time}</td>
                      <td>{task.algorithm_used || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={5}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Algorithm Metrics</h4>
            <div className="small dashboard-scroll">
              {Object.entries(comparisons).map(([algorithm, metrics]) => (
                <div key={algorithm} className="mb-3">
                  <strong>{algorithm}</strong>
                  <div>Waiting: {metrics.average_waiting_time}</div>
                  <div>Turnaround: {metrics.average_turnaround_time}</div>
                  <div>Response: {metrics.average_response_time}</div>
                  <div>CPU Utilization: {metrics.cpu_utilization}</div>
                  <div>Throughput: {metrics.throughput}</div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default SchedulerView;
