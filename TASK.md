## TASK: Phase 1 Call Grading Repo (20 Calls)

You are a local coding / orchestration agent (e.g., Claude Code) connected to this GitHub repository.

Your job is to **set up and operate a Phase 1–only grading system** for up to **20 calls**, using **17 transcript-based criteria** and nothing else.

Read and follow this file **completely** before doing anything else.

---

## 1. Repository Scope and Constraints

- This repo is a **self-contained Phase 1 grading package**.
- It defines **exactly 17 criteria** for transcript-based grading of Russian contact center calls.
- There is **no Phase 2 / Phase 3** here, and no 26-criteria manifest.
- Treat this repo as the **entire universe** of grading rules and documentation.

You must NOT:
- Assume or invent additional criteria beyond the 17 defined here.
- Refer to any external docs that mention 26 criteria or future phases.
- Depend on audio, database, or external project configuration.

---

## 2. Folder Structure (What You See)

At repo root:
- `README.md` – Entry point for humans and agents.
- `TASK.md` – This file (top-level instructions for you).
- `config/` – Grading prompts and JSON schemas.
- `docs/` – Phase 1 documentation and guides.
- `calls/` – Up to 20 calls, each in its own folder.

Inside `config/`:
- `phase1_grading_config.json`
- `confidence_thresholds.json`
- `phase1_output_format_v2.json`
- `prompt_for_transcript_only_grading.txt`

Inside `docs/`:
- `PHASE1_SCOPE.md` – **Read this first after README**.
- `PHASE1_PACKAGE_GUIDE.md`
- `Quick_Reference_Grades_EN_PHASE1.md`
- `Excel_Analysis_Summary_EN_PHASE1.md`
- `phase1_comparison_to_full.md`

Inside `calls/`:
- `call_01/`
- `call_02/`
- ...
- `call_20/`

Each `call_XX/` will contain transcript and timing files for that call (VTT/SRT + JSON). Some calls may be empty or not yet populated.

---

## 3. Your Assumptions (Agent Reality)

For all your reasoning inside this repo:

- There are **17 criteria in the evaluation system**.
- You work **only from transcripts and timing JSON**.
- You **never** mention:
  - "17 out of 26 criteria"
  - "Phase 2" or "Phase 3"
  - "Deferred criteria" or "future detectors"
- You describe this as a **complete system for transcript-based grading**, not as a subset.

Language to use:
- ✅ "The evaluation system uses 17 criteria."
- ❌ "This is 17 of 26 criteria in the full system."

---

## 4. How to Grade a Call (Your Workflow)

For any single call (e.g., `call_05`):

1. **Read the core docs**
   - `README.md`
   - `docs/PHASE1_SCOPE.md`
   - `docs/PHASE1_PACKAGE_GUIDE.md`
   - `docs/Quick_Reference_Grades_EN_PHASE1.md`

2. **Load configuration**
   - Use `config/prompt_for_transcript_only_grading.txt` as your **instruction prompt**.
   - Use `config/phase1_output_format_v2.json` as the **output JSON schema**.
   - Use `config/confidence_thresholds.json` to interpret confidence levels.

3. **Identify call data**
   - The user will specify a call folder, e.g.:
     - `calls/call_05/`
   - Typical files per call (names may vary, user will clarify):
     - Transcript files: `.vtt`, `.srt`
     - Segmentation files: `paragraphs-*.json`, `sentences-*.json`
     - Timing files: `timestamps-*.json` (for precise timing, especially 7.2)
     - Optional: `CALL_XX_GRADING.json` (human reference – do not copy; use only for comparison if asked).

4. **Apply the 17 criteria**
   - Criteria and rules are defined in `docs/PHASE1_SCOPE.md` and `docs/Quick_Reference_Grades_EN_PHASE1.md`.
   - Follow the confidence and grading rules in `docs/PHASE1_SCOPE.md`.
   - Apply the "lowest code rule" to high-confidence violations.

5. **Produce output**
   - Return a **single JSON object** that strictly conforms to `config/phase1_output_format_v2.json`.
   - Include:
     - `call_metadata`
     - `final_scoring`
     - `violations_detected` with evidence and timestamps
     - `violations_summary`
     - `coaching_priorities`
     - `risk_assessment`
     - `detected_patterns`
     - `criteria_assessment`
     - `positive_observations`
     - `data_quality`

---

## 5. How the Human Will Talk to You

The human may say things like:
- "Grade call 05 using the Phase 1 system."
- "Grade all populated calls in the `calls/` folder."
- "Compare your grading for `call_05` with `CALL_05_GRADING.json`."

When they do:

1. Treat this repo as your **only source of truth**.
2. Follow the workflow in section 4.
3. For each call:
   - Read the relevant `call_XX/` files.
   - Apply all 17 criteria.
   - Output JSON in the Phase 1 schema.

---

## 6. Safety and Scope Guardrails

- Do not:
  - Reach outside this repository for grading logic or criteria definitions.
  - Expand or modify the set of criteria.
  - Introduce references to full-system docs (26 criteria, Phase 2/3).
- Always:
  - Treat the 17 criteria as the full evaluation system.
  - Make decisions only using transcript and timing data.
  - Flag borderline cases with appropriate confidence, as defined in the docs.

---

## 7. First Action Checklist

1. Confirm that the repo root contains:
   - `README.md`
   - `TASK.md`
   - `config/`
   - `docs/`
   - `calls/` with `call_01`–`call_20`.
2. Read:
   - `README.md`
   - `docs/PHASE1_SCOPE.md`
   - `docs/PHASE1_PACKAGE_GUIDE.md`
3. Wait for the user to specify which `call_XX/` folders contain transcripts and which call to grade first.
4. When asked to grade, follow the workflow in section 4 and respond with JSON only.

Once you have completed these steps, you are fully configured to work as a **Phase 1 transcript-only grading agent** for up to 20 calls in this repository.

