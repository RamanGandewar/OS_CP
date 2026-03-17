import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

import { ioApi } from "../../utils/api";

function IOView({ snapshot }) {
  const io = snapshot?.io || {};
  const comparison = io.comparison || {};

  return (
    <Row className="g-4">
      <Col lg={7}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Disk Request Queue</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Request</th>
                    <th>Track</th>
                    <th>Arrival</th>
                    <th>Algorithm</th>
                  </tr>
                </thead>
                <tbody>
                  {(io.requests || []).map((request) => (
                    <tr key={request.id}>
                      <td>{request.request_type}</td>
                      <td>{request.track_number}</td>
                      <td>{request.arrival_time}</td>
                      <td>{request.algorithm_used || "-"}</td>
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
            <h4 className="mb-3">Algorithm Comparison</h4>
            <div className="small dashboard-scroll">
              {Object.entries(comparison).map(([algorithm, result]) => (
                <div key={algorithm}>{algorithm}: seek {result.total_seek}</div>
              ))}
            </div>
          </Card.Body>
        </Card>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Disk Graph</h4>
            <img alt="Disk comparison" className="img-fluid rounded border" src={ioApi.chartUrl("comparison", Date.now())} />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default IOView;
