# Deliverable A: Phase 1 Specification Assessment
## Ambiguities, Inconsistencies, and Recommended Improvements

**Author**: Expert Reviewer
**Date**: 2025-11-19
**Documents Reviewed**:
- `docs/PHASE1_SCOPE.md`
- `docs/Quick_Reference_Grades_EN_PHASE1.md`
- `config/prompt_for_transcript_only_grading.txt`
- `config/phase1_grading_config.json`
- `config/confidence_thresholds.json`

**Key Finding**: The Phase 1 specification is well-structured overall, but **5 critical ambiguities** in criteria 7.2, 9.1, 9.3, and 4.1 directly cause the 40-50% disagreement rates observed in the 3-way grader comparison.

---

## Critical Ambiguities (Must Fix)

### 1. Criterion 9.1 (Long Information Search) ⚠️⚠️⚠️

**Current Spec** (`PHASE1_SCOPE.md` lines 45-50):
```
**9.1 - Long Information Search**
- Standard questions: Answer within 3 seconds
- Complex questions: Answer within 40 seconds
- **40-45 seconds: FLAG for improvement (NO score reduction)**
- **>45 seconds: Score reduction applies**
- Timer: From "Сейчас посмотрю" to information delivery start
```

**Current Prompt** (`prompt_for_transcript_only_grading.txt` lines 61-70):
```
**9.1 - Long Information Search**
- Standard question answer within 3 seconds, complex/database lookup max 40 seconds.
  Timer START when operator announces search, END when operator begins delivering information.
  Returns to customer don't reset timer (total search duration counted).

**Thresholds**:
- 0-40s: PASS
- 40-45s: FLAG for improvement only (NO score reduction)
- >45s: VIOLATION (score reduction)
```

**Ambiguities Identified**:

1. **Timer endpoint ambiguous** ("information delivery start"):
   - Does this mean first word of answer ("Вот")?
   - Or first substantive word ("Размеры")?
   - Or complete sentence ("Вот, размеры следующие...")?
   - **Impact**: ±3-5 second variance in search duration calculation

2. **Check-in behavior unclear**:
   - Prompt says "don't reset timer" but doesn't explain HOW to measure if there are check-ins
   - Example: Operator says "Минутку" at 2:00, "Еще немного" at 2:30, delivers info at 2:50
     - Is this 50s total (violation)?
     - Or 20s since last check-in (pass)?
   - **Current wording suggests 50s total**, but graders interpreted both ways

3. **40-45s grading decision ambiguous**:
   - Spec says "NO score reduction" — but what final_grade to assign?
   - Option A: Grade 10 (no violation occurred) with note "flagged for improvement"
   - Option B: Grade 9 (violation code) with flag_window=true and score_reduction=false
   - **3-way comparison shows graders chose different options**

4. **Standard vs complex question classification missing**:
   - When is 3s threshold vs 40s threshold applied?
   - Examples:
     - "Сколько стоит доставка?" — standard (3s) or complex (40s)?
     - "Какие размеры у вас есть?" — requires database, so complex (40s)?
   - **No decision tree provided**

**Observed Disagreement Evidence**:
- Call_01: Sonnet=BORDERLINE(42s), BLIND1=PASS, BLIND2=BORDERLINE
- Call_13: All three graders gave DIFFERENT assessments (all_different pattern)
- **Field agreement: 41%** (worst of all 22 fields)

**Recommended Fixes**:

**Fix 1.1**: Add explicit timer endpoint definition
```markdown
**Timer Measurement**:
- START: First word of search announcement ("Минутку", "Сейчас посмотрю", "Подождите")
- END: First SUBSTANTIVE word of answer (not filler like "Вот", "Так", "Итак")
- Example:
  - [2:00] Op: "Минутку, пожалуйста" ← START
  - [2:35] Op: "Вот..." ← NOT end (filler word)
  - [2:37] Op: "Размеры следующие: 205/55/R16" ← END (substantive info)
  - Duration: 37 seconds (PASS)
```

**Fix 1.2**: Clarify check-in handling with example
```markdown
**Check-ins to Customer**:
Check-ins do NOT reset the timer. Total duration from first search announcement to final answer delivery is counted.

Example:
- [3:00] Op: "Минутку" ← Timer STARTS
- [3:30] Op: "Еще немного ищу" ← Check-in, timer continues
- [3:55] Op: "Нашел информацию: ..." ← Timer ENDS
- Total: 55 seconds (VIOLATION)

Note: Frequent check-ins improve customer experience but don't excuse >45s total search time.
```

