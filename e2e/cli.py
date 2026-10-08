from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .adapters import capabilities, detect
from .benchmark import run_case
from .blueprints import check as check_blueprints, list_blueprints, status as blueprint_status
from .brain import CodeBrain
from .context import build_context
from .deploy import GATES as DEPLOY_GATES, gate as deploy_gate, status as deploy_status
from .evaluation import evaluate_run
from .eval_harness import compare_baseline, load_suite, run_suite, command_runner
from .executor import execute
from .guardrails import check as check_guardrails, policy as guardrail_policy, write_policy as write_guardrail_policy
from .intelligence import build_intelligence, synthesize_run
from .introspection import diagnose
from .memory import Memory
from .orchestrator import plan, write_plan
from .project import init as init_project
from .release import release_check
from .run_artifacts import persist_run
from .runtime_contract import contract, parity
from .skills import diagnose as diagnose_skills, discover, match
from .stories import check as check_stories, load as load_stories, new as new_story, ready as ready_stories
from .templates import copy as copy_template, list_templates
from .tool_gateway import serve, write_mcp_configs
from .tools import check_registry, load_tools, policy_for_role
from .verify import verify

SUCCESS_EXECUTION_STATUSES = {"approved", "planned", "runtime-unavailable"}


def _root() -> Path:
    return Path.cwd()


