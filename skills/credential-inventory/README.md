# credential-inventory

A committed `CREDENTIALS.md` that says which credentials a project needs, where
each value lives, and who owns it, with a checker that refuses to let a value
in. See `SKILL.md` for the workflow.

Requirements: Python 3.9+, no third-party packages.

```text
scripts/credentials_check.py   validate the register; --code-scan compares it with env references in code
templates/CREDENTIALS.md       starting file to copy into a project root
examples/CREDENTIALS.example.md a filled register for a Next.js + Postgres + Stripe project
examples/check-output.txt      what the checker prints for the example
```

Quick start in a project:

```sh
cp skills/credential-inventory/templates/CREDENTIALS.md ./CREDENTIALS.md
python skills/credential-inventory/scripts/credentials_check.py --root . --code-scan
```

Exit 0 means the file is well-formed and value-free. Drift between the register
and the code is a warning by default and an error with `--strict`.
