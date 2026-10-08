# E2E Tool System

## Purpose

The Tool System is the controlled capability layer between SD1/SD2/SD3 agents and external actions. It is runtime-neutral: Claude Code and Codex receive the same E2E capability model, while runtime adapters translate approved capabilities into runtime-specific tool or MCP configuration.

MCP is treated as an interoperability boundary, not as the E2E security boundary. The 2026-07-28 MCP specification provides standardized tools, resources, and prompts and adds stronger authorization and cacheability primitives; E2E still performs its own capability and policy checks before an agent is allowed to use a capability. 

## Architecture

```text
SD1 / SD2 / SD3
      |
      v
Tool Registry
      |
      +--> Capability Policy
      |      +-- role
      |      +-- scope
      |      +-- risk
      |      +-- approval
      |
      +--> Adapter
      |      +-- native
      |      +-- MCP
      |      +-- runtime-specific
      |
      +--> Audit / Evidence
      |
      v
External Tool
```

## Capability model

Every registered tool has:

- stable name
- description
- transport (`native`, `mcp`, or `runtime`)
- risk (`read`, `write`, `destructive`, `network`, `secret`)
- allowed SD roles
- allowed scopes
- explicit approval requirement
- executable/endpoint metadata

Default posture is deny-by-default. Unknown tools are denied. Destructive and secret-bearing capabilities require explicit approval.

## Scopes

Use narrow scopes instead of broad access:

- `repo.read`
- `repo.write`
- `git.read`
- `git.write`
- `shell.read`
- `shell.write`
- `browser.read`
- `browser.write`
- `network.read`
- `network.write`
- `secrets.use`
- `db.read`
- `db.write`
- `deploy.preview`
- `deploy.production`
- `deploy.rollback`
- `mobile.build`
- `store.submit`

A worker receives only the scopes required by its assigned task.

## Deploy gate

Deploy capabilities carry a `gate` in the registry. `decide()` refuses a gated tool unless that gate has passed for the tree as it is now:

| Tool | Approval | Gate |
|---|---|---|
| `deploy.preview` | none | `preview` |
| `mobile.build` | none | `preview` |
| `deploy.production` | explicit | `production` |
| `store.submit` | explicit | `production` |
| `deploy.rollback` | explicit | none, so an incident is never blocked by a failing check |

`e2e deploy check --env preview|production [--test "<command>"]` runs the gate (`e2e/deploy.py`): version control, secret scan, story check, credential register, deploy preflight, and the mobile and workflow checks where they apply. It composes the deployment skills' own scripts rather than duplicating them. The result is recorded in `.e2e/deploy-gate.json` with the commit and a digest of local changes; any edit or new commit makes it stale. A passing production gate also satisfies preview.

Production fails closed: a check that cannot run counts as a failure. The gate comes before approval in the decision order, so an owner is never asked to approve a deploy that has not passed its checks. The gate verifies that owner approval is *recorded* in `RELEASE-CHECKLIST.md`; it does not grant it.

`e2e deploy status` shows each gate and whether it still applies to the current tree.

## MCP boundary

MCP servers can expose tools, resources, and prompts. E2E does not blindly inherit server permissions. An MCP registration is first converted into an E2E capability record, then evaluated by policy before being surfaced to a worker.

The first implementation deliberately does not add a mandatory MCP SDK dependency. Native E2E tooling and external MCP clients can be added incrementally without making the core runtime unavailable offline.

## Audit

Every allowed or denied tool request should produce an audit event containing:

- timestamp
- agent/runtime
- tool
- operation
- decision
- scopes requested/granted
- approval state
- arguments fingerprint, never raw secrets
- result status
- evidence references

Secrets must never be persisted in audit events.

## SD3 visibility

SD3 receives a summarized tool-use ledger and evidence references. SD3 can reject execution when:

- a tool was used outside granted scope
- an approval-required tool was used without approval
- a destructive action lacks evidence
- secret material appears in logs/evidence
- a worker reports an action that is absent from the ledger

## Initial implementation

The dependency-free control plane lives in `e2e/tools.py` and `runtime/tools.json`.

Useful commands:

```bash
e2e tool list
e2e tool check
e2e tool inspect browser
```

Execution of arbitrary external tools is intentionally not enabled by the registry alone. A later runtime adapter can bind a registered capability to a concrete MCP/native implementation after policy approval.
