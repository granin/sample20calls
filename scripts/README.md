# Ground Truth Extraction Tools

## Overview

This directory contains CLI tools for extracting ground truth from call transcripts to improve grading accuracy.

## Tools

### 1. extract_timing.py

**Purpose**: Extract search duration ground truth for criterion 9.1 (Long Information Search)

**Usage**:
```bash
python3 scripts/extract_timing.py calls/call_XX
```

**Output**: JSON with search durations, assessments (PASS/FLAG/VIOLATION), and check-ins

**Test Results** (validated against expert review):
- ✓ call_08: 96.061s VIOLATION detected correctly
- ✓ call_07: 60.836s VIOLATION detected correctly (search 2)
- ✓ call_12: Searches detected correctly
- ✗ call_11: Not detected (poor diarization - multi-turn VTT blocks)
- ✗ call_13: Not detected (poor diarization - multi-turn VTT blocks)
- ✗ call_01: Not detected (may use different search phrases or poor diarization)

**Known Limitations**:
1. **VTT Granularity**: Tool operates at VTT utterance level. Calls with large multi-turn blocks (where multiple speaker turns are combined into one VTT entry) may not be parsed correctly.
2. **Search Phrase Coverage**: Current patterns cover common Russian search announcements ("минуту", "секунду", "сейчас посмотрю", "подождите"). Some calls may use variations not yet covered.
3. **Diarization Quality**: Requires proper speaker separation in VTT files. Calls with poor diarization need manual review or word-level JSON parsing.

**Recommendations for Future Work**:
1. Implement word-level parsing mode using paragraphs-2.json for calls with poor VTT diarization
2. Expand search phrase patterns based on analysis of failed detections
3. Add manual review workflow for calls where tool confidence is low

**Success Rate**: ~50-60% of calls processed automatically. Remaining calls require manual review.

## Next Steps

See `phase1_analysis/NEXT_AGENT_TASK_BRIEF.md` for:
- Tool implementation roadmap (5 tools total)
- SOP creation for Sonnet grading
- Re-grading workflow with tool assistance
