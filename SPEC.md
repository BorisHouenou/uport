# Uportai — Technical Product Specification v2.0

**Product:** Rules of Origin (RoO) Compliance Engine
**Founder:** Boris Houenou
**Working directory:** `/Users/borishouenou/Uportai`
**GitHub:** https://github.com/BorisHouenou/uport
**Stage:** Pre-seed / active development
**Current date:** May 2026

---

## 1. Executive Summary

Every year, exporters worldwide forfeit an estimated **$180 billion** in preferential tariff savings because they cannot prove where their products come from. Rules of Origin compliance — the legal determination of whether a product qualifies for reduced or zero-duty treatment under a Free Trade Agreement — is one of the most technically dense, time-consuming, and error-prone processes in global trade. It sits at the intersection of customs law, product engineering, and supply chain management. No software has solved it end-to-end.

**Uportai is the AI-native compliance infrastructure layer that eliminates this gap.**

We are building the API-first, embeddable Rules of Origin engine that any exporter, freight forwarder, customs broker, or trade platform can plug into. Think Stripe for trade compliance: a clean API, a white-label portal, subscription pricing, and an AI backbone that gets smarter with every determination it makes.

Phase 1 targets Canadian SME exporters — the 47,000+ firms trading under CUSMA, CETA, and CPTPP — who collectively lose an estimated **$6.3 billion annually** in unclaimed preferential tariffs. The average affected SME loses $134,000 per year, not because the savings aren't available, but because the compliance process is too complex to operate without a specialist.

The architecture is agreement-agnostic by design. After Canada, the same engine expands to AfCFTA (55 countries, $3.4T GDP), EU bilateral agreements, ASEAN, CPTPP non-Canada members, and Mercosur — without re-engineering the core. Every new agreement is a data ingestion problem, not a software development problem.

Uportai's defensible moat is its proprietary training corpus. Each human correction to an AI-generated origin determination becomes a labeled training example. Each supplier declaration collected becomes a verified ground-truth data point. The accuracy advantage compounds over time in a way that cannot be replicated by a competitor starting from scratch.

This document is the definitive technical and product specification for the Uportai compliance engine. It covers product architecture, AI system design, database schema, go-to-market, and delivery roadmap.

---

## 2. Problem

### 2.1 The Compliance Gap

Free Trade Agreements eliminate or reduce tariffs on qualifying goods — but only for goods that can prove their origin. This proof, formalized as a Certificate of Origin or origin declaration, requires the exporter to demonstrate that their product meets the specific Rules of Origin defined in each agreement. These rules vary by agreement, by product category (HS chapter), and sometimes by trade corridor.

The problem is structural:

- **170+ active FTAs worldwide**, each with its own RoO methodology. CUSMA uses Regional Value Content (RVC) with three calculation methods. CETA uses tariff shift rules with product-specific exceptions. AfCFTA uses a tiered approach still being finalized country-by-country. No single team can hold this in their heads.
- **RoO analysis requires BOM-level data** — input materials, their HS codes, their origin countries, and their costs. Most SMEs don't maintain this data in a compliance-ready format.
- **Errors trigger penalties** that dwarf the savings: customs audits, retroactive duty recovery, shipment holds, and reputational damage with trading partners.
- **Manual compliance costs $15,000–$50,000 per year** in specialist consultant fees for an SME doing meaningful export volume. Enterprise firms spend millions.
- **Existing software is designed for large enterprises**, not exportable as an API, and requires months of implementation.

### 2.2 Why Existing Solutions Fail

Thomson Reuters ONESOURCE, Amber Road (now E2open), and Descartes are the dominant incumbents. They share the same failure modes:

| Failure mode | Detail |
|---|---|
| Enterprise lock-in | 6–18 month implementation cycles, $200K+ annual contracts. SMEs are locked out entirely. |
| Static rule databases | Rules are coded by human analysts and updated quarterly at best. FTA amendments, transitional periods, and new protocols are perpetually stale. |
| No AI augmentation | Classification and determination are rule-based expert systems. No machine learning, no confidence scoring, no improving accuracy curve. |
| Monolithic architecture | Cannot be embedded, licensed as an API, or white-labeled. Designed to be the destination, not a component. |
| No network effects | Each customer's data improves nothing. No shared learning, no compound value over time. |

Newer entrants (Zonos, Avalara for trade) solve adjacent problems (duty calculation, DDP pricing) but do not perform origin determination — they assume the product already qualifies.

### 2.3 Why Now

Three structural forces have converged:

1. **FTA proliferation.** The number of active FTAs has tripled since 2000. CUSMA replaced NAFTA in 2020 with significantly revised RoO. AfCFTA launched in 2021. CPTPP expansion continues. Each new agreement creates a new compliance surface for every exporter.

2. **LLM capability inflection.** Reasoning over dense legal text — the specific skill RoO compliance requires — became tractable with models like Claude Sonnet in 2024. The combination of structured tool use, retrieval-augmented generation, and confidence-calibrated output makes AI-native RoO determination viable for the first time.

3. **Geopolitical supply chain pressure.** Tariff volatility (US-China, US-Canada), nearshoring, and friend-shoring are forcing companies to re-examine their sourcing strategies. Origin optimization — structuring supply chains to maximize preferential access — is now a CFO-level priority, not just a customs team problem.

---

## 3. Solution

### 3.1 Product Narrative

Uportai is not a compliance checklist tool. It is an **origin intelligence engine** — a system that ingests product and supply chain data, reasons over the applicable legal frameworks, makes a defensible determination, generates the required documentation, and learns from every case it processes.

