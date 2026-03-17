import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import SearchBar from "../components/SearchBar";
import { customersApi, enquiriesApi, usersApi } from "../utils/api";

const initialForm = {
  customer_id: "",
  product: "",
  description: "",
  status: "Open",
  assigned_to: ""
};

function EnquiriesPage() {
  const [enquiries, setEnquiries] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const loadEnquiries = () => {
    enquiriesApi
      .list(search, status)
      .then((response) => {
        setEnquiries(response.data);
        setError("");
      })
      .catch(() => {
        setEnquiries([]);
        setError("Enquiries could not be loaded because the backend is unavailable.");
      });
  };

  useEffect(() => {
    customersApi.list().then((response) => setCustomers(response.data)).catch(() => setCustomers([]));
    usersApi.list().then((response) => setUsers(response.data)).catch(() => setUsers([]));
  }, []);

  useEffect(() => {
    loadEnquiries();
  }, [search, status]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await enquiriesApi.create({
        ...form,
        customer_id: Number(form.customer_id),
        assigned_to: form.assigned_to ? Number(form.assigned_to) : null
      });
      setForm(initialForm);
      setError("");
      loadEnquiries();
    } catch (err) {
      setError(err.response?.data?.error || "Enquiry could not be saved.");
    }
  };

  return (
    <Row className="g-4">
      <Col lg={4}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Create Enquiry</h3>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Customer</Form.Label>
                <Form.Select value={form.customer_id} onChange={(event) => setForm({ ...form, customer_id: event.target.value })}>
                  <option value="">Select customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>{customer.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Product</Form.Label>
                <Form.Control value={form.product} onChange={(event) => setForm({ ...form, product: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control as="textarea" rows={3} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Status</Form.Label>
                <Form.Select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                  <option>Open</option>
                  <option>Qualified</option>
                  <option>Closed</option>
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Assign To</Form.Label>
                <Form.Select value={form.assigned_to} onChange={(event) => setForm({ ...form, assigned_to: event.target.value })}>
                  <option value="">Unassigned</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>{user.username}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Button type="submit" className="w-100">Save Enquiry</Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={8}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Enquiries</h3>
            {error && <Alert variant="warning">{error}</Alert>}
            <SearchBar
              search={search}
              setSearch={setSearch}
              filter={status}
              setFilter={setStatus}
              filterOptions={["Open", "Qualified", "Closed"]}
            />
            <EntityTable
              columns={[
                { key: "customer_name", label: "Customer" },
                { key: "product", label: "Product" },
                { key: "status", label: "Status" },
                { key: "assigned_user", label: "Assigned User" }
              ]}
              rows={enquiries}
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default EnquiriesPage;
