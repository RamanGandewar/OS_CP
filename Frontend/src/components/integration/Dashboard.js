import React from "react";
import { Alert, Badge, Button, Card, Col, Row, Tab, Tabs } from "react-bootstrap";

import ProcessMonitor from "./ProcessMonitor";
import SchedulerView from "./SchedulerView";
import ThreadView from "./ThreadView";
import SyncView from "./SyncView";
import DeadlockView from "./DeadlockView";
import MemoryView from "./MemoryView";
import IOView from "./IOView";

const CARD_META = {
  "Active Processes": { accent: "#3B82F6", icon: "PR" },
  "Task Queue": { accent: "#8B5CF6", icon: "TS" },
  Threads: { accent: "#10B981", icon: "TH" },
  "I/O Queue": { accent: "#F59E0B", icon: "IO" },
  "Page Faults": { accent: "#EF4444", icon: "PF" },
  "Cache Ratio": { accent: "#14B8A6", icon: "CR" },
};

function formatCacheRatio(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function getTrend(current, previous) {
  if (previous === null || previous === undefined) {
    return null;
  }
  if (current > previous) {
    return { direction: "up", label: "^ up" };
  }
  if (current < previous) {
    return { direction: "down", label: "v down" };
  }
  return { direction: "flat", label: "= steady" };
}

function ModuleStatusBadge({ label, status }) {
  return (
    <div className="module-status-row">
      <span>{label}</span>
      <span className={`module-status-badge module-status-${status}`}>{status.toUpperCase()}</span>
    </div>
  );
}

function MetricCard({ label, value, rawValue, previousValue }) {
  const meta = CARD_META[label];
  const trend = getTrend(rawValue, previousValue);
  const isEmpty = rawValue === 0;

  return (
    <Col md={6} xl={4}>
      <Card className="dashboard-card dashboard-metric-card border-0 shadow-sm h-100" style={{ "--card-accent": meta.accent }}>
        <Card.Body>
          <div className="metric-card-header">
            <span className="metric-icon">{meta.icon}</span>
            <div>
              <div className="text-muted mb-1">{label}</div>
              <div className="display-6">{value}</div>
            </div>
          </div>
          <div className="metric-card-footer">
            {trend && <span className={`metric-trend metric-trend-${trend.direction}`}>{trend.label}</span>}
            {isEmpty && <div className="metric-empty-hint">No data yet - run seed script to populate</div>}
          </div>
        </Card.Body>
      </Card>
    </Col>
  );
}

function buildModuleStatuses(snapshot, health, isLive) {
  const queueSize = snapshot?.overview?.task_queue_size || 0;
  const lockQueueSize = snapshot?.synchronization?.lock_queue?.length || 0;
  const pageFaults = health?.page_faults ?? snapshot?.overview?.memory_usage?.page_faults ?? 0;
  const cacheRatio = health?.cache_ratio ?? snapshot?.overview?.memory_usage?.cache_hit_ratio ?? 0;
  const deadlockDetected = Boolean(snapshot?.deadlock?.visualization?.deadlock);
  const ioQueue = health?.io_queue ?? snapshot?.overview?.io_queue_size ?? 0;

  return [
    { label: "Process Management", status: !isLive ? "red" : (health?.active_processes || snapshot?.overview?.active_processes) > 0 ? "green" : "amber" },
    { label: "CPU Scheduling", status: queueSize > 25 ? "red" : queueSize > 0 ? "amber" : "green" },
    { label: "Thread Management", status: !isLive ? "red" : (health?.threads || snapshot?.overview?.thread_count) > 3 ? "green" : "amber" },
    { label: "Synchronization", status: lockQueueSize > 3 ? "red" : lockQueueSize > 0 ? "amber" : "green" },
    { label: "Deadlock Management", status: deadlockDetected ? "red" : "green" },
    { label: "Memory Management", status: pageFaults > 6 || cacheRatio < 0.5 ? "amber" : "green" },
    { label: "I/O Management", status: ioQueue > 8 ? "amber" : "green" },
  ];
}

function OverviewTab({
  snapshot,
  previousSnapshot,
  health,
  isLive,
  onRefresh,
  onExportCsv,
  onExportReport,
  theme,
  onToggleTheme,
}) {
  const overview = snapshot?.overview || {};
  const previousOverview = previousSnapshot?.overview || {};
  const crm = overview.crm_counts || {};
  const alerts = snapshot?.alerts || [];
  const cards = [
    {
      label: "Active Processes",
      rawValue: health?.active_processes ?? overview.active_processes ?? 0,
      previousValue: previousOverview.active_processes,
      value: health?.active_processes ?? overview.active_processes ?? 0,
    },
    {
      label: "Task Queue",
      rawValue: health?.task_queue ?? overview.task_queue_size ?? 0,
      previousValue: previousOverview.task_queue_size,
      value: health?.task_queue ?? overview.task_queue_size ?? 0,
    },
    {
      label: "Threads",
      rawValue: health?.threads ?? overview.thread_count ?? 0,
      previousValue: previousOverview.thread_count,
      value: health?.threads ?? overview.thread_count ?? 0,
    },
    {
      label: "I/O Queue",
      rawValue: health?.io_queue ?? overview.io_queue_size ?? 0,
      previousValue: previousOverview.io_queue_size,
      value: health?.io_queue ?? overview.io_queue_size ?? 0,
    },
    {
      label: "Page Faults",
      rawValue: health?.page_faults ?? overview.memory_usage?.page_faults ?? 0,
      previousValue: previousOverview.memory_usage?.page_faults,
      value: health?.page_faults ?? overview.memory_usage?.page_faults ?? 0,
    },
    {
      label: "Cache Ratio",
      rawValue: health?.cache_ratio ?? overview.memory_usage?.cache_hit_ratio ?? 0,
      previousValue: previousOverview.memory_usage?.cache_hit_ratio,
      value: formatCacheRatio(health?.cache_ratio ?? overview.memory_usage?.cache_hit_ratio ?? 0),
    },
  ];
  const moduleStatuses = buildModuleStatuses(snapshot, health, isLive);

  return (
    <div>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
        <div>
          <h2 className="mb-1">Unified OS Monitoring Dashboard</h2>
          <p className="text-muted mb-0">One place to observe processes, scheduling, threads, locks, deadlocks, memory, and disk activity.</p>
        </div>
        <div className="d-flex gap-2 flex-wrap align-items-center">
          <Button variant="primary" onClick={onRefresh}>Refresh</Button>
          <div className={`live-indicator ${isLive ? "live-indicator-online" : "live-indicator-offline"}`}>
            <span className="live-indicator-dot" />
            <span>{isLive ? "Live" : "Offline"}</span>
          </div>
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
          <MetricCard key={card.label} {...card} />
        ))}
      </Row>

      <Row className="g-4">
        <Col lg={7}>
          <Card className="shadow-sm border-0 h-100 dashboard-panel-card">
            <Card.Body>
              <h4 className="mb-3">System Status Summary</h4>
              <div className="d-flex flex-wrap gap-2 mb-3">
                <Badge bg="success">Uptime {overview.uptime_seconds || 0}s</Badge>
                <Badge bg="info">Processes {health?.active_processes ?? overview.active_processes ?? 0}</Badge>
                <Badge bg="secondary">Locks {overview.resource_utilization?.active_locks || 0}</Badge>
                <Badge bg="warning" text="dark">Allocations {overview.resource_utilization?.resource_allocations || 0}</Badge>
              </div>
              <div className="module-status-grid">
                {moduleStatuses.map((module) => (
                  <ModuleStatusBadge key={module.label} {...module} />
                ))}
              </div>
              <hr />
              <div className="small status-summary-list">
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
          <Card className="shadow-sm border-0 h-100 dashboard-panel-card">
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

function IntegrationDashboard({
  snapshot,
  previousSnapshot,
  health,
  isLive,
  theme,
  onRefresh,
  onExportCsv,
  onExportReport,
  onToggleTheme,
}) {
  return (
    <Tabs defaultActiveKey="overview" className="mb-4 crm-dashboard-tabs" fill>
      <Tab eventKey="overview" title="Overview">
        <OverviewTab
          snapshot={snapshot}
          previousSnapshot={previousSnapshot}
          health={health}
          isLive={isLive}
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