**Fix 1.3**: Clarify 40-45s flag grading
```markdown
**40-45s Flag Window Grading**:
- Assign: final_grade = 10 (no violation occurred)
- Set: flag_window = true, requires_improvement = true
- Note: "Search duration 40-45s: flag for coaching, no score penalty"
- Coaching priority: "Medium" (not urgent, but track for pattern)

**>45s Violation Grading**:
- Assign: final_grade = 9 (violation applies)
- Set: score_reduction = true
- Coaching priority: "High" (immediate improvement needed)
```

**Fix 1.4**: Add standard vs complex decision tree
```markdown
**Question Classification**:
- **Standard (3s threshold)**: Simple factual questions operator should know
  - "Какой ваш адрес?", "Во сколько вы работаете?", "Какой номер для заказа?"
- **Complex (40s threshold)**: Requires database lookup, calculation, or system check
  - "Какие размеры шин у вас есть в наличии?"
  - "Сколько будет стоить доставка в Усть-Катав?"
  - "Когда ближайший слот для записи?"

If uncertain, use 40s threshold (conservative approach).
```

---

### 2. Criterion 9.3 (No Thank You for Waiting) ⚠️⚠️

**Current Spec** (`Quick_Reference_Grades_EN_PHASE1.md` lines 59-66):
```
**9.3 - No Thank You for Waiting**
**Rule**: Not thanking customer for waiting after information search completion,
even if operator returned to customer every 40 seconds during search

**Detection**: Look for "(спасибо|благодарю).*(ожидани|подождал|ждал)" within 5s after search
```

**Ambiguities Identified**:

1. **Acceptable gratitude phrases not enumerated**:
   - Explicit: "Спасибо за ожидание" ✓ (clear)
   - Implicit: "Вот, нашёл" — does this count? ❓
   - Embedded: "Спасибо, что подождали, вот результат" ✓ or ❓?
   - Abbreviated: "Спасибо за терпение" ✓ or ❓?
   - **Graders disagreed on what counts as "thank you"**

2. **Multiple searches in one call**:
   - If operator searches 3 times (10s, 25s, 45s), how many thank-yous required?
   - Spec says "after information search completion" — does this mean EVERY search?
   - Or only searches >10 seconds?
   - Or only the final/longest search?

3. **Search duration threshold for 9.3**:
   - Does 9.3 apply to ALL searches, or only >40s searches?
   - Example: 8-second search — must operator still thank customer?
   - **No guidance provided**

**Observed Disagreement Evidence**:
- Call_01: Sonnet=VIOLATION (no thank you), BLIND1=PASS, BLIND2=PASS
- Call_09: BLIND1 detected violation, Sonnet/BLIND2 did not
- **Field agreement: 47%** (2nd worst field)

**Recommended Fixes**:

**Fix 2.1**: Enumerate acceptable gratitude phrases
```markdown
**Acceptable "Thank You for Waiting" Phrases**:

**Explicit (always count)**:
- "Спасибо за ожидание"
- "Спасибо, что подождали"
- "Благодарю за терпение"
- "Спасибо за ваше время"

**Embedded (count if gratitude clear)**:
- "Спасибо, что дождались, вот информация" ✓
- "Благодарю, нашёл данные: ..." ✓

**NOT acceptable (do NOT count)**:
- "Вот" (no gratitude)
- "Нашёл" (no gratitude)
- "Итак, размеры следующие" (no gratitude)

**Detection Pattern**: (спасибо|благодарю).*(ожидани|подождал|ждал|терпение|время)
```

**Fix 2.2**: Clarify multi-search requirement
```markdown
**Multiple Searches in One Call**:

Operator must thank customer after EVERY search lasting >10 seconds.

**Example**:
- Search 1: 8 seconds → NO thank you required (too short)
- Search 2: 25 seconds → Thank you REQUIRED
- Search 3: 45 seconds → Thank you REQUIRED

**Violation occurs if**:
- Any search >10s completes WITHOUT gratitude within 5 seconds
- Even if operator thanked customer after other searches

**Rationale**: Each search inconveniences customer; each deserves gratitude.
```

**Fix 2.3**: Add detection examples to prompt
```markdown
**Detection Walkthrough**:

**PASS Example**:
[2:13] Operator: "Минутку, пожалуйста"
[2:26] Operator: "Спасибо за ожидание. Вот информация..."
→ 13s search, gratitude within 5s of info delivery ✓

**VIOLATION Example**:
[2:13] Operator: "Минутку"
[2:38] Operator: "Вот, размеры: 205/55/R16"
→ 25s search, NO gratitude ✗ VIOLATION

**PASS Example** (embedded gratitude):
[2:13] Operator: "Секунду"
[2:29] Operator: "Благодарю за терпение, нашёл: ..."
→ 16s search, embedded gratitude ✓
```

