import React from "react";
import { Alert, Badge, Button, Card, Col, Row, Tab, Tabs } from "react-bootstrap";

import ProcessMonitor from "./ProcessMonitor";
import SchedulerView from "./SchedulerView";
import ThreadView from "./ThreadView";
import SyncView from "./SyncView";
import DeadlockView from "./DeadlockView";
import MemoryView from "./MemoryView";
import IOView from "./IOView";

function OverviewTab({ snapshot, onRefresh, onExportCsv, onExportReport, theme, onToggleTheme }) {
  const overview = snapshot?.overview || {};
  const crm = overview.crm_counts || {};
  const alerts = snapshot?.alerts || [];
  const cards = [
    { label: "Active Processes", value: overview.active_processes || 0 },
    { label: "Task Queue", value: overview.task_queue_size || 0 },
    { label: "Threads", value: overview.thread_count || 0 },
    { label: "I/O Queue", value: overview.io_queue_size || 0 },
    { label: "Page Faults", value: overview.memory_usage?.page_faults || 0 },
    { label: "Cache Ratio", value: `${Math.round((overview.memory_usage?.cache_hit_ratio || 0) * 100)}%` },
  ];

  return (
    <div>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h2 className="mb-1">Unified OS Monitoring Dashboard</h2>
          <p className="text-muted mb-0">One place to observe processes, scheduling, threads, locks, deadlocks, memory, and disk activity.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <Button variant="primary" onClick={onRefresh}>Refresh</Button>
          <Button variant="outline-primary" onClick={onExportCsv}>Export CSV</Button>
          <Button variant="outline-secondary" onClick={onExportReport}>Performance Report</Button>
          <Button variant="dark" onClick={onToggleTheme}>{theme === "dark" ? "Light Theme" : "Dark Theme"}</Button>
        </div>
      </div>

      {alerts.map((alert, index) => (
        <Alert key={`${alert.type}-${index}`} variant={alert.type}>{alert.message}</Alert>
      ))}

      <Row className="g-4 mb-4">
        {cards.map((card) => (
          <Col md={6} xl={4} key={card.label}>
            <Card className="dashboard-card border-0 shadow-sm h-100">
              <Card.Body>
                <div className="text-muted mb-2">{card.label}</div>
                <div className="display-6">{card.value}</div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="g-4">
        <Col lg={7}>
          <Card className="shadow-sm border-0 h-100">
            <Card.Body>
              <h4 className="mb-3">System Status Summary</h4>
              <div className="d-flex flex-wrap gap-2 mb-3">
                <Badge bg="success">Uptime {overview.uptime_seconds || 0}s</Badge>
                <Badge bg="info">Processes {overview.active_processes || 0}</Badge>
                <Badge bg="secondary">Locks {overview.resource_utilization?.active_locks || 0}</Badge>
                <Badge bg="warning" text="dark">Deadlock Resources {overview.resource_utilization?.deadlock_resources || 0}</Badge>
              </div>
              <div className="small">
                <div>Customers: {crm.customers || 0}</div>
                <div>Enquiries: {crm.enquiries || 0}</div>
                <div>Quotations: {crm.quotations || 0}</div>
                <div>Orders: {crm.orders || 0}</div>
                <div>Invoices: {crm.invoices || 0}</div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={5}>
          <Card className="shadow-sm border-0 h-100">
            <Card.Body>
              <h4 className="mb-3">Analytics Snapshot</h4>
              <div className="small">
                {Object.entries(snapshot?.analytics || {}).map(([key, value]) => (
                  <div key={key}>{key.replaceAll("_", " ")}: {String(value)}</div>
                ))}
              </div>
              <hr />
              <div className="small">
                {Object.entries(snapshot?.performance_report || {}).map(([key, value]) => (
                  <div key={key}>{key.replaceAll("_", " ")}: {String(value)}</div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

function IntegrationDashboard({ snapshot, theme, onRefresh, onExportCsv, onExportReport, onToggleTheme }) {
  return (
    <Tabs defaultActiveKey="overview" className="mb-4 crm-dashboard-tabs" fill>
      <Tab eventKey="overview" title="Overview">
        <OverviewTab
          snapshot={snapshot}
          theme={theme}
          onRefresh={onRefresh}
          onExportCsv={onExportCsv}
          onExportReport={onExportReport}
          onToggleTheme={onToggleTheme}
        />
      </Tab>
      <Tab eventKey="processes" title="Processes">
        <ProcessMonitor snapshot={snapshot} />
      </Tab>
      <Tab eventKey="scheduler" title="Scheduler">
        <SchedulerView snapshot={snapshot} />
      </Tab>
      <Tab eventKey="threads" title="Threads">
        <ThreadView snapshot={snapshot} />
      </Tab>
      <Tab eventKey="sync" title="Synchronization">
        <SyncView snapshot={snapshot} />
      </Tab>
      <Tab eventKey="deadlock" title="Deadlock">
        <DeadlockView snapshot={snapshot} />
      </Tab>
      <Tab eventKey="memory" title="Memory">
        <MemoryView snapshot={snapshot} />
      </Tab>
      <Tab eventKey="io" title="I/O">
        <IOView snapshot={snapshot} />
      </Tab>
    </Tabs>
  );
}

export default IntegrationDashboard;
