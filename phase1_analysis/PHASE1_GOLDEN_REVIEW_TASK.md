# Phase 1 Golden Dataset – Expert Review Task

This repo contains 20 Russian support calls (Phase 1 scope) and multiple independent LLM gradings for each call. Your task is to help us decide how to construct a **golden dataset** and how to **tighten the grading prompts/spec** so future graders are more consistent.

You should assume **no prior context** beyond this repo.

---

## 1. What we did so far (grading passes)

For each call `call_01`–`call_20` under `calls/`:

- We used the **Phase 1 17‑criteria system** as defined in:
  - `config/phase1_grading_config.json`
  - `config/confidence_thresholds.json`
  - `config/phase1_output_format_v2.json`
  - `config/prompt_for_transcript_only_grading.txt`
  - `docs/PHASE1_SCOPE.md`
  - `docs/Quick_Reference_Grades_EN_PHASE1.md`
  - `docs/PHASE1_PACKAGE_GUIDE.md`
- Input data per call:
  - Transcript package: `calls/call_XX/transcript-2.vtt` (+ `paragraphs-2.json`, `sentences-2.json`, `timestamps-2.json`).
  - Call‑specific instructions: `calls/call_XX/CALL_XX_TASK.md`.

We then ran **four grading waves** with different LLM setups:

1. **Sonnet grading (original “gold” candidate)**
   - One Sonnet‑based run per call using `prompt_for_transcript_only_grading.txt`.
   - Output JSONs are normalized under:
     - `phase1_consolidated/sonnet/call_XX/CALL_XX_GRADING.json`

2. **Haiku grading (cost‑optimized model)**
   - One Haiku‑based run per call using the same high‑level grading instructions.
   - Original outputs came from `/tmp/phase1_haiku` and `~/Downloads/phase1_call_01/haiku/CALL_01_GRADING.json`.
   - They are normalized into this repo under:
     - `phase1_consolidated/haiku/call_XX/CALL_XX_HAIKU.json`

3. **BLIND1 grading (first blind pass, Codex transcript‑only)**
   - A second agent (Codex, via this repo) graded each call from scratch using only the transcript and Phase 1 docs.
   - Output JSONs are in:
     - Per‑call package: `calls/call_XX/CALL_XX_BLIND.json`
     - Normalized copy: `phase1_consolidated/blind1/call_XX/CALL_XX_BLIND.json`

4. **BLIND2 grading (third, more constrained blind pass, also Codex)**
   - For calls where Sonnet vs BLIND1 disagreed noticeably, we created **isolated per‑call repos** (no access to any grading JSONs or git history) and asked a third, independent Codex run to grade again.
   - Source repos (for context, not needed here) were under `/Users/m/phase1_blind2/call_XX/…`.
   - The per‑call BLIND2 task prompts used in those isolated runs are copied into this repo at:
     - `phase1_analysis/blind2_tasks/BLIND2_TASK_call_XX.md`
   - BLIND2 output JSONs are normalized under:
     - `phase1_consolidated/blind2/call_XX/CALL_XX_BLIND2.json`
   - BLIND2 exists for 17 calls:
     - `call_01`, `call_02`, `call_06`–`call_20` (excluding `call_03`, `call_04`, `call_05`).

In addition, we previously compared Sonnet vs Haiku vs BLIND1; that earlier comparison (before BLIND2) is saved as:

- `phase1_analysis/sonnet_haiku_blind1_comparison.json`

---

## 2. What data is available to you

You have **three types of artifacts** for analysis:

1. **Raw calls and tasks**
   - Calls: `calls/call_XX/…`
     - Transcript: `transcript-2.vtt` (+ JSON timing helpers).
     - First blind tasks: `calls/call_XX/CALL_XX_TASK.md`.
   - Global grading prompt & spec:
     - `config/prompt_for_transcript_only_grading.txt`
     - `docs/PHASE1_SCOPE.md`
     - `docs/Quick_Reference_Grades_EN_PHASE1.md`
     - `docs/PHASE1_PACKAGE_GUIDE.md`
   - BLIND2 per‑call task prompts:
     - `phase1_analysis/blind2_tasks/BLIND2_TASK_call_XX.md`

2. **Grading outputs (JSON)**
   - Sonnet:
     - `phase1_consolidated/sonnet/call_XX/CALL_XX_GRADING.json`
   - BLIND1:
     - `phase1_consolidated/blind1/call_XX/CALL_XX_BLIND.json`
     - (original copies also under `calls/call_XX/CALL_XX_BLIND.json`)
   - BLIND2 (only for 17 calls: 01,02,06–20):
     - `phase1_consolidated/blind2/call_XX/CALL_XX_BLIND2.json`
     - Some calls also have a copy under `calls/call_XX/CALL_XX_BLIND2.json`.

   All JSONs follow the schema in `config/phase1_output_format_v2.json`.

