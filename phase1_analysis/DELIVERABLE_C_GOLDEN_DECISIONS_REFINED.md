# Deliverable C: Refined Golden Decision Proposals
## Per-Call Golden Dataset Recommendations

**Author**: Expert Reviewer
**Date**: 2025-11-19
**Methodology**:
- Reviewed current golden decisions in `sonnet_haiku_blind_core_decisions.json`
- Analyzed 3-way comparison patterns in `analysis_3way_per_call.json`
- Sampled transcript gradings for calls with disagreements
- Applied criteria: Agreement on **core fields** (final_grade, 7.1, 7.2, 7.3, 9.1, 9.3) + **high overall field agreement**

---

## Executive Summary

**Current State**:
- 3/20 calls (15%) marked as "Sonnet" golden source (calls 03, 04, 05)
- 1/20 calls (5%) marked as "BLIND" golden source (call 15)
- 1/20 calls (5%) marked as "Sonnet" with high confidence (call 18)
- 15/20 calls (75%) marked as "none" (low confidence)

**Refined Proposal**:
- **5 calls** → High-confidence golden labels (Sonnet or BLIND consensus)
- **8 calls** → Medium-confidence golden labels (pending spec clarification on fragile fields)
- **7 calls** → Defer or exclude (significant disagreements on core fields)

**Key Finding**: Most "none" calls have disagreements on **fragile fields 9.1 and 9.3** (identified in Deliverable B). After implementing spec fixes from Deliverable A, these calls should be re-evaluated.

---

## Golden Decision Framework

### Core Fields Definition
Based on analysis, I recommend **expanding** the "core fields" definition:

**Tier 1 (Critical Core)**: Must agree for golden label
- final_grade
- 7.2 (Echo method - VERY_HIGH confidence, protocol violation)

**Tier 2 (Important Core)**: Should agree, but acceptable disagreement if spec ambiguous
- 9.1, 9.3 (Fragile fields - will stabilize after spec fix)
- 7.1, 7.3, 7.4 (Protocol violations - high stability observed)

**Tier 3 (Secondary)**: Can disagree without disqualifying golden label
- 3.1 (Spec acknowledges MEDIUM confidence, borderline cases expected)
- 4.1 (Spec acknowledges LOW confidence, text-only limitation)
- risk_* fields (Derivative of criteria assessments, not primary)
- final_confidence (Calibration difference, not factual disagreement)

**Rationale**: Focus on objective, high-confidence criteria that will form the basis of future training. Exclude criteria with known ambiguities until spec is fixed.

---

## Refined Golden Decisions by Call

### Group A: High Confidence Golden Labels (5 calls)

#### call_03, call_04, call_05
**Current Decision**: Sonnet (medium confidence)
**Refined Decision**: **Sonnet (high confidence)** ✓ KEEP

**Evidence**:
- Sonnet and BLIND1 agree on ALL core fields
- Overall Sonnet vs BLIND1 match rate: ≥95.5%
- No BLIND2 run (not needed due to high agreement)

**Rationale**: Perfect agreement on core fields justifies high confidence. These calls can be used as calibration examples.

**Usage Recommendation**:
- call_03: Use for few-shot examples of clear PASS on all criteria
- call_04: Use for script compliance (7.1) examples
- call_05: Use for timing compliance (7.3) examples

---

#### call_18
**Current Decision**: Sonnet (high confidence)
**Refined Decision**: **Sonnet (high confidence)** ✓ KEEP

**Evidence**:
- final_grade: S=10, B1=10, B2=10 (all agree)
- 7.2: All agree PASS
- 9.1, 9.3: All agree PASS
- Only disagreement: 3.1 (B1=BORDERLINE, S/B2=PASS), 4.1 (Sonnet=N/A, BLIND=PASS)

**Rationale**: Core fields agreement is perfect. 3.1 and 4.1 are Tier 3 (acceptable disagreement). This is a clean "Grade 10 / no violations" call.

**Usage Recommendation**:
- Use as few-shot example of "excellent call, no violations"
- Baseline for comparison with violation-containing calls

---

#### call_15
**Current Decision**: BLIND (medium confidence)
**Refined Decision**: **BLIND consensus (high confidence)** ✓ UPGRADE

