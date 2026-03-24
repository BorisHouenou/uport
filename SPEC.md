# Uportai — Technical Specification v1.0

**Project:** Rules of Origin (RoO) Compliance Engine
**Working directory:** `/Users/borishouenou/Uportai`
**GitHub:** https://github.com/BorisHouenou/uport

---

## 1. Product Context

Uportai automates Rules of Origin compliance for SME exporters. The average SME loses $134K/year to unclaimed preferential tariffs due to incorrect or missing origin certification. Uportai eliminates that gap.

**Phase 1 — Canada** (6 months): CUSMA/USMCA, CETA, CPTPP. Positioned to qualify for CanExport SME federal grants. First 50 design partners targeted from Canadian Trade Commissioner Service network.

**Phase 2 — Global** (12–24 months): EU (EUR.1, REX), AfCFTA, ASEAN, Mercosur, bilateral FTAs. Full multi-agreement arbitrage (best available preferential rate).

---

## 2. Core Engine Requirements

| Module | Description |
|---|---|
| **HS Classifier** | AI-assisted HS code assignment from product description / BOM line items. Confidence scoring. Human-in-the-loop for edge cases. |
| **Origin Resolver** | Per-agreement rule evaluation: Tariff Shift (TS), Regional Value Content (RVC — Build-Down, Build-Up, Net Cost), Wholly Obtained. Multi-agreement arbitrage. |
| **BOM Analyzer** | Parses uploaded BOMs (CSV, Excel, ERP export). Maps each input to origin country + HS code. Calculates cumulation where applicable. |
| **Certificate Generator** | Produces CUSMA Statement on Origin, EUR.1, Form A, and generic CO. PDF + structured data output. Digital signature ready. |
| **Supplier Portal** | Self-serve portal for suppliers to submit origin declarations. Reminder workflows. Expiry tracking. |
| **RAG Compliance Assistant** | LLM chat grounded in indexed trade agreement texts (CUSMA, CETA, CPTPP, AfCFTA annexes). Cites article + annex. |
| **Savings Calculator** | Real-time ROI dashboard. Compares MFN rate vs preferential rate per shipment. Aggregates annual savings. |
| **Audit Vault** | Immutable audit log. Document storage with retention policies. Export-ready for customs authority review. |

---

## 3. Technology Stack

**Frontend**
- Next.js 14 (App Router, TypeScript, strict mode)
- Tailwind CSS + shadcn/ui component library
- Zustand (client state) + React Query (server state)
- Deployed on Vercel (Phase 1) → AWS CloudFront (Phase 2)

**Backend**
- FastAPI (Python 3.12) — async, OpenAPI auto-docs
- Celery + Redis for async job queue (BOM processing, certificate generation, LLM calls)
- PostgreSQL 16 (primary DB) + pgvector extension (embeddings)
- Redis 7 (cache + queues)
- Alembic (migrations)

**AI / GenAI**
- Primary LLM: `claude-sonnet-4-6` via Anthropic SDK (tool use + structured output)
- Embeddings: `voyage-3` (Voyage AI) or `text-embedding-3-small` (OpenAI)
- RAG pipeline: LlamaIndex over pgvector — trade agreement texts + tariff schedules
- Agents: LangGraph for multi-step origin determination workflows
- Fine-tuning data pipeline: collect human corrections → periodic fine-tune loop

**Auth & Multi-tenancy**
- Clerk (auth provider) — org-level multi-tenancy, SSO-ready
- Row-level security in PostgreSQL per `org_id`

**Payments**
- Stripe — subscription tiers (Starter / Growth / Enterprise) + usage-based billing for certificate volume

**Integrations (Phase 1)**
- QuickBooks Online, NetSuite, SAP B1 (ERP — product/BOM data)
- Flexport, Shipbob (logistics)
- Stripe (payments)
- Zapier / Make (no-code connector)
- Webhooks (outbound events: certificate issued, declaration expired, compliance alert)

**Infrastructure**
- Local: Docker Compose (all services)
- Production: AWS ECS Fargate (API) + RDS PostgreSQL + ElastiCache Redis + S3 (document vault) + CloudFront
- IaC: Terraform (modules for each service)
- CI/CD: GitHub Actions (lint → test → build → deploy)

