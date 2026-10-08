# Small Language Models for Software Security: proof-of-concept demo

A small controlled experiment for the case-study presentation. It is not a chatbot demo and not a benchmark.

```
source code -> SLM -> vulnerable? -> CWE -> vulnerable line -> explanation -> minimal fix
```

## 1. What it demonstrates

Compact open models (3B to 4B parameters) running locally can do a real application-security task on short code snippets: decide whether code is vulnerable, name the CWE, point at the responsible code, explain it, and propose a fix. Every model gets the same prompt, the same files and the same settings. The results are scored against known ground truth, and a traditional scanner (Bandit) is run on the same files for contrast.

## 2. Models

All run locally through [Ollama](https://ollama.com), CPU or GPU, no fine-tuning.

| Slot | Ollama tag | Approx. size |
|---|---|---|
| Qwen (code model) | `qwen2.5-coder:3b` | ~2 GB |
| Gemma | `gemma3:4b` | ~3.3 GB |
| Phi | `phi4-mini` | ~2.5 GB |

They are kept in the same size class on purpose. To change them, edit `MODELS` in `models/model_inference.py` and the list in `run_all.ps1`.

## 3. Security examples

| File | Issue | CWE |
|---|---|---|
| `examples/sql_injection.py` | username concatenated into a SQL string | CWE-89 |
| `examples/path_traversal.py` | `os.path.join(UPLOAD_DIR, filename)` with user-controlled `filename` | CWE-22 |
| `examples/command_injection.py` | `shell=True` with a concatenated host string | CWE-78 |
| `examples/secure_example.py` | the SQL example fixed with a bound parameter. Must **not** be flagged | none |

`examples/ground_truth.json` holds the expected type, CWE (plus accepted close variants), the reason, and the markers used for scoring.

## 4. How to run

Prerequisites: Python 3.9+ and the Ollama app installed and running.

```powershell
pip install -r requirements.txt     # only installs Bandit (the baseline); model code is stdlib-only
ollama pull qwen2.5-coder:3b
ollama pull gemma3:4b
ollama pull phi4-mini

python evaluation/baseline_bandit.py        # traditional scanner baseline -> results/bandit.json
python models/model_inference.py --all      # every model x every example -> results/results.json
python evaluation/compare.py                # scoring + tables -> results/comparison.md
```

Or all of it in one go: `powershell -ExecutionPolicy Bypass -File run_all.ps1`

Useful variations:

```powershell
# look at one model on one file (good for a live moment in the presentation)
python models/model_inference.py qwen2.5-coder:3b examples/sql_injection.py

# re-run one model and keep the others' saved results
python models/model_inference.py --all --models phi4-mini
```

Each model is loaded once before timing starts, so latency numbers exclude model load time.

## 5. How the models are compared

Prompt: `prompts/security_prompt.txt` (the exact task prompt, identical for every model). One extra line asking for a JSON object with fixed keys is appended identically for every model, and Ollama's JSON mode is on, so the output can be scored automatically. Temperature 0 and a fixed seed.

| Row | Counted as correct when |
|---|---|
| Detection | `vulnerable` is true on a vulnerable file |
| Correct CWE | the returned CWE is in the accepted list for that file (CWE-22 also accepts its children CWE-23/36; CWE-78 also accepts its parent CWE-77) |
| Relevant code found | the quoted code contains a marker from the real flaw (for example `shell=True`) |
| Explanation correct | it mentions the actual mechanism (keyword check) |
| Secure fix reasonable | the fix contains a recognised remedy for that flaw (keyword check) |
| False positive | `vulnerable` is true on `secure_example.py` |
| Latency | wall-clock seconds per file, averaged. Hardware-dependent |

Explanation and fix are keyword checks, which are a first pass only. Read the raw outputs in `results/results.json` before presenting. If you disagree with a cell, override it in `evaluation/manual_review.json`:

```json
{"gemma3:4b|path_traversal.py": {"explanation": true, "fix": false}}
```

`compare.py` rebuilds the tables with your corrections applied.

## 6. SLADE connection (conceptual only)

SLADE ("Detecting Dynamic Anomalies in Edge Streams without Labels via Self-Supervised Learning") is the original inspiration for the case study. Nothing from SLADE is implemented here.

```
SLADE                                   Our AppSec use case
-----                                   -------------------
dynamic interactions                    source code
        |                                       |
learn expected behaviour                learn/identify security-relevant patterns
        |                                       |
detect anomalous interactions           detect suspicious/vulnerable code
```

> **SLADE is not an SLM. We are borrowing the conceptual idea of self-supervised anomaly detection, not its architecture.**

SLADE and the SLMs address different problems (anomalies in interaction streams vs. flaws in source code), so this demo does not compare them with each other and reports no SLADE numbers.

## 7. Limitations

- Four hand-written, textbook-style snippets, one run per model. This is a proof of concept, not a statistically meaningful benchmark. Do not quote percentages from it.
- The snippets are short and common, so models may have seen near-identical code in training. Results on real, longer, multi-file code would likely be worse.
- Explanation and fix scoring are keyword heuristics unless you override them manually.
- Only Python source and three vulnerability classes. One secure file means one false-positive trial.
- Models are the 3B to 4B class, run with a token cap and JSON mode. Larger variants or other prompts could change the ranking.
- Latency depends on your CPU/GPU and what else is running.
- Bandit is a rule-based linter, not a full SAST pipeline, and the comparison with it is illustrative: it reports pattern matches (including informational notes such as the `subprocess` import) while the models give a verdict plus reasoning.
