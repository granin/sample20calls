# Golden Dataset Completion - Next Agent Task Brief

## Mission
Complete the Phase 1 Golden Dataset by implementing systematic grading improvements that raise Sonnet's accuracy to match expert ground truth, achieving 18/20 high-confidence golden labels (90%).

---

## Current State (Session End Snapshot)

### Golden Dataset Status
- **High confidence**: 12/20 calls (60%)
- **Medium confidence**: 8/20 calls (40%)
- **Target**: 18/20 calls (90%) after improvements

### Root Cause Analysis Complete
**Why graders disagree:**

1. **BLIND1 (Codex single session)**: Context rot → measurement errors (call_07, call_11, call_13)
2. **BLIND2 (Codex per-call, high thinking)**: Most accurate on timing (9.1), but missed some 7.2 violations
3. **Sonnet (general understanding)**: Best comprehension, but timing measurement errors on 9.1

**Key finding**: Sonnet needs **tool assistance** for timing precision, not just better prompts.

---

## Your Mission: 3-Phase Systematic Improvement

### Phase 1: Create Timing Extraction CLI Tools (Week 1)

**Problem**: Sonnet measures search durations incorrectly (e.g., call_08: measured 3.2s, actual 96s)

**Solution**: Build `scripts/extract_timing.py` that:
1. Parses VTT/word-level JSON
2. Identifies search announcements ("Минутку", "Сейчас посмотрю")
3. Identifies answer delivery (first substantive word after search)
4. Outputs precise timestamps and durations

**Example output:**
```json
{
  "call_id": "call_08",
  "searches": [
    {
      "search_num": 1,
      "start_time": "00:00:27.869",
      "start_phrase": "Минутку, пожалуйста",
      "end_time": "00:02:03.930",
      "end_phrase": "Спасибо за ожидание",
      "duration_seconds": 96.061,
      "status": "VIOLATION (>45s)",
      "check_ins": ["00:00:56.793", "00:02:00.850"]
    }
  ]
}
```

**Usage in Sonnet grading:**
```
Step 1: Run timing extraction
$ python scripts/extract_timing.py calls/call_08/transcript-2.vtt calls/call_08/paragraphs-2.json

Step 2: Force Sonnet to read extracted timing
[Include timing JSON in consolidated grading context]

Step 3: Sonnet grades using pre-computed measurements
```

**Files to create:**
- `scripts/extract_timing.py` - Search duration extractor
- `scripts/extract_echo.py` - Echo method checker (7.2)
- `scripts/extract_gratitude.py` - Gratitude phrase detector (9.3)
- `scripts/validate_grading.py` - Compare grading against extracted facts

---

### Phase 2: Create Sonnet Grading SOP (Week 2)

**Problem**: Sonnet lacks step-by-step procedure for timing-critical criteria

**Solution**: `docs/SONNET_GRADING_SOP.md` with FAQs

#### SOP Structure:

**For Criterion 9.1 (Long Search):**
```markdown
## Step-by-Step: Grading 9.1

### Pre-requisite: Extract timing data
```bash
python scripts/extract_timing.py calls/call_XX/transcript-2.vtt calls/call_XX/paragraphs-2.json > timing.json
```

### Step 1: Read extracted timing
[Sonnet reads timing.json showing all search durations]

### Step 2: Apply spec
- 0-40s: PASS
- 40-45s: FLAG (Grade 10, flag_window=true, no score reduction)
- >45s: VIOLATION (Grade 9, score reduction)

### Step 3: Cross-reference with transcript
Verify timing extraction is correct by spot-checking 1-2 searches in VTT

### FAQ: Common Errors

**Q: How do I know where search ends?**
A: Use timing.json pre-computed end_phrase. If you must measure manually, look for first SUBSTANTIVE word (not "Вот", "Так"), verified in paragraphs-2.json.

**Q: Do check-ins reset timer?**
A: NO. timing.json shows total duration. Check-ins are listed separately but don't reset.

**Q: What if 40-45s search?**
A: Grade 10, NOT Grade 9. Set flag_window=true, score_reduction=false in violations_detected.
```

