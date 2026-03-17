import React from "react";
import { Col, Form, Row } from "react-bootstrap";

function SearchBar({ search, setSearch, filter, setFilter, filterOptions = [] }) {
  return (
    <Row className="g-3 mb-3">
      <Col md={8}>
        <Form.Control
          placeholder="Search..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </Col>
      {filterOptions.length > 0 && (
        <Col md={4}>
          <Form.Select value={filter} onChange={(event) => setFilter(event.target.value)}>
            <option value="">All</option>
            {filterOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </Form.Select>
        </Col>
      )}
    </Row>
  );
}

export default SearchBar;
