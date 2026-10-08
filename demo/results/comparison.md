## Summary (vulnerable files: 110; secure files: 20)

|                                               | Qwen    | Gemma   | Phi     |
|-----------------------------------------------|---------|---------|---------|
| Detection                                     | 108/110 | 110/110 | 110/110 |
| Correct CWE                                   | 57/110  | 44/110  | 1/110   |
| Relevant code found                           | 64/110  | 53/110  | 48/110  |
| Explanation correct                           | 92/110  | 80/110  | 71/110  |
| Secure fix reasonable                         | 20/110  | 16/110  | 13/110  |
| Detection: SQL Injection                      | 15/15   | 15/15   | 15/15   |
| Detection: Command Injection                  | 15/15   | 15/15   | 15/15   |
| Detection: Path Traversal                     | 15/15   | 15/15   | 15/15   |
| Detection: Cross-Site Scripting (XSS)         | 15/15   | 15/15   | 15/15   |
| Detection: Hardcoded Secrets                  | 10/10   | 10/10   | 10/10   |
| Detection: Insecure Deserialization           | 10/10   | 10/10   | 10/10   |
| Detection: Server-Side Request Forgery (SSRF) | 10/10   | 10/10   | 10/10   |
| Detection: Weak Cryptography                  | 10/10   | 10/10   | 10/10   |
| Detection: Other CWEs                         | 8/10    | 10/10   | 10/10   |
| False positive on secure code                 | 8/20    | 14/20   | 18/20   |
| Avg latency / file                            | 4.6 s   | 11.4 s  | 6.9 s   |
| Avg speed (tokens/s)                          | 44.6    | 12.6    | 20.7    |

## Per example

