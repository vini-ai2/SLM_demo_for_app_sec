"""Run source files through local models (via Ollama) with one shared prompt.

    # one model, one file: prints the parsed answer
    python models/model_inference.py qwen2.5-coder:3b examples/sql_injection.py

    # every model x every example -> results/results.json
    python models/model_inference.py --all

    # re-run a single model, keep the other models' saved results
    python models/model_inference.py --all --models phi4-mini
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLLAMA = "http://localhost:11434"

# Same size class on purpose (3B-4B) so the comparison is fair.
MODELS = ["qwen2.5-coder:3b", "gemma3:4b", "phi4-mini"]
EXAMPLES = ["sql_injection.py", "path_traversal.py", "command_injection.py", "secure_example.py"]
OPTIONS = {"temperature": 0, "seed": 0, "num_predict": 800}

# Appended identically for every model so the output can be scored automatically.
# The task prompt itself (prompts/security_prompt.txt) is never changed per model.
JSON_HINT = (
    '\n\nRespond with a single JSON object with keys: "vulnerable" (true/false), '
    '"cwe" (e.g. "CWE-89" or null), "type", "vulnerable_code", "explanation", "fix".'
)


def build_prompt(code: str) -> str:
    template = (ROOT / "prompts" / "security_prompt.txt").read_text(encoding="utf-8")
    return template.replace("{CODE}", code) + JSON_HINT


def _call(path: str, payload: dict | None = None, timeout: int = 600) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(OLLAMA + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def parse_json(raw: str):
    """Parse the model's JSON; fall back to the outermost {...} block."""
    for text in (raw, (re.search(r"\{.*\}", raw, re.S) or [None])[0]):
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def query_model(model: str, code: str, timeout: int = 600) -> dict:
    start = time.perf_counter()
    data = _call("/api/generate", {
        "model": model,
        "prompt": build_prompt(code),
        "stream": False,
        "format": "json",
        "options": OPTIONS,
    }, timeout)
    latency = time.perf_counter() - start
    raw = data.get("response", "")
    tokens = data.get("eval_count")
    eval_ns = data.get("eval_duration")
    tps = round(tokens / (eval_ns / 1e9), 1) if tokens and eval_ns else None
    return {"model": model, "latency_s": round(latency, 1), "tokens": tokens,
            "tokens_per_s": tps, "raw": raw, "parsed": parse_json(raw)}


def local_models() -> list[str]:
    try:
        return [m["name"] for m in _call("/api/tags", timeout=10)["models"]]
    except (urllib.error.URLError, ConnectionError, OSError):
        sys.exit("Can't reach Ollama at localhost:11434. Start the Ollama app "
                 "(or run `ollama serve`) and try again.")


def is_pulled(model: str, available: list[str]) -> bool:
    return any(a == model or a == model + ":latest" for a in available)


def run_all(models: list[str], out_path: Path) -> None:
    available = local_models()
    todo = []
    for m in models:
        if is_pulled(m, available):
            todo.append(m)
        else:
            print(f"SKIP {m}: not pulled. Run: ollama pull {m}")
    if not todo:
        sys.exit("No models to run.")

    runs = []
    if out_path.exists():  # keep results of models we are not re-running
        old = json.loads(out_path.read_text(encoding="utf-8"))
        runs = [r for r in old.get("runs", []) if r["model"] not in todo]

    for m in todo:
        print(f"\n== {m}: loading model (not timed) ==")
        _call("/api/generate", {"model": m, "prompt": "Say OK.", "stream": False,
                                "options": {"num_predict": 1}})
        for ex in EXAMPLES:
            code = (ROOT / "examples" / ex).read_text(encoding="utf-8")
            r = query_model(m, code)
            r["example"] = ex
            runs.append(r)
            status = "ok" if r["parsed"] else "UNPARSEABLE OUTPUT"
            print(f"  {ex:<22} {r['latency_s']:>6.1f}s   {status}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "meta": {"date": datetime.now().isoformat(timespec="seconds"),
                 "options": OPTIONS, "prompt_file": "prompts/security_prompt.txt",
                 "json_hint": JSON_HINT.strip()},
        "runs": runs,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("model", nargs="?", help="Ollama model tag (single-run mode)")
    ap.add_argument("file", nargs="?", help="source file (single-run mode)")
    ap.add_argument("--all", action="store_true", help="run every model on every example")
    ap.add_argument("--models", nargs="+", default=MODELS, help="subset of models for --all")
    ap.add_argument("--out", default=str(ROOT / "results" / "results.json"))
    args = ap.parse_args()

    if args.all:
        run_all(args.models, Path(args.out))
    elif args.model and args.file:
        r = query_model(args.model, Path(args.file).read_text(encoding="utf-8"))
        print(f"model: {r['model']}   latency: {r['latency_s']}s   tokens/s: {r['tokens_per_s']}\n")
        print(json.dumps(r["parsed"], indent=2) if r["parsed"] else r["raw"])
    else:
        ap.error("give <model> <file>, or --all")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    main()
