# E2E Master Engineering System Plan

## Mission

E2E is a runtime-neutral engineering system for AI-assisted software development. It combines project context, rules, specialist skills, SD1/SD2/SD3 agents, codebase intelligence, memory, guardrails, tools, verification, and runtime adapters.

Existing skills remain canonical. The roadmap expands the system around them; it does not replace them.

## Target Architecture

```text
                              E2E
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
     Context                  Rules                Skills
        │                      │                      │
        └──────────────┬───────┴──────────────┬───────┘
                       │                      │
                    CodeBrain              Memory
                       │                      │
                  Minimality                 │
                       └──────────┬───────────┘
                                  │
                           SD3 Supervisor
                                  │
                           SD2 Orchestrator
                                  │
                         ┌────────┼────────┐
                         │        │        │
                        SD1      SD1      SD1 ...
                         │        │        │
                    Specialist Skills
                         │
                  Tool Capability Layer
                         │
                 Claude Code / Codex / MCP
```

## Phase Status

| Phase | Architecture | Engineering implementation |
|---|---|---|
| 1 | Complete | 🟢 Mostly implemented |
| 2 | Complete | 🟢 Context/rules runtime implemented |
| 3 | Complete | 🟢 Native CodeBrain MVP + optional Tree-sitter provider |
| 4 | Complete | 🟢 SD1/SD2/SD3 execution with isolated worktrees and bounded correction loop |
| 5 | Complete | 🟢 Skills + executable registry implemented |
| 6 | Complete | 🟢 Tool registry, scopes, approval policy, audit ledger, MCP boundary implemented |
| 7 | Complete | 🟢 Hooks + persistent memory runtime implemented |
| 8 | Complete | 🟢 Verification runner + independent SD3 review/correction |
| 9 | Complete | 🟢 Claude/Codex runtime contract, parity checks, isolated MCP handoff, and runtime inspection CLI |
| 10 | Complete | 🟢 CLI implemented; visualization remains future presentation layer |
| 11 | Complete | 🟢 Reproducible benchmark runner |
| 12 | Complete | 🟢 Automated release gate checker; explicit SD3/owner approval remains required |

## Runtime Implementation

```text
e2e/
├── brain.py       CodeBrain MVP
├── context.py     context + rules + memory loader
├── skills.py      skill registry/discovery
├── hooks.py       deterministic guardrails
├── guardrails.py  runtime-enforced commit/merge policy
├── memory.py      durable scoped memory with expiry/supersession
├── verify.py      evidence/verification runner
├── adapters.py    runtime capability detection + parity surface
├── runtime_contract.py shared Claude/Codex execution contract
├── tools.py       tool registry + policy + audit
├── tool_gateway.py stdio MCP gateway
├── orchestrator.py SD2 planning and dependency graph
├── worktree.py    isolated SD1 Git workspaces
├── executor.py    SD1 execution + integration + SD3 review/correction
├── benchmark.py   reproducible benchmark runner
├── release.py     release gate checker
└── cli.py         developer CLI

runtime/
├── tools.json     controlled capability registry
└── RUNTIME-ADAPTER-STANDARD.md shared runtime adapter contract

architecture/
└── TOOL-SYSTEM.md tool/MCP architecture and security boundary
```

Generated state remains under `.e2e/` and is ignored by Git. Tool audit records are append-only JSONL and fingerprint argument payloads rather than storing secret values.

## Runtime Adapter Contract

Claude Code and Codex share one runtime-neutral contract. Runtime-specific behavior is limited to launcher/configuration transport:

```text
Task + role
 ↓
Project context + rules + safe memory
 ↓
CodeBrain context + matched skills
 ↓
Role tool policy
 ↓
E2E MCP gateway
 ↓
Runtime-specific launcher
 ↓
Evidence/report contract
 ↓
SD3 verification
```

Use `e2e runtime inspect`, `e2e runtime contract --runtime claude-code`, and `e2e runtime parity` to inspect the contract. Claude uses `CLAUDE.md` and strict MCP JSON configuration; Codex uses `AGENTS.md` and isolated `CODEX_HOME` TOML configuration. Neither runtime may weaken E2E authorization.

## Persistent Memory Contract