The user experience is designed around the workflow of an SME export manager, not a customs specialist. A user uploads a bill of materials or connects their ERP. Uportai classifies every input by HS code, identifies which FTAs apply to their trade corridor, runs the origin determination for each applicable agreement, calculates the preferential tariff savings, and generates the certificate — all in minutes, with a full audit trail and human-review escalation for low-confidence cases.

The same capability is exposed as a REST API so freight forwarders, customs software platforms, and ERP vendors can embed origin determination natively into their own products. This is the API licensing layer that creates the platform business, not just the SaaS business.

### 3.2 The "Stripe for RoO" Positioning

Stripe did not invent payment processing. It made it embeddable, developer-friendly, and reliable enough to build on. The result was a platform that captured a disproportionate share of the value in digital commerce infrastructure.

Uportai makes the same bet on trade compliance infrastructure:

- **API-first**: every product feature is a callable API endpoint, documented, versioned, and available to embed
- **Embeddable**: white-label supplier portal, embeddable certificate widget, React component library
- **Reliable**: confidence-scored output with human escalation, full audit trail, immutable records
- **Improving**: every determination trains the next one — accuracy compounds as volume grows

The target enterprise customer is not the SME directly. It is the platform that serves 10,000 SMEs: customs brokers, freight forwarders, trade finance platforms, government trade portals. One API integration, 10,000 users.

### 3.3 Differentiation Summary

| Capability | Uportai | ONESOURCE | Amber Road | Zonos |
|---|---|---|---|---|
| SME-accessible pricing | Yes | No | No | Partial |
| API-first / embeddable | Yes | No | No | Partial |
| AI-native determination | Yes | No | No | No |
| Multi-agreement arbitrage | Yes | Yes | Yes | No |
| Proprietary training loop | Yes | No | No | No |
| Supplier portal (self-serve) | Yes | Partial | Yes | No |
| Africa / AfCFTA coverage | Yes (Phase 2) | No | Partial | No |
| Time to first determination | Minutes | Months | Months | N/A |

---

## 4. Market

### 4.1 Total Addressable Market

Global trade compliance is a **$180B+ annual market**, encompassing customs management software, compliance consulting, duty drawback services, and origin certification. The software segment alone — where Uportai plays — is estimated at $8–12B and growing at 12% CAGR, driven by FTA proliferation and trade digitalization mandates.

### 4.2 Serviceable Addressable Market — Phase 1 (Canada)

Canada has approximately **47,000 SME exporters** actively trading under preferential FTAs (CUSMA, CETA, CPTPP). Based on Canadian Border Services Agency and Statistics Canada data:

- Average annual lost preferential tariff savings per SME: **$134,000**
- Addressable SME segment (those with RoO complexity): **~18,000 firms**
- At $600 average annual contract value (blended): **$10.8M ARR** at full Canada penetration
- At $3,600 average annual contract value (Growth tier, realistic mid-market): **$64.8M ARR**

Canada is a beachhead, not the destination.

### 4.3 Serviceable Addressable Market — Phase 2 (Global)

| Region | FTA framework | SME exporters | Est. SAM |
|---|---|---|---|
| EU bilateral agreements | EUR.1, REX, cumulation | ~200,000 | $720M ARR |
| AfCFTA | Protocol on Trade in Goods | ~500,000 (growing) | $1.8B ARR (emerging) |
| ASEAN | ATIGA, bilateral | ~150,000 | $540M ARR |
| CPTPP (non-Canada) | RVC/TS unified | ~80,000 | $288M ARR |
| Mercosur | Bilateral agreements | ~60,000 | $216M ARR |

Global SAM at Phase 2 maturity: **>$3.5B ARR** (software layer only, excluding API licensing to platforms).

### 4.4 Serviceable Obtainable Market

12-month target: **150 paying customers**, average ACV $4,800 (mix of Starter and Growth). ARR target at month 12: **$720K**. This is achievable through the Canadian Trade Commissioner Service design partner pipeline without paid acquisition.

24-month target: **1,200 paying customers** plus **3 platform API licensing deals** at $60K–$150K ACV each. ARR target at month 24: **$5.8M**.

---

## 5. Competitive Landscape

### 5.1 Incumbents

**Thomson Reuters ONESOURCE Trade** is the market leader. It serves Fortune 500 firms with a comprehensive (and comprehensively expensive) trade management suite. Implementation takes 6–18 months. Annual contracts start at $200K. It has no AI-native origin determination, no SME offering, and no API licensing model. Its RoO database is maintained by human analysts and updated on quarterly cycles — a structural accuracy ceiling.

**Amber Road (E2open)** operates in the same enterprise segment. After the E2open acquisition, product investment has slowed. Strong in landed cost calculation; weaker in RoO-specific determination. Not embeddable. No machine learning layer.

**Descartes Systems** provides a broader trade compliance platform (denied party screening, export control, customs filing). RoO determination is a feature within a larger suite, not a dedicated product. Designed for freight forwarders and customs brokers at enterprise scale.

**Avalara / Zonos** focus on duty calculation and DDP (Delivered Duty Paid) pricing for e-commerce. They calculate duty at the border based on HS code and country — they do not perform origin determination and explicitly do not certify preferential treatment.

### 5.2 Why Uportai Wins

The incumbents are not building what we are building. They cannot. Their business models require expensive human implementation services. Their architectures predate LLMs. Their customer acquisition depends on long sales cycles and enterprise procurement. None of them can launch an SME product at $299/month with a 5-minute onboarding flow.

Our advantage is structural, not just executional:

1. **LLM-native from day one.** We are not retrofitting AI onto a rules database. The AI is the engine. Every architectural decision — the agent graph, the RAG pipeline, the confidence model — is designed around LLM capabilities.

