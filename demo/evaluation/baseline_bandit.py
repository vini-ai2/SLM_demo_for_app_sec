"""Traditional-scanner baseline: run Bandit on each example.

    python evaluation/baseline_bandit.py

Bandit is a rule-based Python security linter. It is here only to show what a
conventional tool reports on the same files, not as a full SAST setup.
Writes results/bandit.json, which compare.py picks up automatically.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ["sql_injection.py", "path_traversal.py", "command_injection.py", "secure_example.py"]


def scan(path: Path) -> list[dict]:
    proc = subprocess.run([sys.executable, "-m", "bandit", "-f", "json", "-q", str(path)],
                          capture_output=True, text=True, encoding="utf-8")
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit("Bandit did not run. Install it with: pip install -r requirements.txt\n" + proc.stderr)
    return [{
        "test_id": r["test_id"],
        "issue": r["issue_text"],
        "severity": r["issue_severity"],
        "cwe": f"CWE-{r['issue_cwe']['id']}" if r.get("issue_cwe") else None,
        "line": r["line_number"],
    } for r in report["results"]]


def main() -> None:
    out = {}
    print(f"{'example':<22} findings")
    for ex in EXAMPLES:
        findings = scan(ROOT / "examples" / ex)
        out[ex] = {"flagged": bool(findings), "findings": findings}
        if findings:
            desc = "; ".join(f"{f['test_id']} ({f['cwe']}) line {f['line']}" for f in findings)
        else:
            desc = "none"
        print(f"{ex:<22} {desc}")
    path = ROOT / "results" / "bandit.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
