# Deliverable D: Revised Prompt Structure and Few-Shot Example Strategy
## Reducing Disagreement on Fragile Fields 7.2, 9.1, and 9.3

**Author**: Expert Reviewer
**Date**: 2025-11-19
**Target**: Improve agreement on fragile fields from current 41-71% to target 85%+
**Approach**: Few-shot learning with real golden examples + explicit edge case handling

---

## Executive Summary

**Problem**: Three criteria (9.1, 9.3, 7.2) show 29-59% disagreement due to spec ambiguities
**Solution**: Inject 5-7 real transcript examples into grading prompt, targeting specific edge cases
**Expected Impact**: +15-25% agreement improvement on fragile fields based on few-shot learning literature

**Key Principle**: "Show, don't tell" - Provide concrete examples from the golden dataset rather than abstract rules.

---

## Revised Prompt Structure

### Current Prompt Issues

The current `prompt_for_transcript_only_grading.txt` uses a **rule-based approach**:
- Lists criteria definitions
- Provides thresholds (e.g., "40-45s flag only")
- Gives detection patterns

**Problem**: Graders interpret rules differently, especially for edge cases.

**Example** (Current 9.1 section):
```
**9.1 - Long Information Search**
- Standard question answer within 3 seconds, complex/database lookup max 40 seconds.
  Timer START when operator announces search, END when operator begins delivering information.
```

**What's missing**:
- Concrete example of timer start/end
- Borderline case (40-45s) handling
- Multi-search scenario

### Proposed Structure: Hybrid Rule + Few-Shot

```
# Revised Grading Prompt Structure

## Part 1: System Instructions (unchanged)
[Keep existing system prompt, confidence levels, lowest code principle]

## Part 2: Criteria Definitions with Few-Shot Examples (NEW)
For each criterion:
1. Rule statement (concise)
2. ✨ **Golden Examples** (2-3 real transcript excerpts)
   - Example 1: Clear PASS
   - Example 2: Clear VIOLATION
   - Example 3: Borderline case (how to handle)
3. Detection checklist
4. Common pitfalls

## Part 3: Assessment Workflow (enhanced with self-checks)
[Keep existing workflow, add "validate against examples" step]

## Part 4: Output Format (unchanged)
[Keep existing JSON schema]
```

**Rationale**:
- Few-shot examples "anchor" grader interpretation
- Real transcript excerpts prevent abstract misinterpretation
- Explicit borderline cases address the exact disagreements observed

---

## Few-Shot Examples for Fragile Fields

### Strategy for Example Selection

**From golden dataset** (Deliverable C):
- **PASS examples**: calls_03, 04, 05, 18 (high confidence, no violations)
- **VIOLATION examples**: calls_01, 15 (high/medium confidence, violations detected)
- **BORDERLINE examples**: call_01 for 9.1 (40-45s flag window)

**Example Format**:
```markdown
**Example [N]: [Description]**
```
[Timestamp] Speaker: "Quote from transcript"
[Timestamp] Speaker: "Quote from transcript"
```

**Assessment**: [PASS/VIOLATION/BORDERLINE]
**Rationale**: [One-sentence explanation]
**Key indicator**: [What made this clear/borderline]
```

---

## 🎯 Priority 1: Criterion 9.1 (Long Information Search)
**Current Agreement**: 41% → **Target**: 85%+

### Revised 9.1 Section (Full Text)

