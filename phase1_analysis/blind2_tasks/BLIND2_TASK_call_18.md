Read and follow `TASK.md` in this repo.
Then read and follow `calls/call_18/CALL_18_TASK.md`.

CRITICAL RULES:

- Do NOT read any files named `CALL_18_GRADING.json`, `CALL_18_BLIND.json`, or `CALL_18_BLIND2.json` if they appear.
- Do NOT look at git history or any paths outside this repo.
- Grade the call from scratch using only:
  - `config/phase1_grading_config.json`
  - `config/confidence_thresholds.json`
  - `config/phase1_output_format_v2.json`
  - `config/prompt_for_transcript_only_grading.txt`
  - `docs/PHASE1_SCOPE.md`
  - `docs/Quick_Reference_Grades_EN_PHASE1.md`
  - `docs/PHASE1_PACKAGE_GUIDE.md`
  - Transcript files under `calls/call_18/` (`transcript-2.vtt` and, if useful, `paragraphs-2.json` / `sentences-2.json` for navigation).

ADDITIONAL GRADING GUIDANCE (use these rules carefully):

- 7.2 (Echo method):
  - Treat name, surname, city, phone, email, INN, address as contact data.
  - Echo method is only satisfied if operator repeats the data AND asks an explicit confirmation question (“Верно?”, “Правильно?”, “Подтверждаете?”) AND gets a confirmation from the customer.
  - If some contact data are confirmed (e.g. phone) but others (e.g. name/city) are not, grade 7.2 as VIOLATION.
- 9.1 (Search duration):
  - Measure from the first explicit search phrase (“минуту, пожалуйста”, “сейчас проверю/посмотрю”) to the start of the informative answer.
  - < 40s → PASS.
  - 40–45s → BORDERLINE/FLAG‑ONLY (no score reduction).
  - > 45s → VIOLATION (score‑affecting).
  - Include start and end timestamps in evidence.
- 9.3 (Thank you for waiting):
  - PASS only if the operator clearly thanks the customer for waiting after a search (e.g. “Спасибо за ожидание”, “Благодарю за ожидание”).
  - Generic “Спасибо” not tied to waiting does not satisfy 9.3.
- 4.1 (Difficult customer):
  - Text‑only judgment: mark 4.1 as VIOLATION only if transcript shows the operator clearly failing to handle a challenging customer.
  - If the customer is just talkative or asks many questions and the operator stays polite and structured, treat 4.1 as PASS.
- Final grade & confidence:
  - Final grade is driven by the lowest code among HIGH/VERY_HIGH violations.
  - Use VERY_HIGH only when all core criteria (7.1, 7.2, 7.3, 9.1, 9.3) are clear with strong evidence; otherwise use HIGH or MEDIUM accordingly.
- Risk fields:
  - `compliance_risk`: any 7.x or 3.x VIOLATION → at least MEDIUM.
  - `data_security_risk`: only raise above LOW if there is a real 3.3‑type disclosure or clear security problem.
  - `customer_satisfaction_risk`: raise to MEDIUM/HIGH only if there are multiple serious violations or clear unhappiness in the transcript.

TASK:

- Grade this call using the 17‑criteria Phase 1 system and the rules above.
- Use the JSON schema from `config/phase1_output_format_v2.json`.

OUTPUT:

- Write your JSON result to `calls/call_18/CALL_18_BLIND2.json`.
- If that file already exists, stop and report an error instead of overwriting it.
- In chat, only confirm with a short message like:
  - `DONE call_18 -> calls/call_18/CALL_18_BLIND2.json`.

