# E2E Engine

## Engineering Intelligence & Verification System

E2E Engine is a runtime-neutral engineering control plane for AI-assisted software development.

It is designed to coordinate AI engineering work while keeping **engineering context, deterministic guardrails, testing, independent verification, and evidence** as first-class parts of the workflow.

> **AI can generate the code. E2E Engine makes the engineering process verifiable.**

---

## What E2E Engine Does

E2E Engine sits around AI coding runtimes rather than attempting to replace them.

```text
Engineering Request
        │
        ▼
 Context + Rules
        │
        ▼
    CodeBrain
        │
        ▼
 Engineering Intelligence
        │
        ▼
   SD3 Supervisor
        │
        ▼
  SD2 Orchestrator
        │
   ┌────┴────┐
   ▼         ▼
 SD1       SD1       ...
Worker    Worker
   │         │
   └────┬────┘
        ▼
 Testing + Evaluation
        │
        ▼
 SD3 Verification
        │
   ┌────┴────┐
   ▼         ▼
Reject     Approve
   │         │
Correct   Evidence
   │
   └──► Verify Again
```

The goal is to separate **execution** from **engineering judgment**.

---

## Why Use E2E Engine?

AI coding agents can implement software quickly, but an agent saying "done" is not sufficient evidence that a change is correct.

E2E Engine focuses on the engineering questions around AI-generated changes:

- Did the system understand the existing repository?
- Was the change aligned with project rules and architecture?
- Were the right specialists used?
- Were tests meaningful rather than merely green?
- Did the change introduce regressions or security risks?
- Can the implementation be independently verified?
- What evidence supports acceptance?

E2E Engine is therefore an **engineering control and verification layer**, not just another coding agent or E2E test runner.

---

## Core Architecture

### SD1 — Workers

Bounded specialist workers perform implementation tasks and return structured results and evidence.

Examples include frontend, backend, API, database, QA, security, DevOps, UI/UX, architecture, SEO, and web-intelligence work.

### SD2 — Orchestrator

SD2 decomposes engineering requests, selects and prioritizes workers, manages dependencies, performs safe parallelization, aggregates results, and coordinates bounded corrections.

### SD3 — Engineering Supervisor

SD3 acts as an independent engineering authority. It reviews the repository, requirements, architecture, security, integration, tests, regression risk, and worker evidence.

Possible outcomes include:

- **Approve**
- **Correct**
- **Reject**
- **Escalate**

The important principle is that the worker does not get to be the final judge of its own work.

---

## Repository Intelligence — CodeBrain

CodeBrain provides repository-aware context before agents start changing code.

It can model:

- files and metadata
- symbols
- imports and dependencies
- caller/callee relationships
- impact areas
- task-oriented context
- language-aware source structure

The purpose is to reduce the common AI failure mode of making locally reasonable edits without understanding the wider repository.

---

## Engineering Intelligence

E2E Engine can combine:

```text
Task
 ├── Repository context
 ├── Rules
 ├── Skills
 ├── Memory
 ├── Evaluation history
 └── Baseline / regression signals
           │
           ▼
      Risk assessment
           │
           ▼
 Verification plan
```

Historical information is advisory. Memory never becomes an authorization boundary.

Higher-risk changes can trigger stronger testing, security checks, and SD3 verification.

---

## Verification and Proof

E2E Engine deliberately separates **execution success** from **engineering confidence**.

The project uses a proof ladder:

```text
P0  Internal health
 ↓
P1  Deterministic evaluation
 ↓
P2  Orchestration proof
 ↓
P3  Real SD1 execution
 ↓
P4  Independent SD3 verification
 ↓
P5  Failure + recovery
 ↓
P6  Repeated benchmark
 ↓
PROVEN
```

A green CI result is a useful health signal, but it is not automatically a production-proof claim.

The repository's production proof contract is defined in [`architecture/PROOF-STANDARD.md`](../architecture/PROOF-STANDARD.md).

---

## False-Green Protection

One of the important engineering risks in AI-assisted development is the **false green**: a test passes, but the underlying behavior is not actually proven.

E2E Engine is designed to look beyond exit codes and superficial assertions by evaluating evidence, test behavior, regression signals, and independent verification.

A healthy workflow should be:

```text
Implement
   ↓
Test
   ↓
Inspect evidence
   ↓
Verify independently
   ↓
Accept or correct
```

—not simply:

```text
Implement → tests passed → done
```

---

## Guardrails and Tool Governance

Tools are governed by role, scope, risk, and approval rules.

The intended model is:

```text
Worker / Agent
      ↓
E2E Policy
      ↓
Scope + Risk + Approval
      ↓
Allowed Tool
      ↓
Execution
```