---

### 3. Criterion 7.2 (Echo Method Not Used) ⚠️

**Current Spec** (`prompt_for_transcript_only_grading.txt` lines 28-35):
```
**7.2 - Echo Method Not Used** ⭐ CRITICAL
- When recording contact data (name, phone, address, email), operator must:
  1. Repeat data back to customer
  2. Ask for explicit confirmation ("Верно?", "Правильно?", "Подтверждаете?")
  3. Wait for customer to confirm ("Да", "Верно", "Угу")
```

**Ambiguities Identified**:

1. **"Partial echo" scenario undefined**:
   - Call_01 example: Operator echoed phone (with "Верно?") but NOT name or city
   - BLIND1 marked PASS ("partial echo, conservative")
   - Sonnet/BLIND2 marked VIOLATION ("some contact data not echoed")
   - **Spec doesn't say: Is ANY unechoed contact field a violation, or only if ALL fields unechoed?**

2. **Which contact data requires echo?**:
   - Spec lists: "name, phone, address, email"
   - But what about:
     - First name only (vs full name)? Example: "Алексей" without "Калинин"
     - City (as part of address)? Example: "Усть-Катав"
     - Company name (B2B calls)?
   - **Call_01 disagreement was specifically about city echo**

3. **Confirmation timing window**:
   - Spec says operator must repeat "within 10 seconds"
   - But must the confirmation question ("Верно?") also be within 10s?
   - Or can operator repeat at 5s, then ask "Верно?" at 15s?

4. **Implicit confirmation**:
   - If operator repeats data and customer continues talking without objection, is this implicit confirmation?
   - Example: Op: "Алексей из Усть-Катава?" Customer: "Да, мне нужны шины..."
   - Is "Да" confirming the name/city, or just agreeing to continue?

**Observed Disagreement Evidence**:
- Call_01: Sonnet=VIOLATION, BLIND1=PASS, BLIND2=VIOLATION (name/city not echoed, only phone)
- Call_02: BLIND2=VIOLATION, Sonnet/BLIND1=PASS
- **Field agreement: 71%** (worse than expected for "VERY_HIGH confidence" criterion)

**Recommended Fixes**:

**Fix 3.1**: Define partial echo policy
```markdown
**Partial Echo Policy**:

Echo method is REQUIRED for EVERY contact data field separately.

**VIOLATION occurs if**:
- Operator collects contact data field (name, phone, city, email, etc.)
- AND fails to both (a) repeat it AND (b) ask for confirmation

**Example - VIOLATION** (Call_01 pattern):
Customer: "Алексей, из Усть-Катава, номер 912-778-1421"
Operator: "Алексей, из какого города вы звоните?" ← Uses name, doesn't confirm
Operator: "Ваш номер 912-778-1421, верно?" ← Confirms phone ✓
→ Name and city NOT echoed = VIOLATION (even though phone was echoed)

**All-or-nothing rule**: If operator collects 3 contact fields, ALL 3 must be echoed.
```

**Fix 3.2**: Enumerate contact data types requiring echo
```markdown
**Contact Data Requiring Echo Method**:

**Always require echo**:
- Phone number (mobile or landline)
- Full name (first + last) or any name components if collected
- Email address
- Full address (street, house, apartment)
- City (if collected as delivery/contact location)

**Do NOT require echo** (not "contact data"):
- Customer's question/request ("Мне нужны шины" — this is not contact data)
- Product details customer mentions ("205/55/R16" — not contact data, but product spec)
- Payment preference ("Оплата картой" — not contact data)

**Partial name handling**:
- If operator asks for first name only → echo first name
- If operator asks for full name → echo full name
- If customer volunteers both but operator only uses one → echo whichever operator records
```

**Fix 3.3**: Add city echo example (since this was the call_01 issue)
```markdown
**Example: City Echo** (common source of disagreement)

**CORRECT**:
Operator: "Из какого города звоните?"
Customer: "Усть-Катав"
Operator: "Усть-Катав, верно?"
Customer: "Да"
→ City echoed with confirmation ✓

**VIOLATION**:
Operator: "Из какого города?"
Customer: "Усть-Катав"
Operator: "Хорошо, Усть-Катав. Какие шины вам нужны?"
→ City repeated but NO confirmation question ("Верно?") ✗

**VIOLATION**:
Customer: "Я из Усть-Катава"
Operator: "Какие шины вам нужны?"
→ City not repeated at all ✗
```

