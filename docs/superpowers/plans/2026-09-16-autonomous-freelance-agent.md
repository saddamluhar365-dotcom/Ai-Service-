# Autonomous Freelance Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the autonomous freelancing-business agent with deterministic data processing, recoverable job execution, platform adapters, cloud/worker orchestration, finance tracking, reporting, security controls, and CI-gated auto-merge.

**Architecture:** A lightweight controller/orchestrator owns durable job state, queues, checkpoints, pricing, platform events, validation, delivery, and reporting. AI produces only validated structured work plans; deterministic workers execute those plans. Heavy Kaggle compute is on-demand and checkpointed, while the control plane remains provider-independent.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, PostgreSQL, Redis-compatible queue, pytest, Ruff, mypy, GitHub Actions, Gemini adapter, platform adapter interfaces, Kaggle worker adapter.

**Spec:** `docs/superpowers/specs/2026-09-16-autonomous-freelance-agent-design.md`

## Global Constraints

- Order-driven compute: no job = no Kaggle compute.
- Runtime failures never become terminal business `FAILED` or `PAUSED` states; use retry, failover, checkpoint resume, validation, and continuation.
- Private customer data remains isolated; only generalized/verified/shared-safe intelligence may be shared externally.
- AI may create structured plans only; arbitrary generated executable code is prohibited.
- Platform integrations must use official APIs/approved integrations and respect platform policies.
- Pricing must account for platform fees, AI/API cost, compute/storage cost, and minimum profitable price.
- CI must pass before merge; auto-merge may occur only after required checks pass.
- Every integration is behind an interface so providers can be replaced without changing orchestration logic.
- Idempotency and durable checkpoints are mandatory for retriable operations.
- Daily reporting uses Asia/Kolkata time and runs at 19:00.

## File Structure

```text
.github/workflows/ci.yml
.github/workflows/auto-merge.yml
.env.example
.gitignore
README.md
pyproject.toml
src/freelance_agent/
  __init__.py
  config.py
  app.py
  api/
    __init__.py
    routes.py
  core/
    __init__.py
    models.py
    state.py
    orchestrator.py
    recovery.py
    idempotency.py
  ai/
    __init__.py
    contracts.py
    planner.py
    gemini.py
    fallback.py
  data_engine/
    __init__.py
    profile.py
    operations.py
    executor.py
    validator.py
    exporter.py
  platforms/
    __init__.py
    base.py
    registry.py
    upwork.py
    fiverr.py
    freelancer.py
    peopleperhour.py
    truelancer.py
  workers/
    __init__.py
    base.py
    manager.py
    local.py
    kaggle.py
  finance/
    __init__.py
    pricing.py
    payments.py
    earnings.py
  communication/
    __init__.py
    customer_agent.py
    voice.py
  reporting/
    __init__.py
    daily.py
  storage/
    __init__.py
    database.py
    repositories.py
    checkpoints.py
  security/
    __init__.py
    audit.py
    secrets.py

tests/
  unit/
  integration/
  contract/
```