**Evidence**:
- final_grade: S=10, B1=7, B2=7 (BLIND consensus)
- BLIND1 and BLIND2 agree on core violation: 7.2 (echo method)
- Sonnet marked 7.2 as PASS (outlier)
- Only other disagreement: 4.1 (Sonnet=N/A, BLIND=PASS), final_confidence

**Rationale**:
- BLIND consensus on 7.2 violation is strong evidence (2 independent graders vs 1)
- 7.2 is VERY_HIGH confidence criterion - should be reliable
- Sonnet may have missed echo violation; BLIND graders caught it
- Upgrade from medium to high confidence justified by BLIND consensus pattern

**Usage Recommendation**:
- Use as few-shot example of 7.2 (echo method) violation
- Demonstrates importance of BLIND consensus when Sonnet outlier occurs

**Action Required**: Manually review call_15 transcript to verify 7.2 violation before using as golden exemplar.

---

### Group B: Medium Confidence Golden Labels (8 calls)
**Pending spec clarification on 9.1 and 9.3**

These calls have disagreements primarily on fragile fields (9.1, 9.3) but agreement on Tier 1 core fields.

#### call_01
**Current Decision**: none (low)
**Refined Decision**: **Sonnet (medium, pending spec fix)** 🔄 UPGRADE CONDITIONAL

**Evidence**:
- final_grade: S=7, B1=10, B2=7 (Sonnet/BLIND2 consensus = Grade 7)
- 7.2: S=VIOLATION, B1=PASS, B2=VIOLATION (Sonnet/BLIND2 consensus)
- 9.1: S=BORDERLINE, B1=PASS, B2=BORDERLINE (Sonnet/BLIND2 consensus)
- 9.3: S=VIOLATION, B1=PASS, B2=PASS (Sonnet outlier)
- Overall: Sonnet and BLIND2 agree on 17/22 fields (77%)

**Rationale**:
- Sonnet/BLIND2 consensus on **7.2 violation** (most important criterion)
- BLIND1 marked 7.2 as PASS due to "conservative assessment" of partial echo
- Deliverable A identified this as spec ambiguity (partial echo policy)
- After implementing Fix 3.1 (all-or-nothing echo policy), expect BLIND1 to align with Sonnet/BLIND2

**Recommended Action**:
1. **Immediate**: Mark as "Sonnet (medium confidence)" for core fields 7.2, 9.1
2. **After spec fix**: Re-run BLIND grader on call_01 with clarified 7.2 policy
3. **If BLIND aligns**: Upgrade to "Sonnet (high confidence)"

**Usage Recommendation**:
- Use as 7.2 violation example (partial echo scenario)
- Use as 9.1 borderline (40-45s flag window) example

---

#### call_02, call_06
**Current Decision**: none (low)
**Refined Decision**: **Sonnet (medium, pending spec fix)** 🔄 UPGRADE CONDITIONAL

**Evidence**:
- final_grade: All agree on Grade 7
- Core violations: All agree on primary violations
- Disagreements: Only on 4.1 (Tier 3), final_confidence, and minor risk fields

**Rationale**: Near-perfect core field agreement. 4.1 and confidence disagreements are expected per spec.

**Recommended Action**: Mark as "Sonnet (medium)" immediately, upgrade to "high" after spot-check.

---

#### call_09, call_10
**Current Decision**: none (low)
**Refined Decision**: **Sonnet (medium, pending 9.1/9.3 spec fix)** 🔄 UPGRADE CONDITIONAL

**Evidence** (identical pattern for both calls):
- final_grade: S=7, B1=10, B2=7 (Sonnet/BLIND2 consensus)
- 7.2: S=VIOLATION, B1=PASS, B2=VIOLATION (Sonnet/BLIND2 consensus)
- 9.1: S=BORDERLINE, B1=PASS, B2=BORDERLINE (Sonnet/BLIND2 consensus)
- Overall agreement: 18/22 fields (82%)

**Rationale**: Pattern mirrors call_01. BLIND1 outlier on 7.2, Sonnet/BLIND2 consensus strong.

---

#### call_16, call_17, call_19
**Current Decision**: none (low)
**Refined Decision**: **Sonnet (medium)** 🔄 UPGRADE

**Evidence**:
- High overall agreement (86-91% all_equal fields)
- Disagreements limited to 9.1, 9.3, or Tier 3 fields
- Core Tier 1 fields: Agreement

