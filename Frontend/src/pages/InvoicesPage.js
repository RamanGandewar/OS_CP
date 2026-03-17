import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import SearchBar from "../components/SearchBar";
import { invoicesApi, ordersApi } from "../utils/api";

const initialForm = {
  sales_order_id: "",
  invoice_number: "",
  amount: "",
  due_date: "",
  payment_status: "Pending"
};

function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [orders, setOrders] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const loadInvoices = () => {
    invoicesApi
      .list(search)
      .then((response) => {
        setInvoices(response.data);
        setError("");
      })
      .catch(() => {
        setInvoices([]);
        setError("Invoices could not be loaded because the backend is unavailable.");
      });
  };

  useEffect(() => {
    ordersApi.list().then((response) => setOrders(response.data)).catch(() => setOrders([]));
  }, []);

  useEffect(() => {
    loadInvoices();
  }, [search]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await invoicesApi.create({
        ...form,
        sales_order_id: Number(form.sales_order_id),
        amount: Number(form.amount)
      });
      setForm(initialForm);
      setError("");
      loadInvoices();
    } catch (err) {
      setError(err.response?.data?.error || "Invoice could not be saved.");
    }
  };

  return (
    <Row className="g-4">
      <Col lg={4}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Generate Invoice</h3>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Sales Order</Form.Label>
                <Form.Select value={form.sales_order_id} onChange={(event) => setForm({ ...form, sales_order_id: event.target.value })}>
                  <option value="">Select order</option>
                  {orders.map((order) => (
                    <option key={order.id} value={order.id}>{order.order_number}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Invoice Number</Form.Label>
                <Form.Control value={form.invoice_number} onChange={(event) => setForm({ ...form, invoice_number: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Amount</Form.Label>
                <Form.Control type="number" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Due Date</Form.Label>
                <Form.Control type="date" value={form.due_date} onChange={(event) => setForm({ ...form, due_date: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Payment Status</Form.Label>
                <Form.Select value={form.payment_status} onChange={(event) => setForm({ ...form, payment_status: event.target.value })}>
                  <option>Pending</option>
                  <option>Paid</option>
                  <option>Overdue</option>
                </Form.Select>
              </Form.Group>
              <Button type="submit" className="w-100">Save Invoice</Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={8}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Invoices</h3>
            {error && <Alert variant="warning">{error}</Alert>}
            <SearchBar search={search} setSearch={setSearch} filter="" setFilter={() => {}} />
            <EntityTable
              columns={[
                { key: "invoice_number", label: "Invoice #" },
                { key: "order_number", label: "Order #" },
                { key: "amount", label: "Amount" },
                { key: "payment_status", label: "Payment Status" }
              ]}
              rows={invoices}
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default InvoicesPage;
