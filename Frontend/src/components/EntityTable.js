import React from "react";
import Table from "react-bootstrap/Table";

function EntityTable({ columns, rows, emptyMessage = "No records found." }) {
  return (
    <div className="table-responsive">
      <Table striped bordered hover>
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
                  <td key={column.key}>{row[column.key]}</td>
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