**Security**
- SOC 2 Type II controls from day 1 (access logs, encryption at rest/transit, least privilege)
- PIPEDA (Canada) + GDPR (EU) compliant data handling
- AES-256 encryption for stored documents
- TLS 1.3 everywhere
- OWASP Top 10 mitigations built into API layer
- Dependency scanning (Snyk), SAST (CodeQL), secret scanning (Gitleaks)

---

## 4. Monorepo Structure

```
Uportai/
├── apps/
│   ├── web/                  # Next.js 14 frontend
│   └── api/                  # FastAPI backend
├── packages/
│   ├── roo-engine/           # Pure Python: origin determination logic
│   ├── ai-agents/            # LangGraph agents + RAG pipeline
│   ├── certificate-gen/      # PDF certificate generator
│   └── integrations/         # ERP / logistics connectors
├── infra/
│   ├── terraform/
│   └── docker/
├── data/
│   └── trade-agreements/     # Indexed FTA texts + tariff schedules
├── scripts/                  # Seed, migration, ingestion scripts
└── .github/workflows/
```

---

## 5. Database Schema (Key Tables)

```sql
organizations       (id, name, country, plan, created_at)
users               (id, org_id, clerk_id, role, email, created_at)
products            (id, org_id, hs_code, description, origin_country, created_at)
bom_items           (id, product_id, component_id, quantity, unit_cost, origin_country)
shipments           (id, org_id, destination_country, incoterm, status, created_at)
origin_determinations (id, shipment_id, agreement, rule_applied, result, confidence, reasoning, created_at)
certificates        (id, shipment_id, type, pdf_url, issued_at, valid_until, digital_sig)
supplier_declarations (id, supplier_id, product_id, origin, valid_from, valid_until, doc_url)
audit_events        (id, entity_type, entity_id, action, actor_id, payload, created_at)
trade_agreements    (id, code, name, parties[], effective_date)
roo_rules           (id, agreement_id, hs_chapter, hs_heading, rule_type, rule_text, value_threshold)
```

---

## 6. AI Agent Architecture

```
User uploads BOM / product description
        │
        ▼
[HS Classification Agent]
  - Tool: search_tariff_schedule(description)
  - Tool: validate_hs_code(hs_code, country)
  - Output: hs_code + confidence + alternatives
        │
        ▼
[Origin Rule Fetcher]
  - Tool: get_applicable_agreements(origin, destination)
  - Tool: get_roo_rules(hs_code, agreement_id)
  - Output: list of applicable rules per agreement
        │
        ▼
[Origin Determination Agent]
  - Tool: calculate_rvc(bom, method)
  - Tool: check_tariff_shift(input_hs_codes, output_hs_code, rule)
  - Tool: check_wholly_obtained(origin_country, product_type)
  - Output: pass/fail per agreement + reasoning
        │
        ▼
[Certificate Drafting Agent]
  - Tool: fetch_certificate_template(cert_type)
  - Tool: fill_certificate(determination, shipment_data)
  - Tool: generate_pdf(filled_template)
  - Output: signed PDF + structured JSON
        │
        ▼
[Compliance QA Agent] (human-in-loop gate for low confidence)
  - Flags determinations below confidence threshold for human review
```

---

## 7. Delivery Sprints

| Sprint | Deliverable |
|---|---|
| 1–2 | Monorepo scaffold, Docker Compose, DB schema + migrations, Clerk auth, base FastAPI structure, CI/CD |
| 3–4 | HS classifier agent, RVC/TS calculation engine, BOM upload + parsing, origin determination API |
| 5–6 | Dashboard UI, BOM upload flow, origin result display, PDF certificate generation (CUSMA first) |
| 7–8 | Trade agreement RAG pipeline, compliance chat UI, QuickBooks integration, Stripe billing |
| 9–10 | SOC 2 controls, supplier portal, savings dashboard, Canada launch |

---

## 8. Key Files (will be populated during development)

- `apps/api/main.py` — FastAPI entrypoint
- `apps/api/routers/` — route modules (origin, certificates, bom, agreements, suppliers)
- `apps/web/app/` — Next.js App Router pages
- `packages/roo-engine/engine.py` — core RVC/TS logic
- `packages/ai-agents/hs_classifier.py` — HS code agent
- `packages/ai-agents/origin_agent.py` — origin determination agent
- `packages/ai-agents/rag_assistant.py` — RAG compliance assistant
- `packages/certificate-gen/generator.py` — PDF certificate generator
- `infra/docker/docker-compose.yml` — local dev environment
- `.github/workflows/ci.yml` — CI/CD pipeline
