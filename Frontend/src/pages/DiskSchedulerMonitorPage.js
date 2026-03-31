import React, { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Form, Row, Table } from "react-bootstrap";

import { ioApi } from "../utils/api";

function DiskSchedulerMonitorPage() {
  const [monitor, setMonitor] = useState({
    current_head: 50,
    requests: [],
    reference_sequence: [],
    comparison: {},
    best_algorithm: null,
    buffer_pool: { buffers: [], history: [] },
    print_queue: [],
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [chartVersion, setChartVersion] = useState(Date.now());
  const [requestType, setRequestType] = useState("Save Quotation PDF");
  const [trackNumber, setTrackNumber] = useState(45);
  const [headPosition, setHeadPosition] = useState(50);
  const [bufferSize, setBufferSize] = useState(64);
  const [spoolFilename, setSpoolFilename] = useState("invoice-print.pdf");

  const comparisonRows = useMemo(() => Object.entries(monitor.comparison || {}), [monitor.comparison]);

  const loadMonitor = () => {
    ioApi
      .monitor()
      .then((response) => {
        setMonitor(response.data);
        setError("");
      })
      .catch(() => {
        setError("Disk scheduler monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    loadMonitor();
    const timer = window.setInterval(loadMonitor, 4000);
    return () => window.clearInterval(timer);
  }, []);

  const refreshCharts = () => setChartVersion(Date.now());

  const addRequest = async () => {
    try {
      await ioApi.addRequest({ request_type: requestType, track_number: trackNumber });
      setMessage("Disk request added.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to add disk request.");
    }
  };

  const compareAlgorithms = async () => {
    try {
      const requests = monitor.reference_sequence.length ? monitor.reference_sequence : [45, 12, 78, 23, 67, 89, 34, 56];
      await ioApi.compare({ requests, current_head: headPosition });
      setMessage("Disk scheduling comparison updated.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to compare algorithms.");
    }
  };

  const allocateBuffer = async () => {
    try {
      const response = await ioApi.allocateBuffer({ request_type: requestType, size: bufferSize });
      setMessage(response.data.success ? `Buffer ${response.data.buffer_id} allocated.` : response.data.action);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to allocate buffer.");
    }
  };

  const releaseBuffer = async (bufferId) => {
    try {
      await ioApi.releaseBuffer({ buffer_id: bufferId });
      setMessage(`Buffer ${bufferId} released.`);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to release buffer.");
    }
  };

  const enqueuePrint = async () => {
    try {
      await ioApi.enqueuePrint({ job_type: "invoice", filename: spoolFilename, pages: 3, user_id: 1 });
      setMessage("Print job queued.");
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to queue print job.");
    }
  };

  const processPrint = async () => {
    try {
      const response = await ioApi.processPrint();
      setMessage(response.data.success ? `Printed ${response.data.job.filename}.` : response.data.message);
      loadMonitor();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to process print queue.");
    }
  };

  return (
    <div className="monitor-page">
      <div className="monitor-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Disk Scheduler Monitor</h1>
          <p className="text-muted mb-0">Disk request scheduling, seek time comparison, I/O buffering, and invoice/report print spooling in one dashboard.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <Button variant="primary" onClick={addRequest}>Add Request</Button>
          <Button variant="outline-primary" onClick={compareAlgorithms}>Compare Algorithms</Button>
          <Button variant="outline-secondary" onClick={enqueuePrint}>Queue Print</Button>
          <Button variant="dark" onClick={processPrint}>Process Print</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col lg={3}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <div className="text-muted">Current Head</div>
              <div className="display-6">{monitor.current_head}</div>
              <div className="small text-muted">Best: {monitor.best_algorithm || "-"}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <div className="text-muted">Queued Requests</div>
              <div className="display-6">{monitor.requests.length}</div>
              <div className="small text-muted">Sequence: {(monitor.reference_sequence || []).join(", ")}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <div className="text-muted">Buffers In Use</div>
              <div className="display-6">{(monitor.buffer_pool?.buffers || []).filter((item) => item.status === "ALLOCATED").length}</div>
              <div className="small text-muted">Pool size: {monitor.buffer_pool?.buffer_count || 0}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <div className="text-muted">Print Queue</div>
              <div className="display-6">{monitor.print_queue.length}</div>
              <div className="small text-muted">Spooling: FCFS</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Disk Request Controls</h4>
              <Form.Group className="mb-3">
                <Form.Label>Request Type</Form.Label>
                <Form.Select value={requestType} onChange={(event) => setRequestType(event.target.value)}>
                  <option>Save Quotation PDF</option>
                  <option>Load Customer Data</option>
                  <option>Generate Report</option>
                  <option>Save Invoice</option>
                  <option>Export Excel</option>
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Track Number</Form.Label>
                <Form.Control type="number" min="0" max="100" value={trackNumber} onChange={(event) => setTrackNumber(Number(event.target.value))} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Current Head</Form.Label>
                <Form.Control type="number" min="0" max="100" value={headPosition} onChange={(event) => setHeadPosition(Number(event.target.value))} />
              </Form.Group>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">I/O Buffer Pool</h4>
              <Form.Group className="mb-3">
                <Form.Label>Buffer Size Request</Form.Label>
                <Form.Control type="number" min="1" max="256" value={bufferSize} onChange={(event) => setBufferSize(Number(event.target.value))} />
              </Form.Group>
              <div className="d-flex gap-2 flex-wrap mb-3">
                <Button variant="outline-secondary" onClick={allocateBuffer}>Allocate Buffer</Button>
              </div>
              <div className="small text-muted">
                {(monitor.buffer_pool?.buffers || []).map((buffer) => (
                  <div key={buffer.buffer_id}>
                    Buffer {buffer.buffer_id}: {buffer.status} ({buffer.used}/{monitor.buffer_pool.buffer_size})
                    {buffer.status === "ALLOCATED" && (
                      <Button size="sm" variant="link" onClick={() => releaseBuffer(buffer.buffer_id)}>release</Button>
                    )}
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Print Spooling</h4>
              <Form.Group className="mb-3">
                <Form.Label>Filename</Form.Label>
                <Form.Control value={spoolFilename} onChange={(event) => setSpoolFilename(event.target.value)} />
              </Form.Group>
              <div className="d-flex gap-2 flex-wrap mb-3">
                <Button variant="outline-primary" onClick={enqueuePrint}>Enqueue Job</Button>
                <Button variant="outline-dark" onClick={processPrint}>Process Next</Button>
              </div>
              <div className="small text-muted">
                {(monitor.print_queue || []).map((job) => (
                  <div key={job.id}>{job.filename}: {job.status}</div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={7}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Request Queue</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Type</th>
                      <th>Track</th>
                      <th>Arrival</th>
                      <th>Algorithm</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.requests.map((request) => (
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
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Seek Time Comparison</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Algorithm</th>
                      <th>Total Seek</th>
                      <th>Path</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonRows.map(([algorithm, result]) => (
                      <tr key={algorithm}>
                        <td>{algorithm}</td>
                        <td>{result.total_seek}</td>
                        <td>{(result.path || []).join(" -> ")}</td>
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
        <Col lg={4}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Comparison Chart</h4>
              <img alt="Seek comparison" className="img-fluid rounded border" src={ioApi.chartUrl("comparison", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">SSTF Movement</h4>
              <img alt="SSTF movement" className="img-fluid rounded border" src={ioApi.chartUrl("sstf", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">LOOK Movement</h4>
              <img alt="LOOK movement" className="img-fluid rounded border" src={ioApi.chartUrl("look", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default DiskSchedulerMonitorPage;
