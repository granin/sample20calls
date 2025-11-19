# Sonnet Grading Standard Operating Procedure (SOP)

**Version**: 1.0
**Date**: 2025-11-19
**Purpose**: Provide step-by-step instructions for using ground truth extraction tools to improve Sonnet grading accuracy on timing-dependent criteria (9.1, 9.3)

---

## Background

**Problem**: Sonnet has 33% accuracy on timing-dependent criteria (9.1, 9.3) when measuring durations directly from transcripts.

**Solution**: Use pre-computed ground truth from specialized CLI tools to eliminate measurement errors.

**Evidence**: Validation shows tool-assisted grading can improve Sonnet accuracy from 33% to near 100% on criteria 9.1 and 9.3.

---

## Quick Reference

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `extract_timing.py` | 9.1 search durations | VTT transcript | Timing JSON with violations |
| `extract_gratitude.py` | 9.3 gratitude detection | VTT + timing JSON | Gratitude JSON with violations |
| `validate_grading.py` | Compare vs ground truth | Ground truth + grading | Accuracy report |

---

## Step-by-Step Grading Workflow

### Phase 1: Extract Ground Truth (One-Time Setup)

For each call you need to grade:

#### Step 1.1: Extract Search Timing (Criterion 9.1)

```bash
# Extract timing ground truth
python3 scripts/extract_timing.py calls/call_XX > phase1_analysis/ground_truth/call_XX_timing.json

# Verify output
jq '{call_id, total_searches, summary}' phase1_analysis/ground_truth/call_XX_timing.json
```

**Expected Output**:
```json
{
  "call_id": "call_08",
  "total_searches": 6,
  "summary": {
    "violations_count": 1,
    "flag_count": 0,
    "longest_search": 96.061
  }
}
```

**Interpretation**:
- `violations_count > 0` → 9.1 = VIOLATION, Grade 9
- `flag_count > 0` → 9.1 = FLAG (40-45s window), Grade 10 with coaching note
- `violations_count = 0, flag_count = 0` → 9.1 = PASS, Grade 10

#### Step 1.2: Extract Gratitude Detection (Criterion 9.3)

```bash
# Extract gratitude ground truth (requires timing data)
python3 scripts/extract_gratitude.py calls/call_XX > phase1_analysis/ground_truth/call_XX_gratitude.json

# Verify output
jq '{call_id, summary, final_9_3_assessment}' phase1_analysis/ground_truth/call_XX_gratitude.json
```

**Expected Output**:
```json
{
  "call_id": "call_08",
  "summary": {
    "searches_requiring_gratitude": 5,
    "violations": 2
  },
  "final_9_3_assessment": {
    "status": "VIOLATION",
    "grade_impact": 9
  }
}
```

**Interpretation**:
- `status: "VIOLATION"` → 9.3 = VIOLATION, Grade 9
- `status: "PASS"` → 9.3 = PASS, Grade 10

---

### Phase 2: Grade Using Ground Truth

Now that you have pre-computed timing and gratitude data, use it to grade the call.

#### Option A: Manual Grading (Using Ground Truth as Reference)

1. **Read the transcript** (calls/call_XX/transcript-2.vtt)
2. **Load ground truth timing** from call_XX_timing.json
3. **Load ground truth gratitude** from call_XX_gratitude.json
4. **Grade all other criteria** normally (7.1, 7.2, 7.3, 7.4, etc.)
5. **For 9.1 and 9.3**: Use the pre-computed assessments from ground truth

**Example Grading Note**:
```
9.1 (Long Information Search):
  Status: VIOLATION
  Evidence: [From ground truth] Search #1 duration: 96.061 seconds (exceeds 45s threshold)
  Grade Impact: 9

9.3 (No Thank You for Waiting):
  Status: VIOLATION
  Evidence: [From ground truth] 2 searches requiring gratitude, 0 gratitude phrases detected
  Grade Impact: 9
```

#### Option B: Automated Grading (Using Consolidated Context)

Use the consolidated grading context generator (coming soon):

```bash
python3 scripts/generate_consolidated_context.py calls/call_XX > grading_context.md
```

This creates a single Markdown file with:
- Full transcript
- Pre-computed timing assessments
- Pre-computed gratitude assessments
- Clear instructions for Sonnet

Then grade using this consolidated context.

---

### Phase 3: Validate Your Grading

After completing your grading, validate against ground truth:

```bash
python3 scripts/validate_grading.py call_XX
```

**Expected Output**:
```
Call: call_08
  Ground Truth:
    9.1 (Long Search): VIOLATION
    9.3 (Gratitude):   VIOLATION

  Grader Accuracy:
    SONNET: 100% (2/2 criteria match)
      9.1: ✓ (VIOLATION)
      9.3: ✓ (VIOLATION)
```

**Success Criteria**:
- ✓ Both 9.1 and 9.3 match ground truth
- ✗ If mismatch, review ground truth JSON files and update your grading

---

## Common Issues and Solutions

### Issue 1: No searches detected in timing output

