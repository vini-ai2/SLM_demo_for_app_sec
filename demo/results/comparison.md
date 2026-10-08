## Summary (vulnerable files: 3)

|                               | Qwen  | Gemma | Phi    |
|-------------------------------|-------|-------|--------|
| Detection                     | 3/3   | 0/3   | 3/3    |
| Correct CWE                   | 1/3   | 0/3   | 1/3    |
| Relevant code found           | 3/3   | 0/3   | 3/3    |
| Explanation correct           | 2/3   | 0/3   | 3/3    |
| Secure fix reasonable         | 2/3   | 0/3   | 2/3    |
| False positive on secure code | Yes   | No    | Yes    |
| Avg latency / file            | 5.4 s | 9.0 s | 12.7 s |
| Avg speed (tokens/s)          | 42.4  | 16.2  | 27.9   |

## Per example

| Example              | Truth  | Qwen      | Gemma    | Phi       | Bandit       |
|----------------------|--------|-----------|----------|-----------|--------------|
| sql_injection.py     | CWE-89 | ✓ CWE-89  | ✗ no CWE | ✓ CWE-89  | ✓ B608       |
| path_traversal.py    | CWE-22 | ✓ CWE-89  | ✗ no CWE | ✓ CWE-20  | ✗ nothing    |
| command_injection.py | CWE-78 | ✓ CWE-89  | ✗ no CWE | ✓ CWE-209 | ✓ B404, B602 |
| secure_example.py    | secure | ✗ flagged | ✓ clean  | ✗ flagged | ✓ clean      |

_Proof-of-concept on 3 hand-written vulnerable files and 1 secure file, one deterministic run per model. Not a statistically meaningful benchmark._