3. **Comparison and analytics**
   - **Core‑field golden decisions (pre‑BLIND2):**
     - `phase1_analysis/sonnet_haiku_blind_core_decisions.json`
   - **Sonnet vs Haiku vs BLIND1 (legacy, pre‑BLIND2):**
     - `phase1_analysis/sonnet_haiku_blind1_comparison.json`
   - **Three‑way Sonnet vs BLIND1 vs BLIND2 comparison (current):**
     - Detailed per‑call, per‑field:
       - `phase1_consolidated/analysis_3way_per_call.json`
     - Per‑field aggregate stats (counts + percentages):
       - `phase1_consolidated/summary_3way_field_stats.json`
       - `phase1_consolidated/summary_3way_field_stats.csv`
     - Compact coded summary:
       - `phase1_consolidated/compact_3way_summary.json`
     - Matrix of patterns for all calls × 22 fields:
       - `phase1_consolidated/matrix_3way_patterns.csv`
     - HTML reports for visual inspection:
       - `phase1_consolidated/report_3way_comparison.html`
       - `phase1_consolidated/report_3way_charts.html`

The comparison uses 22 key fields per call:

- `final_grade`
- `final_confidence`
- Criteria statuses: `1.1, 2.1, 3.1, 3.3, 3.6, 4.1, 5.1, 6.1, 7.1, 7.2, 7.3, 7.4, 9.1, 9.3, 10.2, 10.3, 10.6`
- Risk fields: `risk_compliance`, `risk_customer_satisfaction`, `risk_data_security`

For each call/field, we classify the pattern:

- `all_equal` – Sonnet, BLIND1, BLIND2 all agree.
- `sonnet_outlier` – BLIND1 == BLIND2 ≠ Sonnet.
- `blind1_outlier` – Sonnet == BLIND2 ≠ BLIND1.
- `blind2_outlier` – Sonnet == BLIND1 ≠ BLIND2.
- `all_different` – all three disagree.
- `missing_data` – BLIND2 not available for that call.

---

## 3. Our current assumptions about “gold”

We have **tentative** golden decisions for each call in:

- `phase1_analysis/sonnet_haiku_blind_core_decisions.json`

In that file, for each `call_XX` we store:

- `golden_source`: `"Sonnet"`, `"BLIND"`, or `"none"`.
- `confidence`: `"high"`, `"medium"`, or `"low"`.
- `reason`: short explanation (e.g., “Sonnet and BLIND1 agree on core fields; no BLIND2.”).

Key assumptions we used when building that file:

- We focus on **core fields**: `final_grade`, plus criteria `7.1`, `7.2`, `7.3`, `9.1`, `9.3`.
- For `call_03`, `call_04`, `call_05`:
  - Sonnet and BLIND1 fully agree on core fields (and Sonnet vs BLIND1 match rate ≥ 95.5%), so we provisionally treat **Sonnet as gold** there (no BLIND2 run).
- For `call_15`:
  - BLIND1 and BLIND2 agree on core fields and both differ from Sonnet, so we treat the BLIND consensus as gold.
- For `call_18`:
  - Sonnet, BLIND1, and BLIND2 fully agree on core fields, so Sonnet is gold with high confidence.
- For the remaining calls:
  - Sonnet, BLIND1, and BLIND2 disagree on at least one core field; we currently mark `golden_source = "none"` and `confidence = "low"` there.

We now want an external, critical review of these assumptions.

---

## 4. What we want from you (expert tasks)

Please work **only inside this repo**. Do not assume any external files or prior conversations.

### 4.1. Understand the grading system and prompts

1. Read the Phase 1 specification:
   - `docs/PHASE1_SCOPE.md`
   - `docs/Quick_Reference_Grades_EN_PHASE1.md`
   - `config/phase1_grading_config.json`
   - `config/confidence_thresholds.json`
   - `config/phase1_output_format_v2.json`
2. Read the main LLM grading prompt:
   - `config/prompt_for_transcript_only_grading.txt`
3. Skim a few call tasks:
   - `calls/call_01/CALL_01_TASK.md`, `calls/call_02/CALL_02_TASK.md`, etc.
4. Skim some BLIND2 task files to see how we constrained the third grader:
   - `phase1_analysis/blind2_tasks/BLIND2_TASK_call_01.md`, etc.

**Deliverable A:** a short written assessment (in a new markdown file you create under `phase1_analysis/`) that:

