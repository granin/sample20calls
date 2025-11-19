## TASK: Grade `call_01` and write JSON output

You are a grading agent working **inside this repository**.

Your job in this task is to:
- Grade **`call_01`** using the **Phase 1, 17‑criteria transcript-only system**, and
- **Write the result to a JSON file** in this repo.

---

### 1. Scope and rules

- Use **only** the materials in this repository.
- Treat this as a **complete 17‑criteria system** (no Phase 2, no 26 criteria, no deferred criteria).
- Data sources: transcript and timing JSON only (no audio, no external DB).

Do **not**:
- Invent additional criteria or reference “26 criteria”, “Phase 2/3”, or “deferred criteria”.
- Reach outside this repo for grading rules.

---

### 2. Files you must read

At repo root:
- `TASK.md` – global instructions for this Phase 1 package.

Configuration:
- `config/prompt_for_transcript_only_grading.txt`
- `config/phase1_output_format_v2.json`
- `config/confidence_thresholds.json`

Documentation:
- `docs/PHASE1_SCOPE.md`
- `docs/Quick_Reference_Grades_EN_PHASE1.md`
- `docs/PHASE1_PACKAGE_GUIDE.md`

Call data for this task:
- `calls/call_01/transcript-2.vtt`
- `calls/call_01/transcript-2.srt`
- `calls/call_01/paragraphs-2.json`
- `calls/call_01/sentences-2.json`
- `calls/call_01/timestamps.json`

---

### 3. What you must do

1. **Load instructions and schema**
   - Use `config/prompt_for_transcript_only_grading.txt` as your **grading instructions**.
   - Use `config/phase1_output_format_v2.json` as the **exact JSON schema** for your output.
   - Interpret confidence levels using `config/confidence_thresholds.json`.

2. **Grade `call_01`**
   - Evaluate all **17 Phase 1 criteria** as defined in `docs/PHASE1_SCOPE.md` and `docs/Quick_Reference_Grades_EN_PHASE1.md`.
   - Use only the transcript and timing data from `calls/call_01/`.
   - Apply:
     - Lowest code rule (final grade = lowest code among high‑confidence violations).
     - 40–45s search rule (flag window, no score reduction).
     - Confidence handling (VERY_HIGH / HIGH / MEDIUM / LOW) as defined in the docs.

3. **Produce output JSON**
   - Build a **single JSON object** that strictly follows `config/phase1_output_format_v2.json`:
     - `call_metadata`
     - `final_scoring`
     - `violations_detected`
     - `violations_summary`
     - `coaching_priorities`
     - `risk_assessment`
     - `detected_patterns`
     - `criteria_assessment`
     - `positive_observations`
     - `data_quality`

4. **Write JSON to file**
   - Write that JSON object to:
     - `calls/call_01/CALL_01_GRADING.json`
   - Overwrite the file if it already exists.
   - Ensure the file contains **only** the JSON object (no extra comments or text).

5. **Chat response**
   - In your chat reply, output **only the JSON object** (no explanations, no markdown).

---

### 4. When to stop

Stop early **only** if you hit a **critical blocker**, for example:
- Required call files are missing or unreadable.
- The JSON schema in `config/phase1_output_format_v2.json` cannot be satisfied.

Otherwise:
- Continue until grading is complete,
- `CALL_01_GRADING.json` is written, and
- The JSON object is returned in chat.