**Fix 3.4**: Clarify confirmation timing
```markdown
**Echo Timing Requirements**:

After customer provides contact data:
- Operator must repeat it within 10 seconds
- Operator must ask confirmation ("Верно?") immediately after repeat (within same utterance or next utterance)
- Customer must confirm within 5 seconds

**Example of correct timing**:
[1:00] Customer: "912-778-1421"
[1:05] Operator: "Итак, ваш номер 912-778-1421, верно?" ← Within 10s ✓
[1:08] Customer: "Да" ← Within 5s of question ✓

**Violation timing example**:
[1:00] Customer: "912-778-1421"
[1:03] Operator: "Номер 912-778-1421" ← Repeats ✓
[1:15] Operator: "Верно?" ← Asks confirmation 15s after data, separated utterance ✗
```

---

### 4. Criterion 4.1 (Difficult Customer Handling) — Text Limitation

**Current Spec** (`PHASE1_SCOPE.md` lines 120-124):
```
**4.1 - Difficult Customer Handling**
- Cannot handle difficult customers
- Note: Text shows behavior indicators, full assessment needs audio
- Use text evidence only, note limitations
```

**Current Confidence** (`confidence_thresholds.json`):
```json
"4.1": {"confidence": "LOW", "action": "FLAG_ONLY",
        "rationale": "Text indicators partial, tone needs audio"}
```

**Ambiguities Identified**:

1. **What text evidence is sufficient?**:
   - Sonnet detected violations in 8 calls where BLIND graders saw none
   - What constitutes "cannot handle" in text?
     - Long pauses while customer talks?
     - Repeated questions?
     - Failure to redirect talkative customer?
   - **No examples given**

2. **Inconsistency between spec and prompt**:
   - Spec (PHASE1_SCOPE.md line 124): "Use text evidence where available, but acknowledge limitations"
   - Confidence thresholds: "FLAG_ONLY, don't penalize"
   - **These conflict**: Should grader FLAG (note indicators) or PENALIZE (mark as violation)?

**Observed Disagreement Evidence**:
- Sonnet marked VIOLATION in 8/17 calls
- BLIND1/BLIND2 marked PASS in same 8 calls
- **Field agreement: 53%** (Sonnet outlier in 47% of calls)

**Recommended Fixes**:

**Fix 4.1**: Strengthen "don't penalize" instruction
```markdown
**4.1 - Difficult Customer Handling (TEXT-ONLY LIMITATION)**

**IMPORTANT**: This criterion CANNOT be reliably assessed from transcript alone.
Tone, frustration, and emotional decline require audio analysis (Phase 3).

**For Phase 1 transcript-only grading**:
- DEFAULT: Mark as PASS unless overwhelming text evidence
- ONLY mark VIOLATION if operator explicitly states frustration:
  - "Я не могу вас понять, давайте закончим разговор"
  - "Вы мне мешаете, прекратите говорить"
  - Multiple unsuccessful redirect attempts with harsh language

**NOT sufficient for violation**:
- Long customer monologues (customer talkative ≠ operator failure)
- Operator asking questions multiple times (may be customer confusion, not operator failure)
- Long call duration (may indicate thorough service, not poor handling)

**Action for Phase 1**:
- Mark as PASS in criteria_assessment
- Add note in positive_observations if operator handled well
- If text shows frustration indicators, add to notes but don't reduce grade
```

**Fix 4.2**: Remove 4.1 from "core fields" consideration
```markdown
**Recommendation**: Exclude criterion 4.1 from "golden dataset core fields" until Phase 3
(audio analysis available). Current text-only assessment has LOW confidence and high
inter-rater disagreement, making it unsuitable for golden labels.
```

---

## Moderate Ambiguities (Should Fix)

### 5. Risk Field Calculations — Aggregation Logic Unclear

**Current Spec**: No explicit documentation of how risk fields are calculated from violations

**Observed Issue**:
- risk_compliance: 53% agreement (3 BLIND1 outliers, 5 BLIND2 outliers)
- risk_data_security: 71% agreement (5 Sonnet outliers)
- risk_customer_satisfaction: 76% agreement (4 BLIND2 outliers)

**Ambiguity**:
- Which criteria violations map to which risk category?
- Is risk calculated as:
  - MAX severity of violations in category?
  - COUNT of violations in category?
  - Weighted sum?