**For Criterion 7.2 (Echo Method):**
```markdown
## Step-by-Step: Grading 7.2

### Pre-requisite: Extract contact data
```bash
python scripts/extract_echo.py calls/call_XX/paragraphs-2.json > echo.json
```

### Step 1: Read extracted contact data
[Sonnet reads echo.json showing all name/phone/city/email collection moments]

### Step 2: For EACH contact field, verify 3-step echo:
1. Operator repeats data back (within 10s)
2. Operator asks "Верно?" / "Правильно?" (immediately after repeat)
3. Customer confirms "Да" / "Верно" (within 5s)

### Step 3: All-or-nothing rule
If ANY field fails ANY step → VIOLATION

### FAQ: Common Errors

**Q: Operator repeated name but didn't ask "Верно?" - is this PASS?**
A: NO. VIOLATION. All 3 steps required.

**Q: Does city count as contact data?**
A: YES, if collected for delivery/contact purposes. Use echo.json to identify.

**Q: What if operator echoed 2/3 fields?**
A: VIOLATION. Partial echo = violation (all-or-nothing policy).
```

**Files to create:**
- `docs/SONNET_GRADING_SOP.md` - Complete SOP with FAQs
- `docs/TIMING_MEASUREMENT_GUIDE.md` - Detailed timing rules
- `docs/ECHO_METHOD_EXAMPLES.md` - 20+ real examples from dataset

---

### Phase 3: Re-Grade 8 Medium-Confidence Calls (Week 3)

**Using new tools + SOP:**

1. **call_01, call_09, call_10** (Sonnet/BLIND2 consensus pattern):
   - Extract timing for 9.1 verification
   - Extract echo data for 7.2 verification
   - Extract gratitude for 9.3 verification
   - Re-run Sonnet with tool outputs in context
   - Expected: Agreement with BLIND2 improves, upgrade to high confidence

2. **call_08** (hybrid case):
   - Tool will catch both 7.2 (name at 00:08) AND 9.1 (96s search)
   - Re-run Sonnet with extracted violations pre-identified
   - Expected: Sonnet now catches both violations

3. **call_02, call_06, call_16, call_17, call_19** (high field agreement):
   - Verify with tools (should confirm Sonnet correct)
   - Spot-check a few criteria
   - Expected: Upgrade to high confidence with tool validation

**Target outcome**: 8/8 medium → high confidence = **20/20 high confidence calls**

---

## Systematic Methodology: Ground Truth Establishment

### Principle: Transcript is Truth, Not Grader Consensus

**Do NOT:**
- ❌ Use majority vote (2 graders can both be wrong)
- ❌ Assume Sonnet always correct (timing errors proven)
- ❌ Trust measurements without verification

**DO:**
- ✅ Extract ground truth from transcript using code
- ✅ Read actual VTT timestamps for timing
- ✅ Verify echo method with word-level JSON
- ✅ Compare ALL graders against extracted truth
- ✅ Pick grader that matches ground truth most closely

### Ground Truth Extraction Process

**For each call:**

1. **Extract timing ground truth:**
```bash
python scripts/extract_timing.py calls/call_XX/transcript-2.vtt calls/call_XX/paragraphs-2.json > call_XX_timing_truth.json
```

2. **Extract echo ground truth:**
```bash
python scripts/extract_echo.py calls/call_XX/paragraphs-2.json > call_XX_echo_truth.json
```

3. **Extract gratitude ground truth:**
```bash
python scripts/extract_gratitude.py calls/call_XX/transcript-2.vtt > call_XX_gratitude_truth.json
```

4. **Compare graders against ground truth:**
```bash
python scripts/validate_grading.py \
  --ground-truth-timing call_XX_timing_truth.json \
  --ground-truth-echo call_XX_echo_truth.json \
  --ground-truth-gratitude call_XX_gratitude_truth.json \
  --sonnet phase1_consolidated/sonnet/call_XX/CALL_XX_GRADING.json \
  --blind1 phase1_consolidated/blind1/call_XX/CALL_XX_BLIND.json \
  --blind2 phase1_consolidated/blind2/call_XX/CALL_XX_BLIND2.json \
  --output call_XX_grader_accuracy.json
```