## Task 1: Repository and CI foundation

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/auto-merge.yml`
- Create: `src/freelance_agent/__init__.py`
- Create: `tests/unit/test_smoke.py`

**Interfaces:**
- CI exposes one stable required check named `ci`.
- Application package must import cleanly with no external credentials.

- [ ] Step 1: Add dependency and tool configuration with pinned-compatible ranges.
- [ ] Step 2: Add a smoke test proving package import and configuration validation.
- [ ] Step 3: Add CI for Python 3.12, formatting/lint, type checks, unit tests, and package build.
- [ ] Step 4: Trigger CI on `pull_request`, `push`, and `merge_group` so required checks work with normal PRs and merge queues. GitHub documents that merge-queue workflows require the `merge_group` event. citeturn0search1turn0search8
- [ ] Step 5: Add auto-merge workflow that enables GitHub auto-merge only for PRs after CI is green; never bypass required checks.
- [ ] Step 6: Run all local checks and fix every failure before commit.
- [ ] Step 7: Commit foundation.

## Task 2: Durable domain model and state machine

**Files:**
- Create: `src/freelance_agent/core/models.py`
- Create: `src/freelance_agent/core/state.py`
- Create: `src/freelance_agent/core/idempotency.py`
- Create: `tests/unit/test_state.py`
- Create: `tests/unit/test_idempotency.py`

**Interfaces:**
- `JobState` exposes recoverable lifecycle states without terminal FAILED/PAUSED business states.
- `JobRecord` carries durable IDs, platform metadata, checkpoint reference, retry metadata, and financial references.
- `IdempotencyStore.claim(key: str) -> bool` and `complete(key: str, result_ref: str) -> None`.

- [ ] Step 1: Write state-transition tests, including retry/resume paths.
- [ ] Step 2: Verify invalid transitions fail safely.
- [ ] Step 3: Implement immutable domain models and transition rules.
- [ ] Step 4: Implement idempotency contract and tests for duplicate delivery/payment operations.
- [ ] Step 5: Run unit tests.
- [ ] Step 6: Commit.

## Task 3: Storage and checkpoint persistence

**Files:**
- Create: `src/freelance_agent/storage/database.py`
- Create: `src/freelance_agent/storage/repositories.py`
- Create: `src/freelance_agent/storage/checkpoints.py`
- Create: `tests/integration/test_storage.py`
- Create: `tests/integration/test_checkpoints.py`

**Interfaces:**
- Repository methods persist and retrieve jobs, checkpoints, artifacts, payment events, and audit events.
- `CheckpointStore.save(job_id, step, payload_ref)` and `CheckpointStore.load_latest(job_id)` are idempotent.

- [ ] Step 1: Write persistence tests against an isolated test database.
- [ ] Step 2: Implement schema/migrations and repositories.
- [ ] Step 3: Implement atomic checkpoint writes.
- [ ] Step 4: Test restart/resume behavior.
- [ ] Step 5: Run integration tests.
- [ ] Step 6: Commit.

## Task 4: Recovery engine and orchestrator

**Files:**
- Create: `src/freelance_agent/core/recovery.py`
- Create: `src/freelance_agent/core/orchestrator.py`
- Create: `tests/unit/test_recovery.py`
- Create: `tests/unit/test_orchestrator.py`

**Interfaces:**
- `RecoveryEngine.run_with_recovery(operation, context)` implements retry → failover → checkpoint resume → validate → continue.
- `Orchestrator.submit`, `Orchestrator.resume`, `Orchestrator.advance` are idempotent.

- [ ] Step 1: Write tests for transient failure, provider failure, timeout, restart, and duplicate execution.
- [ ] Step 2: Implement bounded exponential backoff and provider failover.
- [ ] Step 3: Implement checkpoint resume.
- [ ] Step 4: Implement orchestration loop.
- [ ] Step 5: Verify no business-terminal failure state is produced by runtime exceptions.
- [ ] Step 6: Run tests and commit.

## Task 5: AI planning contract

**Files:**
- Create: `src/freelance_agent/ai/contracts.py`
- Create: `src/freelance_agent/ai/planner.py`
- Create: `src/freelance_agent/ai/gemini.py`
- Create: `src/freelance_agent/ai/fallback.py`
- Create: `tests/unit/test_planner.py`
- Create: `tests/contract/test_ai_contract.py`

**Interfaces:**
- `Planner.plan(request, profile) -> StructuredPlan`.
- Provider adapters implement a common interface and return schema-validated output only.

- [ ] Step 1: Write malformed-output and allowlist tests.
- [ ] Step 2: Implement strict Pydantic structured plan.
- [ ] Step 3: Implement Gemini adapter behind provider interface.
- [ ] Step 4: Implement backup-provider abstraction without hard-coded dependency.
- [ ] Step 5: Ensure AI cannot emit arbitrary executable operations.
- [ ] Step 6: Run contract tests without live credentials.
- [ ] Step 7: Commit.

## Task 6: Deterministic data-processing engine

**Files:**
- Create: `src/freelance_agent/data_engine/profile.py`
- Create: `src/freelance_agent/data_engine/operations.py`
- Create: `src/freelance_agent/data_engine/executor.py`
- Create: `src/freelance_agent/data_engine/validator.py`
- Create: `src/freelance_agent/data_engine/exporter.py`
- Create: `tests/unit/test_data_engine.py`
- Create: `tests/integration/test_data_pipeline.py`

**Interfaces:**
- Profile input describes schema, types, nulls, duplicates, samples, and statistics.
- Executor supports an allowlist: filter, select, rename, sort, normalize, calculate, split, merge, group, deduplicate, export.
- Validator returns structured validation evidence.

- [ ] Step 1: Write representative CSV/XLSX tests.
- [ ] Step 2: Implement profiling without exposing unnecessary raw customer data to AI.
- [ ] Step 3: Implement deterministic operations.
- [ ] Step 4: Implement validation invariants and output checks.
- [ ] Step 5: Implement atomic XLSX/CSV export.
- [ ] Step 6: Test retry/resume at operation boundaries.
- [ ] Step 7: Commit.

## Task 7: Platform adapter framework

**Files:**
- Create: `src/freelance_agent/platforms/base.py`
- Create: `src/freelance_agent/platforms/registry.py`
- Create: `src/freelance_agent/platforms/upwork.py`
- Create: `src/freelance_agent/platforms/fiverr.py`
- Create: `src/freelance_agent/platforms/freelancer.py`
- Create: `src/freelance_agent/platforms/peopleperhour.py`
- Create: `src/freelance_agent/platforms/truelancer.py`
- Create: `tests/contract/test_platform_adapters.py`

**Interfaces:**
- `PlatformAdapter` supports event polling/webhooks, job normalization, permitted messaging, proposal/offer abstraction, delivery, and payment-event normalization.

- [ ] Step 1: Write adapter contract tests using fake providers.
- [ ] Step 2: Implement registry and normalized event model.
- [ ] Step 3: Implement provider adapters only for documented/approved APIs or integrations.
- [ ] Step 4: Ensure prohibited scraping, CAPTCHA bypass, spam, and off-platform payment behavior are impossible through the adapter interface.
- [ ] Step 5: Run contract tests without platform credentials.
- [ ] Step 6: Commit.

## Task 8: Worker manager and Kaggle worker

**Files:**
- Create: `src/freelance_agent/workers/base.py`
- Create: `src/freelance_agent/workers/manager.py`
- Create: `src/freelance_agent/workers/local.py`
- Create: `src/freelance_agent/workers/kaggle.py`
- Create: `tests/unit/test_worker_manager.py`
- Create: `tests/contract/test_kaggle_worker.py`

**Interfaces:**
- `WorkerManager.dispatch(job)` selects CPU/local or Kaggle based on declared resource requirements.
- Kaggle worker is short-lived, checkpointed, and shut down after completion.

- [ ] Step 1: Write tests proving no worker starts for no-job state.
- [ ] Step 2: Implement resource-aware dispatch.
- [ ] Step 3: Implement Kaggle lifecycle adapter behind an interface.
- [ ] Step 4: Add checkpoint transfer and result verification.
- [ ] Step 5: Test worker termination and resume behavior.
- [ ] Step 6: Commit.

## Task 9: Pricing, payments, earnings

**Files:**
- Create: `src/freelance_agent/finance/pricing.py`
- Create: `src/freelance_agent/finance/payments.py`
- Create: `src/freelance_agent/finance/earnings.py`
- Create: `tests/unit/test_pricing.py`
- Create: `tests/unit/test_finance.py`

**Interfaces:**
- `PricingEngine.quote(market_comparables, costs, minimum_profit) -> Quote`.
- Quote target uses the lowest legitimate comparable market price × 0.85, then rejects/defers if below minimum profitable price.
- Payment events are idempotent and ledger-based.

- [ ] Step 1: Write pricing tests.
- [ ] Step 2: Implement comparable-price calculation and cost floor.
- [ ] Step 3: Implement payment release and earnings ledger.
- [ ] Step 4: Test duplicate payment events.
- [ ] Step 5: Commit.

## Task 10: Customer communication and voice abstraction

**Files:**
- Create: `src/freelance_agent/communication/customer_agent.py`
- Create: `src/freelance_agent/communication/voice.py`
- Create: `tests/unit/test_communication.py`

**Interfaces:**
- Communication operates only through platform-permitted channels.
- Voice adapter exposes start/stop/transcript/action-intent interfaces and never bypasses platform restrictions.

- [ ] Step 1: Write tests for message policy and action authorization.
- [ ] Step 2: Implement customer-agent state and approved-channel abstraction.
- [ ] Step 3: Implement voice-provider interface with safe fallback to text.
- [ ] Step 4: Commit.

## Task 11: Daily 7 PM reporting

**Files:**
- Create: `src/freelance_agent/reporting/daily.py`
- Create: `tests/unit/test_reporting.py`
- Modify: scheduler configuration created in Task 1 or deployment configuration.

**Interfaces:**
- `DailyReport.generate(date, timezone="Asia/Kolkata") -> Report`.
- Report includes new jobs, completed jobs, processing/resuming jobs, released payments, total released earnings, pending payments, platform breakdown, and only exceptional human-intervention cases.

- [ ] Step 1: Write report aggregation tests.
- [ ] Step 2: Implement timezone-aware 19:00 report generation.
- [ ] Step 3: Add delivery adapter and dry-run mode.
- [ ] Step 4: Commit.

## Task 12: Security, audit, API, documentation

**Files:**
- Create: `src/freelance_agent/config.py`
- Create: `src/freelance_agent/security/secrets.py`
- Create: `src/freelance_agent/security/audit.py`
- Create: `src/freelance_agent/api/routes.py`
- Create: `src/freelance_agent/app.py`
- Modify: `README.md`
- Create: `tests/unit/test_security.py`
- Create: `tests/integration/test_api.py`

**Interfaces:**
- Secrets are environment/secret-store based and never logged.
- API exposes health, job submission/status, resume, and reporting endpoints with authentication hooks.

- [ ] Step 1: Write secret-redaction and authorization tests.
- [ ] Step 2: Implement configuration validation and audit logging.
- [ ] Step 3: Implement FastAPI routes.
- [ ] Step 4: Add health/readiness checks.
- [ ] Step 5: Update operational documentation.
- [ ] Step 6: Commit.

## Task 13: Full-system verification and CI hardening

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `.github/workflows/auto-merge.yml`
- Modify: `README.md`
- Add/modify tests as required by failures.

- [ ] Step 1: Run formatter/linter.
- [ ] Step 2: Run type checking.
- [ ] Step 3: Run all unit, contract, and integration tests.
- [ ] Step 4: Run package/build validation.
- [ ] Step 5: Inspect GitHub Actions on the latest commit and fix every failure.
- [ ] Step 6: Add regression tests for every discovered defect.
- [ ] Step 7: Repeat until CI is green.
- [ ] Step 8: Verify required check naming is stable and not duplicated; GitHub warns duplicate required job names can create ambiguous status checks. citeturn0search0
- [ ] Step 9: Verify auto-merge is configured to wait for required checks rather than bypass them. GitHub auto-merge activates only after required reviews/status checks are satisfied. citeturn0search6
- [ ] Step 10: Commit final hardening.

## Task 14: PR, auto-merge, and final verification

**Files:**
- No new source files unless verification requires a regression fix.

- [ ] Step 1: Open implementation PR targeting `main`.
- [ ] Step 2: Confirm required `ci` status check is reported on the latest PR commit.
- [ ] Step 3: Confirm all required checks are successful before merge; protected branches can enforce this requirement. citeturn0search0turn0search3
- [ ] Step 4: Enable auto-merge.
- [ ] Step 5: Wait for GitHub to perform the merge only after requirements pass.
- [ ] Step 6: Verify the merged `main` commit and post-merge CI.
- [ ] Step 7: Record the final green CI run and merged commit as the completion evidence.

## CI Failure Prevention Rules

1. Every feature starts with tests before implementation.
2. CI runs the same checks locally and in GitHub Actions.
3. No live API credentials are required for unit/contract CI.
4. External integrations use mocked/fake adapters in CI.
5. Dependency versions are constrained and tested on Python 3.12.
6. CI runs on both `pull_request` and `merge_group` so required checks cannot disappear from a merge queue.
7. Required check names are unique.
8. Any CI failure creates a regression test before the fix is considered complete.
9. Auto-merge never uses a bypass mechanism.
10. Completion is not claimed until the final GitHub Actions run is actually green.

## Final Acceptance Criteria

- [ ] Repository has the complete agent scaffold and implementation.
- [ ] Deterministic data-processing pipeline works for CSV/XLSX examples.
- [ ] Job execution is durable, idempotent, checkpointed, and automatically recoverable.
- [ ] No business-level FAILED/PAUSED terminal state exists.
- [ ] CPU/local and Kaggle workers are selected by resource need.
- [ ] Platform adapters are policy-compliant and replaceable.
- [ ] Pricing and payment ledger are deterministic and idempotent.
- [ ] Daily report is generated at 19:00 Asia/Kolkata.
- [ ] Secrets are not committed or logged.
- [ ] Unit, contract, integration, lint, type, and build checks pass.
- [ ] Required CI check is green on the latest PR commit.
- [ ] Auto-merge is enabled and cannot bypass required CI.
- [ ] `main` receives only a verified green build.
