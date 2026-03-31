import React from "react";
import Table from "react-bootstrap/Table";

const statusPalette = {
  new: "status-pill status-pill-info",
  open: "status-pill status-pill-info",
  qualified: "status-pill status-pill-warning",
  "in progress": "status-pill status-pill-warning",
  processing: "status-pill status-pill-warning",
  draft: "status-pill status-pill-muted",
  sent: "status-pill status-pill-info",
  approved: "status-pill status-pill-success",
  created: "status-pill status-pill-info",
  packed: "status-pill status-pill-warning",
  dispatched: "status-pill status-pill-warning",
  delivered: "status-pill status-pill-success",
  closed: "status-pill status-pill-success",
  paid: "status-pill status-pill-success",
  pending: "status-pill status-pill-warning",
  overdue: "status-pill status-pill-danger",
  running: "status-pill status-pill-info",
  ready: "status-pill status-pill-muted",
  waiting: "status-pill status-pill-warning",
  terminated: "status-pill status-pill-danger",
  completed: "status-pill status-pill-success",
  failed: "status-pill status-pill-danger",
  active: "status-pill status-pill-info",
  released: "status-pill status-pill-success",
  queued: "status-pill status-pill-muted",
};

function renderCell(columnKey, value) {
  if (value === null || value === undefined || value === "") {
    return <span className="cell-placeholder">-</span>;
  }

  const normalizedKey = String(columnKey).toLowerCase();
  const normalizedValue = String(value).toLowerCase();
  const isStatusField =
    normalizedKey.includes("status") ||
    normalizedKey === "state" ||
    normalizedKey.includes("payment") ||
    normalizedKey.includes("lock_type");

  if (isStatusField) {
    const className = statusPalette[normalizedValue] || "status-pill status-pill-muted";
    return <span className={className}>{String(value)}</span>;
  }

  return value;
}

function EntityTable({ columns, rows, emptyMessage = "No records found." }) {
  return (
    <div className="table-responsive entity-table-shell">
      <Table striped bordered hover className="entity-table">
        <thead className="table-dark">
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="text-center">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row, index) => (
              <tr key={row.id || index}>
                {columns.map((column) => (
                  <td key={column.key}>{renderCell(column.key, row[column.key])}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}

export default EntityTable;
