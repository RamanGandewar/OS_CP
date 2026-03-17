# Database Schema Diagram

```text
users (1) -----------< enquiries >----------- (1) customers
                          |
                          v
                    quotations
                          |
                          v
                    sales_orders
                          |
                          v
                       invoices
```

## Tables

- `users(id, username, password, email, role, created_at)`
- `customers(id, name, email, phone, company, address, created_at)`
- `enquiries(id, customer_id, product, description, status, assigned_to, created_at)`
- `quotations(id, enquiry_id, quotation_number, amount, valid_until, status, created_at)`
- `sales_orders(id, quotation_id, order_number, order_date, delivery_date, status)`
- `invoices(id, sales_order_id, invoice_number, amount, due_date, payment_status)`
