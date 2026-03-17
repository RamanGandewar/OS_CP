import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import SearchBar from "../components/SearchBar";
import { customersApi } from "../utils/api";

const initialForm = { name: "", email: "", phone: "", company: "", address: "" };

function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const loadCustomers = () => {
    customersApi
      .list(search)
      .then((response) => {
        setCustomers(response.data);
        setError("");
      })
      .catch(() => {
        setCustomers([]);
        setError("Customers could not be loaded because the backend is unavailable.");
      });
  };

  useEffect(() => {
    loadCustomers();
  }, [search]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await customersApi.create(form);
      setForm(initialForm);
      setError("");
      loadCustomers();
    } catch (err) {
      setError(err.response?.data?.error || "Customer could not be saved.");
    }
  };

  return (
    <Row className="g-4">
      <Col lg={4}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Add Customer</h3>
            <Form onSubmit={handleSubmit}>
              {Object.keys(initialForm).map((field) => (
                <Form.Group className="mb-3" key={field}>
                  <Form.Label className="text-capitalize">{field}</Form.Label>
                  <Form.Control
                    as={field === "address" ? "textarea" : "input"}
                    rows={field === "address" ? 3 : undefined}
                    value={form[field]}
                    onChange={(event) => setForm({ ...form, [field]: event.target.value })}
                  />
                </Form.Group>
              ))}
              <Button type="submit" className="w-100">Save Customer</Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={8}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Customers</h3>
            {error && <Alert variant="warning">{error}</Alert>}
            <SearchBar search={search} setSearch={setSearch} filter="" setFilter={() => {}} />
            <EntityTable
              columns={[
                { key: "name", label: "Name" },
                { key: "email", label: "Email" },
                { key: "phone", label: "Phone" },
                { key: "company", label: "Company" }
              ]}
              rows={customers}
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default CustomersPage;
