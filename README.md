# E2E — Engineering Intelligence & Verification System

> A runtime-neutral engineering system for building, orchestrating, evaluating, and verifying AI-assisted software changes.

E2E is designed around a simple principle: **AI-generated engineering work should be treated as an engineering process, not just a model response.**

It combines repository intelligence, reusable specialist skills, structured context, multi-agent orchestration, deterministic guardrails, evaluation history, regression intelligence, and independent verification into one engineering workflow.

[![E2E Runtime](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-runtime.yml/badge.svg)](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-runtime.yml) [![E2E Proof](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-proof.yml/badge.svg)](https://github.com/Creativestarjsp/e2eskill/actions/workflows/e2e-proof.yml)

> **Proof status:** `NOT PROVEN` until the production-proof gates in [`architecture/PROOF-STANDARD.md`](architecture/PROOF-STANDARD.md) are satisfied. A green CI run means the tested checks passed; it does not by itself prove real-agent engineering reliability.

---

## Why E2E?

AI coding systems can produce useful implementations quickly, but reliable software engineering requires more than generating code. A production-oriented system must understand the repository, respect project rules, select the right expertise, verify changes, learn from previous failures, and provide evidence for its decisions.

E2E provides that engineering control plane.

### E2E focuses on

- **Repository intelligence** — understand files, symbols, imports, dependencies, callers, callees, and impact.
- **Context and rules** — combine repository, project, skill, task, and memory context with explicit precedence.
- **Specialist skills** — reusable engineering expertise for frontend, backend, APIs, databases, security, QA, DevOps, UI/UX, architecture, SEO, and more.
- **SD1 / SD2 / SD3 execution model** — separate implementation, orchestration, and independent supervision.
- **Evaluation** — measure engineering runs with deterministic graders, repeated attempts, pass@k, pass^k, latency, and baseline comparisons.
- **Regression intelligence** — use previous evaluation failures and baseline regressions to strengthen future plans.
- **Guardrails** — enforce secret detection, protected paths, lifecycle checks, and evidence requirements.
- **Runtime adapters** — provide a common engineering layer for Claude Code, Codex, and standalone execution.
- **Run evidence** — persist plans, worker reports, verification, evaluation, introspection, and final outcomes.
- **CI self-healing** — scheduled automation can inspect failed E2E Runtime results, repair the underlying defect with Claude, validate locally, and re-dispatch CI.

---

## Architecture

```text
                         ENGINEERING REQUEST
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Context + Rules         │
                    │ BRD / PRD / Project     │
                    │ Memory / Local Rules    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ CodeBrain                │
                    │ Repository Intelligence  │
                    │ Context / Impact         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Engineering Intelligence │
                    │ Risk / Regression /      │
                    │ Verification Planning    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD3 Supervisor           │
                    │ Independent Engineering  │
                    │ Policy + Quality Gate    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD2 Orchestrator         │
                    │ Decomposition / Workers  │
                    │ Dependencies / Parallel  │
                    └────────────┬────────────┘
                                 │
                         ┌───────┴───────┐
                         ▼               ▼
                    ┌──────────┐   ┌──────────┐
                    │ SD1      │   │ SD1      │
                    │ Worker   │   │ Worker   │   ...
                    └────┬─────┘   └────┬─────┘
                         │              │
                         └──────┬───────┘
                                ▼
                    ┌─────────────────────────┐
                    │ Testing + Evaluation     │
                    │ Regression + Evidence    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SD3 Verification        │
                    │ Approve / Correct /     │
                    │ Reject / Escalate       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Run Artifacts + Memory  │
                    │ Evidence / Learning     │
                    └─────────────────────────┘
```

### SD1 — Worker

Executes a bounded engineering task using a specialist skill. Workers are responsible for implementation and evidence, not final approval.

### SD2 — Orchestrator

Decomposes the request, selects and prioritizes workers, manages dependencies, parallelizes safe work, aggregates results, and coordinates corrections.

### SD3 — Engineering Supervisor

Acts as an independent engineering authority. SD3 inspects the actual repository and evidence, evaluates requirements, architecture, security, integration, tests, and regression risk, then approves, requests correction, rejects, or escalates.

---

## Engineering Intelligence

E2E does not treat every task as a fresh task.

Before execution, intelligence can combine:

```text
Task
 │
 ├── CodeBrain context + impact
 ├── Project rules
 ├── Relevant skills
 ├── Memory
 ├── Evaluation history
 └── Baseline comparison
          │
          ▼
   Regression Risk
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
   LOW  MEDIUM  HIGH
          │      │
          │      ├── stronger verification
          │      ├── QA / security escalation
          │      └── SD3 regression gate
          │
          └── targeted verification
```

Historical failures are advisory signals, not authorization. High-risk regressions can strengthen the execution plan and verification requirements without bypassing independent SD3 review.

---

## Repository Intelligence

**CodeBrain** builds a lightweight repository model without requiring a heavyweight runtime dependency.

It can provide:

- file and content metadata
- language-aware symbol discovery
- imports and dependency relationships
- approximate call relationships
- caller / callee analysis
- impact analysis
- task-oriented context retrieval
- optional Tree-sitter parsing for supported languages

Supported source families include Python, JavaScript, JSX, TypeScript, Java, Go, Rust, PHP, Ruby, C#, Kotlin, and Swift.

---

## Evaluation, Verification & Proof

E2E separates **execution success** from **engineering confidence**.

The evaluation layer supports:

- deterministic command-based evaluation suites
- exit-code, content, and file-existence graders
- independent repeated attempts
- `pass@k`
- `pass^k`
- pass-rate and latency statistics
- baseline comparison
- regression detection
- persisted evaluation evidence

The repository now has a dedicated proof ladder:

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

The automated **E2E Proof Gate** runs P0-P2 across Python 3.9, 3.10, 3.11, and 3.12. The separate **E2E Real Agent Proof** workflow is manual and cost-bearing: it runs real SD1/SD3 agents against a disposable repository and stores evidence without pushing agent changes to `main`.

A production-proof claim requires the thresholds and evidence defined in [`architecture/PROOF-STANDARD.md`](architecture/PROOF-STANDARD.md), including repeated real-agent tasks and recovery scenarios. GitHub Actions supports matrix testing and persistent workflow artifacts, which E2E uses to make this evidence reproducible and inspectable. citeturn0search2turn0search0

### CI Self-Healing

The repository also contains a scheduled repair workflow:

```text
.github/workflows/e2e-self-heal.yml
```

It checks the latest `E2E Runtime` result, collects failed-run logs, asks Claude to diagnose and repair the underlying defect, runs local verification, commits only validated changes, and explicitly dispatches the runtime workflow again. The scheduler repeats on later runs if the runtime remains red.

The repair loop does **not** weaken or delete tests and does not replace SD3 verification. It requires a Claude Actions secret such as `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`.

See [`architecture/CI-SELF-HEAL.md`](architecture/CI-SELF-HEAL.md) for the operating contract.

---

## Quick Start

### Requirements

- Python 3.9+
- Git
- `pytest` for running the test suite
- Claude Code and/or Codex when using external agent runtimes

### Install

```bash
python -m pip install -e .
```

### Set up a project

```bash
e2e init                              # writes e2e.json and .e2e/
e2e init --skills-path shared/skills  # when skills live somewhere else
```

`init` records where this project keeps its skills. Discovery searches
`skills/` and `.e2e/skills/` by default; override with `skills_paths` in
`e2e.json`, or with the `E2E_SKILLS_PATH` environment variable (`PATH`
syntax, highest precedence).

### Inspect the runtime

```bash
e2e doctor
e2e status
e2e skill diagnose   # what the registry found, and why it found nothing
```

### Enforce guardrails automatically

`runtime/hooks.yaml` describes the guardrail stages, but nothing invokes them
on its own — `e2e guardrails check` only runs when something calls it. To make
a stage actually block, wire it to your runtime's hook system. For Claude Code,
`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{ "type": "command", "command": "./bin/e2e-guardrails.sh pre-edit" }]
    }]
  }
}
```

`guardrails check --stage pre-edit --file <path>` checks a single path, which is
what a pre-edit hook needs: the write has not happened, so there is no staged
diff to read. It exits non-zero when a rule blocks.

### Build repository intelligence

```bash
e2e brain build
e2e brain check
```

### Generate engineering context

```bash
e2e context "add authentication"
e2e intelligence "add authentication"
```

### Plan and execute

```bash
e2e orchestrate "add authentication"
e2e execute "add authentication"
```

Execution is dry-run by default. Use `--execute` only when an external runtime is configured and the task is authorized.

### Run evaluations

```bash
e2e eval-suite run evals/smoke.json
e2e eval-suite run evals/proof.json
```

---

## Project Structure

```text
E2E/
├── .codex/                    # Codex runtime instructions and agents
├── .github/workflows/         # CI, proof, and self-healing automation
├── architecture/              # Runtime and engineering architecture
├── e2e/                        # Native Python runtime
├── evals/                      # Deterministic evaluation suites
├── runtime/                    # Runtime adapter contracts
├── skills/                     # Shared specialist skills
├── standards/                  # Authoring, browser, quality, review standards
├── templates/                  # Reusable project templates
├── tests/                      # Runtime tests
├── AGENTS.md                   # Agent operating instructions
├── BRD.md                      # Business requirements
├── CLAUDE.md                   # Claude Code instructions
├── CONVENTIONS.md              # Repository conventions
└── E2E-PLAN.md                 # Master roadmap
```

---

## Runtime Model

E2E keeps domain expertise separate from runtime-specific adapters.

```text
Shared E2E Skills
      │
      ├───────────────┐
      ▼               ▼
 Claude Code        Codex
      │               │
      └───────┬───────┘
              ▼
        E2E Runtime
              │
       SD1 / SD2 / SD3
```

This allows engineering standards and specialist skills to remain portable while runtime-specific execution behavior stays isolated.

---

## Design Principles

1. **Evidence over assertions** — a worker must show what changed and how it was verified.
2. **Independent verification** — SD3 is not the same role as implementation.
3. **Deterministic guardrails** — safety boundaries are enforced by code, not model memory.
4. **Minimal changes** — agents should implement the smallest correct solution.
5. **Research before implementation** — non-trivial work should establish relevant facts before editing.
6. **Memory is advisory** — remembered information never becomes an authorization boundary.
7. **Failure should teach the system** — evaluation and introspection feed regression intelligence.
8. **No blind retries** — persistent failures escalate instead of looping indefinitely.
9. **Runtime neutrality** — Claude Code and Codex share the same engineering contract.
10. **Proof is earned** — green CI is a health signal; repeated real-world evidence earns `PROVEN`.

---

## Documentation

Key architecture documents include:

- [`E2E-PLAN.md`](E2E-PLAN.md) — master roadmap
- [`SD-AGENT-SYSTEM.md`](SD-AGENT-SYSTEM.md) — SD1/SD2/SD3 model
- [`architecture/REGRESSION-INTELLIGENCE.md`](architecture/REGRESSION-INTELLIGENCE.md) — regression intelligence
- [`architecture/CI-SELF-HEAL.md`](architecture/CI-SELF-HEAL.md) — CI repair loop
- [`architecture/PROOF-STANDARD.md`](architecture/PROOF-STANDARD.md) — production proof contract
- [`architecture/TOOL-SYSTEM.md`](architecture/TOOL-SYSTEM.md) — tool architecture
- [`architecture/DATABASE-ABSTRACTION.md`](architecture/DATABASE-ABSTRACTION.md) — persistence abstraction
- [`runtime/RUNTIME-ADAPTER-STANDARD.md`](runtime/RUNTIME-ADAPTER-STANDARD.md) — runtime contract
- [`standards/BROWSER-EXECUTION-STANDARD.md`](standards/BROWSER-EXECUTION-STANDARD.md) — browser execution policy
- [`standards/SKILL-AUTHORING-STANDARD.md`](standards/SKILL-AUTHORING-STANDARD.md) — skill quality standard

---

## Development Workflow

For repository changes:

```bash
git checkout -b feature/<name>
python -m pytest -q
python -m e2e brain build
python -m e2e brain check
python -m e2e guardrails check --stage verification
python -m e2e eval-suite run evals/smoke.json
git diff --check
git commit
```

For non-trivial engineering work, prefer:

```bash
e2e intelligence "<task>"
e2e orchestrate "<task>"
e2e execute "<task>" --execute
```

---

## Project Status

The repository is actively building toward production-grade engineering automation.

Current foundation includes:

- repository intelligence
- context and rule precedence
- specialist skill system
- SD1 / SD2 / SD3 architecture
- multi-worker orchestration
- deterministic guardrails
- memory and evaluation history
- regression intelligence
- runtime adapters
- MCP tool gateway
- execution artifacts
- introspection
- deterministic evaluation harness
- CI self-healing
- repeatable P0-P2 proof gate
- manual P3-P4 real-agent proof workflow

**Current status: `VALIDATED` only after the proof gate is green. `PROVEN` requires the full production-proof standard.**

---

## Contributing

1. Read `AGENTS.md` and `CLAUDE.md`.
2. Follow the relevant authoring standard.
3. Keep changes minimal and evidence-based.
4. Add or update tests for behavioral changes.
5. Run guardrails and relevant evaluation suites.
6. Do not weaken tests to make a workflow pass.
7. Include verification evidence with substantive changes.

---

## License

See [`LICENSE`](LICENSE).

---

## Maintainer

**Creative Star JSP**