def _relative_to_root(root: Path, path: str) -> str:
    """Normalise a path for guardrail rules, which match repo-relative paths."""
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        # Outside the repository: keep it absolute so the rule still sees it.
        return candidate.as_posix()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="e2e", description="E2E engineering runtime")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("doctor", "status", "release"):
        sub.add_parser(name)
    ini = sub.add_parser("init")
    ini.add_argument("--skills-path", dest="skills_paths", action="append", help="Directory holding <skill>/SKILL.md; repeatable")
    ini.add_argument("--blueprints-path", dest="blueprints_paths", action="append", help="Directory holding blueprint *.json files; repeatable. Defaults to workflows/ beside the skills path")
    ini.add_argument("--templates-path", dest="templates_paths", action="append", help="Directory holding document templates; repeatable. Defaults to templates/ beside the skills path")
    ini.add_argument("--force", action="store_true", help="Overwrite an existing e2e.json")
    c = sub.add_parser("context"); c.add_argument("task")
    intel = sub.add_parser("intelligence"); intel.add_argument("task")
    s = sub.add_parser("skill"); ss = s.add_subparsers(dest="skill_cmd", required=True); ss.add_parser("list"); ss.add_parser("diagnose"); si = ss.add_parser("inspect"); si.add_argument("name")
    t = sub.add_parser("tool"); ts = t.add_subparsers(dest="tool_cmd", required=True); ts.add_parser("list"); ts.add_parser("check"); ti = ts.add_parser("inspect"); ti.add_argument("name"); tp = ts.add_parser("policy"); tp.add_argument("role", choices=("sd1", "sd2", "sd3")); tg = ts.add_parser("gateway"); tg.add_argument("--role", choices=("sd1", "sd2", "sd3"), default="sd1"); tg.add_argument("--serve", action="store_true")
    g = sub.add_parser("guardrails"); gs = g.add_subparsers(dest="guardrail_cmd", required=True); gs.add_parser("policy"); gc = gs.add_parser("check"); gc.add_argument("--stage", choices=("pre-edit", "pre-commit", "pre-merge", "verification"), default="verification"); gc.add_argument("--file", dest="files", action="append", help="Check these paths instead of the staged diff; repeatable"); gs.add_parser("write")
    m = sub.add_parser("memory"); ms = m.add_subparsers(dest="memory_cmd", required=True); ml = ms.add_parser("list"); ml.add_argument("--scope"); ml.add_argument("--include-expired", action="store_true"); mq = ms.add_parser("search"); mq.add_argument("query"); mq.add_argument("--scope"); mq.add_argument("--limit", type=int, default=20); ma = ms.add_parser("add"); ma.add_argument("kind"); ma.add_argument("scope"); ma.add_argument("summary"); ma.add_argument("--evidence", action="append", default=[]); ma.add_argument("--source", default="runtime"); ma.add_argument("--confidence", default="verified"); ma.add_argument("--expires-days", type=int); ma.add_argument("--supersedes")
    b = sub.add_parser("brain"); bs = b.add_subparsers(dest="brain_cmd", required=True); bs.add_parser("build"); bs.add_parser("check"); bm = bs.add_parser("map"); bm.add_argument("path", nargs="?", default=""); bx = bs.add_parser("search"); bx.add_argument("query"); bi = bs.add_parser("impact"); bi.add_argument("target")
    rt = sub.add_parser("runtime"); rts = rt.add_subparsers(dest="runtime_cmd", required=True); rti = rts.add_parser("inspect"); rti.add_argument("--runtime", choices=("claude-code", "codex")); rti.add_argument("--role", choices=("sd1", "sd2", "sd3"), default="sd1"); rtc = rts.add_parser("contract"); rtc.add_argument("--runtime", choices=("claude-code", "codex"), required=True); rtc.add_argument("--role", choices=("sd1", "sd2", "sd3"), default="sd1"); rtp = rts.add_parser("parity"); rtp.add_argument("--role", choices=("sd1", "sd2", "sd3"), default="sd1")
    st = sub.add_parser("story"); sts = st.add_subparsers(dest="story_cmd", required=True); sts.add_parser("list"); sts.add_parser("check"); sts.add_parser("next"); stn = sts.add_parser("new"); stn.add_argument("title")
    tm = sub.add_parser("template"); tms = tm.add_subparsers(dest="template_cmd", required=True); tms.add_parser("list"); tmc = tms.add_parser("copy"); tmc.add_argument("name"); tmc.add_argument("destination", nargs="?")
    bp = sub.add_parser("blueprint"); bps = bp.add_subparsers(dest="blueprint_cmd", required=True); bps.add_parser("list"); bps.add_parser("check"); bpst = bps.add_parser("status"); bpst.add_argument("name")
    dp = sub.add_parser("deploy"); dps = dp.add_subparsers(dest="deploy_cmd", required=True); dpc = dps.add_parser("check"); dpc.add_argument("--env", choices=DEPLOY_GATES, default="preview"); dpc.add_argument("--test", dest="test_command", help="Test command to run as part of the gate"); dps.add_parser("status")
    r = sub.add_parser("run"); r.add_argument("task")
    o = sub.add_parser("orchestrate"); o.add_argument("task")
    e = sub.add_parser("execute"); e.add_argument("task"); e.add_argument("--runtime", choices=("auto", "claude-code", "codex"), default="auto"); e.add_argument("--execute", dest="execute_agents", action="store_true", help="Actually launch SD1/SD3 agents; default is dry-run"); e.add_argument("--max-workers", type=int, default=4)
    for planner in (r, o, e):
        planner.add_argument("--blueprint", help="Follow this blueprint's next ready phase instead of matching skills by task text")
        planner.add_argument("--story", help="Build one story, e.g. STORY-012; its acceptance criteria go to SD3")
    v = sub.add_parser("verify"); v.add_argument("--test", dest="test_command")
    be = sub.add_parser("benchmark"); be.add_argument("command"); be.add_argument("--repetitions", type=int, default=1)
    ev = sub.add_parser("evaluate"); ev.add_argument("task"); ev.add_argument("--reports", required=True, help="Path to a JSON file containing worker reports")
    es = sub.add_parser("eval-suite"); ess = es.add_subparsers(dest="eval_cmd", required=True); er = ess.add_parser("run"); er.add_argument("suite"); eb = ess.add_parser("compare"); eb.add_argument("current"); eb.add_argument("baseline"); eb.add_argument("--min-pass-rate", type=float, default=0.0); eb.add_argument("--max-latency-regression", type=float, default=0.25)
    ins = sub.add_parser("introspect"); ins.add_argument("--run", required=True, help="Path to a JSON execution report")
    args = p.parse_args(argv)
    root = _root()
    if args.cmd == "init":
        report = init_project(root, skills=args.skills_paths, force=args.force, blueprints=args.blueprints_paths, templates=args.templates_paths)
        print(json.dumps(report, indent=2))
        return 0
    if args.cmd == "doctor":
        print(json.dumps({"runtime": detect(root), "capabilities": capabilities(root), "tools": check_registry(root), "python": os.sys.version}, indent=2)); return 0
    if args.cmd == "status":
        brain = CodeBrain(root); print(json.dumps({"runtime": detect(root), "brain": brain.check(), "skills": diagnose_skills(root), "tools": check_registry(root), "capabilities": capabilities(root), "memory": len(Memory(root).list())}, indent=2)); return 0
    if args.cmd == "context":
        brain = CodeBrain(root)
        if not brain.store.exists(): brain.build()
        print(json.dumps({"context": build_context(root, args.task, brain), "skills": match(root, args.task)}, indent=2)); return 0
    if args.cmd == "intelligence":
        result = build_intelligence(root, args.task, plan(root, args.task)); print(json.dumps(result, indent=2)); return 0
    if args.cmd == "skill":
        if args.skill_cmd == "diagnose":
            print(json.dumps(diagnose_skills(root), indent=2)); return 0
        skills = discover(root)
        if args.skill_cmd == "list":
            print(json.dumps(skills, indent=2))
            # An empty or degraded registry is nearly always a path problem;
            # say so on stderr rather than letting `[]` look like a valid answer.
            for warning in diagnose_skills(root)["warnings"]:
                print(f"warning: {warning}", file=sys.stderr)
            return 0
        found = next((s for s in skills if s["name"] == args.name), None); print(json.dumps(found or {"error":"skill-not-found"}, indent=2)); return 0 if found else 1
    if args.cmd == "tool":
        tools = load_tools(root)
        if args.tool_cmd == "list": print(json.dumps([tool.__dict__ for tool in tools], indent=2)); return 0
        if args.tool_cmd == "check":
            result = check_registry(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
        if args.tool_cmd == "policy": print(json.dumps(policy_for_role(root, args.role), indent=2)); return 0
        if args.tool_cmd == "gateway":
            configs = write_mcp_configs(root, args.role)
            if args.serve: return serve(root, args.role)
            print(json.dumps(configs, indent=2)); return 0
        found = next((tool for tool in tools if tool.name == args.name), None); print(json.dumps(found.__dict__ if found else {"error":"tool-not-found"}, indent=2)); return 0 if found else 1
    if args.cmd == "guardrails":
        if args.guardrail_cmd == "policy": print(json.dumps(guardrail_policy(), indent=2)); return 0
        if args.guardrail_cmd == "write": print(str(write_guardrail_policy(root))); return 0
        files = [_relative_to_root(root, f) for f in args.files] if args.files else None
        result = check_guardrails(root, args.stage, files); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd == "memory":
        memory = Memory(root)
        if args.memory_cmd == "list": print(json.dumps(memory.list(args.scope, args.include_expired), indent=2)); return 0
        if args.memory_cmd == "search": print(json.dumps(memory.search(args.query, args.scope, args.limit), indent=2)); return 0
        try:
            record = memory.add(args.kind, args.scope, args.summary, args.evidence, args.source, args.confidence, args.expires_days, args.supersedes)
        except ValueError as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
        print(json.dumps(record, indent=2)); return 0
    if args.cmd == "brain":
        brain = CodeBrain(root)
        if args.brain_cmd == "build": print(json.dumps({"indexed_files": len(brain.build()["files"])}, indent=2)); return 0
        if not brain.store.exists(): brain.build()
        if args.brain_cmd == "check": print(json.dumps(brain.check(), indent=2)); return 0
        if args.brain_cmd == "map": print(json.dumps(brain.map(args.path), indent=2)); return 0
        if args.brain_cmd == "search": print(json.dumps(brain.search(args.query), indent=2)); return 0
        if args.brain_cmd == "impact": print(json.dumps(brain.impact(args.target), indent=2)); return 0
    if args.cmd == "runtime":
        if args.runtime_cmd == "inspect":
            if args.runtime: print(json.dumps(contract(root, args.runtime, args.role), indent=2))
            else: print(json.dumps({"claude-code": contract(root, "claude-code", args.role), "codex": contract(root, "codex", args.role)}, indent=2))
            return 0
        if args.runtime_cmd == "contract": print(json.dumps(contract(root, args.runtime, args.role), indent=2)); return 0
        result = parity(root, args.role); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd == "story":
        if args.story_cmd == "check":
            result = check_stories(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
        if args.story_cmd == "new":
            try:
                result = new_story(root, args.title)
            except ValueError as exc:
                print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
            print(json.dumps(result, indent=2)); return 0
        stories = ready_stories(root) if args.story_cmd == "next" else load_stories(root)
        print(json.dumps(stories, indent=2)); return 0
    if args.cmd == "template":
        if args.template_cmd == "list":
            print(json.dumps(list_templates(root), indent=2)); return 0
        try:
            result = copy_template(root, args.name, args.destination)
        except ValueError as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
        print(json.dumps(result, indent=2)); return 0
    if args.cmd == "blueprint":
        if args.blueprint_cmd == "check":
            result = check_blueprints(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
        if args.blueprint_cmd == "list":
            print(json.dumps([{"name": b["name"], "description": b.get("description", ""), "inputs": b.get("inputs", []), "phases": [ph.get("id") for ph in b.get("phases", [])]} for b in list_blueprints(root)], indent=2)); return 0
        try:
            result = blueprint_status(root, args.name)
        except ValueError as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
        print(json.dumps(result, indent=2)); return 0
    if args.cmd == "deploy":
        if args.deploy_cmd == "status":
            print(json.dumps(deploy_status(root), indent=2)); return 0
        result = deploy_gate(root, args.env, args.test_command); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd in {"run", "orchestrate"}:
        try:
            result = write_plan(root, args.task, blueprint=args.blueprint, story=args.story)
        except ValueError as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
        print(json.dumps(result, indent=2)); return 0
    if args.cmd == "execute":
        try:
            result = execute(root, args.task, runtime=args.runtime, execute_agents=args.execute_agents, max_workers=max(1, min(args.max_workers, 4)), blueprint=args.blueprint, story=args.story)
        except ValueError as exc:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, indent=2)); return 1
        if args.execute_agents:
            evaluation = evaluate_run(root, args.task, result.get("workers", []))
            introspection = diagnose(root, result)
            intelligence_result = synthesize_run(result, evaluation, introspection)
            result["evaluation"] = evaluation
            result["introspection"] = introspection
            result["intelligence"] = intelligence_result
            result["run_artifacts"] = persist_run(root, result, evaluation, introspection, intelligence_result)
        print(json.dumps(result, indent=2)); return 0 if result["status"] in SUCCESS_EXECUTION_STATUSES else 1
    if args.cmd == "verify":
        result = verify(root, args.test_command); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd == "benchmark":
        result = run_case(root, args.command, args.repetitions); print(json.dumps(result, indent=2)); return 0 if result["success_rate"] == 1 else 1
    if args.cmd == "evaluate":
        reports = json.loads(Path(args.reports).read_text(encoding="utf-8"))
        if not isinstance(reports, list): return 1
        result = evaluate_run(root, args.task, reports); print(json.dumps(result, indent=2)); return 0 if not result["blocking"] else 1
    if args.cmd == "eval-suite":
        if args.eval_cmd == "run":
            report = run_suite(root, load_suite(args.suite), command_runner)
            print(json.dumps(report, indent=2)); return 0 if report["summary"]["pass_rate"] == 1 else 1
        current = json.loads(Path(args.current).read_text(encoding="utf-8"))
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        result = compare_baseline(current, baseline, args.min_pass_rate, args.max_latency_regression)
        print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd == "introspect":
        run = json.loads(Path(args.run).read_text(encoding="utf-8"))
        result = diagnose(root, run); print(json.dumps(result, indent=2)); return 0
    if args.cmd == "release":
        result = release_check(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