```markdown
### 9.1 - Long Information Search

**Rule**: Answer standard questions within 3s, complex questions within 40s.
- **0-40s**: PASS
- **40-45s**: FLAG for improvement (Grade 10, no score reduction)
- **>45s**: VIOLATION (Grade 9, score reduction)

**Timer**: Start = first search announcement word, End = first substantive answer word (not filler)

---

**Example 1: CLEAR PASS (Search <40s)**

[From call_04 - Golden Example]
```
[3:42] Operator: "Минутку, пожалуйста, сейчас посмотрю наличие"
[3:58] Operator: "Есть в наличии, размер 205/55/R16, цена..."
```

**Assessment**: PASS (16 seconds)
**Timer calculation**:
- START: 3:42 ("Минутку" - search announcement)
- END: 3:58 ("Есть в наличии" - substantive answer, not filler)
- Duration: 16s < 40s ✓

**Key indicator**: First substantive word is "Есть" (factual info), not "Вот" (filler).

---

**Example 2: BORDERLINE FLAG (40-45s window)**

[From call_01 - Golden Example]
```
[3:57] Operator: "Минуту, пожалуйста"
[4:18] Customer: [silence - operator searching]
[4:39] Operator: "Спасибо за ожидание. Размеры сверяю..."
```

**Assessment**: FLAG for improvement (42 seconds, no score reduction)
**Timer calculation**:
- START: 3:57 ("Минуту" - search announcement)
- END: 4:39 ("Размеры" - first substantive word after gratitude)
- Duration: 42s (falls in 40-45s window)

**Grading**:
- final_grade: 10 (NOT 9, no violation occurred)
- flag_window: true
- coaching_priority: "Medium" (improve search speed, but not urgent)

**Key indicator**: "Спасибо за ожидание" is gratitude (separate from 9.3), substantive answer starts at "Размеры".

---

**Example 3: CLEAR VIOLATION (>45s)**

[Synthetic example based on call patterns]
```
[2:30] Operator: "Сейчас посмотрю в системе"
[2:55] Operator: "Еще немного..." [check-in, timer continues]
[3:17] Operator: "Нашёл информацию: адрес следующий..."
```

**Assessment**: VIOLATION (47 seconds)
**Timer calculation**:
- START: 2:30 ("Сейчас посмотрю")
- Check-in at 2:55 - timer does NOT reset
- END: 3:17 ("Нашёл информацию" - substantive phrase)
- Duration: 47s > 45s ✗

**Grading**:
- final_grade: 9 (violation applies)
- score_reduction: true
- coaching_priority: "High"

**Key indicator**: Check-ins are good for customer experience but don't reset timer. Total duration matters.

---

**Common Pitfalls for 9.1**:
1. ❌ Stopping timer at "Вот" (filler word) - Should continue to first substantive word
2. ❌ Resetting timer after check-ins - Should count total duration
3. ❌ Grading 40-45s as Grade 9 - Should be Grade 10 with flag

**Detection Checklist**:
- [ ] Identified search announcement phrase ("Минутку", "Сейчас посмотрю", "Подождите")
- [ ] Identified first substantive answer word (not "Вот", "Так", "Итак")
- [ ] Calculated total duration (including check-ins)
- [ ] Applied correct grading: <40s PASS, 40-45s FLAG, >45s VIOLATION
```

---

## 🎯 Priority 2: Criterion 9.3 (No Thank You for Waiting)
**Current Agreement**: 47% → **Target**: 85%+

### Revised 9.3 Section (Full Text)

