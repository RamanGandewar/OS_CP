import React from "react";
import { Card, Col, Row, Table } from "react-bootstrap";

import { memoryApi } from "../../utils/api";

function MemoryView({ snapshot }) {
  const memory = snapshot?.memory || {};
  const pageTable = memory.page_table || {};
  const cache = memory.cache || {};

  return (
    <Row className="g-4">
      <Col lg={7}>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Page Table</h4>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-dark">
                  <tr>
                    <th>Page</th>
                    <th>Access Count</th>
                    <th>In Memory</th>
                    <th>Last Accessed</th>
                  </tr>
                </thead>
                <tbody>
                  {(memory.memory_pages || []).map((page) => (
                    <tr key={page.page_number}>
                      <td>{page.page_number}</td>
                      <td>{page.access_count}</td>
                      <td>{page.in_memory ? "Yes" : "No"}</td>
                      <td>{page.last_accessed || "-"}</td>
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
            <h4 className="mb-3">Memory Metrics</h4>
            <div className="small">
              <div>Loaded pages: {(pageTable.loaded_pages || []).join(", ") || "-"}</div>
              <div>Page hits: {pageTable.page_hits || 0}</div>
              <div>Page faults: {pageTable.page_faults || 0}</div>
              <div>Fault rate: {Math.round((pageTable.fault_rate || 0) * 100)}%</div>
            </div>
          </Card.Body>
        </Card>
        <Card className="shadow-sm border-0">
          <Card.Body>
            <h4 className="mb-3">Cache Ratios</h4>
            <div className="small mb-3">
              {Object.entries(cache).map(([name, value]) => (
                <div key={name}>{name}: {Math.round((value.hit_ratio || 0) * 100)}%</div>
              ))}
            </div>
            <img alt="Memory usage" className="img-fluid rounded border" src={memoryApi.chartUrl("memory-usage", Date.now())} />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default MemoryView;
