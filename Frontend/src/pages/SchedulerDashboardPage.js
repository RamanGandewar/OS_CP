import React, { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Form, Row, Table } from "react-bootstrap";

import { customersApi, schedulerApi } from "../utils/api";

const initialTask = {
  task_type: "REPORT",
  burst_time: 4,
  priority: 5,
  operation: "manual-task"
};

function SchedulerDashboardPage() {
  const [tasks, setTasks] = useState([]);
  const [comparison, setComparison] = useState({});
  const [selectedAlgorithm, setSelectedAlgorithm] = useState("FCFS");
  const [timeQuantum, setTimeQuantum] = useState(2);
  const [result, setResult] = useState(null);
  const [form, setForm] = useState(initialTask);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadTasks = () => {
    schedulerApi
      .tasks()
      .then((response) => {
        setTasks(response.data);
        setError("");
      })
      .catch(() => {
        setTasks([]);
        setError("Scheduler backend is not reachable.");
      });
  };

  const loadComparison = () => {
    schedulerApi.compare().then((response) => setComparison(response.data.comparisons || {})).catch(() => setComparison({}));
  };

  useEffect(() => {
    loadTasks();
    loadComparison();
  }, []);

  const runScheduler = async () => {
    try {
      const response = await schedulerApi.run({
        algorithm: selectedAlgorithm,
        time_quantum: Number(timeQuantum)
      });
      setResult(response.data);
      setMessage(`${selectedAlgorithm} scheduling completed.`);
      setError("");
      loadTasks();
      loadComparison();
    } catch (err) {
      setError(err.response?.data?.error || "Scheduler run failed.");
    }
  };

  const addTask = async (event) => {
    event.preventDefault();
    try {
      await schedulerApi.addTask({
        ...form,
        burst_time: Number(form.burst_time),
        priority: Number(form.priority)
      });
      setForm(initialTask);
      setMessage("Task added to queue.");
      setError("");
      loadTasks();
      loadComparison();
    } catch (err) {
      setError(err.response?.data?.error || "Task could not be added.");
    }
  };

  const queueSummary = useMemo(() => {
    return tasks.reduce(
      (summary, task) => {
        summary[task.status] = (summary[task.status] || 0) + 1;
        return summary;
      },
      {}
    );
  }, [tasks]);

  const enqueueCustomerExport = async () => {
    try {
      await customersApi.exportList();
      setMessage("Customer export task added.");
      loadTasks();
      loadComparison();
    } catch (err) {
      setError(err.response?.data?.error || "Customer export task could not be added.");
    }
  };

  const resetTasks = async () => {
    await schedulerApi.reset();
    setResult(null);
    setMessage("Tasks reset to pending.");
    loadTasks();
  };

  return (
    <div className="monitor-page">
      <div className="monitor-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h1 className="mb-1">CPU Scheduler Dashboard</h1>
          <p className="text-muted mb-0">FCFS, SJF, Priority, and Round Robin applied to CRM task management.</p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="outline-primary" onClick={enqueueCustomerExport}>Queue Customer Export</Button>
          <Button variant="outline-secondary" onClick={resetTasks}>Reset Queue</Button>
        </div>
      </div>

      {message && <Alert variant="info">{message}</Alert>}
      {error && <Alert variant="warning">{error}</Alert>}

      <Row className="g-4 mb-4">
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Add Task</h4>
              <Form onSubmit={addTask}>
                <Form.Group className="mb-3">
                  <Form.Label>Task Type</Form.Label>
                  <Form.Select value={form.task_type} onChange={(event) => setForm({ ...form, task_type: event.target.value })}>
                    <option>REPORT</option>
                    <option>EMAIL</option>
                    <option>PDF</option>
                    <option>NOTIFICATION</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Burst Time</Form.Label>
                  <Form.Control type="number" min="1" value={form.burst_time} onChange={(event) => setForm({ ...form, burst_time: event.target.value })} />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Control type="number" min="1" max="10" value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value })} />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Operation</Form.Label>
                  <Form.Control value={form.operation} onChange={(event) => setForm({ ...form, operation: event.target.value })} />
                </Form.Group>
                <Button type="submit" className="w-100">Add To Queue</Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Run Scheduler</h4>
              <Form.Group className="mb-3">
                <Form.Label>Algorithm</Form.Label>
                <Form.Select value={selectedAlgorithm} onChange={(event) => setSelectedAlgorithm(event.target.value)}>
                  <option>FCFS</option>
                  <option>SJF</option>
                  <option>PRIORITY</option>
                  <option>RR</option>
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Time Quantum</Form.Label>
                <Form.Control type="number" min="1" value={timeQuantum} disabled={selectedAlgorithm !== "RR"} onChange={(event) => setTimeQuantum(event.target.value)} />
              </Form.Group>
              <Button className="w-100 mb-3" onClick={runScheduler}>Execute {selectedAlgorithm}</Button>
              <div className="small text-muted">
                <div>PENDING: {queueSummary.PENDING || 0}</div>
                <div>RUNNING: {queueSummary.RUNNING || 0}</div>
                <div>COMPLETED: {queueSummary.COMPLETED || 0}</div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm h-100 monitor-stat-card">
            <Card.Body>
              <h4 className="mb-3">Latest Metrics</h4>
              {result ? (
                <div className="small">
                  <div>Average Waiting Time: {result.metrics.average_waiting_time}s</div>
                  <div>Average Turnaround Time: {result.metrics.average_turnaround_time}s</div>
                  <div>Average Response Time: {result.metrics.average_response_time}s</div>
                  <div>CPU Utilization: {result.metrics.cpu_utilization}%</div>
                  <div>Throughput: {result.metrics.throughput} tasks/s</div>
                </div>
              ) : (
                <p className="text-muted mb-0">Run an algorithm to see metrics and Gantt output.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col lg={8}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Current Task Queue</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Task ID</th>
                      <th>Type</th>
                      <th>Burst</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Algorithm</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.task_id}>
                        <td>{task.task_id}</td>
                        <td>{task.task_type}</td>
                        <td>{task.burst_time}s</td>
                        <td>{task.priority}</td>
                        <td>{task.status}</td>
                        <td>{task.algorithm_used || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Gantt Chart</h4>
              {result ? (
                <img
                  alt={`${result.algorithm} gantt chart`}
                  src={`${schedulerApi.ganttUrl(result.algorithm)}?t=${Date.now()}`}
                  className="img-fluid rounded border"
                />
              ) : (
                <p className="text-muted mb-0">Gantt chart will appear after a scheduler run.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        <Col lg={7}>
          <Card className="shadow-sm monitor-panel-card">
            <Card.Body>
              <h4 className="mb-3">Performance Comparison</h4>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead className="table-dark">
                    <tr>
                      <th>Algorithm</th>
                      <th>Avg Wait</th>
                      <th>Avg TAT</th>
                      <th>Avg Response</th>
                      <th>CPU Utilization</th>
                      <th>Throughput</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(comparison).map(([algorithm, metrics]) => (
                      <tr key={algorithm}>
                        <td>{algorithm}</td>
                        <td>{metrics.average_waiting_time}</td>
                        <td>{metrics.average_turnaround_time}</td>
                        <td>{metrics.average_response_time}</td>
                        <td>{metrics.cpu_utilization}%</td>
                        <td>{metrics.throughput}</td>
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
              <h4 className="mb-3">Execution Timeline</h4>
              <div className="scheduler-timeline-list">
                {(result?.timeline || []).map((segment, index) => (
                  <div key={`${segment.task_id}-${index}`} className="process-log-item">
                    <strong>{segment.task_id}</strong>
                    <div>{segment.task_type}</div>
                    <small>Start: {segment.start}s | Duration: {segment.duration}s</small>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default SchedulerDashboardPage;
