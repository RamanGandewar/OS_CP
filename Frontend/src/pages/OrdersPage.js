import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import SearchBar from "../components/SearchBar";
import { ordersApi, quotationsApi } from "../utils/api";

const initialForm = {
  quotation_id: "",
  order_number: "",
  order_date: "",
  delivery_date: "",
  status: "Created"
};

function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const loadOrders = () => {
    ordersApi
      .list(search)
      .then((response) => {
        setOrders(response.data);
        setError("");
      })
      .catch(() => {
        setOrders([]);
        setError("Sales orders could not be loaded because the backend is unavailable.");
      });
  };

  useEffect(() => {
    quotationsApi
      .list()
      .then((response) => setQuotations(response.data.filter((item) => item.status === "Approved")))
      .catch(() => setQuotations([]));
  }, []);

  useEffect(() => {
    loadOrders();
  }, [search]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await ordersApi.create({
        ...form,
        quotation_id: Number(form.quotation_id)
      });
      setForm(initialForm);
      setError("");
      loadOrders();
    } catch (err) {
      setError(err.response?.data?.error || "Sales order could not be saved.");
    }
  };

  return (
    <Row className="g-4">
      <Col lg={4}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Create Sales Order</h3>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Approved Quotation</Form.Label>
                <Form.Select value={form.quotation_id} onChange={(event) => setForm({ ...form, quotation_id: event.target.value })}>
                  <option value="">Select quotation</option>
                  {quotations.map((quotation) => (
                    <option key={quotation.id} value={quotation.id}>{quotation.quotation_number}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Order Number</Form.Label>
                <Form.Control value={form.order_number} onChange={(event) => setForm({ ...form, order_number: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Order Date</Form.Label>
                <Form.Control type="date" value={form.order_date} onChange={(event) => setForm({ ...form, order_date: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Delivery Date</Form.Label>
                <Form.Control type="date" value={form.delivery_date} onChange={(event) => setForm({ ...form, delivery_date: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Status</Form.Label>
                <Form.Select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                  <option>Created</option>
                  <option>Processing</option>
                  <option>Delivered</option>
                </Form.Select>
              </Form.Group>
              <Button type="submit" className="w-100">Save Sales Order</Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={8}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Sales Orders</h3>
            {error && <Alert variant="warning">{error}</Alert>}
            <SearchBar search={search} setSearch={setSearch} filter="" setFilter={() => {}} />
            <EntityTable
              columns={[
                { key: "order_number", label: "Order #" },
                { key: "quotation_number", label: "Quotation #" },
                { key: "order_date", label: "Order Date" },
                { key: "status", label: "Status" }
              ]}
              rows={orders}
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default OrdersPage;
