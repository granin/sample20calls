# Phase 1 Grading Project - Quick Reference Card

## Critical Paths

### Configuration
```
/config/phase1_grading_config.json       ← 17-criteria definitions
/config/phase1_output_format_v2.json    ← JSON schema
/config/confidence_thresholds.json       ← When to auto-grade
/config/prompt_for_transcript_only_grading.txt ← LLM prompt
```

### Grading Data Access
```
/calls/call_XX/                          ← Raw call transcripts (20 calls)
/phase1_consolidated/sonnet/call_XX/     ← Sonnet gradings (20)
/phase1_consolidated/haiku/call_XX/      ← Haiku gradings (20)
/phase1_consolidated/blind1/call_XX/     ← BLIND1 gradings (20)
/phase1_consolidated/blind2/call_XX/     ← BLIND2 gradings (17)
```

### Analysis & Deliverables
```
/phase1_analysis/PHASE1_GOLDEN_REVIEW_TASK.md       ← 4-wave comparison
/phase1_analysis/NEXT_AGENT_TASK_BRIEF.md           ← Next steps
/phase1_analysis/TOOL_SPECIFICATIONS.md             ← Tool roadmap
/phase1_analysis/DELIVERABLE_A_*.md through D_*.md  ← 4 deliverables
/phase1_consolidated/analysis_3way_per_call.json    ← All comparisons
```

### Tools
```
/scripts/extract_timing.py                          ← Timing extraction tool
/scripts/README.md                                  ← Tool documentation
```

---

## 17 Criteria by Grade

### Grade 1: Misconduct
- 1.1 Rudeness/profanity

### Grade 2: Service Failures
- 2.1 Call dropout/refusal

### Grade 3: Serious Problems
- 3.1 Unresolved request
- 3.3 Confidential info disclosure
- 3.6 Unverified information

### Grade 4: Customer Handling
- 4.1 Difficult customer (partial detection)

### Grade 5: Information
- 5.1 Incomplete information

### Grade 6: Critical Issues
- 6.1 Critical silence/hangup

### Grade 7: Protocol Compliance
- 7.1 Script violations
- 7.2 Echo method not used (CRITICAL)
- 7.3 5-second timing rules
- 7.4 Interruption without apology

### Grade 9: Search Quality
- 9.1 Long search (>45s VIOLATION, 40-45s FLAG)
- 9.3 No thank you

### Grade 10: Baseline Quality
- 10.2 Script work
- 10.3 Dialogue management
- 10.6 Information completeness

---

## Data Files Per Call

Each call has:
- transcript-2.vtt (3-23 KB)
- transcript-2.srt (3-23 KB)
- paragraphs-2.json (35-273 KB)
- sentences-2.json (41-309 KB)
- timestamps-2.json (23-184 KB) ← For 7.2 (echo method)
- CALL_XX_TASK.md (1-3 KB)

---

## Golden Dataset Status

| Metric | Value |
|--------|-------|
| High confidence calls | 12/20 (60%) |
| Medium confidence calls | 8/20 (40%) |
| Target for golden set | 18/20 (90%) |
| BLIND2 coverage | 17/20 (85%) |
| Missing BLIND2 | Calls 3, 4, 5 |

---

## Key Findings

1. **Echo Method (7.2)**: Most common violation; requires word-level timing
2. **Search Timing (9.1)**: Graders disagree on measurement; needs tool assistance
3. **Sonnet accuracy**: Good on comprehension, poor on timing precision
4. **Tool need**: Extract_timing.py shows 50-60% success; others needed

---

## Next Phase Tasks

1. Build 5 CLI tools (extract_timing.py is tool #1)
2. Create Sonnet SOP with tool integration
3. Re-grade calls with tool assistance
4. Target: Reach 18/20 high-confidence labels (90%)

---

## File Statistics

- **Total files**: ~170
- **Config files**: 4
- **Doc files**: 5
- **Call data**: 20 directories
- **Gradings**: 80 JSON files (20+20+20+17)
- **Analysis files**: 8 (JSON + CSV + HTML)
- **Scripts**: 2

---

## Most Important Files to Review First

1. `/docs/PHASE1_SCOPE.md` - Start here
2. `/config/phase1_grading_config.json` - Criteria definitions
3. `/phase1_analysis/PHASE1_GOLDEN_REVIEW_TASK.md` - Understand what was done
4. `/phase1_consolidated/analysis_3way_per_call.json` - See disagreements
5. `/phase1_analysis/TOOL_SPECIFICATIONS.md` - Roadmap for improvements

---

**For detailed exploration**: See `REPOSITORY_MAP.md` (483 lines, complete inventory)
