# Ground Truth Extraction Tools

## Overview

This directory contains CLI tools for extracting ground truth from call transcripts to improve grading accuracy. These tools address measurement errors in LLM graders by providing pre-computed, precise timing and pattern detection.

## Tools Implemented

### 1. extract_timing.py

**Purpose**: Extract search duration ground truth for criterion 9.1 (Long Information Search)

**Usage**:
```bash
python3 scripts/extract_timing.py calls/call_XX > phase1_analysis/ground_truth/call_XX_timing.json
```

**Output**: JSON with search durations, assessments (PASS/FLAG/VIOLATION), and check-ins

**Test Results** (validated against expert review):
- ✓ call_08: 96.061s VIOLATION detected correctly
- ✓ call_07: 60.836s VIOLATION detected correctly (search 2: 60.8s)
- ✓ call_12: Searches detected correctly (no violations)
- ✗ call_11: Not detected (poor diarization - multi-turn VTT blocks)
- ✗ call_13: Not detected (poor diarization - multi-turn VTT blocks)
- ✗ call_01: Not detected (may use different search phrases or poor diarization)

**Success Rate**: ~50-60% of calls processed automatically. Remaining calls require manual review.

---

### 2. extract_gratitude.py

**Purpose**: Extract gratitude phrase detection ground truth for criterion 9.3 (No Thank You for Waiting)

**Usage**:
```bash
# Requires timing data from extract_timing.py first
python3 scripts/extract_timing.py calls/call_XX > phase1_analysis/ground_truth/call_XX_timing.json
python3 scripts/extract_gratitude.py calls/call_XX > phase1_analysis/ground_truth/call_XX_gratitude.json
```

**Output**: JSON with gratitude detection for each search (required for searches >10s)

**Test Results**:
- ✓ call_07: 2 violations detected (matches expert review)
- ✓ call_08: 2 violations detected
- ✓ call_12: 1 violation detected

**Success Rate**: ~100% when timing data is available. Depends on extract_timing.py success rate.

---

### 3. validate_grading.py

**Purpose**: Compare grader outputs (Sonnet, BLIND1, BLIND2) against ground truth extractions

**Usage**:
```bash
python3 scripts/validate_grading.py call_07 call_08 call_12
```

**Output**: Validation report showing which graders matched ground truth for criteria 9.1 and 9.3

**Validation Results** (3 calls, 6 criteria total):

| Grader | Accuracy | Correct | Notes |
|--------|----------|---------|-------|
| **BLIND2** | **83.3%** | 5/6 | Best on timing and gratitude detection |
| Sonnet | 33.3% | 2/6 | Missed many violations, needs tool assistance |
| BLIND1 | 16.7% | 1/6 | Context rot issues (single session grading) |

**Key Finding**: BLIND2 (Codex with high thinking, per-call sessions) is most reliable on 9.1/9.3, validating expert review conclusions. Sonnet needs pre-computed timing data to eliminate measurement errors.

---

### 4. batch_extract_ground_truth.sh

**Purpose**: Batch processing script to run timing and gratitude extraction on all 20 calls

**Usage**:
```bash
bash scripts/batch_extract_ground_truth.sh
```

**Output**: Creates phase1_analysis/ground_truth/ directory with timing and gratitude JSON files for all calls

**Status**: Implemented but slow. Optimized for sequential processing with progress tracking.

---

## Known Limitations

1. **VTT Granularity**: Tools operate at VTT utterance level. Calls with large multi-turn blocks (where multiple speaker turns are combined into one VTT entry) may not be parsed correctly.
2. **Search Phrase Coverage**: Current patterns cover common Russian search announcements ("минутку", "секунду", "сейчас посмотрю", "подождите"). Some calls may use variations not yet covered.
3. **Diarization Quality**: Requires proper speaker separation in VTT files. Calls with poor diarization need manual review or word-level JSON parsing.

## Recommendations for Future Work

1. Implement word-level parsing mode using paragraphs-2.json for calls with poor VTT diarization
2. Expand search phrase patterns based on analysis of failed detections
3. Add manual review workflow for calls where tool confidence is low
4. Implement extract_echo.py for criterion 7.2 (Echo Method) verification
5. Implement consolidated grading context generator for Sonnet

## Next Steps

See `phase1_analysis/NEXT_AGENT_TASK_BRIEF.md` for:
- Tool implementation roadmap (5 tools total, 3 completed)
- SOP creation for Sonnet grading with tool integration
- Re-grading workflow for 8 medium-confidence calls
- Target: 18/20 high-confidence golden labels (90%)
