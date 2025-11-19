## TASK: Grade `call_02` (JSON response only)

You are a grading agent working **inside this repository**.

Your job in this task is to:
- Grade **`call_02`** using the **Phase 1, 17‑criteria transcript-only system**.
- Return your grading result as a **single JSON object** in chat.

Follow the same Phase 1 rules as in `TASK.md`:
- 17 criteria only (no Phase 2/3, no 26‑criteria context).
- Transcript + timing JSON only (no audio, no external DB).

### Files to use

Configuration:
- `config/prompt_for_transcript_only_grading.txt`
- `config/phase1_output_format_v2.json`
- `config/confidence_thresholds.json`

Documentation:
- `docs/PHASE1_SCOPE.md`
- `docs/Quick_Reference_Grades_EN_PHASE1.md`
- `docs/PHASE1_PACKAGE_GUIDE.md`

Call data:
- `calls/call_02/transcript-2.vtt`
- `calls/call_02/transcript-2.srt`
- `calls/call_02/paragraphs-2.json`
- `calls/call_02/sentences-2.json`
- `calls/call_02/timestamps-2.json`

### What to do

1. Load the instructions and schema from `config/` and `docs/`.
2. Evaluate all 17 Phase 1 criteria for `call_02` using the data in `calls/call_02/`.
3. Produce one JSON object that strictly follows `config/phase1_output_format_v2.json`:
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
4. In your chat reply, output **only** that JSON object (no extra text).