2. **Data flywheel.** Every human correction to an AI determination is a labeled training example. At 1,000 monthly determinations, we are generating training data at a rate no incumbent can match without building the same product.

3. **Agreement-agnostic architecture.** Adding a new FTA requires ingesting and indexing the agreement text, mapping HS-level RoO rules to our rule schema, and testing the determination logic. It does not require re-engineering the engine. This is a weeks-long data operation, not a months-long engineering project.

4. **Platform business model.** We are not just selling to exporters. We are licensing the API to platforms that serve exporters. A freight forwarder with 5,000 SME clients represents one contract and 5,000 end users. The incumbent players have no product for this.

---

## 6. Product Modules

### 6.1 HS Classifier

Assigns Harmonized System (HS) codes to products from natural language descriptions, bill of materials line items, or product catalog data. The classifier uses a fine-tuned classification model grounded in the current WCO tariff schedule, with retrieval over historical classification rulings (CBSA, US CBP, EU Customs) to surface precedent.

Output includes a primary HS code, confidence score (0–1.0), alternative codes where confidence is close, and a natural-language explanation of the classification rationale. Determinations below the confidence threshold route to a human review queue. All human corrections feed back into the training pipeline.

Supports 6-digit (WCO standard) and 8/10-digit national subheadings for Canada (CBSA), US (HTS), and EU (CN).

### 6.2 Origin Resolver

The core engine. Given a product's HS code, BOM inputs with their origin countries and costs, and a target trade agreement, the resolver applies the specific product rule to determine whether the product qualifies for preferential treatment.

Supported rule types:
- **Wholly Obtained (WO)**: animal, vegetable, mineral products sourced and manufactured entirely in one country
- **Tariff Shift (TS)**: change in HS chapter, heading, or subheading between inputs and output, per agreement-specific rule
- **Regional Value Content (RVC)**: minimum local/regional value threshold, calculated via Build-Down, Build-Up, or Net Cost method depending on agreement
- **Specific Process Rules**: technical operations specified in product annexes (e.g., weaving, dyeing, assembly)
- **Combinations**: rules that require both tariff shift AND minimum RVC

Multi-agreement arbitrage: given a destination country with multiple applicable FTAs, the resolver evaluates all applicable agreements and returns the optimal one (lowest effective duty rate) alongside the full determination for each.

### 6.3 BOM Analyzer

Ingests bill of materials files in CSV, Excel, or ERP export format (QuickBooks, NetSuite, SAP B1). Each line item is processed to extract: component description, quantity, unit cost, supplier identity, and supplier-declared origin country.

The analyzer runs HS classification on each input component, flags missing or inconsistent origin declarations, calculates the RVC denominator and numerator for each applicable method, identifies cumulation opportunities (where permitted by agreement — e.g., CETA diagonal cumulation with EU countries), and outputs a structured BOM enrichment report.

Supports version-tracked BOM snapshots: a new BOM version triggers a re-determination, with a diff view showing which components changed and how the origin qualification was affected.

### 6.4 Certificate Generator

Generates legally compliant certificates of origin in the correct format for each agreement:

| Certificate type | Agreement | Format |
|---|---|---|
| CUSMA Statement on Origin | CUSMA/USMCA | Producer/exporter self-declaration |
| EUR.1 Movement Certificate | CETA, EU bilateral | Official form, customs-stampable |
| Form A (GSP) | GSP schemes | Official form |
| REX Declaration | EU REX scheme | Self-declaration with REX number |
| AfCFTA Certificate of Origin | AfCFTA | Protocol-defined format |
| Generic Certificate of Origin | Non-FTA, chamber-certified | ISO 17442 compliant |

Output is PDF (print-ready, digitally signed) plus structured JSON for downstream system consumption. Certificates are linked to their underlying origin determination record, creating an unbreakable audit chain. Digital signature is implemented via Docusign or in-house PKI.

Certificates stored in the Audit Vault with configurable retention (minimum 5 years, matching Canadian customs record-keeping requirements).

### 6.5 Supplier Portal

A branded, self-serve web portal where exporters invite their suppliers to submit and maintain origin declarations. The portal handles:

