import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import SearchBar from "../components/SearchBar";
import { enquiriesApi, quotationsApi } from "../utils/api";

const initialForm = {
  enquiry_id: "",
  quotation_number: "",
  amount: "",
  valid_until: "",
  status: "Draft"
};

function QuotationsPage() {
  const [quotations, setQuotations] = useState([]);
  const [enquiries, setEnquiries] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const loadQuotations = () => {
    quotationsApi
      .list(search)
      .then((response) => {
        setQuotations(response.data);
        setError("");
      })
      .catch(() => {
        setQuotations([]);
        setError("Quotations could not be loaded because the backend is unavailable.");
      });
  };

  useEffect(() => {
    enquiriesApi.list().then((response) => setEnquiries(response.data)).catch(() => setEnquiries([]));
  }, []);

  useEffect(() => {
    loadQuotations();
  }, [search]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await quotationsApi.create({
        ...form,
        enquiry_id: Number(form.enquiry_id),
        amount: Number(form.amount)
      });
      setForm(initialForm);
      setError("");
      loadQuotations();
    } catch (err) {
      setError(err.response?.data?.error || "Quotation could not be saved.");
    }
  };

  return (
    <Row className="g-4">
      <Col lg={4}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Generate Quotation</h3>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Enquiry</Form.Label>
                <Form.Select value={form.enquiry_id} onChange={(event) => setForm({ ...form, enquiry_id: event.target.value })}>
                  <option value="">Select enquiry</option>
                  {enquiries.map((enquiry) => (
                    <option key={enquiry.id} value={enquiry.id}>{enquiry.product} - {enquiry.customer_name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Quotation Number</Form.Label>
                <Form.Control value={form.quotation_number} onChange={(event) => setForm({ ...form, quotation_number: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Amount</Form.Label>
                <Form.Control type="number" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Valid Until</Form.Label>
                <Form.Control type="date" value={form.valid_until} onChange={(event) => setForm({ ...form, valid_until: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Status</Form.Label>
                <Form.Select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                  <option>Draft</option>
                  <option>Sent</option>
                  <option>Approved</option>
                  <option>Rejected</option>
                </Form.Select>
              </Form.Group>
              <Button type="submit" className="w-100">Save Quotation</Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      <Col lg={8}>
        <Card className="shadow-sm">
          <Card.Body>
            <h3 className="mb-3">Quotations</h3>
            {error && <Alert variant="warning">{error}</Alert>}
            <SearchBar search={search} setSearch={setSearch} filter="" setFilter={() => {}} />
            <EntityTable
              columns={[
                { key: "quotation_number", label: "Quotation #" },
                { key: "enquiry_product", label: "Product" },
                { key: "amount", label: "Amount" },
                { key: "status", label: "Status" }
              ]}
              rows={quotations}
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
}

export default QuotationsPage;