```markdown
### 9.3 - No Thank You for Waiting

**Rule**: After EVERY search >10s, operator must thank customer within 5s of delivering answer.

**Acceptable phrases**:
- "Спасибо за ожидание"
- "Спасибо, что подождали"
- "Благодарю за терпение"
- "Спасибо за ваше время"
- Embedded: "Спасибо, нашёл информацию: ..."

**NOT acceptable**:
- "Вот" (no gratitude)
- "Нашёл" (no gratitude)
- Just delivering answer without thanks

---

**Example 1: CLEAR PASS (Explicit gratitude)**

[From call_05 - Golden Example]
```
[2:13] Operator: "Минутку, проверю"
[2:26] Operator: "Спасибо за ожидание. Доставка будет стоить 500 рублей"
```

**Assessment**: PASS (13s search, explicit gratitude)
**Rationale**: Operator explicitly thanked customer ("Спасибо за ожидание") within 5s of answer delivery.
**Key indicator**: Pattern match for "(спасибо|благодарю).*(ожидани|подождал)" found.

---

**Example 2: CLEAR VIOLATION (No gratitude)**

[From call_01 - Golden Example, first search]
```
[2:13] Operator: "Минуту, пожалуйста"
[2:26] Operator: "Вот, размеры следующие: 205/55/R16"
```

**Assessment**: VIOLATION (13s search, no gratitude)
**Rationale**: Operator delivered answer without thanking customer. "Вот" is filler, not gratitude.
**Key indicator**: No pattern match for gratitude phrase. Search >10s requires thank you.

---

**Example 3: PASS (Embedded gratitude)**

[Synthetic example based on patterns]
```
[4:20] Operator: "Сейчас посмотрю"
[4:38] Operator: "Благодарю за терпение, нашёл: адрес улица Ленина..."
```

**Assessment**: PASS (18s search, embedded gratitude)
**Rationale**: "Благодарю за терпение" counts as gratitude, even though embedded in answer.
**Key indicator**: Gratitude phrase present before substantive answer.

---

**Example 4: SHORT SEARCH (No gratitude required)**

[From call_18 - Golden Example]
```
[1:45] Operator: "Секунду"
[1:51] Operator: "Вот, цена 3500 рублей"
```

**Assessment**: PASS (6s search, too short to require gratitude)
**Rationale**: Searches <10s don't require gratitude (customer barely waited).
**Key indicator**: Search duration below 10s threshold.

---

**Example 5: MULTIPLE SEARCHES (All >10s require gratitude)**

[Synthetic example for multi-search scenario]
```
[2:00] Op: "Минутку" [Search 1 starts]
[2:18] Op: "Спасибо за ожидание, размер есть" [Search 1: 18s, thanked ✓]
[3:00] Op: "Сейчас проверю цену" [Search 2 starts]
[3:25] Op: "Цена 4000 рублей" [Search 2: 25s, NOT thanked ✗]
```

**Assessment**: VIOLATION (Search 2 completed without gratitude)
**Rationale**: Operator thanked after Search 1 but NOT after Search 2. Each search >10s requires gratitude.
**Key indicator**: Multiple searches = multiple gratitude checks.

---

**Common Pitfalls for 9.3**:
1. ❌ Accepting "Вот" as gratitude - Not a gratitude phrase
2. ❌ Skipping short searches (<10s) check - Should only penalize >10s
3. ❌ Assuming one thank-you covers all searches - Each search needs separate gratitude
4. ❌ Missing embedded gratitude - "Спасибо, нашёл..." counts

**Detection Checklist**:
- [ ] Identified all searches >10 seconds in the call
- [ ] For each search >10s, checked for gratitude phrase within 5s of answer
- [ ] Pattern match: (спасибо|благодарю).*(ожидани|подождал|ждал|терпение|время)
- [ ] Excluded searches <10s from check
- [ ] If ANY search >10s lacks gratitude → VIOLATION
```

---

## 🎯 Priority 3: Criterion 7.2 (Echo Method Not Used)
**Current Agreement**: 71% → **Target**: 90%+

### Revised 7.2 Section (Full Text)