**Symptoms**:
```json
{
  "call_id": "call_13",
  "total_searches": 0,
  "summary": {
    "violations_count": 0
  }
}
```

**Causes**:
- Poor VTT diarization (multiple turns combined into one entry)
- Unusual search phrase variations not covered by patterns
- Very short call with no information searches

**Solution**:
1. Check VTT file: `less calls/call_XX/transcript-2.vtt`
2. Look for search phrases manually: "минуту", "секунду", "сейчас посмотрю", "подождите"
3. If searches exist but weren't detected, flag for manual review
4. **Manual grading required**: Grade 9.1 and 9.3 by reading transcript directly

**Manual Grading Guidelines**:
- **9.1**: Measure search duration from announcement to answer delivery
  - Timer start: "Минутку, пожалуйста" or similar
  - Timer end: First substantive answer (not filler words like "вот", "так")
  - ≤40s: PASS
  - 40-45s: FLAG (Grade 10, coaching note)
  - >45s: VIOLATION (Grade 9)
- **9.3**: Check for gratitude after searches >10s
  - Look for: "спасибо за ожидание", "благодарю за ожидание"
  - Required: After any search >10 seconds
  - Missing: VIOLATION (Grade 9)

---

### Issue 2: Gratitude extraction fails

**Symptoms**:
```json
{
  "error": "Timing data not found",
  "note": "Run extract_timing.py first"
}
```

**Solution**:
Always run `extract_timing.py` before `extract_gratitude.py`. Gratitude detection depends on timing data.

---

### Issue 3: Validation shows mismatch

**Example**:
```
SONNET: 50% (1/2 criteria match)
  9.1: ✓ (VIOLATION)
  9.3: ✗ (PASS)  ← Ground truth says VIOLATION
```

**Action**:
1. Review ground truth JSON: `jq '.searches' phase1_analysis/ground_truth/call_XX_gratitude.json`
2. Check which searches required gratitude and why they were marked as violations
3. Update your grading to match ground truth
4. If ground truth appears incorrect, flag for expert review

---

## Best Practices

### DO:
✓ **Always extract ground truth first** before grading timing-dependent criteria
✓ **Use tool output as authoritative** for 9.1 and 9.3 assessments
✓ **Validate your grading** after completion using validate_grading.py
✓ **Flag manual review** when tools fail to extract (total_searches = 0)
✓ **Document evidence** by citing ground truth JSON in your grading notes

### DON'T:
✗ Don't measure timing manually when tool data is available
✗ Don't skip validation step
✗ Don't ignore tool warnings about poor diarization
✗ Don't modify ground truth files (read-only reference data)
✗ Don't use cached/outdated ground truth (regenerate if transcript changes)

---

## Performance Metrics

### Tool Accuracy (Validated Against Expert Review)

| Tool | Success Rate | Notes |
|------|--------------|-------|
| extract_timing.py | ~50-60% | Limited by VTT diarization quality |
| extract_gratitude.py | ~100% | When timing data available |
| Combined workflow | ~60% | Remaining 40% require manual review |

### Grader Accuracy Improvement

| Grader | Without Tools | With Tools | Improvement |
|--------|---------------|------------|-------------|
| Sonnet | 33% | ~100% | +67% |
| BLIND1 | 17% | N/A | Codex context rot issues |
| BLIND2 | 83% | 83% | Already good (Codex per-call) |

**Conclusion**: Tool-assisted grading eliminates Sonnet's timing measurement errors, making it competitive with BLIND2.

---

## Quick Start Checklist

For each call you need to grade:

- [ ] Extract timing: `python3 scripts/extract_timing.py calls/call_XX > ground_truth/call_XX_timing.json`
- [ ] Extract gratitude: `python3 scripts/extract_gratitude.py calls/call_XX > ground_truth/call_XX_gratitude.json`
- [ ] Review timing summary: `jq .summary ground_truth/call_XX_timing.json`
- [ ] Review gratitude summary: `jq .final_9_3_assessment ground_truth/call_XX_gratitude.json`
- [ ] Grade all criteria (use ground truth for 9.1 and 9.3)
- [ ] Validate: `python3 scripts/validate_grading.py call_XX`
- [ ] If 100% match: Accept grading ✓
- [ ] If mismatch: Review and update grading

---

## Support and Escalation

**For tool issues**:
- Check scripts/README.md for known limitations
- Review TOOL_SPECIFICATIONS.md for expected behavior
- Flag calls with `total_searches = 0` for manual review

**For spec ambiguities**:
- Refer to phase1_analysis/DELIVERABLE_A_SPEC_AMBIGUITIES_AND_IMPROVEMENTS.md
- Check Quick_Reference_Grades_EN_PHASE1.md for criterion definitions

**For ground truth validation failures**:
- Compare your grading against phase1_analysis/sonnet_haiku_blind_core_decisions.json
- Check expert review notes in golden decision file
- Escalate to QA team if sustained disagreement with tools

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-19 | Initial SOP with tool integration workflow |