```text
Verified event / decision / constraint
 ↓
Secret-safe Memory.add()
 ↓
Scoped record + evidence + confidence
 ↓
Optional expiry / supersession
 ↓
Memory.search(task)
 ↓
Bounded Context package
 ↓
SD2 / SD1 / SD3
```

Memory is advisory context, not an authorization source. Current repository rules, security policy, tool policy, and fresh inspection always outrank memory. Secret-like summaries/evidence are rejected. Expired memories are omitted from normal retrieval, and superseded records are retained for audit/history but omitted from default search.

## Tool / MCP Contract

```text
Agent
 ↓
Tool Registry
 ↓
Role + Scope + Approval Policy
 ↓
Runtime/MCP Adapter
 ↓
External Tool
 ↓
Audit + Evidence
 ↓
SD3 Inspection
```

Unknown capabilities are denied by default. Mutation, destructive, and secret-bearing capabilities require explicit approval. MCP is an interoperability layer, not the E2E authorization boundary.

## SD1 / SD2 / SD3 Execution Contract

```text
Task
 ↓
SD2 plan
 ↓
dependency-ready SD1 workers
 ↓
isolated worktrees (max 4 active)
 ↓
worker evidence + tool ledger
 ↓
deterministic integration
 ↓
CodeBrain refresh
 ↓
SD3 independent inspection
 ├── approved → DONE
 ├── rejected → ESCALATE
 └── needs-correction
       ↓
   fresh SD1 correction workspace
       ↓
   integrate + refresh CodeBrain
       ↓
   SD3 review again
```

The correction loop is bounded at two rounds. Failed workers, merge conflicts, malformed supervisor decisions, and persistent correction failures remain explicit in execution reports rather than triggering blind retries.

## Completed Architecture Contracts

- `architecture/CONTEXT-AND-RULES.md`
- `architecture/CODEBRAIN.md`
- `architecture/SKILL-REGISTRY.md`
- `architecture/HOOKS-AND-GUARDRAILS.md`
- `architecture/MEMORY.md`
- `architecture/VERIFICATION.md`
- `architecture/RUNTIME-ADAPTERS.md`
- `architecture/DEVELOPER-EXPERIENCE.md`
- `architecture/BENCHMARKS.md`
- `architecture/RELEASE-GATES.md`
- `architecture/MINIMALITY-AND-CORRECTNESS.md`
- `architecture/TOOL-SYSTEM.md`
- `architecture/BLUEPRINTS-AND-STORIES.md`

## Engineering Principles

1. Preserve existing skills unless a replacement has passed migration and verification.
2. Shared domain knowledge lives in `skills/` and `standards/`.
3. Claude/Codex-specific behavior belongs in runtime adapters.
4. SD1 executes; SD2 orchestrates; SD3 independently verifies.
5. Every meaningful action has inputs, outputs, verification, failure handling, and evidence.
6. Parallel work is allowed only when edits and dependencies are safe.
7. Security-sensitive actions require explicit guardrails and verification.
8. Agents must distinguish facts, inspected evidence, assumptions, and unknowns.
9. Repeated failure triggers diagnosis and escalation rather than infinite retries.
10. Before implementing, prefer the smallest correct solution: need → reuse → stdlib → native → installed dependency → simple implementation → custom abstraction.
11. Minimality never removes trust-boundary validation, data-loss protection, security, accessibility, or required correctness.
12. Tool permissions are capability-based and deny-by-default.
13. Tool audit evidence must never persist raw secrets.
14. Benchmark claims must be reproduced with real agentic execution and executed verification.
15. Memory is contextual evidence, never permission to bypass current policy.
16. Runtime parity is measured on the shared contract, not identical launcher syntax.

## Verification

CI runs the Python runtime tests and smoke-checks CodeBrain and status. Real repository tasks should still be evaluated by the configured Claude/Codex runtime and independently approved by SD3.

## Definition of Done

A supported runtime should be able to:

```text
load project context
→ load applicable rules
→ retrieve relevant safe memory
→ discover relevant skills
→ retrieve targeted code context
→ apply minimality decision ladder
→ decompose work through SD2
→ execute through SD1 in isolated workspaces
→ request only approved tool capabilities
→ record tool evidence
→ integrate safely
→ verify independently through SD3
→ perform bounded corrections when necessary
→ preserve useful memory
→ enforce hooks/guardrails
→ report a reproducible result
→ satisfy release gates
```