```markdown
### 7.2 - Echo Method Not Used ⭐ CRITICAL

**Rule**: For EVERY contact data field (name, phone, city, email, address), operator must:
1. Repeat it back to customer
2. Ask explicit confirmation ("Верно?", "Правильно?", "Подтверждаете?")
3. Receive customer confirmation ("Да", "Верно", "Угу")

**All-or-nothing policy**: If operator collects 3 contact fields, ALL 3 must be echoed. Partial echo = VIOLATION.

---

**Example 1: CLEAR PASS (Full echo for all contact data)**

[From call_05 - Golden Example]
```
[0:45] Op: "Как вас зовут?"
[0:47] Customer: "Иван Петров"
[0:50] Op: "Иван Петров, верно?"
[0:52] Customer: "Да"
[1:10] Op: "Ваш номер телефона?"
[1:12] Customer: "912-555-1234"
[1:15] Op: "Итак, 912-555-1234, правильно?"
[1:17] Customer: "Правильно"
```

**Assessment**: PASS (name and phone both echoed with confirmation)
**Rationale**:
- Name: Repeated ✓, Confirmation requested ✓, Customer confirmed ✓
- Phone: Repeated ✓, Confirmation requested ✓, Customer confirmed ✓

**Key indicator**: For EACH contact field, all 3 steps completed.

---

**Example 2: VIOLATION (Partial echo - only phone echoed, not name/city)**

[From call_01 - Golden Example]
```
[0:14] Op: "Как вас зовут?"
[0:15] Customer: "Алексей"
[0:17] Op: "Алексей, из какого города вы звоните?"
[0:18] Customer: "Усть-Катав"
[0:20] Op: "Хорошо, Усть-Катав. Какой ваш номер?"
[0:25] Customer: "912-778-1421"
[0:28] Op: "Ваш номер 912-778-1421, верно?"
[0:30] Customer: "Да"
```

**Assessment**: VIOLATION (phone echoed ✓, but name and city NOT echoed)
**Rationale**:
- Name "Алексей": Operator used it but never asked "Алексей, верно?" ✗
- City "Усть-Катав": Operator repeated it ("Хорошо, Усть-Катав") but no "верно?" ✗
- Phone "912-778-1421": Echoed correctly ✓

**All-or-nothing rule**: Since name and city were NOT echoed, this is a 7.2 violation.

**Key indicator**: Partial echo (1/3 fields echoed) = VIOLATION. All contact data must be echoed.

---

**Example 3: VIOLATION (Repeat without confirmation request)**

[Synthetic example]
```
[1:00] Customer: "Мой email: ivan@example.com"
[1:05] Op: "Хорошо, ivan@example.com, записал"
[1:08] Op: "Что-то еще?"
```

**Assessment**: VIOLATION (email repeated but no confirmation requested)
**Rationale**:
- Email repeated: "ivan@example.com" ✓
- Confirmation requested: NO ("Хорошо, записал" ≠ "Верно?") ✗

**Key indicator**: Operator acknowledged data ("записал") but never asked for explicit confirmation.

---

**Example 4: PASS (City as part of address echoed)**

[Synthetic example]
```
[2:00] Op: "В какой город доставить?"
[2:03] Customer: "Екатеринбург"
[2:05] Op: "Екатеринбург, верно?"
[2:06] Customer: "Да"
```

**Assessment**: PASS (city echoed with confirmation)
**Rationale**: City counts as contact data (delivery location). Echoed correctly.
**Key indicator**: "Верно?" asked, customer confirmed "Да".

---

**Example 5: BORDERLINE (First name only, last name not collected)**

[Synthetic example]
```
[0:30] Op: "Как к вам обращаться?"
[0:32] Customer: "Александр"
[0:34] Op: "Александр, правильно?"
[0:35] Customer: "Да"
```

**Assessment**: PASS (only first name collected, and it was echoed)
**Rationale**: Operator only asked for first name ("как обращаться"), not full name. Echo applied to what was collected.
**Key indicator**: If operator collects partial name intentionally (first only), echo applies to what was collected.

**NOTE**: If customer volunteers full name ("Александр Иванов") but operator only echoes first name, this is VIOLATION.

---

**Contact Data Types Requiring Echo**:
- ✅ Phone (mobile or landline)
- ✅ Full name OR first/last name components (whichever operator collects)
- ✅ Email address
- ✅ Full address OR city (if collected as delivery location)
- ❌ Product preferences (e.g., "Размер 205/55" - NOT contact data)
- ❌ Customer requests (e.g., "Мне нужны шины" - NOT contact data)

---

**Common Pitfalls for 7.2**:
1. ❌ Marking partial echo as PASS - If ANY contact field not echoed, it's VIOLATION
2. ❌ Accepting implicit confirmation - Must have explicit "Верно?"/"Да" exchange
3. ❌ Confusing "usage" with "echo" - Using name in conversation ≠ echoing for confirmation
4. ❌ Excluding city from echo requirement - City counts as contact data if collected

**Detection Checklist**:
- [ ] Identified ALL contact data fields collected (name, phone, city, email, address)
- [ ] For EACH field, checked: (a) repeated, (b) confirmation requested, (c) customer confirmed
- [ ] If ANY field fails (a), (b), or (c) → VIOLATION
- [ ] Confirmed "Верно?"/"Правильно?"/"Да" exchange present for each field
```

---

## Implementation Strategy

### Phase 1: Inject Examples into Prompt (Week 1)

**Action**: Create new prompt file `prompt_for_transcript_only_grading_v2_with_examples.txt`

