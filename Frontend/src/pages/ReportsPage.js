import React, { useEffect, useState } from "react";
import { Alert, Card, Col, Row } from "react-bootstrap";

import EntityTable from "../components/EntityTable";
import { reportsApi } from "../utils/api";

function ReportsPage() {
  const [data, setData] = useState({
    enquiries: [],
    quotations: [],
    sales_orders: []
  });
  const [error, setError] = useState("");

  useEffect(() => {
    reportsApi
      .summary()
      .then((response) => {
        setData(response.data);
        setError("");
      })
      .catch(() => {
        setData({ enquiries: [], quotations: [], sales_orders: [] });
        setError("Reports could not be loaded because the backend is unavailable.");
      });
  }, []);

  return (
    <div>
      <h2 className="mb-4">Basic Reports</h2>
      {error && <Alert variant="warning">{error}</Alert>}
      <Row className="g-4">
        <Col xs={12}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4>Enquiries</h4>
              <EntityTable
                columns={[
                  { key: "customer_name", label: "Customer" },
                  { key: "product", label: "Product" },
                  { key: "status", label: "Status" }
                ]}
                rows={data.enquiries}
              />
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4>Quotations</h4>
              <EntityTable
                columns={[
                  { key: "quotation_number", label: "Quotation #" },
                  { key: "amount", label: "Amount" },
                  { key: "status", label: "Status" }
                ]}
                rows={data.quotations}
              />
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12}>
          <Card className="shadow-sm">
            <Card.Body>
              <h4>Sales Orders</h4>
              <EntityTable
                columns={[
                  { key: "order_number", label: "Order #" },
                  { key: "quotation_number", label: "Quotation #" },
                  { key: "status", label: "Status" }
                ]}
                rows={data.sales_orders}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ReportsPage;
