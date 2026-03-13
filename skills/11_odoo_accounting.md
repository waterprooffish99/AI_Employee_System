# Odoo Accounting - Agent Skill for Business Accounting

## Overview

Complete accounting operations via Odoo Community 19+ integration.

## Capabilities

- Create and send invoices
- Track payments
- Generate financial reports
- Manage customers and vendors
- Bank reconciliation

## Usage

### Create Invoice

```
Create invoice for Client ABC:
- Item 1: Consulting services - $500
- Item 2: Software license - $200
Payment terms: Net 30
Send to: billing@clientabc.com
```

### Get Outstanding Invoices

```
Show all outstanding invoices over $1000
```

### Register Payment

```
Register payment for invoice INV-2026-001:
Amount: $500
Method: Bank transfer
Date: 2026-01-07
```

### Generate Financial Report

```
Generate Profit & Loss report for Q1 2026
```

### Add Customer

```
Add new customer:
Name: XYZ Corporation
Email: contact@xyz.com
Phone: +1-555-1234
Type: customer
```

## Response Format

### Invoice Creation
```json
{
  "success": true,
  "invoice_id": 12345,
  "invoice": {
    "name": "INV/2026/0001",
    "partner_id": ["Client ABC"],
    "amount_total": 700.00,
    "state": "draft"
  }
}
```

### Outstanding Invoices
```markdown
| Invoice | Customer | Amount | Due Date |
|---------|----------|--------|----------|
| INV-001 | Client A | $500   | Jan 15   |
| INV-002 | Client B | $750   | Jan 20   |
```

## Approval Workflow

All accounting actions require approval:
1. Create action plan
2. Move to `/Pending_Approval/`
3. User reviews and approves
4. Execute via Odoo MCP
5. Log to audit trail

## Financial Reports

### Profit & Loss
- Revenue
- Cost of Goods Sold
- Gross Profit
- Operating Expenses
- Net Income

### Balance Sheet
- Assets (Current, Fixed)
- Liabilities (Current, Long-term)
- Equity

### Cash Flow
- Operating Activities
- Investing Activities
- Financing Activities

## Error Handling

- **Connection Failed**: Retry 3 times, then alert
- **Authentication Error**: Request credential refresh
- **Validation Error**: Show specific field errors
- **Duplicate Detected**: Warn and request confirmation

## Security

- All actions logged to audit trail
- DRY_RUN mode for testing
- Approval required for amounts > $1000
- No direct database access

## Integration

Works with:
- CEO Briefing generator
- Dashboard updater
- Email MCP (for sending invoices)

---

*Skill Version: 1.0.0 | Gold Tier*
