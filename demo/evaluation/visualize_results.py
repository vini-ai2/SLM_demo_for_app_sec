"""Generate slide-ready charts from the saved model and Bandit results.

    python evaluation/visualize_results.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "visualizations"
PALETTE = {"qwen2.5-coder:3b": "#2563EB", "gemma3:4b": "#0F9D78", "phi4-mini": "#D97706"}
NAMES = {"qwen2.5-coder:3b": "Qwen", "gemma3:4b": "Gemma", "phi4-mini": "Phi"}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.titlesize": 16, "axes.titleweight": "bold",
    "axes.labelcolor": "#334155", "text.color": "#0F172A",
    "xtick.color": "#475569", "ytick.color": "#334155",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.png", dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    from compare import score

    truth = json.loads((ROOT / "examples" / "ground_truth.json").read_text(encoding="utf-8"))
    results = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    bandit_path = ROOT / "results" / "bandit.json"
    bandit = json.loads(bandit_path.read_text(encoding="utf-8")) if bandit_path.exists() else {}
    manual_path = ROOT / "evaluation" / "manual_review.json"
    overrides = json.loads(manual_path.read_text(encoding="utf-8")) if manual_path.exists() else {}
    runs = results["runs"]
    models = list(dict.fromkeys(r["model"] for r in runs))
    vulnerable = [f for f, t in truth.items() if t["vulnerable"]]
    secure = [f for f, t in truth.items() if not t["vulnerable"]]
    by = {(r["model"], r["example"]): r for r in runs}
    scores = {
        (m, f): score(by[(m, f)], truth[f], overrides.get(f"{m}|{f}", {}))
        for m in models for f in truth if (m, f) in by
    }

    # 1. Summary criteria, including specificity on the negative examples.
    criteria = ["Detection", "Correct CWE", "Relevant code", "Explanation", "Secure fix", "Secure specificity"]
    check_key = ["detect", "cwe", "code", "explanation", "fix", "specificity"]
    vals: dict[str, list[float]] = {}
    for m in models:
        row = []
        for key in check_key:
            fs = secure if key == "specificity" else vulnerable
            good = sum((not scores.get((m, f), {}).get("false_positive", False)) if key == "specificity"
                       else bool(scores.get((m, f), {}).get(key, False)) for f in fs)
            row.append(100 * good / len(fs) if fs else 0)
        vals[m] = row
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    y = np.arange(len(criteria))
    height = 0.22
    for i, m in enumerate(models):
        bars = ax.barh(y + (i - (len(models)-1)/2) * height, vals[m], height=height * .88,
                       color=PALETTE.get(m, "#64748B"), label=NAMES.get(m, m), zorder=3)
        for bar, v in zip(bars, vals[m]):
            ax.text(min(v + 1.3, 96), bar.get_y() + bar.get_height()/2, f"{v:.0f}%",
                    va="center", ha="left", fontsize=9, color="#334155")
    ax.set_yticks(y, criteria)
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks(np.arange(0, 101, 20), [f"{x}%" for x in range(0, 101, 20)])
    ax.set_xlabel("Share of examples scored correct")
    ax.set_title("Model performance across evaluation criteria", loc="left", pad=17)
    ax.text(0, 1.02, "Detection/CWE/code/explanation/fix: 110 vulnerable cases  •  Specificity: 20 secure cases",
            transform=ax.transAxes, fontsize=9, color="#64748B")
    ax.grid(axis="x", color="#E2E8F0", linewidth=.8, zorder=0)
    ax.legend(frameon=False, ncol=len(models), loc="lower right", bbox_to_anchor=(1, -0.2))
    fig.tight_layout()
    save(fig, "overall-performance")

    # 2. Per-category detection rates.
    categories = list(dict.fromkeys(truth[f]["type"] for f in vulnerable))
    counts = [sum(truth[f]["type"] == c for f in vulnerable) for c in categories]
    matrix = []
    for m in models:
        matrix.append([100 * sum(bool(scores.get((m, f), {}).get("detect"))
                                 for f in vulnerable if truth[f]["type"] == c) / n
                       for c, n in zip(categories, counts)])
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    image = ax.imshow(matrix, cmap="YlGnBu", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(categories)), [f"{c}\n(n={n})" for c, n in zip(categories, counts)], rotation=25, ha="right")
    ax.set_yticks(range(len(models)), [NAMES.get(m, m) for m in models])
    ax.set_title("Vulnerability detection by category", loc="left", pad=17)
    for i, m in enumerate(models):
        for j, (c, n) in enumerate(zip(categories, counts)):
            hit = round(matrix[i][j] * n / 100)
            ax.text(j, i, f"{hit}/{n}\n{matrix[i][j]:.0f}%", ha="center", va="center",
                    fontsize=9, color="white" if matrix[i][j] >= 70 else "#0F172A", fontweight="bold")
    cb = fig.colorbar(image, ax=ax, fraction=.035, pad=.025)
    cb.set_label("Detection rate")
    cb.set_ticks([0, 20, 40, 60, 80, 100], labels=["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.set_xticks(np.arange(-.5, len(categories), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.tight_layout()
    save(fig, "detection-by-category")

    # 3. Confusion matrices make false alarms and missed detections explicit.
    fig, axes = plt.subplots(1, len(models), figsize=(12, 4.7))
    confusion = {}
    for ax, m in zip(axes, models):
        cells = np.zeros((2, 2), dtype=int)  # rows: actual vulnerable/secure; cols: predicted vulnerable/secure
        unknown = 0
        for f, t in truth.items():
            s = scores.get((m, f), {})
            pred = s.get("said_vuln")
            if pred is None:
                unknown += 1
                continue
            row = 0 if t["vulnerable"] else 1
            col = 0 if pred else 1
            cells[row, col] += 1
        confusion[m] = (cells, unknown)
        row_totals = cells.sum(axis=1, keepdims=True)
        rates = np.divide(cells * 100, row_totals, out=np.zeros_like(cells, dtype=float), where=row_totals != 0)
        ax.imshow(rates, cmap="Blues", vmin=0, vmax=100, aspect="equal")
        ax.set_xticks([0, 1], ["Flagged", "Clean"])
        ax.set_yticks([0, 1], ["Vulnerable", "Secure"])
        ax.set_xlabel("Model prediction")
        ax.set_title(NAMES.get(m, m), color=PALETTE.get(m, "#334155"), fontsize=13, pad=12)
        for i in range(2):
            for j in range(2):
                term = {(0, 0): "TP", (0, 1): "FN", (1, 0): "FP", (1, 1): "TN"}[(i, j)]
                fg = "white" if rates[i, j] >= 60 else "#0F172A"
                ax.text(j, i, f"{term}\n{cells[i,j]}  ·  {rates[i,j]:.0f}%", ha="center", va="center",
                        color=fg, fontsize=10, fontweight="bold")
        # Highlight the error cells (false negatives and false positives).
        for i, j in ((0, 1), (1, 0)):
            if cells[i, j] > 0:
                ax.add_patch(plt.Rectangle((j - .48, i - .48), .96, .96, fill=False,
                                           edgecolor="#DC2626", linewidth=2.3))
        ax.set_xticks(np.arange(-.5, 2, 1), minor=True)
        ax.set_yticks(np.arange(-.5, 2, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=2)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.tick_params(axis="both", length=0, pad=7)
        if unknown:
            ax.text(.5, -.18, f"{unknown} unparsed responses", transform=ax.transAxes,
                    ha="center", color="#B91C1C", fontsize=9)
    fig.suptitle("Confusion matrices: false positives and false negatives", x=.06, ha="left",
                 fontsize=16, fontweight="bold")
    fig.text(.06, .02, "Rows are actual labels; columns are predictions. Cells show count and row percentage. Red outlines mark errors.",
             fontsize=9, color="#64748B")
    fig.tight_layout(rect=[0, .07, 1, .91], w_pad=2)
    save(fig, "confusion-matrices")

    # 4. One balanced metric compares all model verdicts with the scanner.
    # Balanced accuracy weights the vulnerable and secure classes equally.
    tools = models + ["Bandit"]
    balanced = {}
    components = {}
    for tool in tools:
        if tool == "Bandit":
            predict = lambda f: bool(bandit.get(f, {}).get("flagged", False))
        else:
            predict = lambda f, tool=tool: scores.get((tool, f), {}).get("said_vuln") is True
        recall = sum(predict(f) for f in vulnerable) / len(vulnerable)
        specificity = sum(not predict(f) for f in secure) / len(secure)
        components[tool] = (recall * 100, specificity * 100)
        balanced[tool] = (recall + specificity) * 50
    ordered = sorted(tools, key=lambda tool: balanced[tool], reverse=True)
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    positions = np.arange(len(ordered))
    bar_colors = [PALETTE.get(tool, "#7C3AED") for tool in ordered]
    bars = ax.barh(positions, [balanced[t] for t in ordered], color=bar_colors, height=.58, zorder=3)
    ax.set_yticks(positions, [NAMES.get(t, t) for t in ordered])
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks(np.arange(0, 101, 20), [f"{x}%" for x in range(0, 101, 20)])
    ax.set_xlabel("Balanced accuracy (higher is better)")
    ax.set_title("Models and Bandit on one balanced metric", loc="left", pad=17)
    ax.text(0, 1.02, "Mean of detection rate on 110 vulnerable examples and specificity on 20 secure examples",
            transform=ax.transAxes, fontsize=9, color="#64748B")
    ax.grid(axis="x", color="#E2E8F0", linewidth=.8, zorder=0)
    for bar, tool in zip(bars, ordered):
        value = balanced[tool]
        recall, specificity = components[tool]
        ax.text(value + 1.2, bar.get_y() + bar.get_height()/2,
                f"{value:.1f}%  (detection {recall:.0f}% · specificity {specificity:.0f}%)",
                va="center", fontsize=9, color="#334155")
    fig.tight_layout()
    save(fig, "balanced-accuracy-vs-bandit")

    # 5. Separate axes avoid mixing latency and throughput scales.
    runtime = {}
    for m in models:
        model_runs = [r for r in runs if r["model"] == m]
        runtime[m] = (float(np.mean([r["latency_s"] for r in model_runs])),
                      float(np.mean([r["tokens_per_s"] for r in model_runs if r.get("tokens_per_s")])))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"wspace": .5})
    labels = [NAMES.get(m, m) for m in models]
    colors = [PALETTE.get(m, "#64748B") for m in models]
    y = np.arange(len(models))
    latencies = [runtime[m][0] for m in models]
    speeds = [runtime[m][1] for m in models]
    for ax, values, title, xlabel, fmt, xmax in [
        (ax1, latencies, "Average latency", "Seconds per example (lower is faster)", "{:.1f} s", max(latencies) * 1.35),
        (ax2, speeds, "Generation throughput", "Tokens per second (higher is faster)", "{:.1f}", max(speeds) * 1.35),
    ]:
        bars = ax.barh(y, values, color=colors, height=.55, zorder=3)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_xlim(0, xmax)
        ax.set_title(title, loc="left", fontsize=12, pad=12)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.grid(axis="x", color="#E2E8F0", linewidth=.8, zorder=0)
        for bar, value in zip(bars, values):
            ax.text(value + xmax * .025, bar.get_y() + bar.get_height()/2, fmt.format(value),
                    va="center", fontsize=10, color="#334155")
    fig.suptitle("Inference speed on this machine", x=.08, ha="left", fontsize=16, fontweight="bold")
    fig.subplots_adjust(top=.78, bottom=.22, left=.1, right=.97)
    save(fig, "inference-speed")

    report = """# Evaluation visuals

These charts summarize the completed run over 110 vulnerable and 20 secure examples. Detection, CWE, code, explanation, and fix are scored on vulnerable examples; specificity is scored on secure examples. Explanation and fix scores use keyword heuristics.

## Model performance

![Overall model performance across six criteria](overall-performance.png)

## Detection by category

![Detection rate by vulnerability category](detection-by-category.png)

## False positives and false negatives

![Three confusion matrices showing model false positives and false negatives](confusion-matrices.png)

## Models versus Bandit

![Balanced accuracy comparison of the three models and Bandit](balanced-accuracy-vs-bandit.png)

## Inference speed

![Average latency and generation speed](inference-speed.png)

PNG files are convenient for slides; matching SVG files are available for editing and scaling.
"""
    (OUT / "visualizations.md").write_text(report, encoding="utf-8")
    print(f"Saved five charts (PNG and SVG) plus {OUT / 'visualizations.md'}")


if __name__ == "__main__":
    main()
