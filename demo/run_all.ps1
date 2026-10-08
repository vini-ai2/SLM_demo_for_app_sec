# Full demo run on Windows.
#   powershell -ExecutionPolicy Bypass -File run_all.ps1
# Needs the Ollama app installed and running (https://ollama.com/download).
# Keep this model list in sync with MODELS in models/model_inference.py.

$ErrorActionPreference = "Stop"

function Step($cmd) {
    Write-Host "`n>> $cmd" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "Failed: $cmd" }
}

Step "pip install -r requirements.txt"
foreach ($m in "qwen2.5-coder:3b", "gemma3:4b", "phi4-mini") { Step "ollama pull $m" }
Step "python examples/generate_corpus.py"
Step "python evaluation/baseline_bandit.py"
Step "python models/model_inference.py --all"
Step "python evaluation/compare.py"