**Rationale**: These calls have very high stability overall. Safe to use as golden with medium confidence.

---

### Group C: Defer or Exclude (7 calls)
**Significant disagreements on core fields, or fragile field dominance**

#### call_07, call_08, call_11, call_12, call_13, call_14, call_20
**Current Decision**: none (low)
**Refined Decision**: **DEFER pending spec fix, then re-evaluate** ⏸️

**Evidence**:
- Primary disagreements on 9.1 and/or 9.3 (fragile fields)
- Some have "all_different" pattern (call_13 on 9.1)
- BLIND2 outliers on multiple fields (call_08: 5 fields, call_11: 3 fields)

**Rationale**:
- These calls expose the exact spec ambiguities identified in Deliverable A
- Cannot assign golden label until 9.1/9.3 spec is clarified
- BLIND2 outliers suggest call-specific complexity (e.g., multiple searches, edge cases)

**Recommended Action**:
1. **Implement Deliverable A spec fixes** (9.1, 9.3 clarifications)
2. **Re-run all 3 graders** on these 7 calls with updated prompt
3. **Re-evaluate golden decisions** after observing new agreement rates

**Do NOT use** these calls for few-shot examples until re-evaluation complete.

---

## Summary Table: Refined Golden Decisions

| Call ID | Current | Refined Decision | Confidence | Rationale | Action |
|---------|---------|------------------|------------|-----------|--------|
| call_01 | none | Sonnet | Medium→High | Sonnet/B2 consensus on 7.2 | Upgrade conditional on spec fix |
| call_02 | none | Sonnet | Medium | High core agreement | Upgrade |
| call_03 | Sonnet | Sonnet | High | Perfect agreement | Keep |
| call_04 | Sonnet | Sonnet | High | Perfect agreement | Keep |
| call_05 | Sonnet | Sonnet | High | Perfect agreement | Keep |
| call_06 | none | Sonnet | Medium | High core agreement | Upgrade |
| call_07 | none | DEFER | — | 9.1/9.3 fragile | Re-evaluate after spec fix |
| call_08 | none | DEFER | — | Multiple B2 outliers | Re-evaluate after spec fix |
| call_09 | none | Sonnet | Medium→High | S/B2 consensus pattern | Upgrade conditional |
| call_10 | none | Sonnet | Medium→High | S/B2 consensus pattern | Upgrade conditional |
| call_11 | none | DEFER | — | 9.3 fragile, B2 outliers | Re-evaluate after spec fix |
| call_12 | none | DEFER | — | 9.3 fragile, B2 outliers | Re-evaluate after spec fix |
| call_13 | none | DEFER | — | 9.1 all_different | Re-evaluate after spec fix |
| call_14 | none | DEFER | — | 9.1/9.3 fragile | Re-evaluate after spec fix |
| call_15 | BLIND | BLIND consensus | High | B1/B2 agree on 7.2 violation | Upgrade confidence |
| call_16 | none | Sonnet | Medium | 91% agreement | Upgrade |
| call_17 | none | Sonnet | Medium | 86% agreement | Upgrade |
| call_18 | Sonnet | Sonnet | High | Perfect core agreement | Keep |
| call_19 | none | Sonnet | Medium | 86% agreement | Upgrade |
| call_20 | none | DEFER | — | 9.1/9.3 fragile, mixed outliers | Re-evaluate after spec fix |

**Summary**:
- **High confidence golden**: 5 calls (25%) — Usable immediately for training/calibration
- **Medium confidence golden**: 8 calls (40%) — Usable with caveats, upgrade after spec fix
- **Deferred**: 7 calls (35%) — Re-evaluate after spec fix

---

## Validation Protocol for Medium Confidence Calls

Before using medium-confidence golden calls for training:

### Step 1: Spot-Check Review (Manual)
For each medium-confidence call, human expert should:
1. Read transcript
2. Verify core field assessments (final_grade, 7.2, 7.1)
3. Confirm golden source choice aligns with Phase 1 spec intent
4. Flag any concerns for team discussion

**Time estimate**: 30 minutes per call × 8 calls = 4 hours

### Step 2: Cross-Validation (Automated)
After spec fixes implemented:
1. Re-run Sonnet and BLIND graders on all 8 medium-confidence calls
2. Measure agreement improvement on 9.1, 9.3
3. If agreement >85%, upgrade to high confidence
4. If agreement <70%, move to deferred group

