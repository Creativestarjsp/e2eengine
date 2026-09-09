---
name: research-first-engineering
description: "Establish what already exists before writing new code, so the repository's own patterns and dependencies get reused. Use when starting a feature that may already have a pattern, adding a dependency or abstraction, replacing existing code, or making an architectural decision."
---

# Research-First Engineering

## Purpose
Prevent unnecessary custom implementation by researching the repository, existing dependencies, established patterns, and suitable external references before architecture or code changes.

## Use When
- Starting a feature or integration that may already have an implementation pattern.
- Adding a dependency, abstraction, service, MCP tool, or framework integration.
- Replacing existing code.
- Making an architectural decision.

## Workflow
1. Inspect the repository and CodeBrain context first.
2. Search existing files, skills, dependencies, tests, and configuration for reusable solutions.
3. Check project conventions and constraints.
4. Research credible external references only when the repository is insufficient.
5. Compare the smallest viable alternatives.
6. Record the decision, rejected alternatives, evidence, and uncertainty.
7. Only then implement.

## Output
Produce a research packet containing the question, repository evidence, relevant dependencies/patterns, external references when needed, alternatives, recommendation, risks, and unknowns.

## Quality Bar
Never claim research without evidence. Research is read-only: do not install packages, change external systems, or make irreversible changes.

## Composition
Use before architecture and integration work. SD2 uses the packet to refine plans; SD3 verifies major architectural choices have evidence.

## Claude/Codex Compatibility
Runtime-neutral. Claude Code and Codex may execute it through their respective adapters.