**Structure**:
```
[Existing system instructions - lines 1-50]

========================================
FEW-SHOT EXAMPLES FOR FRAGILE CRITERIA
========================================

[Insert 9.1 examples section above]
[Insert 9.3 examples section above]
[Insert 7.2 examples section above]

========================================
WORKFLOW: ASSESS WITH EXAMPLE VALIDATION
========================================

For criteria 7.2, 9.1, 9.3:
1. Make initial assessment (PASS/VIOLATION/BORDERLINE)
2. Compare your assessment to examples above
3. If borderline, ask: "Which example does this most resemble?"
4. If your case matches Example 2 (violation pattern), mark VIOLATION
5. If uncertain, use conservative approach: FLAG for review, don't penalize

[Rest of existing prompt]
```

**Estimated impact**: +10-15% agreement improvement on first iteration

---

### Phase 2: A/B Test with Validation Set (Week 2)

**Action**: Run Sonnet and Haiku with both prompt versions on 5 held-out calls

**Metrics**:
- Agreement on 9.1: Current ~41% → Target >75%
- Agreement on 9.3: Current ~47% → Target >75%
- Agreement on 7.2: Current ~71% → Target >85%

**Success criteria**: If target met, proceed to Phase 3. If not, iterate on examples.

---

### Phase 3: Full Dataset Re-Grading (Week 3)

**Action**: Re-run all 20 calls with updated prompt

**Compare**:
- Old prompt vs new prompt agreement
- Sonnet vs BLIND1 vs BLIND2 agreement improvement

**Expected outcome**: 7 "deferred" calls (Deliverable C) should stabilize → upgrade to medium/high confidence

---

### Phase 4: Production Deployment (Week 4)

**Action**: Replace `prompt_for_transcript_only_grading.txt` with v2 in production

**Monitoring**:
- Track agreement rates on new calls
- Flag any new edge cases not covered by examples
- Iterate on examples quarterly based on production patterns

---

## Additional Recommendations

### Recommendation 1: Create Example Library

Build a structured example library in `examples/criterion_examples/`:
```
examples/
  criterion_7.2_echo_method/
    pass_example_1_full_echo.md
    violation_example_1_partial_echo.md
    violation_example_2_no_confirmation.md
  criterion_9.1_long_search/
    pass_example_1_under_40s.md
    borderline_example_1_42s_flag.md
    violation_example_1_over_45s.md
  criterion_9.3_thank_you/
    pass_example_1_explicit_gratitude.md
    pass_example_2_embedded_gratitude.md
    violation_example_1_no_gratitude.md
```

**Usage**:
- Prompt construction (dynamically inject examples)
- Human QA training
- Documentation for future graders

---

### Recommendation 2: Self-Consistency Checks in Prompt

Add explicit validation steps to prompt:
```markdown
## Self-Consistency Checks (Run before finalizing assessment)

For criterion 9.1:
- [ ] If I marked VIOLATION, is search duration >45s?
- [ ] If I marked FLAG, is duration 40-45s AND final_grade=10?
- [ ] Did I count total duration (including check-ins)?

For criterion 9.3:
- [ ] Did I check EVERY search >10s for gratitude?
- [ ] Did I accept only explicit gratitude phrases (not "Вот")?

For criterion 7.2:
- [ ] Did I check echo for ALL contact fields collected?
- [ ] Did I verify "Верно?"+confirmation exchange for each field?
- [ ] If ANY field lacks full echo, did I mark VIOLATION?

If any check fails, re-assess before finalizing.
```

**Rationale**: Forces grader (human or LLM) to validate against common pitfalls.

---

### Recommendation 3: Prompt Versioning and A/B Testing Infrastructure

**Setup**:
```python
# config/prompt_versions.json
{
  "v1_baseline": {
    "path": "prompt_for_transcript_only_grading.txt",
    "deployment_date": "2025-11-19",
    "agreement_9.1": 0.41,
    "agreement_9.3": 0.47,
    "agreement_7.2": 0.71
  },
  "v2_with_examples": {
    "path": "prompt_for_transcript_only_grading_v2_with_examples.txt",
    "deployment_date": "2025-12-01",
    "agreement_9.1": null,  # To be measured
    "agreement_9.3": null,
    "agreement_7.2": null,
    "examples_used": ["call_01", "call_04", "call_05", "call_15"]
  }
}
```

**Usage**:
- Track which prompt version was used for each grading
- Compare agreement rates across versions
- Roll back if new prompt performs worse