**Time estimate**: 1 hour compute + 1 hour analysis

### Step 3: Inter-Rater Reliability Test (Human QA)
Sample 3 calls from medium-confidence group:
1. Have 2 independent human QA specialists grade same calls
2. Measure human vs Sonnet vs BLIND agreement
3. If human agreement with chosen golden source >90%, validate
4. If human agreement <75%, investigate call-specific issues

**Time estimate**: 2 hours per specialist × 2 specialists = 4 hours

**Total validation time**: ~10 hours

---

## Usage Recommendations for Golden Dataset

### Tier 1 Exemplars (High Confidence, Immediately Usable)

**Perfect PASS examples**:
- call_03, call_04, call_05, call_18: Use for "baseline quality" demonstrations
- Few-shot example: "Here's a call with no violations, Grade 10"

**7.2 Violation examples**:
- call_15 (BLIND consensus): Echo method violation
- Few-shot example: "Name/phone/city collected, but not all echoed with confirmation → VIOLATION"

### Tier 2 Exemplars (Medium Confidence, Use with Caveats)

**7.2 Violation (partial echo pattern)**:
- call_01, call_09, call_10: Partial echo scenarios
- Few-shot example: "Phone echoed correctly, but name/city not echoed → VIOLATION per all-or-nothing policy"

**9.1 Borderline (40-45s flag window)**:
- call_01, call_09, call_10: Use for demonstrating flag vs violation distinction
- Few-shot example: "Search duration 42s → Grade 10 with flag, not Grade 9"

### Tier 3 Exemplars (Deferred, Do Not Use Yet)

**Edge cases for 9.1/9.3**:
- call_07, call_08, call_13: Multiple searches, complex timing scenarios
- **Wait until spec clarified**, then use as advanced examples

---

## Recommended Next Steps

### Immediate (This Week)
1. ✅ **Accept high-confidence golden labels** for calls 03, 04, 05, 15, 18
2. 📝 **Update `sonnet_haiku_blind_core_decisions.json`** with refined decisions
3. 🔍 **Manual spot-check call_15** to verify BLIND consensus on 7.2 violation

### Short-term (Next 2 Weeks)
4. 📋 **Implement Deliverable A spec fixes** for 9.1, 9.3, 7.2
5. 🔄 **Re-run graders** on 7 deferred calls with updated spec
6. ✅ **Validate medium-confidence calls** (8 calls) using protocol above
7. 📊 **Measure agreement improvement** after spec fixes

### Long-term (Next Month)
8. 🎓 **Build training dataset** using 13 high+medium confidence calls
9. 🧪 **Test revised prompt** (Deliverable D) on held-out validation set
10. 📈 **Monitor production grading** for continued agreement with golden labels

---

## Acceptance Criteria for Golden Dataset Finalization

Before declaring the golden dataset "production-ready":

**Minimum Requirements**:
- ✅ 10+ calls with high confidence golden labels (currently: 5, target: 13)
- ✅ Core field agreement >85% on high-confidence calls (currently: 95%+)
- ✅ Spec ambiguities in 9.1, 9.3, 7.2 resolved (pending Deliverable A implementation)

**Stretch Goals**:
- 🎯 15+ calls with high confidence (75% of 20-call dataset)
- 🎯 Core field agreement >90% across all golden calls
- 🎯 Independent human QA validation of sample calls

**Current Status**: 5/20 high-confidence (25%) → **Need spec fix + re-evaluation to reach 13/20 (65%)**

---

## Conclusion

The current golden dataset has a **strong foundation** with 5 high-confidence calls showing near-perfect agreement. An additional 8 calls can achieve high confidence **after spec fixes** (Deliverable A) are implemented.

**Key insight**: The 15 "none" (low confidence) calls are NOT fundamentally problematic - they simply expose **known spec ambiguities** in criteria 9.1 and 9.3. Once these are resolved, we expect 8 of these calls to become golden-worthy, bringing the total to **13/20 (65%) high-confidence golden labels**.

**Critical path**:
1. Implement spec fixes (Deliverable A)
2. Re-run graders on deferred calls
3. Validate medium-confidence calls
4. Finalize golden dataset for production use

**Timeline**: 2-3 weeks from spec fix implementation to golden dataset finalization.
