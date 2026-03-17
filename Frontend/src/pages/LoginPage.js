import React, { useState } from "react";
import { Alert, Button, Card, Col, Container, Form, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

import { authApi } from "../utils/api";

function LoginPage({ setUser }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "user1", password: "password123" });
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await authApi.login(form);
      setUser(response.data.user);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <Container className="min-vh-100 d-flex align-items-center justify-content-center">
      <Row className="w-100 justify-content-center">
        <Col md={5} lg={4}>
          <Card className="shadow-lg border-0">
            <Card.Body className="p-4">
              <h2 className="mb-3 text-center">SalesCRM Login</h2>
              <p className="text-muted text-center">Use seeded credentials to access the platform.</p>
              {error && <Alert variant="danger">{error}</Alert>}
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    value={form.username}
                    onChange={(event) => setForm({ ...form, username: event.target.value })}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    value={form.password}
                    onChange={(event) => setForm({ ...form, password: event.target.value })}
                  />
                </Form.Group>
                <Button type="submit" className="w-100">Login</Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default LoginPage;
