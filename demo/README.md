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

The evaluation corpus contains 130 short Python examples:

| Category | Examples |
|---|---:|
| SQL Injection | 15 |
| Command Injection | 15 |
| Path Traversal | 15 |
| XSS | 15 |
| Hardcoded Secrets | 10 |
| Insecure Deserialization | 10 |
| SSRF | 10 |
| Weak Cryptography | 10 |
| Other CWEs | 10 |
| Secure/negative examples | 20 |
| **Total** | **130** |

`examples/generate_corpus.py` creates the category files and `ground_truth.json`. The ground-truth file is the source of truth for which examples the inference and Bandit scripts process. Run the generator after changing the corpus.

## 4. How to run

Prerequisites: Python 3.9+ and the Ollama app installed and running.

```powershell
pip install -r requirements.txt     # only installs Bandit (the baseline); model code is stdlib-only
ollama pull qwen2.5-coder:3b
ollama pull gemma3:4b
ollama pull phi4-mini

python evaluation/baseline_bandit.py        # traditional scanner baseline -> results/bandit.json
python examples/generate_corpus.py          # regenerate the 130 labeled examples
python models/model_inference.py --all      # every model x every example -> results/results.json
python evaluation/compare.py                # scoring + tables -> results/comparison.md
python evaluation/visualize_results.py      # slide-ready charts -> results/visualizations/
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
| False positive | the report counts flagged secure examples out of 20 |
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

- 130 small hand-written examples, one run per model. This remains a controlled evaluation set, not a statistically validated benchmark; examples may not represent real applications.
- The snippets are short and common, so models may have seen near-identical code in training. Results on real, longer, multi-file code would likely be worse.
- Explanation and fix scoring are keyword heuristics unless you override them manually.
- Python source only. “Other CWEs” groups several additional weakness patterns into one reporting category.
- Models are the 3B to 4B class, run with a token cap and JSON mode. Larger variants or other prompts could change the ranking.
- Latency depends on your CPU/GPU and what else is running.
- Bandit is a rule-based linter, not a full SAST pipeline, and the comparison with it is illustrative: it reports pattern matches (including informational notes such as the `subprocess` import) while the models give a verdict plus reasoning.