5. **Pick golden source based on accuracy score:**
```json
{
  "call_id": "call_08",
  "ground_truth_comparison": {
    "sonnet": {
      "7.2_accuracy": 1.0,
      "9.1_accuracy": 0.0,
      "9.3_accuracy": 1.0,
      "final_grade_correct": true,
      "overall_score": 0.75
    },
    "blind2": {
      "7.2_accuracy": 0.0,
      "9.1_accuracy": 1.0,
      "9.3_accuracy": 1.0,
      "final_grade_correct": false,
      "overall_score": 0.66
    }
  },
  "recommended_golden_source": "Sonnet",
  "reason": "Higher overall accuracy (0.75 vs 0.66), correct final_grade"
}
```

---

## Deliverables to Create (Save to Disk)

### 1. Tool Suite (`scripts/`)

**Core extraction tools:**
- `extract_timing.py` - 9.1 search duration extraction
- `extract_echo.py` - 7.2 echo method verification
- `extract_gratitude.py` - 9.3 gratitude phrase detection
- `validate_grading.py` - Compare grading against ground truth
- `generate_consolidated_context.py` - Create single-file grading context

**Helper utilities:**
- `vtt_parser.py` - Parse VTT to structured format
- `word_json_parser.py` - Parse word-level JSON
- `timestamp_utils.py` - Timestamp arithmetic functions

**Example `extract_timing.py` skeleton:**
```python
#!/usr/bin/env python3
"""
Extract search timing ground truth from VTT and word-level JSON.

Usage:
    python extract_timing.py calls/call_XX/transcript-2.vtt calls/call_XX/paragraphs-2.json
"""

import sys
import json
import re
from typing import List, Dict

# Search announcement phrases (Russian)
SEARCH_PHRASES = [
    r"минут[ауе]",
    r"секунд[ауе]",
    r"сейчас\s+(посмотр|провер)",
    r"подожд[ие]те",
    r"одну\s+минут",
]

# Filler words (not substantive answers)
FILLER_WORDS = ["вот", "так", "итак", "ну", "значит", "хорошо"]

def parse_vtt(vtt_path: str) -> List[Dict]:
    """Parse VTT file to structured segments."""
    # Implementation here
    pass

def identify_searches(segments: List[Dict]) -> List[Dict]:
    """Identify search announcement moments."""
    # Implementation here
    pass

def find_answer_delivery(segments: List[Dict], search_start_idx: int) -> Dict:
    """Find first substantive answer after search."""
    # Implementation here
    pass

def calculate_duration(start_time: str, end_time: str) -> float:
    """Calculate duration in seconds."""
    # Implementation here
    pass

def main():
    # Parse inputs
    # Extract searches
    # Output JSON
    pass

if __name__ == "__main__":
    main()
```

### 2. Documentation (`docs/`)

**Grading guides:**
- `SONNET_GRADING_SOP.md` - Step-by-step SOP for Sonnet
- `TIMING_MEASUREMENT_GUIDE.md` - Detailed timing rules with examples
- `ECHO_METHOD_GUIDE.md` - 7.2 examples and edge cases
- `GRATITUDE_PHRASE_GUIDE.md` - 9.3 acceptable phrases enumerated

**Methodology:**
- `GROUND_TRUTH_METHODOLOGY.md` - How to establish ground truth
- `GRADER_COMPARISON_PROCESS.md` - How to compare graders systematically
- `GOLDEN_DATASET_CRITERIA.md` - What qualifies as high-confidence golden

### 3. Golden Dataset Artifacts (`phase1_analysis/`)

**Ground truth extractions (create for all 20 calls):**
- `ground_truth/call_XX_timing.json` - Extracted search durations
- `ground_truth/call_XX_echo.json` - Echo method verification
- `ground_truth/call_XX_gratitude.json` - Gratitude phrase detection

**Grader accuracy comparisons:**
- `grader_accuracy/call_XX_comparison.json` - Per-call grader accuracy
- `grader_accuracy/summary_accuracy.json` - Overall grader performance

