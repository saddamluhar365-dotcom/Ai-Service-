# Autonomous Freelance Agent — Design Specification

## Goal
Build an autonomous, recovery-first freelancing business agent that can receive permitted work from connected freelance platforms, understand customer requirements, price and communicate within platform rules, execute data-processing work, validate and deliver results, track payments, and produce a daily 7 PM business report.

## Core Principle
**Order-driven compute. No job = no Kaggle compute.** The always-on control plane stays lightweight; Kaggle is an on-demand processing worker and is stopped immediately after validated work is safely persisted.

## Scope
- Five platform connector slots: Upwork, Fiverr, Freelancer.com, PeoplePerHour, Truelancer.
- Only official APIs, approved integrations, or workflows permitted by each platform. No CAPTCHA bypass, prohibited scraping, phone-number harvesting, spam, or off-platform payment bypass.
- AI requirement understanding through Gemini as primary provider with compatible backup providers.
- Deterministic data execution engine; AI produces a validated structured plan, not arbitrary executable code.
- Work-order/job lifecycle with durable checkpoints, idempotency, retries, provider failover, and resume.
- Kaggle worker orchestration for eligible heavy jobs.
- Customer communication and voice-agent adapters where platform policy and integration capability permit.
- Dynamic pricing based on the lowest legitimate comparable market price × 0.85, bounded by configured economics and manual-review rules when unprofitable.
- Payment/release tracking and earnings ledger.
- Daily 7 PM report in Asia/Kolkata time.

## Non-Goals
- Do not claim unlimited free compute or guaranteed platform automation.
- Do not bypass platform restrictions.
- Do not make terminal FAILED or PAUSED business states. Technical attempts may fail internally, but the orchestrator must retry, fail over, or resume from checkpoint. Only an explicit HUMAN_INTERVENTION_REQUIRED state may stop autonomous execution.

## Architecture
```text
Platform Events / Pollers / Webhooks
                |
                v
        MASTER ORCHESTRATOR
                |
       +--------+---------+
       |                  |
       v                  v
   Job Queue          AI Planner
       |                  |
       v                  v
 Worker Manager      Structured Plan
       |                  |
       +--------+---------+
                v
         Data Work Engine
                |
      +---------+----------+
      |                    |
      v                    v
 Validation           Checkpoint Store
      |                    |
      +---------+----------+
                v
          Delivery Engine
                |
        Payment/Earnings
                |
           7 PM Report
```

## Job Lifecycle
1. DISCOVERED — job detected from an allowed platform integration.
2. QUALIFYING — requirements, scope, policy constraints and economics checked.
3. COMMUNICATING — customer clarification/confirmation through permitted channel.
4. OFFERED — permitted proposal/offer submitted.
5. ACCEPTED — customer/platform acceptance confirmed.
6. PAYMENT_CONFIRMED — required platform payment/escrow condition confirmed.
7. WORK_ORDER_CREATED — immutable internal job ID and idempotency key created.
8. ANALYZING — input files profiled.
9. PLANNING — AI returns schema-validated processing recipe.
10. PROCESSING — deterministic engine executes recipe, using Kaggle only when selected.
11. VALIDATING — output and business constraints checked.
12. DELIVERING — final artifact delivered through permitted channel.
13. PAYMENT_TRACKING — release status monitored.
14. COMPLETED — output delivered and job/payment ledger finalized.
15. HUMAN_INTERVENTION_REQUIRED — only for cases automation cannot legally or technically resolve.

Technical attempt states are stored separately from business state so a transient provider failure never becomes a customer-visible terminal failure.

## Recovery Contract
Every meaningful stage writes a durable checkpoint before advancing.

```text
attempt failure
   -> bounded retry with backoff
   -> compatible backup provider/worker
   -> resume from last committed checkpoint
   -> validate state/artifact
   -> continue
```

