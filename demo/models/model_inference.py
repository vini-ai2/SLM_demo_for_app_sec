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


def examples() -> list[str]:
    truth = json.loads((ROOT / "examples" / "ground_truth.json").read_text(encoding="utf-8"))
    missing = [name for name in truth if not (ROOT / "examples" / name).is_file()]
    if missing:
        sys.exit("Missing example files: " + ", ".join(missing))
    return list(truth)


OPTIONS = {
    "temperature": 0,
    "seed": 0,
    "num_predict": 160,
    "repeat_penalty": 1.15,
    "repeat_last_n": 64,
    "num_ctx": 2048,
}

# Appended identically for every model so the output can be scored automatically.
# The task prompt itself (prompts/security_prompt.txt) is never changed per model.
JSON_HINT = (
    '\n\nReturn exactly the required JSON fields. Use an empty string when a field does not apply. '
    'Keep explanation and fix to one short sentence each.'
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "vulnerable": {"type": "boolean"},
        "cwe": {"type": ["string", "null"]},
        "type": {"type": ["string", "null"]},
        "vulnerable_code": {"type": "string"},
        "explanation": {"type": "string"},
        "fix": {"type": "string"},
    },
    "required": ["vulnerable", "cwe", "type", "vulnerable_code", "explanation", "fix"],
    "additionalProperties": False,
}


def build_prompt(code: str) -> str:
    template = (ROOT / "prompts" / "security_prompt.txt").read_text(encoding="utf-8")
    return template.replace("{CODE}", code) + JSON_HINT


def _call(path: str, payload: dict | None = None, timeout: int = 600) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(OLLAMA + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail or exc.reason}") from exc


def parse_json(raw: str):
    """Parse only complete responses matching the fields used by the scorer."""
    for text in (raw, (re.search(r"\{.*\}", raw, re.S) or [None])[0]):
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if (isinstance(obj, dict)
                and set(obj) == set(RESPONSE_SCHEMA["required"])
                and isinstance(obj["vulnerable"], bool)
                and all(isinstance(obj[k], str) for k in ("vulnerable_code", "explanation", "fix"))
                and (obj["cwe"] is None or isinstance(obj["cwe"], str))
                and (obj["type"] is None or isinstance(obj["type"], str))):
            return obj
    return None


def query_model(model: str, code: str, timeout: int = 600) -> dict:
    start = time.perf_counter()
    payload = {"model": model, "prompt": build_prompt(code), "stream": False,
               "format": RESPONSE_SCHEMA, "options": OPTIONS}
    for attempt in range(3):
        try:
            data = _call("/api/generate", payload, timeout)
            break
        except RuntimeError as exc:
            error = str(exc)
            if "Ollama HTTP 500" not in error or attempt == 2:
                return {"model": model, "latency_s": round(time.perf_counter() - start, 1),
                        "tokens": None, "tokens_per_s": None, "raw": "", "parsed": None,
                        "error": error}
            if "repeat limit reached" in error.lower():
                payload["options"] = {**OPTIONS, "repeat_penalty": 1.3, "temperature": 0.1}
                print(f"    Ollama hit a token repeat loop; retry {attempt + 1}/2 with stronger repetition control", flush=True)
            else:
                print(f"    Ollama returned HTTP 500; retry {attempt + 1}/2 in 3s: {error}", flush=True)
                time.sleep(3)
    latency = time.perf_counter() - start
    raw = data.get("response", "")
    parsed = parse_json(raw)
    if parsed is None:
        retry_payload = {**payload, "options": {**OPTIONS, "num_predict": 240,
                                                   "repeat_penalty": 1.3, "temperature": 0.1}}
        print("    Response did not match the required fields; retrying once with a larger JSON budget", flush=True)
        try:
            retry_data = _call("/api/generate", retry_payload, timeout)
            retry_raw = retry_data.get("response", "")
            retry_parsed = parse_json(retry_raw)
            if retry_parsed is not None:
                data, raw, parsed = retry_data, retry_raw, retry_parsed
        except RuntimeError:
            pass
    tokens = data.get("eval_count")
    eval_ns = data.get("eval_duration")
    tps = round(tokens / (eval_ns / 1e9), 1) if tokens and eval_ns else None
    return {"model": model, "latency_s": round(latency, 1), "tokens": tokens,
            "tokens_per_s": tps, "raw": raw, "parsed": parsed}


def local_models() -> list[str]:
    try:
        return [m["name"] for m in _call("/api/tags", timeout=10)["models"]]
    except (urllib.error.URLError, ConnectionError, OSError):
        sys.exit("Can't reach Ollama at localhost:11434. Start the Ollama app "
                 "(or run `ollama serve`) and try again.")


def is_pulled(model: str, available: list[str]) -> bool:
    return any(a == model or a == model + ":latest" for a in available)


def run_all(models: list[str], out_path: Path, limit: int | None = None) -> None:
    available = local_models()
    todo = []
    for m in models:
        if is_pulled(m, available):
            todo.append(m)
        else:
            print(f"SKIP {m}: not pulled. Run: ollama pull {m}")
    missing = [m for m in models if not is_pulled(m, available)]
    if missing:
        sys.exit("Required models are not available locally: " + ", ".join(missing))
    if not todo:
        sys.exit("No models to run.")

    runs = []
    if out_path.exists():  # keep results of models we are not re-running
        old = json.loads(out_path.read_text(encoding="utf-8"))
        runs = [r for r in old.get("runs", []) if r["model"] not in todo]

    for m in todo:
        print(f"\n== {m}: loading model (not timed) ==")
        try:
            _call("/api/generate", {"model": m, "prompt": "Say OK.", "stream": False,
                                    "options": {"num_predict": 1}})
        except RuntimeError as exc:
            print(f"  Model warmup failed; per-example requests will retry: {exc}")
        selected_examples = examples()
        if limit is not None:
            selected_examples = selected_examples[:limit]
        for ex in selected_examples:
            code = (ROOT / "examples" / ex).read_text(encoding="utf-8")
            r = query_model(m, code)
            r["example"] = ex
            runs.append(r)
            status = "ok" if r["parsed"] else ("ERROR: " + r["error"] if r.get("error") else "UNPARSEABLE OUTPUT")
            print(f"  {ex:<22} {r['latency_s']:>6.1f}s   {status}", flush=True)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps({
                "meta": {"date": datetime.now().isoformat(timespec="seconds"),
                         "options": OPTIONS, "prompt_file": "prompts/security_prompt.txt",
                         "json_hint": JSON_HINT.strip(), "response_schema": RESPONSE_SCHEMA},
                "runs": runs,
            }, indent=2, ensure_ascii=False), encoding="utf-8")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "meta": {"date": datetime.now().isoformat(timespec="seconds"),
                 "options": OPTIONS, "prompt_file": "prompts/security_prompt.txt",
                 "json_hint": JSON_HINT.strip(), "response_schema": RESPONSE_SCHEMA},
        "runs": runs,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("model", nargs="?", help="Ollama model tag (single-run mode)")
    ap.add_argument("file", nargs="?", help="source file (single-run mode)")
    ap.add_argument("--all", action="store_true", help="run every model on every example")
    ap.add_argument("--models", nargs="+", default=MODELS, help="subset of models for --all")
    ap.add_argument("--limit", type=int, help="run only the first N examples (quick smoke run)")
    ap.add_argument("--out", default=str(ROOT / "results" / "results.json"))
    args = ap.parse_args()

    if args.all:
        run_all(args.models, Path(args.out), args.limit)
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