**Recommended Fix**:

```markdown
**Risk Assessment Calculation**:

**risk_compliance**: Based on criteria 7.1, 7.2, 7.3, 7.4, 3.3, 3.6
- HIGH: Any Grade 7 violation OR 2+ Grade 9 violations
- MEDIUM: Any Grade 9 violation OR 1 Grade 10 weakness
- LOW: All criteria PASS

**risk_data_security**: Based on criteria 3.3 (confidential info), 7.2 (echo method for phone/address)
- HIGH: Criterion 3.3 violation
- MEDIUM: Criterion 7.2 violation
- LOW: All PASS

**risk_customer_satisfaction**: Based on criteria 3.1, 6.1, 9.1, 9.3, 2.1
- HIGH: Criterion 6.1 or 2.1 violation (customer hung up / service refused)
- MEDIUM: Criteria 3.1 violation OR 9.1 >60s violation
- LOW: Minor 9.x violations or all PASS
```

---

### 6. Final Confidence Calculation — Not Documented

**Observed Issue**:
- final_confidence: 53% agreement (4 Sonnet, 3 BLIND1, 1 BLIND2 outliers)
- Graders assigning different confidence levels (VERY_HIGH vs HIGH) for identical violation patterns

**Ambiguity**:
- How is final_confidence derived from individual criterion confidences?
- When is final_confidence VERY_HIGH vs HIGH vs MEDIUM?

**Recommended Fix**:

```markdown
**Final Confidence Calculation**:

**VERY_HIGH** (0.95+):
- All violations detected have VERY_HIGH individual confidence (e.g., 7.2, 7.3)
- Objective, measurable violations only

**HIGH** (0.75-0.94):
- Mix of VERY_HIGH and HIGH confidence violations
- Clear pattern, minimal interpretation needed

**MEDIUM** (0.50-0.74):
- At least one MEDIUM confidence violation
- OR borderline cases requiring manager review

**LOW** (<0.50):
- Multiple LOW confidence indicators
- OR contradictory evidence
- OR missing data affecting assessment
```

---

## Summary of Required Changes

### Critical (Must Fix for Golden Dataset)

| Criterion | Current Agreement | Issue | Recommended Fix Location |
|-----------|-------------------|-------|--------------------------|
| 9.1 | 41% | Timer boundaries, flag grading | `prompt_for_transcript_only_grading.txt` lines 61-70 |
| 9.3 | 47% | Gratitude phrase variants | `Quick_Reference_Grades_EN_PHASE1.md` lines 59-66 |
| 7.2 | 71% | Partial echo, contact data scope | `prompt_for_transcript_only_grading.txt` lines 28-35 |

### Important (Should Fix)

| Criterion | Current Agreement | Issue | Recommended Fix Location |
|-----------|-------------------|-------|--------------------------|
| 4.1 | 53% | Text-only over-detection | `PHASE1_SCOPE.md` line 120-124 + prompt |
| risk_* | 53-71% | Aggregation logic undefined | Add to `phase1_grading_config.json` |

---

## Implementation Priority

**Week 1 (Before finalizing golden dataset)**:
1. Add 9.1 timer endpoint definition + examples (Fixes 1.1, 1.2, 1.3, 1.4)
2. Add 9.3 gratitude phrase enumeration + examples (Fixes 2.1, 2.2, 2.3)
3. Add 7.2 partial echo policy + city example (Fixes 3.1, 3.2, 3.3, 3.4)

**Week 2 (After golden dataset, before production)**:
4. Strengthen 4.1 "don't penalize" instruction (Fix 4.1, 4.2)
5. Document risk calculation logic (Fix 5)
6. Document confidence calculation (Fix 6)

---

## Validation Plan

After implementing fixes 1-3:
1. Re-run Sonnet, BLIND1, BLIND2 on **5 test calls** (not in golden set)
2. Measure agreement on 9.1, 9.3, 7.2
3. **Target**: >85% agreement on these 3 criteria
4. If target not met, iterate on wording and examples

---

## Conclusion

The Phase 1 spec is fundamentally sound, with 13/22 fields achieving 100% agreement. However, **3 critical ambiguities in criteria 9.1, 9.3, and 7.2** account for the majority of inter-rater disagreement and must be addressed before the golden dataset can be finalized.

The recommended fixes are concrete, actionable, and include real transcript examples. Implementing these changes should increase overall field agreement from **current 69% average** (weighted by field variance) to **target 85%+**, making the golden dataset reliable for future model training and calibration.