---

### Recommendation 4: Dynamic Example Selection

**Advanced strategy** (for future iteration):

Instead of static examples in prompt, dynamically select examples based on call characteristics:

```python
def select_examples_for_call(call_metadata):
    examples = []

    # If call has multiple searches, inject multi-search 9.3 example
    if call_metadata['search_count'] > 1:
        examples.append(load_example('9.3_multiple_searches'))

    # If call has city collection, inject city echo example
    if 'city' in call_metadata['contact_data_collected']:
        examples.append(load_example('7.2_city_echo'))

    # Always include baseline examples
    examples.extend([
        load_example('9.1_borderline_flag'),
        load_example('9.3_explicit_gratitude'),
        load_example('7.2_partial_echo_violation')
    ])

    return examples
```

**Benefit**: Reduces prompt length while maximizing relevance.

---

## Expected Outcomes

### Quantitative Targets

| Criterion | Current Agreement | Target (Post-Examples) | Improvement |
|-----------|-------------------|------------------------|-------------|
| 9.1 | 41% | 85% | +44% |
| 9.3 | 47% | 85% | +38% |
| 7.2 | 71% | 90% | +19% |
| **Overall (22 fields)** | **~69%** | **~85%** | **+16%** |

### Qualitative Benefits

1. **Reduced ambiguity**: Graders can point to specific examples when uncertain
2. **Faster onboarding**: New graders (human or LLM) learn patterns from examples
3. **Consistent edge case handling**: Borderline cases (40-45s, partial echo) standardized
4. **Auditability**: Decisions traceable to specific examples

### Risk Mitigation

**Risk**: Overfitting to example patterns, missing novel edge cases
**Mitigation**:
- Include diverse examples (PASS, VIOLATION, BORDERLINE)
- Update example library quarterly based on production patterns
- Monitor for "out-of-distribution" calls that don't match any example

**Risk**: Prompt length increases, higher LLM costs
**Mitigation**:
- Keep examples concise (3-5 lines per example)
- Total addition: ~500 tokens (vs 2000 token baseline prompt = +25%)
- Cost increase acceptable for +16% agreement improvement

---

## Conclusion

The revised prompt strategy targets the **root cause** of inter-rater disagreement: **abstract rules interpreted differently**.

By injecting 15-20 concrete few-shot examples from the golden dataset, we:
1. Anchor grader interpretation to real patterns
2. Explicitly handle edge cases (40-45s flag, partial echo, multi-search)
3. Provide self-validation checklists

**Expected outcome**: 7 "deferred" calls become golden-worthy, bringing total high-confidence golden dataset from **5 calls (25%)** to **13 calls (65%)**.

**Critical success factor**: Examples must be drawn from validated golden calls (Deliverable C) to avoid propagating errors.

**Timeline**: 4 weeks from prompt v2 creation to production deployment with validated agreement improvement.

---

## Appendix: Example Prompt Diff

**Before** (Current prompt, criterion 9.1):
```
**9.1 - Long Information Search**
- Standard question answer within 3 seconds, complex/database lookup max 40 seconds.
  Timer START when operator announces search, END when operator begins delivering information.
  Returns to customer don't reset timer (total search duration counted).
```

**After** (Revised prompt with examples):
```
**9.1 - Long Information Search**
[Rule statement]

**Example 1: CLEAR PASS (Search <40s)**
[3:42] Op: "Минутку, пожалуйста, сейчас посмотрю наличие"
[3:58] Op: "Есть в наличии, размер 205/55/R16..."
→ PASS (16s)

**Example 2: BORDERLINE FLAG (40-45s)**
[3:57] Op: "Минуту, пожалуйста"
[4:39] Op: "Спасибо за ожидание. Размеры сверяю..."
→ FLAG (42s, Grade 10, no score reduction)

**Example 3: VIOLATION (>45s)**
[2:30] Op: "Сейчас посмотрю"
[3:17] Op: "Нашёл информацию..."
→ VIOLATION (47s, Grade 9)

[Detection checklist]
[Common pitfalls]
```

**Diff**: +15 lines per criterion × 3 criteria = ~45 lines, ~500 tokens added.
