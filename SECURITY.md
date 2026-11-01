# Security policy

## Reporting a vulnerability

Do not report vulnerabilities in public issues. Use a private [security advisory](https://github.com/Kural-Bench/kural-bench/security/advisories/new).

Include the affected commit or version, steps to reproduce, and the impact.

## Scope

- `kuralbench/`, `evals/` and `tools/`
- the integrity data of a release: the sha256 values in `data/dev/MANIFEST.json` and `source/MANIFEST.json`

A file that does not match its sha256 is a security report, not a bug report.
