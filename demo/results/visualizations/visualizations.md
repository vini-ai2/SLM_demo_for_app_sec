# Evaluation visuals

These charts summarize the completed run over 110 vulnerable and 20 secure examples. Detection, CWE, code, explanation, and fix are scored on vulnerable examples; specificity is scored on secure examples. Explanation and fix scores use keyword heuristics.

## Model performance

![Overall model performance across six criteria](overall-performance.svg)

## Detection by category

![Detection rate by vulnerability category](detection-by-category.svg)

## False positives and false negatives

![Three confusion matrices showing model false positives and false negatives](confusion-matrices.svg)

## Models versus Bandit

![Balanced accuracy comparison of the three models and Bandit](balanced-accuracy-vs-bandit.svg)

## Inference speed

![Average latency and generation speed](inference-speed.svg)

PNG files are convenient for slides; matching SVG files are available for editing and scaling.
