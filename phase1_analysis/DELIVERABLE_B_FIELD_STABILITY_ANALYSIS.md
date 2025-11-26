# Deliverable B: Field Stability Analysis
## Phase 1 Golden Dataset Expert Review

**Author**: Expert Reviewer
**Date**: 2025-11-19
**Scope**: 17 calls with 3-way comparison (Sonnet, BLIND1, BLIND2)
**Data Source**: `phase1_consolidated/summary_3way_field_stats.json`

---

## Executive Summary

Out of 22 key fields analyzed across 17 calls (call_01, call_02, call_06–call_20), we identified **5 fragile fields** with agreement rates below 60%, while 13 fields achieved perfect (100%) agreement. The most unstable field is **9.1 (Long Search)** with only 41% agreement, followed by **9.3 (Thank You for Waiting)** at 47%.

---

## Field Stability Ranking

### Tier 1: Perfect Stability (100% Agreement) — 13 Fields

All three graders (Sonnet, BLIND1, BLIND2) agree on every single call for these criteria:

| Rank | Field | Agreement % | Notes |
|------|-------|-------------|-------|
| 1 | 1.1 (Rudeness/Profanity) | 100.0% | Text-based detection, no ambiguity |
| 1 | 2.1 (Call Dropout/Refusal) | 100.0% | Clear binary outcome |
| 1 | 3.3 (Confidential Info) | 100.0% | Keyword-based detection |
| 1 | 3.6 (Unverified Info) | 100.0% | Search cue detection |
| 1 | 5.1 (Incomplete Info) | 100.0% | Information completeness |
| 1 | 6.1 (Critical Silence) | 100.0% | Objective timing + hangup pattern |
| 1 | 7.3 (5-Second Timing) | 100.0% | Objective timestamp arithmetic |
| 1 | 7.4 (Interruption) | 100.0% | Clear overlap + apology detection |
| 1 | 10.2 (Script Work) | 100.0% | Script compliance clear |
| 1 | 10.3 (Dialogue Management) | 100.0% | Conversation flow indicators |
| 1 | 10.6 (Info Completeness) | 100.0% | Baseline quality assessment |

**Interpretation**: These fields have clear, unambiguous detection criteria. The grading prompts work well for these.

---

### Tier 2: Very High Stability (90–99% Agreement) — 1 Field

| Rank | Field | Agreement % | Outliers | Notes |
|------|-------|-------------|----------|-------|
| 14 | 7.1 (Script Violations) | 94.1% | 1 BLIND1 outlier | Nearly perfect, minor interpretation variance |

**Interpretation**: 7.1 has just one disagreement case (call_17), likely a borderline greeting/closing format judgment.

---

### Tier 3: High Stability (70–89% Agreement) — 3 Fields

| Rank | Field | Agreement % | Outlier Pattern | Notes |
|------|-------|-------------|-----------------|-------|
| 15 | final_grade | 76.5% | 3 BLIND1, 1 BLIND2 | Grade depends on underlying criteria |
| 16 | risk_customer_satisfaction | 76.5% | 4 BLIND2 outliers | Risk scoring variance |
| 17 | 7.2 (Echo Method) | 70.6% | 3 BLIND1, 2 BLIND2 | **Critical** - see fragile analysis |
| 18 | risk_data_security | 70.6% | 5 Sonnet outliers | Sonnet more conservative |

**Interpretation**: 7.2 (Echo Method) is supposed to be "VERY_HIGH" confidence but shows 30% disagreement. This indicates a **spec/prompt issue** (see Section 3).

---

### Tier 4: Moderate Stability (50–69% Agreement) — 3 Fields

| Rank | Field | Agreement % | Outlier Pattern | Notes |
|------|-------|-------------|-----------------|-------|
| 19 | final_confidence | 52.9% | 4 Sonnet, 3 BLIND1, 1 BLIND2 | Confidence calibration differs |
| 20 | 3.1 (Unresolved Request) | 52.9% | 8 BLIND1 outliers | **Borderline cases** - spec flagged this as MEDIUM confidence |
| 21 | 4.1 (Difficult Customer) | 52.9% | 8 Sonnet outliers | **Text-only limitation** - Sonnet more cautious |
| 22 | risk_compliance | 52.9% | 3 BLIND1, 5 BLIND2 | Risk aggregation logic differs |

**Interpretation**: These fields have expected variability (3.1, 4.1 are flagged as MEDIUM/LOW confidence in spec). However, the high disagreement rate validates the spec's caution.

---

### Tier 5: **FRAGILE** Fields (<50% Agreement) — 2 Fields ⚠️

| Rank | Field | Agreement % | Outlier Pattern | Impact |
|------|-------|-------------|-----------------|--------|
| **23** | **9.3 (No Thank You)** | **47.1%** | 1 Sonnet, 6 BLIND1, 2 BLIND2 | **HIGH** - Grade 9 violation |
| **24** | **9.1 (Long Search)** | **41.2%** | 6 BLIND1, 3 BLIND2, 1 all_different | **VERY HIGH** - Grade 9 violation |

