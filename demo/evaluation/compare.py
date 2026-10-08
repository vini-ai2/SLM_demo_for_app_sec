"""Score results/results.json against examples/ground_truth.json and print the comparison.

    python evaluation/compare.py

Scoring is automatic and deliberately simple:
  - Detection:     model said vulnerable=true on a vulnerable file
  - Correct CWE:   returned CWE is in the accepted list for that file
  - Relevant code: the quoted code contains a marker line/token from the real flaw
  - Explanation:   mentions the actual mechanism (keyword check)
  - Secure fix:    fix contains a recognised remedy for that flaw (keyword check)
  - False positive: model said vulnerable=true on the secure file
The keyword checks are a first pass. Read the raw outputs, and put corrections in
evaluation/manual_review.json (format below) to override any cell.

    {"gemma3:4b|path_traversal.py": {"explanation": true, "fix": false}}
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"qwen": "Qwen", "gemma": "Gemma", "phi": "Phi"}
CHECKS = ["detect", "cwe", "code", "explanation", "fix"]


def label(model: str) -> str:
    return next((v for k, v in LABELS.items() if model.lower().startswith(k)), model)


def as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes", "y", "vulnerable"):
            return True
        if s in ("false", "no", "n", "not vulnerable", "secure"):
            return False
    return None


def as_cwe(v):
    if v is None:
        return None
    s = str(v)
    m = re.search(r"CWE[-\s_:]*(\d+)", s, re.I) or re.fullmatch(r"\s*(\d+)\s*", s)
    return f"CWE-{m.group(1)}" if m else None


def flat(v) -> str:
    if v is None:
        return ""
    if not isinstance(v, str):
        v = json.dumps(v, ensure_ascii=False).replace('\\"', '"')
    return re.sub(r"\s+", " ", v).lower()


def score(run: dict, truth: dict, override: dict) -> dict:
    p = run["parsed"]
    if p is None:
        return {"parsed": False}
    said_vuln = as_bool(p.get("vulnerable"))
    cwe = as_cwe(p.get("cwe"))
    s = {"parsed": True, "said_vuln": said_vuln, "cwe_returned": cwe}
    if truth["vulnerable"]:
        d = said_vuln is True
        s.update(
            detect=d,
            cwe=d and cwe in truth["cwe_accept"],
            code=d and any(m in flat(p.get("vulnerable_code")) for m in truth["code_markers"]),
            explanation=d and any(k in flat(p.get("explanation")) for k in truth["explanation_keywords"]),
            fix=d and any(k in flat(p.get("fix")) for k in truth["fix_keywords"]),
        )
    else:
        s["false_positive"] = said_vuln is True
    s.update({k: v for k, v in override.items() if k in CHECKS + ["false_positive"]})
    return s


def render(rows: list[list[str]]) -> str:
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    def line(r):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(r, widths)) + " |"
    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    return "\n".join([line(rows[0]), sep] + [line(r) for r in rows[1:]])


def build_tables(runs, truth, overrides, bandit, tick, cross):
    models = list(dict.fromkeys(r["model"] for r in runs))
    vuln_files = [f for f, t in truth.items() if t["vulnerable"]]
    secure_files = [f for f, t in truth.items() if not t["vulnerable"]]
    by = {(r["model"], r["example"]): r for r in runs}
    scores = {k: score(r, truth[k[1]], overrides.get(f"{k[0]}|{k[1]}", {})) for k, r in by.items()}

    # Summary table (the slide table)
    head = [""] + [label(m) for m in models]
    rows = [head]
    names = {"detect": "Detection", "cwe": "Correct CWE", "code": "Relevant code found",
             "explanation": "Explanation correct", "fix": "Secure fix reasonable"}
    for c in CHECKS:
        row = [names[c]]
        for m in models:
            hits = sum(1 for f in vuln_files if scores.get((m, f), {}).get(c))
            row.append(f"{hits}/{len(vuln_files)}")
        rows.append(row)
    row = ["False positive on secure code"]
    for m in models:
        fps = [scores.get((m, f), {}) for f in secure_files]
        if any(not s.get("parsed") for s in fps):
            row.append("parse error")
        else:
            row.append("Yes" if any(s.get("false_positive") for s in fps) else "No")
    rows.append(row)
    row = ["Avg latency / file"]
    for m in models:
        ls = [r["latency_s"] for (mm, _), r in by.items() if mm == m]
        row.append(f"{sum(ls) / len(ls):.1f} s" if ls else "-")
    rows.append(row)
    row = ["Avg speed (tokens/s)"]
    for m in models:
        ts = [r["tokens_per_s"] for (mm, _), r in by.items() if mm == m and r.get("tokens_per_s")]
        row.append(f"{sum(ts) / len(ts):.1f}" if ts else "-")
    rows.append(row)
    summary = render(rows)

    # Per-example table
    head = ["Example", "Truth"] + [label(m) for m in models] + (["Bandit"] if bandit else [])
    rows = [head]
    for f, t in truth.items():
        row = [f, t["cwe"] or "secure"]
        for m in models:
            s = scores.get((m, f))
            if s is None:
                row.append("-")
            elif not s["parsed"]:
                row.append("parse error")
            elif t["vulnerable"]:
                row.append(f"{tick if s['detect'] else cross} {s['cwe_returned'] or 'no CWE'}")
            else:
                row.append(f"{cross} flagged" if s["false_positive"] else f"{tick} clean")
        if bandit:
            b = bandit.get(f)
            if b is None:
                row.append("-")
            elif t["vulnerable"]:
                ids = ", ".join(x["test_id"] for x in b["findings"])
                row.append(f"{tick} {ids}" if b["flagged"] else f"{cross} nothing")
            else:
                row.append(f"{cross} flagged" if b["flagged"] else f"{tick} clean")
        rows.append(row)
    detail = render(rows)
    return summary, detail


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(ROOT / "results" / "results.json"))
    ap.add_argument("--out", default=str(ROOT / "results" / "comparison.md"))
    args = ap.parse_args()

    res = Path(args.results)
    if not res.exists():
        sys.exit(f"{res} not found. Run: python models/model_inference.py --all")
    runs = json.loads(res.read_text(encoding="utf-8"))["runs"]
    truth = json.loads((ROOT / "examples" / "ground_truth.json").read_text(encoding="utf-8"))
    man = ROOT / "evaluation" / "manual_review.json"
    overrides = json.loads(man.read_text(encoding="utf-8")) if man.exists() else {}
    bp = ROOT / "results" / "bandit.json"
    bandit = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else None

    note = ("Proof-of-concept on 3 hand-written vulnerable files and 1 secure file, one deterministic "
            "run per model. Not a statistically meaningful benchmark.")

    # File version always uses unicode marks; console falls back to Y/N if it cannot print them.
    s_file, d_file = build_tables(runs, truth, overrides, bandit, "✓", "✗")
    Path(args.out).write_text(
        f"## Summary (vulnerable files: {sum(t['vulnerable'] for t in truth.values())})\n\n{s_file}\n\n"
        f"## Per example\n\n{d_file}\n\n_{note}_\n", encoding="utf-8")

    try:
        "✓✗".encode(sys.stdout.encoding or "ascii")
        tick, cross = "✓", "✗"
    except (UnicodeEncodeError, LookupError):
        tick, cross = "Y", "N"
    s_con, d_con = build_tables(runs, truth, overrides, bandit, tick, cross)
    print("\nSUMMARY\n" + s_con + "\n\nPER EXAMPLE\n" + d_con + f"\n\n{note}")
    print(f"\nSaved {args.out}")


if __name__ == "__main__":
    main()