- Identifies any **ambiguities or inconsistencies** in the Phase 1 spec and the main prompt (especially around 7.2, 4.1, 9.1, 9.3, and risk fields).
- Suggests concrete wording changes or additional examples to make these criteria easier to apply consistently.

### 4.2. Analyze agreement/disagreement patterns

1. Open:
   - `phase1_consolidated/summary_3way_field_stats.json`
   - `phase1_consolidated/compact_3way_summary.json`
   - Optionally visualize using:
     - `phase1_consolidated/report_3way_comparison.html`
     - `phase1_consolidated/report_3way_charts.html`
2. For each of the 22 fields, note:
   - `% all_equal`
   - `% sonnet_outlier`, `% blind1_outlier`, `% blind2_outlier`
   - `% all_different`
3. Identify:
   - Which fields are **very stable** (high `all_equal%`, low outliers).
   - Which fields are **fragile** (high outlier or `all_different%`).

**Deliverable B:** a concise summary (preferably a table or bullet list) that:

- Ranks the fields by stability.
- Highlights the **top 3–5 fragile fields** that most often diverge between Sonnet and the blind graders.
- For each fragile field, links this back to specific **prompt/spec weaknesses** you see in the Phase 1 docs.

### 4.3. Review and refine golden decisions per call

Using:

- `phase1_analysis/sonnet_haiku_blind_core_decisions.json`
- `phase1_consolidated/analysis_3way_per_call.json`
- The per‑call JSONs for Sonnet, BLIND1, and BLIND2:
  - `phase1_consolidated/sonnet/call_XX/CALL_XX_GRADING.json`
  - `phase1_consolidated/blind1/call_XX/CALL_XX_BLIND.json`
  - `phase1_consolidated/blind2/call_XX/CALL_XX_BLIND2.json` (where present)

Please:

1. For calls currently marked `golden_source = "Sonnet"` or `"BLIND"`:
   - Spot‑check at least:
     - `call_03`, `call_04`, `call_05`, `call_15`, `call_18`.
   - For each, verify that the chosen source genuinely aligns best with the Phase 1 rules on **core fields**.
   - If you disagree, propose a different golden source and explain why.
2. For calls with `golden_source = "none"`:
   - Sample several representative cases across different types of disagreement (e.g., Sonnet outlier on 7.2 vs BLIND outliers on 4.1, etc.).
   - For each sampled call:
     - Read the transcript and all three JSONs.
     - Decide whether a **reasonable gold choice** can be made (Sonnet vs BLIND consensus), or whether the call should remain “ambiguous / needs human review”.
   - You do not have to re‑grade all 20 calls; focus on **explaining patterns and criteria** for accepting/rejecting a gold label, using concrete examples.

**Deliverable C:** an updated golden‑decision proposal (you may either):

- Edit `phase1_analysis/sonnet_haiku_blind_core_decisions.json` directly, **or**
- Create a new file under `phase1_analysis/` with your proposed golden decisions per call, including:
  - `golden_source` per call,
  - `confidence` (e.g., numeric between 0 and 1 or a short label),
  - short rationale, especially where you change our current decision.

### 4.4. Suggest how to use this for future graders

Finally, we want advice on how to:

- Use the **golden calls** as calibration/few‑shot examples.
- Improve the prompt so Haiku/Sonnet‑like models converge more reliably to the gold.

Please propose:

- Which calls (and which parts of their transcripts + JSONs) you would use as **few‑shot exemplars** for:
  - Correct handling of 7.2 (Echo method).
  - Clear 9.1 (search duration) violations vs borderline vs pass.
  - 9.3 (thank‑you‑for‑waiting) edge cases.
  - 4.1 (difficult customer) under text‑only constraints.
- How you would **structure a revised prompt** (sections, examples, and checks) using:
  - The existing `prompt_for_transcript_only_grading.txt` as a base, and
  - A small number of real “gold” snippets from the data here.

**Deliverable D:** a short design note (markdown under `phase1_analysis/`) that:

- Outlines a revised prompt structure and example selection.
- Explains how this should reduce disagreement on the top fragile fields you identified.

---

## 5. How to work and what not to do

- Stay entirely within this repo.
- Do **not** assume any previous chat logs or external artifacts.
- Do **not** call external APIs; work with the transcripts and JSONs as static data.
- Prefer writing your outputs under:
  - `phase1_analysis/` (new markdown/JSON files),
  - without modifying original call packages under `calls/call_XX/` unless strictly necessary.

At the end of your work, we expect:

- A clarified, documented proposal for the Phase 1 **golden dataset** for these 20 calls.
- Concrete suggestions for how to adjust the **prompt/spec** to make future graders (Haiku/Sonnet/Opus) match that gold more reliably on the most fragile criteria.