**Critical Issue**: 9.1 and 9.3 are supposed to be "HIGH confidence" auto-gradable criteria, yet they show the **worst agreement rates** of all 22 fields. This is the **#1 priority for prompt/spec improvement**.

---

## Top 5 Fragile Fields — Detailed Analysis

### 1. 9.1 (Long Information Search) — 41% Agreement ⚠️⚠️⚠️

**Agreement**: Only 7/17 calls (41%) had full agreement
**Disagreements**:
- BLIND1 outlier: 6 calls (35%) — BLIND1 sees violation where Sonnet/BLIND2 see PASS
- BLIND2 outlier: 3 calls (18%) — BLIND2 sees violation where others see PASS
- All different: 1 call (6%) — All three graders disagree

**Root Cause**:
1. **Ambiguous timing boundaries**: When does search "start" and "end"?
   - Is it from "Минутку" to first word of answer?
   - Or from "Минутку" to complete answer delivery?
   - Do check-ins to customer reset the timer? (Spec says NO, but graders interpret differently)

2. **40-45s flag window confusion**: Graders unclear whether 42s is PASS, FLAG, or VIOLATION
   - Spec says: 40-45s = flag only, no score reduction
   - But what grade to assign? Grade 9 with note, or Grade 10?

3. **"Complex question" threshold unclear**: When is 40s vs 3s threshold applied?
   - Spec says "standard question" = 3s, "complex/database" = 40s
   - Graders disagree on classification

**Link to Spec Weakness**:
- `PHASE1_SCOPE.md` line 48-50: "40-45s FLAG for improvement (NO score reduction)" — but how to represent in final_grade?
- `prompt_for_transcript_only_grading.txt` line 61-70: Timing rules explained, but edge cases (check-ins, borderline cases) not clarified

---

### 2. 9.3 (No Thank You for Waiting) — 47% Agreement ⚠️⚠️

**Agreement**: Only 8/17 calls (47%) had full agreement
**Disagreements**:
- BLIND1 outlier: 6 calls (35%) — BLIND1 sees PASS where others see VIOLATION
- BLIND2 outlier: 2 calls (12%) — BLIND2 sees VIOLATION where others see PASS
- Sonnet outlier: 1 call (6%) — Sonnet sees VIOLATION where BLIND graders see PASS

**Root Cause**:
1. **Gratitude phrase variants not enumerated**: What counts as "thank you for waiting"?
   - Explicit: "Спасибо за ожидание" ✓
   - Implicit: "Вот, нашёл информацию" — does this count? ❓
   - Embedded: "Спасибо, что подождали, вот..." ✓ or ❓?

2. **Multiple searches in one call**: Which search needs gratitude?
   - If operator searches 3 times, must they thank customer 3 times?
   - Or just after the longest search?

3. **Search duration threshold for 9.3**: Does 9.3 apply to ALL searches, or only >40s searches?
   - Spec says: "Required even if operator checked in during search"
   - But does it apply to 5-second searches too?

**Link to Spec Weakness**:
- `Quick_Reference_Grades_EN_PHASE1.md` line 60: "Not thanking customer for waiting after information search completion"
- No examples of acceptable gratitude phrases
- No clarification of short vs long search requirements

---

### 3. 7.2 (Echo Method Not Used) — 71% Agreement ⚠️

**Agreement**: Only 12/17 calls (71%) — **CRITICAL** because spec says this should be "VERY_HIGH" confidence
**Disagreements**:
- BLIND1 outlier: 3 calls (18%) — BLIND1 sees PASS where Sonnet/BLIND2 see VIOLATION
- BLIND2 outlier: 2 calls (12%) — BLIND2 sees VIOLATION where others see PASS

**Root Cause**:
1. **"Partial echo" interpretation**: What if operator repeats data but doesn't ask "Верно?"?
   - Example (call_01): Operator says "Алексей, из какого города..." (uses name) but never asks "Верно?"
   - BLIND1 marked this PASS ("partial echo, conservative assessment")
   - Sonnet/BLIND2 marked VIOLATION ("no confirmation requested")

2. **Which contact data requires echo?**: Spec says "name, phone, address, email" — but:
   - Does "city" count as address? (call_01 disagreement suggests yes)
   - Does "first name only" require echo, or just "full name"?
   - What about "company name" if customer is B2B?

3. **Confirmation timing window**: Within how many seconds must operator ask for confirmation?
   - Spec says 10s window for echo
   - But does the confirmation request itself have a time limit?

**Link to Spec Weakness**:
- `prompt_for_transcript_only_grading.txt` line 28-33: Echo method described as "repeat back AND ask for confirmation"
- Example given is phone number, but name/city examples missing
- "Partial echo" scenario not addressed (what if 2/3 contact fields are echoed correctly?)

---

### 4. 3.1 (Unresolved Customer Request) — 53% Agreement

**Agreement**: Only 9/17 calls (53%)
**Disagreements**:
- BLIND1 outlier: 8 calls (47%) — BLIND1 sees VIOLATION where Sonnet/BLIND2 see PASS