- Supplier onboarding (email-based, no account required for suppliers)
- Declaration submission (product-level and shipment-level)
- Document upload (supporting evidence: manufacturer's declarations, cost breakdowns)
- Automated reminders at 90/30/7 days before declaration expiry
- Supplier audit history and declaration version control

The supplier portal is the network effect driver. Each supplier who joins the portal contributes verified origin data that improves determination accuracy for every other exporter using the same supplier. This is the data network effect that compounds with scale.

White-labeling available for Enterprise tier customers (customs brokers, freight forwarders) who want to offer the portal under their own brand.

### 6.6 RAG Compliance Assistant

An LLM-powered compliance assistant grounded in a curated, indexed corpus of trade agreement texts, product-specific annexes, customs authority guidance, and binding rulings. The assistant can answer natural language questions about origin rules, walk through hypothetical scenarios, and explain determination rationale in plain English.

Every response cites the specific article, annex, and paragraph in the source agreement. The assistant does not hallucinate legal text — all cited content is retrieved from the indexed corpus, not generated. When a question falls outside the indexed corpus, the assistant flags this explicitly rather than speculating.

The RAG corpus is updated on a rolling basis as new FTA guidance, transitional provisions, and customs authority rulings are published. Agreement updates trigger a re-ingestion and re-indexing pipeline with version control, so historical determinations remain traceable to the agreement text version that was in effect at the time.

### 6.7 Savings Calculator

A real-time ROI dashboard that quantifies the financial value of preferential tariff access. For each shipment or product, the calculator displays:

- MFN (Most Favoured Nation) duty rate — the default tariff without FTA
- Applicable preferential rate under each qualifying FTA
- Duty savings per shipment (in both absolute currency and percentage)
- Annualized savings projection based on shipment frequency
- Cumulative savings across all shipments to date
- Payback period: how many shipments until the Uportai subscription cost is recovered (typically 1–3 shipments for an active SME exporter)

The savings calculator serves a dual purpose: it is the primary acquisition hook in outbound sales ("you left $134K on the table last year"), and it is the retention anchor inside the product ("we've saved you $312K this year").

### 6.8 Audit Vault

An immutable, tamper-evident record store for all compliance documentation. Every origin determination, certificate, supplier declaration, and human review decision is logged with a cryptographic hash chain. The audit trail is designed to satisfy the record-keeping requirements of:

- Canadian Border Services Agency (CBSA) — 7-year minimum
- US Customs and Border Protection (CBP) — 5-year minimum
- European Customs Union — 4-year minimum
- AfCFTA Protocol — 5-year minimum

The vault supports export in customs-authority formats for audit response. Documents are stored in S3 with server-side AES-256 encryption and versioned access logs. Vault access events are logged in the audit trail (who accessed what, when, from what IP).

The Audit Vault is the product feature most likely to expand the platform into legal defensibility territory — where the existence of a high-quality audit trail becomes a material factor in customs dispute resolution.

---

## 7. AI Architecture

### 7.1 Design Philosophy

The AI system is designed around three principles: **verifiability** (every AI claim is traceable to a source), **calibration** (confidence scores reflect actual accuracy), and **improvability** (every human correction makes the next determination better).

These principles preclude certain common AI architectures. We do not use a general-purpose LLM in a chat wrapper. We use a structured multi-agent system with tool calls, retrieval, and explicit confidence modeling.

### 7.2 Agent Graph

```
User Input (BOM / product description / shipment data)
        │
        ▼
[HS Classification Agent]
  Tools:
    - search_tariff_schedule(description, country) → HS candidates
    - lookup_classification_ruling(description, hs_candidate) → precedent
    - validate_hs_code(hs_code, country) → validity check
  Output: { hs_code, confidence, alternatives[], rationale }
  Routing: confidence < 0.75 → human review queue; else continue
        │
        ▼
[Agreement Selector]
  Tools:
    - get_active_agreements(origin_country, destination_country) → FTA list
    - get_transitional_provisions(agreement_id, date) → phase-in status
  Output: ranked list of applicable FTAs for this trade corridor
        │
        ▼
[Origin Rule Fetcher]
  Tools:
    - get_roo_rules(hs_code, agreement_id) → product-specific rules
    - get_general_notes(agreement_id) → cross-cutting provisions
    - get_cumulation_rules(agreement_id, origin_country) → cumulation eligibility
  Output: structured rule objects per agreement
        │
        ▼
[Origin Determination Agent]  ← runs once per applicable agreement
  Tools:
    - calculate_rvc_builddown(bom, qualifying_threshold) → pass/fail + margin
    - calculate_rvc_buildup(bom, qualifying_threshold) → pass/fail + margin
    - calculate_rvc_netcost(bom, qualifying_threshold) → pass/fail + margin
    - check_tariff_shift(input_hs_codes[], output_hs_code, rule) → pass/fail
    - check_wholly_obtained(origin_country, product_type) → pass/fail
    - apply_specific_process_rule(process_description, rule_text) → pass/fail
  Output: { agreement, result: pass|fail|marginal, rule_applied, confidence,
            reasoning, qualifying_value_content, margin_of_compliance }
        │
        ▼
[Multi-Agreement Arbitrage Engine]
  - Ranks all passing agreements by effective duty rate at destination
  - Flags marginal cases (confidence 0.6–0.8) for enhanced review
  - Selects optimal agreement for certificate generation
  Output: recommended agreement + full comparison table
        │
        ▼
[Certificate Drafting Agent]
  Tools:
    - fetch_certificate_template(cert_type, agreement_id) → blank form
    - fill_certificate(determination, shipment_data, exporter_data) → filled form
    - validate_certificate(filled_form, agreement_rules) → validation check
    - generate_pdf(filled_template) → signed PDF
    - store_certificate(pdf, determination_id) → audit vault reference
  Output: { pdf_url, json_data, audit_id, digital_signature }
        │
        ▼
[Compliance QA Gate]
  - Triggers when: overall confidence < 0.80, marginal RVC (within 3%), novel HS code
  - Routes to human expert review interface
  - Human decision logged; correction fed to training pipeline
  - Approved determinations re-enter the vault with human-validated flag
```

### 7.3 RAG Pipeline

The compliance knowledge base is the factual substrate the agents reason over. It is structured as a retrieval-augmented generation (RAG) system built on LlamaIndex with pgvector for vector storage.

**Corpus structure:**

| Source type | Examples | Chunking strategy |
|---|---|---|
| FTA agreement text | CUSMA Chapter 4, CETA Annex II | Article-level chunks with metadata (chapter, article, agreement, version) |
| Product-specific annexes | CUSMA Annex 4-B HS-level rules | Row-level (one rule per HS heading/range) |
| Customs authority guidance | CBSA D-Memos, CBP rulings | Document-level with section-level indexing |
| Binding rulings | CBSA advance rulings, EU BTI | Case-level with HS code tagging |
| Tariff schedules | Canada Schedule, US HTS | HS-code-keyed key-value store (not vector search) |

**Retrieval logic:**

Queries are constructed from the agent context (HS code, agreement ID, rule type) to maximize precision. The pipeline uses hybrid retrieval: dense vector similarity (voyage-3 embeddings) combined with sparse BM25 keyword matching over legal terminology. Retrieved chunks are re-ranked using a cross-encoder before being injected into the agent prompt.

All retrieved chunks are returned with source metadata (agreement, article, version date). The LLM is instructed to cite sources in its reasoning and to flag when a query falls outside the retrieved context.

**Corpus update pipeline:**

When an FTA is amended or a new guidance document is published, an ingestion pipeline (Celery task) fetches the document, chunks it, generates embeddings, updates the pgvector index, and increments the version tag. Existing determinations store a reference to the corpus version at determination time, preserving traceability.

### 7.4 Fine-Tuning Loop

Every human-reviewed determination produces a labeled training example:

```
Input:  { hs_code, bom, origin_countries, agreement }
Output: { result, rule_applied, confidence, correction_type }
Label:  { human_decision, human_reasoning, correction_delta }
```

Corrections are classified by type: HS misclassification, RVC calculation error, incorrect rule application, missing cumulation, incorrect certificate format. Correction type distributions are monitored as quality metrics.

Training data is accumulated in a structured dataset. When the dataset for a given correction type reaches a statistical threshold (target: 500+ labeled examples), a fine-tuning run is triggered. Fine-tuned models are evaluated on a held-out test set before promotion to production. The production model is versioned; determinations record which model version produced them.

This loop creates a proprietary training corpus that is a direct function of production usage. At 10,000 cumulative determinations, the corpus begins to exhibit knowledge that no public dataset contains: the edge cases, the product-specific ambiguities, the agreement-interpretation conventions that only emerge from real compliance work at scale.

### 7.5 Confidence Model

Confidence scores are calibrated — a 0.85 confidence should correspond to approximately 85% accuracy on held-out data. Calibration is evaluated monthly using Platt scaling and isotonic regression against human-reviewed outcomes.

Confidence routing thresholds:

| Confidence range | Action |
|---|---|
| 0.90 – 1.00 | Auto-approve; certificate generated without human review |
| 0.75 – 0.89 | Soft flag; surfaced in dashboard for optional human review |
| 0.60 – 0.74 | Hard escalation; certificate blocked until human approves |
| < 0.60 | Determination returned as inconclusive; human determination required |

Thresholds are configurable per customer tier and per certificate type (some certificate types carry higher liability and warrant lower auto-approve thresholds).

---

## 8. Technology Stack

### 8.1 Frontend

- **Next.js 14** (App Router, TypeScript strict mode)
- **Tailwind CSS** + shadcn/ui component library
- **Zustand** (client state) + **React Query / TanStack Query** (server state, caching)
- **Deployment:** Vercel (Phase 1) → AWS CloudFront + S3 (Phase 2, multi-region)

### 8.2 Backend

- **FastAPI** (Python 3.12) — async-first, OpenAPI auto-docs, Pydantic v2 for all data models
- **Celery** + **Redis 7** — async job queue for BOM processing, certificate generation, LLM agent invocations
- **PostgreSQL 16** (primary relational store) + **pgvector** extension (embedding storage and similarity search)
- **Alembic** — schema migrations with down-migration support
- **LlamaIndex** — RAG orchestration over the trade agreement corpus
- **LangGraph** — multi-agent workflow orchestration with stateful graphs and conditional routing

### 8.3 AI / GenAI

- **Primary LLM:** `claude-sonnet-4-6` via Anthropic SDK — structured tool use, extended context, confidence-aware prompting
- **Embeddings:** `voyage-3` (Voyage AI) — state-of-the-art retrieval performance, or `text-embedding-3-small` (OpenAI) as fallback
- **Reranker:** cross-encoder reranking for RAG retrieval quality
- **Model versioning:** determinations record model version at inference time for full traceability

### 8.4 Authentication and Multi-tenancy

- **Clerk** — authentication provider with organization-level multi-tenancy, SSO (SAML/OIDC) ready for enterprise
- **Row-level security (RLS)** in PostgreSQL enforced per `org_id` — data isolation is at the database layer, not the application layer
- API key management for platform API licensing customers (separate from user auth)

### 8.5 Payments and Billing

- **Stripe** — subscription billing (Starter / Growth / Enterprise tiers) + usage-based metering for certificate volume above plan limits
- Stripe Billing Portal for self-serve plan management, invoice download
- Usage webhooks feed into internal metering DB for real-time quota enforcement

### 8.6 Integrations

**Phase 1:**
- QuickBooks Online (product catalog, BOM data)
- NetSuite, SAP Business One (ERP — BOM, cost data)
- Flexport, Shipbob (logistics — shipment data)
- Zapier / Make (no-code automation for non-ERP users)
- Outbound webhooks: certificate issued, declaration expired, compliance alert, determination flagged

**Phase 2:**
- Customs filing platforms (Descartes, Integration Point) — push approved certificates directly to filing workflow
- TradeLens / GSBN (maritime logistics data)
- Bank trade finance APIs (document-of-origin as collateral)

### 8.7 Infrastructure

- **Local development:** Docker Compose (all services: API, worker, PostgreSQL, Redis, pgvector)
- **Production (AWS):** ECS Fargate (API + worker containers) + RDS PostgreSQL Multi-AZ + ElastiCache Redis + S3 (document vault) + CloudFront
- **Infrastructure as Code:** Terraform, modular (separate modules per service, environment-parametrized)
- **CI/CD:** GitHub Actions — lint → type-check → test → build → staging deploy → production deploy (manual gate)

### 8.8 Security and Compliance Posture

Security is designed for the compliance market — customers are, by definition, operating in a regulatory environment. Weak security posture is a disqualifying condition.

| Control | Implementation |
|---|---|
| Encryption at rest | AES-256 for all stored documents (S3 SSE-KMS + RDS encryption) |
| Encryption in transit | TLS 1.3 enforced; HSTS with preloading |
| Access control | RBAC at application layer + RLS at database layer |
| Audit logging | All data access events logged to immutable audit store |
| Dependency scanning | Snyk (continuous) + automated PR blocking on critical CVEs |
| SAST | CodeQL on every PR |
| Secret scanning | Gitleaks pre-commit hook + GitHub secret scanning |
| OWASP Top 10 | API-layer mitigations: input validation (Pydantic), rate limiting (Redis), SQL injection prevention (parameterized queries via SQLAlchemy), XSS prevention (React default escaping) |
| SOC 2 Type II | Controls implemented from day one; audit-ready by month 10 (target certification month 12) |
| PIPEDA (Canada) | Data residency options in Canadian AWS regions; consent management; data subject request handling |
| GDPR (EU) | Required for Phase 2 EU customers; data processing agreements, right to erasure workflow |

---

## 9. Monorepo Structure

```
Uportai/
├── apps/
│   ├── web/                    # Next.js 14 frontend
│   │   ├── app/                # App Router pages and layouts
│   │   ├── components/         # Shared UI components
│   │   └── lib/                # Client utilities, API client
│   └── api/                    # FastAPI backend
│       ├── main.py             # Application entrypoint
│       ├── routers/            # Route modules: origin, certificates, bom, agreements, suppliers, billing
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       └── services/           # Business logic layer
├── packages/
│   ├── roo-engine/             # Pure Python: origin determination logic (TS, RVC, WO, specific process)
│   ├── ai-agents/              # LangGraph agents + RAG pipeline
│   │   ├── hs_classifier.py    # HS classification agent
│   │   ├── origin_agent.py     # Origin determination agent graph
│   │   ├── rag_assistant.py    # Compliance RAG assistant
│   │   └── confidence.py       # Confidence model + calibration
│   ├── certificate-gen/        # PDF certificate generator, template registry
│   └── integrations/           # ERP / logistics connectors (QuickBooks, NetSuite, Flexport)
├── infra/
│   ├── terraform/              # Modular IaC: ECS, RDS, Redis, S3, CloudFront, IAM
│   └── docker/                 # docker-compose.yml (local dev), Dockerfiles
├── data/
│   ├── trade-agreements/       # Source FTA texts (canonical, versioned)
│   ├── tariff-schedules/       # HS code databases by country
│   └── ingestion/              # Ingestion scripts: chunking, embedding, indexing
├── tasks/
│   ├── todo.md                 # Sprint task tracker
│   └── lessons.md              # Engineering lessons log
├── scripts/                    # Seed, migration runner, corpus update scripts
└── .github/
    └── workflows/
        ├── ci.yml              # Lint, typecheck, test, build
        └── deploy.yml          # Staging and production deploy pipelines
```

---

## 10. Database Schema

```sql
-- Core multi-tenancy
organizations       (id UUID PK, name TEXT, country CHAR(2), plan TEXT,
                     stripe_customer_id TEXT, created_at TIMESTAMPTZ)

users               (id UUID PK, org_id UUID FK, clerk_id TEXT UNIQUE,
                     role TEXT CHECK (role IN ('admin','analyst','viewer')),
                     email TEXT, created_at TIMESTAMPTZ)

-- Product and supply chain data
products            (id UUID PK, org_id UUID FK, hs_code TEXT, hs_code_confidence NUMERIC,
                     description TEXT, origin_country CHAR(2), created_at TIMESTAMPTZ)

bom_items           (id UUID PK, product_id UUID FK, component_id UUID FK,
                     quantity NUMERIC, unit_cost NUMERIC, cost_currency CHAR(3),
                     origin_country CHAR(2), supplier_id UUID FK)

-- Trade operations
shipments           (id UUID PK, org_id UUID FK, destination_country CHAR(2),
                     incoterm TEXT, status TEXT, created_at TIMESTAMPTZ)

origin_determinations (id UUID PK, shipment_id UUID FK, agreement_id UUID FK,
                        rule_applied TEXT, result TEXT CHECK (result IN ('pass','fail','marginal','inconclusive')),
                        confidence NUMERIC, reasoning TEXT, model_version TEXT,
                        corpus_version TEXT, human_reviewed BOOLEAN DEFAULT FALSE,
                        human_reviewer_id UUID FK, created_at TIMESTAMPTZ)

-- Certificates
certificates        (id UUID PK, shipment_id UUID FK, determination_id UUID FK,
                     cert_type TEXT, pdf_url TEXT, json_data JSONB,
                     issued_at TIMESTAMPTZ, valid_until TIMESTAMPTZ,
                     digital_sig TEXT, revoked BOOLEAN DEFAULT FALSE)

-- Supplier network
suppliers           (id UUID PK, org_id UUID FK, name TEXT, country CHAR(2),
                     portal_token TEXT, onboarded_at TIMESTAMPTZ)

supplier_declarations (id UUID PK, supplier_id UUID FK, product_id UUID FK,
                        origin CHAR(2), valid_from DATE, valid_until DATE,
                        doc_url TEXT, verified BOOLEAN DEFAULT FALSE)

-- Audit and compliance
audit_events        (id UUID PK, org_id UUID FK, entity_type TEXT,
                     entity_id UUID, action TEXT, actor_id UUID,
                     payload JSONB, ip_address INET, created_at TIMESTAMPTZ)

-- Agreement and rule registry
trade_agreements    (id UUID PK, code TEXT UNIQUE, name TEXT, parties TEXT[],
                     effective_date DATE, corpus_version TEXT)

roo_rules           (id UUID PK, agreement_id UUID FK, hs_chapter TEXT,
                     hs_heading TEXT, hs_subheading TEXT,
                     rule_type TEXT CHECK (rule_type IN ('WO','TS','RVC','SP','COMBO')),
                     rule_text TEXT, value_threshold NUMERIC,
                     rvc_method TEXT, updated_at TIMESTAMPTZ)

-- RAG corpus versioning
corpus_versions     (id UUID PK, agreement_id UUID FK, version TEXT,
                     chunk_count INTEGER, embedded_at TIMESTAMPTZ, active BOOLEAN)

-- Metering (for usage-based billing)
usage_events        (id UUID PK, org_id UUID FK, event_type TEXT,
                     quantity INTEGER, recorded_at TIMESTAMPTZ,
                     stripe_metering_id TEXT)
```

---

## 11. Delivery Roadmap

### 11.1 Sprint Plan

| Sprint | Duration | Deliverables | Milestone / Grant Signal |
|---|---|---|---|
| 1–2 | Weeks 1–4 | Monorepo scaffold, Docker Compose, DB schema + Alembic migrations, Clerk auth, base FastAPI structure, CI/CD pipeline | Eligible: NRC IRAP "Concept" stage funding; SR&ED clock starts |
| 3–4 | Weeks 5–8 | HS Classifier agent (LangGraph), RVC/TS/WO calculation engine, BOM upload + parsing, origin determination API, pgvector corpus setup | Core AI system operational — SR&ED eligible activity |
| 5–6 | Weeks 9–12 | Next.js dashboard, BOM upload flow, origin result display, PDF certificate generation (CUSMA first), Audit Vault v1 | Working prototype — eligible for CanExport SME (product development stage) |
| 7–8 | Weeks 13–16 | Trade agreement RAG pipeline, compliance chat UI, multi-agreement arbitrage, QuickBooks integration, Stripe billing | Beta product — CanExport SME application trigger; NRC IRAP "Feasibility" milestone |
| 9–10 | Weeks 17–20 | SOC 2 controls audit-readiness, supplier portal v1, savings dashboard, confidence model calibration, PIPEDA review | Canada launch-ready — design partner onboarding; BDC Growth Capital conversation |
| 11–12 | Weeks 21–24 | CETA and CPTPP agreement coverage, API licensing layer, white-label portal, NetSuite integration | Paid customers onboarded — Series seed fundraise eligibility |

### 11.2 Canadian Grant Eligibility Map

| Program | Eligibility trigger | Target ask |
|---|---|---|
| **NRC IRAP** (Industrial Research Assistance) | AI R&D work on novel classification and determination methodology (Sprints 1–6) | $50K–$250K non-dilutive |
| **CanExport SME** | Product developed for export market, targeting international SME customers | $50K–$75K reimbursable |
| **SR&ED Tax Credit** | AI/ML development, LLM fine-tuning loop, confidence model research (ongoing) | 35% ITC on eligible R&D expenditure |
| **BDC Advisory** | Post-launch with first paying customers | Advisory services + growth capital |
| **CDAP** (Canada Digital Adoption Plan) | Digital product for Canadian businesses | Up to $15K for tech adoption advisory |

---

## 12. Business Model

### 12.1 Subscription Tiers

| Tier | Price | Included | Target customer |
|---|---|---|---|
| **Starter** | $299/month | 50 origin determinations/month, 3 FTAs (CUSMA, CETA, CPTPP), 2 users, CUSMA certificate generation, basic savings dashboard | Canadian SME, first-time FTA user |
| **Growth** | $999/month | 250 determinations/month, all Phase 1 FTAs, 10 users, all certificate types, supplier portal (25 suppliers), QuickBooks integration, compliance chat | Active exporter, multiple FTAs, small trade team |
| **Enterprise** | Custom | Unlimited determinations, all agreements, unlimited users, API access, white-label portal, SSO, SOC 2 report, dedicated onboarding, SLA | Customs brokers, freight forwarders, large exporters |

Annual billing offers 20% discount. Month-to-month available on Starter and Growth.

### 12.2 Usage-Based Overage

Determinations above plan limits: **$3.50 per determination** (Starter), **$2.50 per determination** (Growth). Certificate generation above plan limits: **$1.50 per certificate**. Usage metered in real time via Stripe; customers see live usage in the dashboard.

### 12.3 API Licensing

For platforms embedding Uportai via API (customs brokers, freight forwarders, trade finance platforms, government trade portals):

- Base API license: **$2,500/month** (up to 1,000 determination API calls/month)
- Volume pricing: **$1.50–$2.50 per API call** above base, depending on commitment tier
- White-label supplier portal: **$500/month** add-on
- Custom agreement coverage (e.g., a specific bilateral FTA not in standard coverage): **$5K–$15K** one-time data ingestion fee + ongoing maintenance

### 12.4 Revenue Model at Scale

| Month 12 | Target |
|---|---|
| Paying customers | 150 |
| Blended ACV | $4,800 |
| ARR | $720K |
| API deals | 1 at $30K ACV |
| Total ARR | $750K |

| Month 24 | Target |
|---|---|
| Paying customers | 1,200 |
| Blended ACV | $5,400 |
| ARR from subscriptions | $6.48M |
| API deals | 3 at avg $80K ACV |
| Total ARR | $6.72M |

### 12.5 Unit Economics (Starter tier)

- Customer acquisition cost (CTS channel): $600 estimated
- Gross margin at Starter: ~78% (infrastructure + LLM API costs at $299/month load)
- LTV at 24-month average customer life: $7,176
- LTV:CAC ratio: ~12x

---

## 13. Go-to-Market

### 13.1 Phase 1 — Canada (Months 1–12)

**Channel: Canadian Trade Commissioner Service (CTS)**

The CTS operates 160+ offices in 110 countries and actively connects Canadian exporters with market opportunities. The Trade Commissioner network is a warm channel: exporters who engage with a Trade Commissioner are actively trying to export, often for the first time, and have no compliance infrastructure.

Engagement strategy:
- Formal partnership conversation with Global Affairs Canada / CTS central office
- Design partner recruitment: 50 SME exporters from CTS referrals, targeted at CUSMA corridor (Canada-US, Canada-Mexico)
- Co-branded content: "FTA Savings Calculator" white paper, distributed through CTS channels
- Trade events: Canadian Manufacturers & Exporters (CME) conference, Export Development Canada (EDC) events

**Channel: Customs Brokers**

Canada has approximately 2,400 licensed customs brokers. The top 50 firms collectively serve 60%+ of Canadian import/export volume. A single customs broker integration is a force multiplier — each broker represents hundreds to thousands of SME clients.

Engagement strategy:
- Target 10 mid-size brokers (not the top 5, who have enterprise contracts) for pilot API integration
- Value proposition: automate the RoO analysis that currently takes their analysts 2–4 hours per shipment
- Revenue share model: broker earns commission on referred customers who convert to direct subscription

**Channel: Inbound / Content**

- SEO-driven content: "CUSMA Rules of Origin explained", "How to claim preferential tariffs under CETA"
- Free "FTA Savings Estimator" tool (email capture, not gated by account)
- LinkedIn thought leadership: Canadian trade compliance, AfCFTA opportunity

### 13.2 Phase 2 — Global Expansion (Months 13–36)

**AfCFTA corridor (months 13–24):** Africa is the strategic growth market. AfCFTA covers 55 countries and is still operationalizing its Rules of Origin framework — the window to be the dominant digital infrastructure layer is open. Boris's existing network across African fintech and trade infrastructure is a structural advantage here.

**EU corridor (months 18–30):** CETA creates a high-value Canada-EU corridor. EUR.1 and REX certificate generation + EU customs authority integration opens the European market. EU data residency requirements (GDPR) must be satisfied before launch.

**CPTPP / ASEAN (months 24–36):** The Asia-Pacific trade corridor is the highest-volume opportunity. CPTPP (Canada-Japan, Canada-Australia, Canada-Vietnam, etc.) is a natural extension of Phase 1 coverage. ASEAN ATIGA adds Southeast Asian corridors.

**Platform strategy:** By month 18, the API licensing model should be generating revenue from at least one non-Canada platform partner. This is the leverage point for global expansion without proportional CAC growth.

---

## 14. Team and Traction

### 14.1 Founder

**Boris Houenou** — Founder and CTO. Builder at the intersection of technology, finance, and Africa's digital economy. Prior experience building pan-African fintech and loyalty infrastructure (Loyalty Africa). Technical depth across TypeScript/Next.js, Python/FastAPI, PostgreSQL, AI/LLM systems. Operates as a technical co-founder with product and commercial instincts.

Boris's background in African trade infrastructure is a strategic asset for AfCFTA expansion: existing network with trade authorities, financial institutions, and technology operators across West Africa.

### 14.2 Current Traction

- Technical specification complete; architecture validated
- Monorepo scaffold in progress
- Design partner conversations underway with Canadian Trade Commissioner Service network
- NRC IRAP pre-engagement initiated
- GitHub: https://github.com/BorisHouenou/uport

### 14.3 Advisory and Partnership Targets

- **Trade law advisor:** Canadian trade attorney with FTA and customs law background (in conversation)
- **Customs broker partner:** Mid-size Canadian licensed customs broker for Phase 1 pilot (targeting)
- **Global Affairs Canada / CTS:** Formal channel partnership (targeting)
- **Export Development Canada (EDC):** Potential co-marketing and customer referral (targeting)

### 14.4 What We're Looking For

- **NRC IRAP / SR&ED:** Non-dilutive R&D funding to accelerate AI agent development and training data pipeline (target: $150K–$300K combined)
- **CanExport SME:** Export market development funding for Phase 1 Canada-US and Canada-EU corridor launch
- **Seed capital:** $750K–$1.5M to fund 18 months of development, first commercial team hire, and Phase 2 agreement coverage expansion

---

## 15. Key Files

| File | Purpose |
|---|---|
| `apps/api/main.py` | FastAPI application entrypoint |
| `apps/api/routers/` | Route modules: origin, certificates, bom, agreements, suppliers, billing |
| `apps/web/app/` | Next.js App Router pages and layouts |
| `packages/roo-engine/engine.py` | Core RVC, TS, WO, and specific process rule logic |
| `packages/ai-agents/hs_classifier.py` | HS classification agent (LangGraph) |
| `packages/ai-agents/origin_agent.py` | Multi-step origin determination agent graph |
| `packages/ai-agents/rag_assistant.py` | RAG-grounded compliance assistant |
| `packages/ai-agents/confidence.py` | Confidence model, calibration, and routing logic |
| `packages/certificate-gen/generator.py` | PDF certificate generator and template registry |
| `infra/docker/docker-compose.yml` | Local development environment |
| `.github/workflows/ci.yml` | CI pipeline: lint → typecheck → test → build |
| `data/trade-agreements/` | Canonical FTA texts, versioned |
| `tasks/todo.md` | Active sprint task tracker |

---

*Uportai — Rules of Origin Compliance Engine*
*Technical Product Specification v2.0 — May 2026*
*Confidential — Boris Houenou*