Requirements:
- Idempotency key per job/stage.
- Transactional state updates.
- Atomic artifact finalization.
- No duplicate delivery on retries.
- Provider circuit breakers and timeouts.
- Dead-letter diagnostics are internal only; the business job remains recoverable.
- If all compatible providers are temporarily unavailable, preserve state and retry automatically; escalate only after configurable recovery policy is exhausted.

## AI Contract
AI providers must implement one internal interface:
- `understand_requirement(context) -> RequirementPlan`
- `clarify_requirement(context) -> ClarificationRequest`
- `create_processing_recipe(profile, requirement) -> ProcessingRecipe`
- `summarize_job(context) -> JobSummary`

`ProcessingRecipe` is strict JSON with an allowlisted operation vocabulary such as filter, select_columns, rename_columns, sort, deduplicate, normalize, calculate, split, merge, group, and export. The engine rejects unknown operations.

Raw customer data is not sent to AI unless required. Prefer schema, statistics, sampled/redacted values and task context. Full files remain in controlled storage/worker environments.

## Data Engine
Initial input formats: CSV, XLSX, XLS.
Initial output formats: XLSX, CSV.
Planned adapters: JSON, XML, PDF, TXT, ZIP, images, Google Sheets, APIs and databases.

The engine must be deterministic and testable independently of AI providers.

## Kaggle Worker
Kaggle is an on-demand compute worker, not the control plane.

```text
No order -> no Kaggle session
Order -> queue -> launch eligible Kaggle job
       -> process/checkpoint
       -> persist artifact
       -> validate
       -> stop worker
```

Jobs must be checkpointable and bounded so a finite notebook session cannot corrupt a work order. If a Kaggle run terminates unexpectedly, the Worker Manager retries or routes the work to another compatible worker and resumes from the last checkpoint.

## Pricing
Default market rule:
`our_price = lowest_legitimate_comparable_market_price * 0.85`

Before accepting:
- account for platform fees;
- account for AI/API cost;
- account for compute/storage cost;
- enforce minimum profitable price;
- send to HUMAN_INTERVENTION_REQUIRED rather than accepting an uneconomic job.

## Security
- Secrets only through runtime secret stores/environment configuration; never commit credentials.
- Encrypt sensitive data in transit and at rest where supported.
- Least-privilege service credentials.
- Customer files isolated by job ID and access policy.
- Audit every external action, price decision, state transition and delivery.
- Retention/deletion policy configurable per platform and customer requirement.
- Secret scanning and dependency/security checks in CI.

## CI Quality Gate
Every change must pass automated checks before merge. CI should run formatting/linting, type checks where configured, unit tests, integration tests, security checks and packaging/import validation. GitHub Actions supports repository workflows under `.github/workflows` and Python test workflows. citeturn0search0turn0search1

No claim of “zero failures” is made. The engineering target is **no known CI failures before merge** and automatic recovery for runtime/transient failures.

## Reporting
Every day at 19:00 Asia/Kolkata:
- new jobs;
- completed jobs;
- jobs currently processing/resuming;
- payment released today;
- total released earnings;
- unreleased/pending payment;
- platform-wise breakdown;
- only exceptional human-intervention cases, with recovery action/reason.

No terminal “failed/paused jobs” section.

## Deployment Independence
The application must be container-friendly and avoid hard dependency on one hosting provider. The control plane, database, object storage and workers must communicate through explicit interfaces so the deployment can later move from free resources to paid cloud or dedicated infrastructure without redesigning business logic.

## Success Criteria
- A work order survives process restarts and transient provider outages.
- Re-running any stage does not duplicate customer delivery or payment ledger entries.
- AI provider replacement does not change the deterministic execution contract.
- Kaggle is launched only for eligible queued work and stopped after validated persistence.
- A complete sample CSV/XLSX job can execute from intake through validated output and delivery simulation.
- CI is green before merge; runtime failures are recoverable rather than terminal.