| Example                        | Truth   | Qwen      | Gemma      | Phi       | Bandit       |
|--------------------------------|---------|-----------|------------|-----------|--------------|
| sql_injection_01.py            | CWE-89  | ✓ CWE-89  | ✓ no CWE   | ✓ no CWE  | ✓ B608       |
| sql_injection_02.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_03.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_04.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_05.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_06.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_07.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_08.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_09.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_10.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_11.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_12.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_13.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_14.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| sql_injection_15.py            | CWE-89  | ✓ CWE-89  | ✓ CWE-89   | ✓ no CWE  | ✓ B608       |
| command_injection_01.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✗ nothing    |
| command_injection_02.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B605       |
| command_injection_03.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B602       |
| command_injection_04.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-937  | ✓ no CWE  | ✗ nothing    |
| command_injection_05.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B607, B603 |
| command_injection_06.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✗ nothing    |
| command_injection_07.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B605       |
| command_injection_08.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B602       |
| command_injection_09.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-93   | ✓ no CWE  | ✗ nothing    |
| command_injection_10.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B607, B603 |
| command_injection_11.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-937  | ✓ no CWE  | ✗ nothing    |
| command_injection_12.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B605       |
| command_injection_13.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B602       |
| command_injection_14.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-937  | ✓ no CWE  | ✗ nothing    |
| command_injection_15.py        | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B607, B603 |
| path_traversal_01.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_02.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_03.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_04.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_05.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_06.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_07.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_08.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_09.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_10.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_11.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_12.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-918  | ✓ CWE-20  | ✗ nothing    |
| path_traversal_13.py           | CWE-22  | ✓ no CWE  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_14.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| path_traversal_15.py           | CWE-22  | ✓ CWE-23  | ✓ CWE-22   | ✓ CWE-20  | ✗ nothing    |
| xss_01.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_02.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_03.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_04.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_05.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_06.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_07.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_08.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_09.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_10.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_11.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_12.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_13.py                      | CWE-79  | ✓ CWE-79  | ✓ CWE-79   | ✓ no CWE  | ✗ nothing    |
| xss_14.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| xss_15.py                      | CWE-79  | ✓ CWE-79  | ✓ no CWE   | ✓ no CWE  | ✗ nothing    |
| hardcoded_secrets_01.py        | CWE-798 | ✓ CWE-79  | ✓ CWE-319  | ✓ no CWE  | ✗ nothing    |
| hardcoded_secrets_02.py        | CWE-798 | ✓ CWE-79  | ✓ CWE-289  | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_03.py        | CWE-798 | ✓ CWE-250 | ✓ CWE-28   | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_04.py        | CWE-798 | ✓ CWE-250 | ✓ CWE-319  | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_05.py        | CWE-798 | ✓ CWE-259 | ✓ CWE-319  | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_06.py        | CWE-798 | ✓ CWE-79  | ✓ CWE-310  | ✓ no CWE  | ✗ nothing    |
| hardcoded_secrets_07.py        | CWE-798 | ✓ CWE-259 | ✓ CWE-89   | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_08.py        | CWE-798 | ✓ CWE-250 | ✓ CWE-319  | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_09.py        | CWE-798 | ✓ CWE-259 | ✓ CWE-319  | ✓ no CWE  | ✓ B105       |
| hardcoded_secrets_10.py        | CWE-798 | ✓ CWE-250 | ✓ CWE-28   | ✓ no CWE  | ✓ B105       |
| insecure_deserialization_01.py | CWE-502 | ✓ CWE-73  | ✓ CWE-94   | ✓ no CWE  | ✓ B301       |
| insecure_deserialization_02.py | CWE-502 | ✓ CWE-73  | ✓ CWE-94   | ✓ no CWE  | ✗ nothing    |
| insecure_deserialization_03.py | CWE-502 | ✓ CWE-73  | ✓ CWE-129  | ✓ no CWE  | ✓ B301       |
| insecure_deserialization_04.py | CWE-502 | ✓ CWE-73  | ✓ CWE-1072 | ✓ no CWE  | ✓ B302       |
| insecure_deserialization_05.py | CWE-502 | ✓ CWE-73  | ✓ CWE-1073 | ✓ no CWE  | ✓ B301       |
| insecure_deserialization_06.py | CWE-502 | ✓ CWE-73  | ✓ CWE-1072 | ✓ no CWE  | ✓ B301       |
| insecure_deserialization_07.py | CWE-502 | ✓ CWE-20  | ✓ CWE-94   | ✓ no CWE  | ✗ nothing    |
| insecure_deserialization_08.py | CWE-502 | ✓ CWE-73  | ✓ CWE-120  | ✓ no CWE  | ✓ B301       |
| insecure_deserialization_09.py | CWE-502 | ✓ CWE-73  | ✓ CWE-1072 | ✓ no CWE  | ✓ B302       |
| insecure_deserialization_10.py | CWE-502 | ✓ CWE-73  | ✓ CWE-94   | ✓ no CWE  | ✓ B301       |
| ssrf_01.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-94   | ✓ no CWE  | ✓ B113       |
| ssrf_02.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B310       |
| ssrf_03.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B113       |
| ssrf_04.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✗ nothing    |
| ssrf_05.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B113       |
| ssrf_06.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B113       |
| ssrf_07.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B310       |
| ssrf_08.py                     | CWE-918 | ✓ CWE-912 | ✓ CWE-94   | ✓ no CWE  | ✓ B113       |
| ssrf_09.py                     | CWE-918 | ✓ CWE-113 | ✓ CWE-918  | ✓ no CWE  | ✗ nothing    |
| ssrf_10.py                     | CWE-918 | ✓ CWE-918 | ✓ CWE-918  | ✓ no CWE  | ✓ B113       |
| weak_cryptography_01.py        | CWE-327 | ✓ CWE-321 | ✓ CWE-312  | ✓ no CWE  | ✓ B324       |
| weak_cryptography_02.py        | CWE-327 | ✓ CWE-326 | ✓ CWE-326  | ✓ no CWE  | ✗ nothing    |
| weak_cryptography_03.py        | CWE-327 | ✓ CWE-250 | ✓ CWE-312  | ✓ no CWE  | ✓ B324       |
| weak_cryptography_04.py        | CWE-327 | ✓ CWE-326 | ✓ CWE-326  | ✓ no CWE  | ✗ nothing    |
| weak_cryptography_05.py        | CWE-327 | ✓ CWE-321 | ✓ CWE-338  | ✓ no CWE  | ✓ B311       |
| weak_cryptography_06.py        | CWE-327 | ✓ CWE-327 | ✓ CWE-312  | ✓ no CWE  | ✓ B324       |
| weak_cryptography_07.py        | CWE-327 | ✓ CWE-326 | ✓ CWE-326  | ✓ no CWE  | ✗ nothing    |
| weak_cryptography_08.py        | CWE-327 | ✓ CWE-326 | ✓ CWE-312  | ✓ no CWE  | ✓ B324       |
| weak_cryptography_09.py        | CWE-327 | ✓ CWE-326 | ✓ CWE-326  | ✓ no CWE  | ✗ nothing    |
| weak_cryptography_10.py        | CWE-327 | ✓ CWE-327 | ✓ CWE-338  | ✓ no CWE  | ✓ B311       |
| other_cwes_01.py               | CWE-362 | ✗ no CWE  | ✓ CWE-34   | ✓ no CWE  | ✗ nothing    |
| other_cwes_02.py               | CWE-862 | ✓ CWE-20  | ✓ CWE-918  | ✓ CWE-942 | ✗ nothing    |
| other_cwes_03.py               | CWE-22  | ✓ CWE-20  | ✓ CWE-20   | ✓ CWE-22  | ✗ nothing    |
| other_cwes_04.py               | CWE-489 | ✓ CWE-126 | ✓ CWE-20   | ✓ no CWE  | ✓ B104       |
| other_cwes_05.py               | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B607, B603 |
| other_cwes_06.py               | CWE-362 | ✗ no CWE  | ✓ CWE-34   | ✓ no CWE  | ✗ nothing    |
| other_cwes_07.py               | CWE-862 | ✓ CWE-20  | ✓ CWE-918  | ✓ CWE-941 | ✗ nothing    |
| other_cwes_08.py               | CWE-22  | ✓ CWE-23  | ✓ CWE-20   | ✓ no CWE  | ✗ nothing    |
| other_cwes_09.py               | CWE-489 | ✓ CWE-126 | ✓ CWE-20   | ✓ no CWE  | ✓ B104       |
| other_cwes_10.py               | CWE-78  | ✓ CWE-78  | ✓ CWE-94   | ✓ no CWE  | ✓ B607, B603 |
| secure_01.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_02.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✗ flagged    |
| secure_03.py                   | secure  | ✓ clean   | ✓ clean    | ✗ flagged | ✗ flagged    |
| secure_04.py                   | secure  | ✓ clean   | ✓ clean    | ✗ flagged | ✓ clean      |
| secure_05.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_06.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_07.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_08.py                   | secure  | ✓ clean   | ✓ clean    | ✓ clean   | ✓ clean      |
| secure_09.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_10.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_11.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_12.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✗ flagged    |
| secure_13.py                   | secure  | ✓ clean   | ✓ clean    | ✗ flagged | ✗ flagged    |
| secure_14.py                   | secure  | ✓ clean   | ✓ clean    | ✗ flagged | ✓ clean      |
| secure_15.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_16.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_17.py                   | secure  | ✓ clean   | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_18.py                   | secure  | ✓ clean   | ✓ clean    | ✓ clean   | ✓ clean      |
| secure_19.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |
| secure_20.py                   | secure  | ✗ flagged | ✗ flagged  | ✗ flagged | ✓ clean      |

_130 hand-written examples, one deterministic run per model. Explanation and fix scores use keyword heuristics; results are an illustrative evaluation, not a statistically validated benchmark._