Security boundaries are enforced by deterministic mechanisms rather than relying on model memory.

MCP can provide interoperability, but it is not treated as the E2E authorization boundary.

---

## Runtime Neutrality

E2E Engine is designed to remain independent of a single AI provider.

```text
                 E2E Engine
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Claude Code   Codex     Other Runtimes
          │           │           │
          └───────────┼───────────┘
                      ▼
              Common Engineering
                   Contract
```

Runtime adapters keep provider-specific behavior isolated while engineering standards remain portable.

---

## Web Intelligence

Web Intelligence is a capability rather than a hard dependency on a single crawler.

Current integration includes an optional Crawl4AI adapter for use cases such as:

- public website research
- UI and information-architecture research
- schema and mock-data discovery
- SEO and marketing intelligence

The capability is intentionally vendor-neutral so the provider can evolve without changing the E2E Engine core.

See [`architecture/WEB-INTELLIGENCE.md`](../architecture/WEB-INTELLIGENCE.md).

---

## Evidence and Run Artifacts

Engineering runs can produce evidence covering:

- requirements and plans
- worker actions and reports
- test and evaluation results
- verification decisions
- introspection data
- final outcomes

This makes engineering decisions inspectable instead of relying on a conversational claim from an AI agent.

---

## CI and Self-Healing

The repository includes deterministic CI proof workflows and an optional CI self-healing loop.

The self-healing workflow can inspect failed runtime checks, diagnose the underlying defect, attempt a repair, validate locally, and re-dispatch CI.

The repair process is explicitly designed **not to weaken or delete tests** and does not replace independent SD3 verification.

See [`architecture/CI-SELF-HEAL.md`](../architecture/CI-SELF-HEAL.md).

---

## Minimality Principle

E2E Engine follows a minimality ladder:

```text
Need
 ↓
Reuse
 ↓
Standard library
 ↓
Native tooling
 ↓
Installed dependency
 ↓
Simple implementation
 ↓
Custom abstraction
```

The system should prefer the smallest reliable mechanism instead of adding unnecessary agents, dependencies, or abstractions.

---

## Typical Workflow

A typical engineering request can look like:

```bash
e2e intelligence "add authentication"
e2e orchestrate "add authentication"
e2e execute "add authentication"
```

Execution remains dry-run by default. Actual execution requires the configured external runtime and appropriate authorization.

Useful runtime inspection commands include:

```bash
e2e doctor
e2e status
e2e skill diagnose
```

Repository intelligence:

```bash
e2e brain build
e2e brain check
```

Evaluation:

```bash
e2e eval-suite run evals/smoke.json
e2e eval-suite run evals/proof.json
```

---

## Design Principles

1. **Evidence over assertions** — show what happened and how it was verified.
2. **Independent verification** — implementation and final judgment are separate roles.
3. **Deterministic guardrails** — security and policy boundaries should not depend on model memory.
4. **Minimal changes** — implement the smallest correct solution.
5. **Research before implementation** — establish relevant facts before making non-trivial changes.
6. **Memory is advisory** — historical knowledge does not grant permission.
7. **Failure should teach** — evaluation and introspection strengthen future engineering decisions.
8. **No blind retries** — repeated failures should escalate rather than loop indefinitely.
9. **Runtime neutrality** — engineering standards remain portable across agent runtimes.
10. **Proof is earned** — higher confidence requires stronger evidence.

---

## Project Documentation

Important repository documents:

- [`E2E-PLAN.md`](../E2E-PLAN.md) — master roadmap
- [`SD-AGENT-SYSTEM.md`](../SD-AGENT-SYSTEM.md) — SD1/SD2/SD3 architecture
- [`architecture/PROOF-STANDARD.md`](../architecture/PROOF-STANDARD.md) — production proof contract
- [`architecture/REGRESSION-INTELLIGENCE.md`](../architecture/REGRESSION-INTELLIGENCE.md) — regression intelligence
- [`architecture/TOOL-SYSTEM.md`](../architecture/TOOL-SYSTEM.md) — tool architecture
- [`architecture/WEB-INTELLIGENCE.md`](../architecture/WEB-INTELLIGENCE.md) — web intelligence capability
- [`architecture/CI-SELF-HEAL.md`](../architecture/CI-SELF-HEAL.md) — CI repair loop
- [`runtime/RUNTIME-ADAPTER-STANDARD.md`](../runtime/RUNTIME-ADAPTER-STANDARD.md) — runtime contract
- [`standards/SKILL-AUTHORING-STANDARD.md`](../standards/SKILL-AUTHORING-STANDARD.md) — skill quality standard

For the repository overview and current implementation status, see the main [`README.md`](../README.md).
