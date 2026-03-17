import React, { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Form, Row, Table } from "react-bootstrap";

import { memoryApi } from "../utils/api";

function MemoryMonitorPage() {
  const [monitor, setMonitor] = useState({
    page_table: { loaded_pages: [], history: [], page_hits: 0, page_faults: 0, fault_rate: 0 },
    memory_pages: [],
    cache: {},
    allocator: { free_blocks: [], allocated: {}, used_memory: 0, total_free: 0 },
    replacement_comparison: {},
    reference_string: [],
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [chartVersion, setChartVersion] = useState(Date.now());
  const [pageNumber, setPageNumber] = useState(0);
  const [frameCount, setFrameCount] = useState(5);
  const [referenceString, setReferenceString] = useState("7,0,1,2,0,3,0,4,2,3,0,3,2");
  const [allocationSize, setAllocationSize] = useState(60);
  const [strategy, setStrategy] = useState("first_fit");

  const loadMonitor = () => {
    memoryApi
      .monitor()
      .then((response) => {
        setMonitor(response.data);
        setError("");
      })
      .catch(() => {
        setError("Memory monitor is unavailable because the backend is not reachable.");
      });
  };

  useEffect(() => {
    loadMonitor();
    const timer = window.setInterval(loadMonitor, 4000);
    return () => window.clearInterval(timer);
  }, []);

  const replacementRows = useMemo(
    () => Object.entries(monitor.replacement_comparison || {}),
    [monitor.replacement_comparison]
  );

  const refreshCharts = () => setChartVersion(Date.now());

  const runLoadPage = async () => {
    try {
      const response = await memoryApi.loadPage({ page_number: pageNumber });
      setMessage(response.data.hit ? `Page ${pageNumber} served from memory.` : `Page fault handled for page ${pageNumber}.`);
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Unable to load report page.");
    }
  };

  const runCustomerCache = async () => {
    try {
      const response = await memoryApi.customerCache({ customer_id: 1 });
      setMessage(response.data.hit ? "Customer cache hit recorded." : "Customer cache miss recorded and loaded.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Customer cache request failed.");
    }
  };

  const runQuotationCache = async () => {
    try {
      const response = await memoryApi.quotationCache({ quotation_id: 1 });
      setMessage(response.data.hit ? "Quotation cache hit recorded." : "Quotation cache miss recorded and loaded.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Quotation cache request failed.");
    }
  };

  const runUserPreferenceCache = async () => {
    try {
      const response = await memoryApi.userPreferenceCache({ user_id: 1 });
      setMessage(response.data.hit ? "User preference cache hit recorded." : "User preference cache miss recorded and loaded.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "User preference cache request failed.");
    }
  };

  const runReplacementComparison = async () => {
    try {
      const parsed = referenceString.split(",").map((item) => Number(item.trim())).filter((item) => !Number.isNaN(item));
      await memoryApi.compareReplacement({ reference_string: parsed, frame_count: frameCount });
      setMessage("Page replacement comparison updated.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Page replacement comparison failed.");
    }
  };

  const runAllocation = async () => {
    try {
      const response = await memoryApi.allocate({ strategy, size: allocationSize });
      setMessage(response.data.success ? `Memory allocated using ${strategy}.` : response.data.message);
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Memory allocation failed.");
    }
  };

  const resetMonitor = async () => {
    try {
      await memoryApi.reset();
      setMessage("Memory monitor reset complete.");
      loadMonitor();
      refreshCharts();
    } catch (err) {
      setError(err.response?.data?.error || "Reset failed.");
    }
  };

  return (
    <div>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">Memory Monitor</h1>
          <p className="text-muted mb-0">Paging, cache hit ratios, page replacement performance, and memory allocation strategies for the CRM workload.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <Button variant="primary" onClick={runLoadPage}>Load Report Page</Button>
          <Button variant="outline-primary" onClick={runReplacementComparison}>Compare Replacement</Button>
          <Button variant="outline-secondary" onClick={runAllocation}>Allocate Memory</Button>
          <Button variant="dark" onClick={resetMonitor}>Reset</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <div className="text-muted">Page Faults</div>
              <div className="display-6">{monitor.page_table?.page_faults ?? 0}</div>
              <div className="small text-muted">Fault rate: {((monitor.page_table?.fault_rate ?? 0) * 100).toFixed(1)}%</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <div className="text-muted">Page Hits</div>
              <div className="display-6">{monitor.page_table?.page_hits ?? 0}</div>
              <div className="small text-muted">Loaded pages: {(monitor.page_table?.loaded_pages || []).join(", ") || "-"}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <div className="text-muted">Used Memory</div>
              <div className="display-6">{monitor.allocator?.used_memory ?? 0}</div>
              <div className="small text-muted">Free memory: {monitor.allocator?.total_free ?? 0}</div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <div className="text-muted">Customer Cache Ratio</div>
              <div className="display-6">{(((monitor.cache?.customer?.hit_ratio ?? 0) * 100)).toFixed(0)}%</div>
              <div className="small text-muted">Keys: {(monitor.cache?.customer?.keys || []).join(", ") || "-"}</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <h4 className="mb-3">Paging Controls</h4>
              <Form.Group className="mb-3">
                <Form.Label>Page Number</Form.Label>
                <Form.Control type="number" min="0" max="99" value={pageNumber} onChange={(event) => setPageNumber(Number(event.target.value))} />
              </Form.Group>
              <div className="d-flex gap-2 flex-wrap">
                <Button variant="primary" onClick={runLoadPage}>Load Page</Button>
                <Button variant="outline-primary" onClick={runCustomerCache}>Customer Cache</Button>
                <Button variant="outline-secondary" onClick={runQuotationCache}>Quotation Cache</Button>
                <Button variant="outline-dark" onClick={runUserPreferenceCache}>User Pref Cache</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <h4 className="mb-3">Replacement Simulation</h4>
              <Form.Group className="mb-3">
                <Form.Label>Reference String</Form.Label>
                <Form.Control value={referenceString} onChange={(event) => setReferenceString(event.target.value)} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Frame Count</Form.Label>
                <Form.Control type="number" min="3" max="10" value={frameCount} onChange={(event) => setFrameCount(Number(event.target.value))} />
              </Form.Group>
              <Button variant="outline-primary" onClick={runReplacementComparison}>Run Comparison</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <h4 className="mb-3">Allocator</h4>
              <Form.Group className="mb-3">
                <Form.Label>Placement Strategy</Form.Label>
                <Form.Select value={strategy} onChange={(event) => setStrategy(event.target.value)}>
                  <option value="first_fit">First Fit</option>
                  <option value="best_fit">Best Fit</option>
                  <option value="worst_fit">Worst Fit</option>
                  <option value="next_fit">Next Fit</option>
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Allocation Size</Form.Label>
                <Form.Control type="number" min="10" max="300" value={allocationSize} onChange={(event) => setAllocationSize(Number(event.target.value))} />
              </Form.Group>
              <Button variant="outline-secondary" onClick={runAllocation}>Allocate</Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={7}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Page Table</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Page</th>
                      <th>Loaded</th>
                      <th>Last Accessed</th>
                      <th>Access Count</th>
                      <th>In Memory</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monitor.memory_pages.map((page) => (
                      <tr key={page.page_number}>
                        <td>{page.page_number}</td>
                        <td>{page.loaded_at || "-"}</td>
                        <td>{page.last_accessed || "-"}</td>
                        <td>{page.access_count}</td>
                        <td>{page.in_memory ? "Yes" : "No"}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={5}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Recent Page Accesses</h4>
              <div className="small text-muted">
                {(monitor.page_table?.history || []).map((item, index) => (
                  <div key={`${item.page_number}-${index}`}>
                    Page {item.page_number}: {item.result}{item.evicted !== undefined && item.evicted !== null ? `, evicted ${item.evicted}` : ""}
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={6}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Page Replacement Comparison</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Algorithm</th>
                      <th>Faults</th>
                      <th>Final Frames</th>
                    </tr>
                  </thead>
                  <tbody>
                    {replacementRows.map(([algorithm, result]) => (
                      <tr key={algorithm}>
                        <td>{algorithm}</td>
                        <td>{result.page_faults}</td>
                        <td>{(result.frames || []).join(", ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Cache Snapshot</h4>
              <div className="small">
                {Object.entries(monitor.cache || {}).map(([cacheType, snapshot]) => (
                  <div key={cacheType} className="mb-3">
                    <strong>{cacheType}</strong>: hits {snapshot.hits}, misses {snapshot.misses}, ratio {(snapshot.hit_ratio * 100).toFixed(1)}%
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        <Col lg={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Page Fault Graph</h4>
              <img alt="Page fault comparison" className="img-fluid rounded border" src={memoryApi.chartUrl("page-faults", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Cache Performance</h4>
              <img alt="Cache performance" className="img-fluid rounded border" src={memoryApi.chartUrl("cache-performance", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4 className="mb-3">Memory Usage</h4>
              <img alt="Memory usage" className="img-fluid rounded border" src={memoryApi.chartUrl("memory-usage", chartVersion)} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default MemoryMonitorPage;