**Root Cause**:
1. **Workaround vs full resolution**: When customer has a systemic issue (e.g., "website broken"), is a manual workaround sufficient?
   - Sonnet/BLIND2: YES, immediate need met = PASS
   - BLIND1: NO, root cause not fixed = VIOLATION

2. **Customer satisfaction vs technical resolution**: If customer says "thank you" and hangs up satisfied, but the original problem remains unsolved, is this a violation?

3. **Partial resolution**: If 2 out of 3 customer questions answered, is this PASS or VIOLATION?

**Link to Spec Weakness**:
- `Quick_Reference_Grades_EN_PHASE1.md` line 179-188: "Customer request not resolved by end of call"
- Spec notes "borderline cases need manager review" but doesn't provide clear workaround/resolution distinction
- This is correctly flagged as MEDIUM confidence, so high disagreement is expected

---

### 5. 4.1 (Difficult Customer Handling) — 53% Agreement

**Agreement**: Only 9/17 calls (53%)
**Disagreements**:
- Sonnet outlier: 8 calls (47%) — Sonnet sees VIOLATION where BLIND graders see PASS

**Root Cause**:
1. **Text-only limitation**: Spec says this criterion needs audio for full assessment (tone, frustration)
   - Sonnet appears to detect text patterns ("operator shows frustration") more aggressively
   - BLIND graders mark PASS unless text evidence is overwhelming

2. **What counts as "cannot handle"?**: Spec lists types (rude, talkative, slow, rushed customers) but:
   - How does operator "show" they can't handle customer in text?
   - Sonnet may be inferring from conversation length, repeated questions, etc.
   - BLIND graders require explicit operator frustration language

**Link to Spec Weakness**:
- `PHASE1_SCOPE.md` line 120-124: "Text shows behavior indicators, full assessment needs audio"
- `confidence_thresholds.json` line 154-155: Confidence=LOW, action=FLAG_ONLY
- Spec correctly flags this as LOW confidence, so disagreement is acceptable
- However, Sonnet's high outlier rate (47%) suggests prompt should emphasize "don't penalize without clear text evidence"

---

## Summary Table: Fragile Fields and Spec Weaknesses

| Field | Agreement % | Primary Issue | Spec/Prompt Gap |
|-------|-------------|---------------|-----------------|
| **9.1** | **41%** | Timing boundaries unclear; flag window confusion | Need examples of start/end timestamps; clarify 40-45s grading |
| **9.3** | **47%** | Gratitude phrase variants undefined | Need enumerated list of acceptable phrases; multi-search clarification |
| **7.2** | **71%** | "Partial echo" scenario; contact data scope | Need name/city examples; define "partial echo" handling |
| 3.1 | 53% | Workaround vs resolution; partial answers | Add examples of borderline cases (expected per spec) |
| 4.1 | 53% | Text-only over-detection by Sonnet | Emphasize "don't penalize without clear evidence" |

---

## Recommendations

### Priority 1: Fix 9.1 and 9.3 (Grade 9 criteria)
These are supposed to be HIGH confidence auto-gradable, but show worst agreement. **Must fix before golden dataset finalization.**

**Actions**:
1. Add 3-5 real transcript examples to prompt showing:
   - 9.1: Clear start/end timestamps for search duration
   - 9.1: How to handle check-ins (don't reset timer)
   - 9.1: How to grade 40-45s cases (Grade 10 with flag, not Grade 9)
   - 9.3: Enumerated list of acceptable gratitude phrases
   - 9.3: Multi-search scenario (thank after each >10s search)

2. Revise `prompt_for_transcript_only_grading.txt` lines 61-75 with explicit edge case handling

---

### Priority 2: Clarify 7.2 (Echo Method)
Currently at 71% agreement despite being "VERY_HIGH confidence" criterion.

**Actions**:
1. Add examples for name/city/email echo (not just phone)
2. Define "partial echo" policy: If 2/3 contact fields echoed, is this PASS or VIOLATION?
3. Clarify confirmation timing: Must operator ask "Верно?" within 10s of repeat?

---

### Priority 3: Accept 3.1 and 4.1 variability
These are correctly flagged as MEDIUM/LOW confidence. High disagreement is expected and acceptable.

**Actions**:
1. Ensure prompt emphasizes "flag for review, don't auto-grade" for these criteria
2. Consider excluding 3.1 and 4.1 from "core fields" for golden dataset consensus

---

## Conclusion

**13/22 fields (59%)** are perfectly stable (100% agreement), indicating the Phase 1 grading system is fundamentally sound for most criteria.

**2/22 fields (9%)** — 9.1 and 9.3 — are severely fragile and **must be addressed** before golden dataset can be finalized. These are Protocol Violations (Grade 9) that should have HIGH confidence but show <50% agreement, undermining the entire grading system's reliability.

**Immediate next step**: Use Deliverable D to propose revised prompt structure with few-shot examples specifically targeting 9.1, 9.3, and 7.2.
