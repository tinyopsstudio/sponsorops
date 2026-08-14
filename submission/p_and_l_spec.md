# SponsorOps P&L specification

Period: 2026-05-19 through 2026-08-17

Accounting basis: cash basis, as required by the official template. Revenue is recorded when cash is received and expenses when cash is paid.

## Monthly P&L inputs

| Line item | May 2026 | Jun 2026 | Jul 2026 | Aug 2026 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Arms-length sponsored-content revenue | $0.00 | $0.00 | $99.00 | $0.00 | formula: SUM(months) |
| Related-party revenue | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| Total revenue | formula | formula | formula | formula | formula: SUM(months) |
| Hosting and Google Cloud | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| AI API usage directly invoiced to SponsorOps | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| Contractor and employee expense | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| Marketing and customer acquisition | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| Other direct operating expense | $0.00 | $0.00 | $0.00 | $0.00 | formula: SUM(months) |
| Total expenses | formula | formula | formula | formula | formula: SUM(months) |
| Net income | formula: revenue minus expenses | formula | formula | formula | formula: SUM(months) |

## Explanations

- July revenue is the settled payment for invoice TOS-20260713-ARGENDON-001, received 2026-07-23 from one arms-length advertiser customer.
- No project-specific cash labor, contractor, marketing, or customer-acquisition expense was incurred during the period.
- Founder/member and AI-agent operating time did not create a project-specific cash invoice and is disclosed as contributed, unpaid operating effort.
- Google Cloud will use free-tier or trial credits. The required zero-dollar cost table or invoice will be included when available.
- The $95 Troutmate acquisition payment and $12 domain-transfer deposit were incurred on 2026-05-12, before the submission period. They are disclosed as pre-period resources and excluded from this P&L.
- Other TinyOps expenses unrelated to SponsorOps are excluded.

## Authoritative sources

- Revenue ledger: `agent/finance/transactions.csv`, settled revenue row dated 2026-07-23
- Private payment evidence: `agent/treasury/evidence/argendon_payment_claim_20260723/image.png`
- Corporate ID: `agent/treasury/formation_docs/articles_of_organization.pdf`
- XPRIZE P&L template: https://docs.google.com/spreadsheets/d/1pAJrEMo7_QID6V62sA4C8XwGBHkxDTVX3wtYNE2fulI/edit?usp=sharing
- Downloaded original SHA-256: `47761637573c3c52646d1e1df6d23fc1fad818b4bb6e2e62409e6166a2e06bcf`

## Workbook controls to implement

- monthly totals use formulas
- total revenue equals arms-length plus related-party revenue
- total expenses equals all expense lines
- net income equals total revenue minus total expenses
- marketing spend is shown separately even when zero
- model status is PASS only when revenue, expense, and net-income checks reconcile to zero delta