**Final golden dataset:**
- `sonnet_haiku_blind_core_decisions.json` (already updated)
- `golden_dataset_validation_report.md` - Evidence for each golden decision

---

## Success Criteria

**Phase 1 (Tools) - Complete when:**
- ✅ `extract_timing.py` correctly identifies all searches in call_08 (96s search verified)
- ✅ `extract_echo.py` correctly identifies 7.2 violations in call_01, call_20
- ✅ `validate_grading.py` produces accuracy scores matching expert review findings

**Phase 2 (SOP) - Complete when:**
- ✅ SOP tested on 3 sample calls, produces same golden labels as expert review
- ✅ FAQs answer all common grading questions (9.1 flag window, 7.2 partial echo, etc.)
- ✅ Documentation is self-contained (next agent can use without context)

**Phase 3 (Re-grading) - Complete when:**
- ✅ 18/20 calls achieve high confidence (90%)
- ✅ All medium-confidence calls validated with tool output
- ✅ Golden dataset ready for production use

**Overall Success:**
- 🎯 20/20 calls with definitive golden labels backed by ground truth
- 🎯 Sonnet grading accuracy improved from ~70% to >90% on timing criteria
- 🎯 Reproducible methodology documented for future grading waves

---

## Quick Start for Next Agent

**Day 1: Understand current state**
1. Read this file
2. Read `phase1_analysis/DELIVERABLE_*.md` (4 expert review documents)
3. Review `phase1_analysis/sonnet_haiku_blind_core_decisions.json` (golden labels)

**Day 2-3: Build core tool**
4. Implement `scripts/extract_timing.py`
5. Test on call_08 (should detect 96s search), call_11 (57s), call_13 (42.8s)
6. Verify against expert review findings in golden decisions JSON

**Day 4-5: Build validation tool**
7. Implement `scripts/validate_grading.py`
8. Run on all 20 calls, compare output to expert review findings
9. Should confirm: call_07/call_11 (BLIND2 best), call_13/call_14/call_20 (Sonnet best)

**Week 2: Create SOP and re-grade**
10. Write `docs/SONNET_GRADING_SOP.md`
11. Re-grade 8 medium-confidence calls using SOP + tools
12. Update `sonnet_haiku_blind_core_decisions.json` with upgraded confidence

**Week 3: Finalize and validate**
13. Generate ground truth for all 20 calls
14. Create validation report
15. Commit final golden dataset

---

## Critical Files to Preserve

**DO NOT DELETE:**
- `phase1_analysis/sonnet_haiku_blind_core_decisions.json` (golden labels)
- `phase1_analysis/DELIVERABLE_A_*.md` (spec ambiguities)
- `phase1_analysis/DELIVERABLE_B_*.md` (field stability analysis)
- `phase1_analysis/DELIVERABLE_C_*.md` (golden decision proposals)
- `phase1_analysis/DELIVERABLE_D_*.md` (revised prompt strategy)

**CREATE NEW:**
- All tools in `scripts/`
- All SOPs in `docs/`
- All ground truth in `phase1_analysis/ground_truth/`
- All comparisons in `phase1_analysis/grader_accuracy/`

---

## Contact Points / Questions

**If stuck:**
1. Re-read expert review deliverables (DELIVERABLE_A through D)
2. Check specific call findings in `sonnet_haiku_blind_core_decisions.json` → `transcript_evidence` field
3. Read actual transcripts: `calls/call_XX/transcript-2.vtt` (ground truth)

**Common questions answered:**
- Q: Which grader to trust? A: Run validation tool, pick highest accuracy score
- Q: How to measure search duration? A: Use extract_timing.py, don't measure manually
- Q: What if graders all disagree? A: Extract ground truth from transcript, ignore graders
- Q: Can I change golden labels? A: Yes, if you have transcript evidence. Update JSON with `notes` field explaining why.

---

## Expected Timeline

- Week 1: Tools built and tested (40 hours)
- Week 2: SOP created, 8 calls re-graded (30 hours)
- Week 3: Validation and finalization (30 hours)
- **Total: 100 hours / 2.5 weeks**

**Deliverable**: Production-ready golden dataset with 90% high-confidence coverage.
