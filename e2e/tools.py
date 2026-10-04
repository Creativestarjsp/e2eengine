from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .deploy import GATES, gate_satisfied


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    transport: str
    risk: str
    scopes: tuple[str, ...]
    roles: tuple[str, ...]
    approval: str
    #: Name of the deploy gate that must have passed for the current tree, or "".
    gate: str = ""


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str
    required_approval: bool
    tool: str
    granted_scopes: tuple[str, ...]


def _registry_path(root: Path) -> Path:
    return root / "runtime" / "tools.json"


def load_tools(root: Path) -> list[Tool]:
    path = _registry_path(root)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        Tool(
            name=item["name"],
            description=item.get("description", ""),
            transport=item.get("transport", "runtime"),
            risk=item.get("risk", "read"),
            scopes=tuple(item.get("scopes", [])),
            roles=tuple(item.get("roles", [])),
            approval=item.get("approval", "explicit"),
            gate=item.get("gate", ""),
        )
        for item in data.get("tools", [])
    ]


def tool_map(root: Path) -> dict[str, Tool]:
    return {tool.name: tool for tool in load_tools(root)}


def _policy_entry(tool: Tool, with_approval: bool) -> dict[str, Any]:
    entry: dict[str, Any] = {"name": tool.name, "transport": tool.transport, "risk": tool.risk, "scopes": list(tool.scopes)}
    if with_approval:
        entry["approval"] = tool.approval
    if tool.gate:
        entry["gate"] = tool.gate
    return entry


def policy_for_role(root: Path, role: str) -> dict[str, Any]:
    tools = [tool for tool in load_tools(root) if role in tool.roles]
    return {
        "version": 1,
        "role": role,
        "default_policy": "deny",
        "allowed_tools": [_policy_entry(tool, True) for tool in tools if tool.approval == "none"],
        "approval_required_tools": [_policy_entry(tool, False) for tool in tools if tool.approval == "explicit"],
    }


def write_policy(root: Path, role: str, path: Path | None = None) -> Path:
    target = path or (root / ".e2e" / "tool-policy.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(policy_for_role(root, role), indent=2, sort_keys=True), encoding="utf-8")
    return target


def decide(root: Path, tool_name: str, role: str, scopes: set[str] | None = None, approved: bool = False) -> ToolDecision:
    tool = tool_map(root).get(tool_name)
    if tool is None:
        return ToolDecision(False, "unknown-tool", False, tool_name, ())
    granted = set(scopes or ())
    if role not in tool.roles:
        return ToolDecision(False, "role-not-authorized", tool.approval == "explicit", tool_name, tuple(sorted(granted & set(tool.scopes))))
    missing = set(tool.scopes) - granted if scopes is not None else set()
    if missing:
        return ToolDecision(False, "missing-scope:" + ",".join(sorted(missing)), tool.approval == "explicit", tool_name, tuple(sorted(granted & set(tool.scopes))))
    # The gate comes before approval: an owner should not be asked to approve
    # a deploy that has not passed its checks for the tree being deployed.
    if tool.gate and not gate_satisfied(root, tool.gate):
        return ToolDecision(False, f"deploy-gate-required:{tool.gate}", tool.approval == "explicit", tool_name, tuple(sorted(granted & set(tool.scopes))))
    if tool.approval == "explicit" and not approved:
        return ToolDecision(False, "approval-required", True, tool_name, tuple(sorted(granted & set(tool.scopes))))
    return ToolDecision(True, "allowed", False, tool_name, tuple(sorted(granted & set(tool.scopes))))


def _fingerprint(arguments: dict[str, Any]) -> str:
    redacted = {}
    secret_words = ("secret", "token", "password", "authorization", "api_key", "apikey")
    for key, value in arguments.items():
        if any(word in key.lower() for word in secret_words):
            redacted[key] = "<redacted>"
        else:
            redacted[key] = value
    payload = json.dumps(redacted, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def audit(root: Path, *, agent: str, runtime: str, tool: str, operation: str, decision: ToolDecision, arguments: dict[str, Any], result: str) -> dict[str, Any]:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "runtime": runtime,
        "tool": tool,
        "operation": operation,
        "decision": "allow" if decision.allowed else "deny",
        "reason": decision.reason,
        "required_approval": decision.required_approval,
        "granted_scopes": list(decision.granted_scopes),
        "arguments_fingerprint": _fingerprint(arguments),
        "result": result,
    }
    path = root / ".e2e" / "tool-audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def check_registry(root: Path) -> dict[str, Any]:
    path = _registry_path(root)
    if not path.exists():
        return {"status": "missing", "path": str(path), "tools": 0}
    try:
        tools = load_tools(root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return {"status": "invalid", "path": str(path), "error": str(exc), "tools": 0}
    names = [tool.name for tool in tools]
    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    invalid = [tool.name for tool in tools if not tool.roles or not tool.scopes]
    invalid_gates = [tool.name for tool in tools if tool.gate and tool.gate not in GATES]
    status = "pass" if not duplicate_names and not invalid and not invalid_gates else "fail"
    return {"status": status, "path": str(path), "tools": len(tools), "duplicates": duplicate_names, "invalid": invalid, "invalid_gates": invalid_gates}
