# TASK-001: Fix Timing Extraction Edge Cases - BDD Approach

**Status**: OPEN
**Priority**: HIGH
**Created**: 2025-11-19
**Assigned**: Next Agent
**Related Files**: `scripts/extract_timing.py`, `scripts/extract_gratitude.py`

---

## Problem Statement

The ground truth extraction tool (`extract_timing.py`) is producing incorrect results on call_17, missing the actual search announcement and only detecting partial search activity. Manual analysis reveals the tool failed to detect a clear 69.71s search that violated the 45s threshold.

### Evidence from call_17

**Tool Output (WRONG)**:
- Search #2: 26.9s (claimed PASS)
- Final Assessment: 9.1 PASS

**Manual Analysis (CORRECT)**:
- Search #2: 69.71s (actual VIOLATION)
- Start: Line 25 @ 00:02:02.082 - "Сейчас я посмотрю, подойдет ли он на хавейл. **Минуту, пожалуйста.**"
- End: Line 32 @ 00:03:11.792 - "Ну, 34-35 для 18 дюймовых..."
- Final Assessment: 9.1 VIOLATION

**Sonnet Grading (CORRECT)**:
- Search #2: ~70s (VIOLATION)
- Sonnet correctly identified the violation while tool failed

**Root Cause**: Tool likely detected line 32 "Сейчас посмотрим" as search START instead of recognizing line 25 "Минуту, пожалуйста" as the actual search announcement.

---

## BDD (Behavior Driven Development) Approach

### What is BDD?

BDD is a software development methodology where:
1. **Behavior is specified first** using natural language (Given/When/Then)
2. **Tests are written** to verify the specified behavior
3. **Implementation follows** to make tests pass
4. **Documentation IS the tests** - always up to date

### Why BDD for This Task?

1. **Complex domain logic**: Russian language patterns, multiple search announcement formats, timing edge cases
2. **High stakes**: Wrong timing detection = wrong golden labels = poor LLM training
3. **Regression prevention**: Once we fix call_17, ensure we don't break call_02, call_08, etc.
4. **Knowledge preservation**: Next developer sees EXACTLY what cases must work

### BDD Tools: Python `behave`

We'll use the `behave` framework (Python's Cucumber equivalent):

```bash
pip install behave
```

**Directory Structure**:
```
tests/
├── features/
│   ├── timing_extraction.feature       # Human-readable specs (Gherkin)
│   ├── gratitude_detection.feature
│   └── steps/
│       ├── timing_steps.py             # Step implementations
│       └── gratitude_steps.py
├── fixtures/
│   ├── call_17_transcript.vtt          # Test data
│   └── call_17_expected_timing.json    # Expected output
└── behave.ini                          # Configuration
```

**Run tests**:
```bash
cd /home/user/sample20calls
behave tests/features/timing_extraction.feature
```

**Output format**:
```
Feature: Search Duration Extraction
  Scenario: Detect search with "Минуту, пожалуйста" announcement
    Given a transcript with search announcement at line 25
    When I run timing extraction
    Then search #2 should start at 00:02:02.082
    And search #2 should end at 00:03:11.792
    And search #2 duration should be 69.71 seconds
    And search #2 status should be VIOLATION
```

---

## Edge Cases to Cover

### Category 1: Search Announcement Detection

#### Edge Case 1.1: Multiple Search Patterns in Same Utterance
**Call**: call_17, Line 25
**Text**: "**Сейчас я посмотрю**, подойдет ли он на хавейл. **Минуту, пожалуйста.**"
**Issue**: Two search patterns present - which one marks the start?
**Expected**: Use the FIRST pattern ("Сейчас я посмотрю") as search start
**Current Tool Behavior**: May be skipping this line entirely or using wrong pattern

**BDD Spec**:
```gherkin
Scenario: Search announcement with multiple patterns
  Given agent line "Сейчас я посмотрю, подойдет ли он на хавейл. Минуту, пожалуйста."
  When I detect search announcement
  Then search should start at this line
  And search_start_phrase should be "Сейчас я посмотрю"
```

---

#### Edge Case 1.2: "Сейчас посмотрим" During Search (NOT a new search)
**Call**: call_17, Line 32
**Text**: "Ну, 34-35 для 18 дюймовых. **Сейчас посмотрим**. Здесь у нас 37."
**Issue**: Tool may detect this as NEW search start, but it's actually information delivery continuing
**Context**: Agent is delivering partial results ("34-35 for 18 inch") and checking more ("let's look")
**Expected**: This is the SEARCH END (information delivery), NOT a new search start

**BDD Spec**:
```gherkin
Scenario: "Сейчас посмотрим" as part of answer delivery
  Given active search started at line 25
  When agent says "Ну, 34-35 для 18 дюймовых. Сейчас посмотрим. Здесь у нас 37." at line 32
  Then this should END the current search
  And this should NOT start a new search
  And end_phrase should be "Ну, 34-35 для 18 дюймовых"
```

**Detection Rule**: If agent is providing concrete information (numbers, specifications, product names) in the SAME utterance as "сейчас посмотрим", it's information delivery, not search start.

---

#### Edge Case 1.3: Customer Interruptions During Search
**Call**: call_17, Lines 26-31
**Text**: Customer speaks multiple times while agent searches
**Issue**: Tool must NOT treat customer speech as search end
**Expected**: Search continues until AGENT delivers information

**BDD Spec**:
```gherkin
Scenario: Customer speaks during agent search
  Given active search started by agent at line 25
  When customer speaks at lines 26, 27, 28, 29, 31
  Then search should remain active
  And search should not end until agent delivers information
```

---

#### Edge Case 1.4: Agent Mid-Search Check-in
**Call**: call_17, Line 30
**Text**: "Увы, **сейчас я посмотрю**, какой у вас."
**Issue**: Agent checks in with customer during long search - this is NOT a new search
**Expected**: Continue existing search timer, do NOT reset or start new search

**BDD Spec**:
```gherkin
Scenario: Agent check-in during active search
  Given active search started at line 25 (00:02:02.082)
  When agent says "Увы, сейчас я посмотрю, какой у вас" at line 30 (00:02:53.208)
  Then search should remain active
  And search timer should NOT reset
  And this should be recorded as a check-in
```

**Detection Rule**: If active search exists AND new search pattern appears within 60s AND no concrete information was delivered, it's a check-in, not a new search.

---

### Category 2: Search End Detection

#### Edge Case 2.1: Information Delivery with Continued Search Language
**Call**: call_17, Line 32
**Text**: "Ну, 34-35 для 18 дюймовых. **Сейчас посмотрим**. Здесь у нас 37."
**Issue**: Agent delivers concrete info ("34-35") but also says "let's look" - when does search end?
**Expected**: Search ends when FIRST concrete information is delivered
**Detection**: Look for numbers, product codes, yes/no answers, availability statements

**BDD Spec**:
```gherkin
Scenario: Partial information delivery with continued searching language
  Given active search for product specifications
  When agent says "Ну, 34-35 для 18 дюймовых"
  Then search should end at this timestamp
  Even though agent continues with "Сейчас посмотрим. Здесь у нас 37"
  Because concrete answer was provided
```

**Information Delivery Indicators**:
- Numbers: "34-35", "14400", "96%"
- Product codes: "R306-903", "R32-76-93"
- Availability: "есть в наличии", "нет на складе", "завтра можно"
- Yes/No: "да, подойдет", "нет, не подойдет"
- Specifications: "вылет 34", "18 дюймов", "черный цвет"

---

#### Edge Case 2.2: Multiple Partial Answers
**Call**: call_17, Lines 32-35
**Agent delivers info in multiple chunks**:
- Line 32: "34-35 для 18 дюймовых... Здесь у нас 37"
- Line 35: "Практически такой же дизайн, только алмаз. Они по стоимости 14400..."

**Expected**: Search ends at Line 32 (first concrete answer)
**Do NOT**: Extend search through all information delivery

**BDD Spec**:
```gherkin
Scenario: Multi-part information delivery
  Given active search
  When agent provides first concrete answer at line 32
  Then search ends at line 32
  And subsequent information at lines 33-35 is NOT part of search duration
```

---

### Category 3: Pattern Priority and Ambiguity

#### Edge Case 3.1: Weak vs Strong Search Announcements
**Patterns in Order of Priority**:

1. **STRONGEST** - Explicit time promise:
   - "Минуту, пожалуйста"
   - "Секунду, пожалуйста"
   - "Минуточку"

2. **STRONG** - Active searching verb:
   - "Сейчас посмотрю"
   - "Сейчас проверю"
   - "Сейчас уточню"

3. **MEDIUM** - Passive/plural searching:
   - "Сейчас посмотрим" (we'll look - but context matters!)
   - "Давайте посмотрим"

4. **WEAK** - Vague temporal:
   - "Сейчас" alone
   - "Щас"

**BDD Spec**:
```gherkin
Scenario: Prioritize explicit time promise over vague temporal
  Given agent says "Сейчас посмотрю" at timestamp T1
  And agent says "Минуту, пожалуйста" at timestamp T2
  And T2 is within 3 seconds of T1
  Then use T1 as search start (first pattern)
  And record "Сейчас посмотрю" as start_phrase
```

---

#### Edge Case 3.2: Context-Dependent Pattern Interpretation
**Example**: "Сейчас посмотрим"

**Context A - Search Start**:
```
Customer: А есть ли в наличии?
Agent: Сейчас посмотрим. [SILENCE]
```
→ This IS a search start (no information provided)

**Context B - Continuation During Answer**:
```
Agent: Ну, 34-35 для 18 дюймовых. Сейчас посмотрим. Здесь у нас 37.
```
→ This is NOT a search start (information being delivered)

**Detection Logic**:
```python
def is_search_start(text, speaker, context):
    if speaker != "AGENT":
        return False

    has_search_pattern = contains_search_pattern(text)
    if not has_search_pattern:
        return False

    # Check if concrete information is in the SAME utterance
    has_concrete_info = contains_concrete_information(text)

    if has_concrete_info:
        # Information delivery, not search start
        return False

    return True
```

**BDD Spec**:
```gherkin
Scenario Outline: Context-dependent pattern interpretation
  Given agent utterance "<text>"
  And utterance contains pattern "сейчас посмотрим"
  When I check if this is search start
  Then result should be <is_search_start>
  And reason should be "<reason>"

  Examples:
    | text | is_search_start | reason |
    | Сейчас посмотрим в системе | True | No concrete info present |
    | 34-35 для 18 дюймовых. Сейчас посмотрим. | False | Concrete info provided |
    | Сейчас посмотрим... [silence] | True | Search announced |
```

---

### Category 4: Timing Edge Cases

#### Edge Case 4.1: Long Search with Multiple Check-ins
**Call**: call_10 (similar pattern)
**Issue**: Tool must not split one long search into multiple searches based on check-ins

**BDD Spec**:
```gherkin
Scenario: Single search with multiple check-ins
  Given search starts at T0
  When agent checks in at T0+30s with "Сейчас, минутку"
  And agent checks in at T0+50s with "Еще немного"
  And agent delivers answer at T0+70s
  Then there should be exactly 1 search detected
  And search duration should be 70 seconds
  And check_ins array should have 2 entries
```

---

#### Edge Case 4.2: Back-to-Back Searches
**Expected**: Two searches within 10 seconds should remain separate

**BDD Spec**:
```gherkin
Scenario: Consecutive searches with brief gap
  Given search #1 ends at T0 (00:01:00)
  When search #2 starts at T0+8s (00:01:08)
  Then there should be 2 separate searches
  And search #1 should end at 00:01:00
  And search #2 should start at 00:01:08
```

---

### Category 5: Integration with 9.3 (Gratitude)

#### Edge Case 5.1: Gratitude Detection After Failed Search Detection
**Issue**: If tool missed the search, it won't check for gratitude

**BDD Spec**:
```gherkin
Scenario: Gratitude validation requires correct search detection
  Given timing tool detects search at 00:02:02 - 00:03:11 (69.7s)
  When I run gratitude extraction
  Then it should check for gratitude within 5s after 00:03:11
  And finding no gratitude should result in 9.3 VIOLATION
```

---

## Test Data Requirements

### Fixture: call_17_transcript_snippet.vtt
```vtt
25
00:02:02,082 --> 00:02:06,342 <AGENT>
Сейчас я посмотрю, подойдет ли он на хавейл. Минуту, пожалуйста.

26
00:02:07,382 --> 00:02:10,342 <CUSTOMER>
Еще раз глянем.

30
00:02:53,208 --> 00:02:56,008 <AGENT>
Увы, сейчас я посмотрю, какой у вас.

32
00:03:11,792 --> 00:03:19,612 <AGENT>
Ну, 34-35 для 18 дюймовых. Сейчас посмотрим. Здесь у нас 37.
```

### Expected Output: call_17_expected_timing.json
```json
{
  "call_id": "call_17",
  "total_searches": 2,
  "searches": [
    {
      "search_number": 2,
      "start_timestamp": "0:02:02.082",
      "start_line_number": 25,
      "start_phrase": "Сейчас я посмотрю",
      "end_timestamp": "0:03:11.792",
      "end_line_number": 32,
      "end_phrase": "Ну, 34-35 для 18 дюймовых",
      "duration_seconds": 69.71,
      "check_ins": [
        {
          "timestamp": "0:02:53.208",
          "phrase": "Увы, сейчас я посмотрю, какой у вас",
          "speaker": "AGENT",
          "line_number": 30,
          "note": "Mid-search check-in (not new search)"
        }
      ],
      "assessment": {
        "status": "VIOLATION",
        "threshold_applied": "45s",
        "exceeds_threshold_by": 24.71,
        "grade_impact": 9
      }
    }
  ]
}
```

---

## BDD Feature File: `timing_extraction.feature`

```gherkin
Feature: Search Duration Extraction from VTT Transcripts
  As a quality analyst
  I want to accurately measure agent search durations
  So that I can correctly assess 9.1 violations (searches >45s)

  Background:
    Given the grading rules specify:
      | threshold | action |
      | 0-40s     | PASS   |
      | 40-45s    | FLAG   |
      | >45s      | VIOLATION (Grade 9) |
    And check-ins do not reset the search timer
    And search ends when agent delivers first concrete information

  Scenario: call_17 - Search with multiple patterns and check-in
    Given I have the call_17 VTT transcript
    When I run extract_timing.py on call_17
    Then I should detect exactly 2 searches

    And search #1 should have:
      | property          | value              |
      | start_timestamp   | 0:00:49.918       |
      | end_timestamp     | 0:01:06.738       |
      | duration_seconds  | 16.82             |
      | status            | PASS              |

    And search #2 should have:
      | property          | value              |
      | start_timestamp   | 0:02:02.082       |
      | start_line_number | 25                |
      | start_phrase      | Сейчас я посмотрю |
      | end_timestamp     | 0:03:11.792       |
      | end_line_number   | 32                |
      | duration_seconds  | 69.71             |
      | status            | VIOLATION         |
      | exceeds_by        | 24.71             |

    And search #2 should have 1 check-in:
      | timestamp    | phrase                              | line |
      | 0:02:53.208  | Увы, сейчас я посмотрю, какой у вас | 30   |

    And final 9.1 assessment should be VIOLATION

  Scenario: Distinguish search start from information delivery
    Given agent utterance "Ну, 34-35 для 18 дюймовых. Сейчас посмотрим. Здесь у нас 37."
    When I check if this is a search announcement
    Then result should be False
    Because "utterance contains concrete information (34-35)"

  Scenario: Detect search with explicit time promise
    Given agent utterance "Сейчас я посмотрю, подойдет ли он на хавейл. Минуту, пожалуйста."
    When I detect search announcement
    Then result should be True
    And start_phrase should be "Сейчас я посмотрю"

  Scenario: Agent check-in during active search does not reset timer
    Given active search started at 00:02:02.082
    When agent says "Увы, сейчас я посмотрю, какой у вас" at 00:02:53.208
    Then search should remain active
    And duration should continue from 00:02:02.082
    And this should be recorded as check-in

  Scenario: Customer speech during search is ignored
    Given active search started by agent
    When customer speaks
    Then search timer should continue
    And customer speech should not end the search

  Scenario Outline: Pattern priority in search detection
    Given agent utterance contains "<pattern>"
    And utterance context is "<context>"
    When I classify the pattern
    Then pattern strength should be "<strength>"
    And should start search: <starts_search>

    Examples:
      | pattern           | context              | strength | starts_search |
      | Минуту, пожалуйста | Beginning of speech | STRONG   | True          |
      | Сейчас посмотрю   | Beginning of speech | STRONG   | True          |
      | Сейчас посмотрим  | With concrete info  | MEDIUM   | False         |
      | Сейчас посмотрим  | Without info        | MEDIUM   | True          |

  Scenario: Regression - call_02 should still work
    Given I have the call_02 VTT transcript
    When I run extract_timing.py on call_02
    Then I should detect 3 searches
    And longest search should be 38.9 seconds
    And final 9.1 assessment should be PASS

  Scenario: Regression - call_08 should still work
    Given I have the call_08 VTT transcript
    When I run extract_timing.py on call_08
    Then I should detect at least 1 search
    And at least one search should exceed 45 seconds
    And final 9.1 assessment should be VIOLATION
```

---

## Implementation Steps

### Step 1: Set Up BDD Framework

```bash
# Install behave
pip install behave

# Create directory structure
mkdir -p tests/features/steps
mkdir -p tests/fixtures

# Create behave configuration
cat > tests/behave.ini << 'EOF'
[behave]
paths = features
show_timings = true
show_skipped = false
format = pretty
junit = true
junit_directory = test-results
EOF
```

### Step 2: Write Step Definitions

**File**: `tests/features/steps/timing_steps.py`

```python
from behave import given, when, then, step
import sys
sys.path.insert(0, '/home/user/sample20calls/scripts')
from extract_timing import extract_timing
import json

@given('I have the {call_id} VTT transcript')
def step_load_transcript(context, call_id):
    context.call_id = call_id
    context.vtt_path = f'/home/user/sample20calls/calls/{call_id}/transcript-2.vtt'

@when('I run extract_timing.py on {call_id}')
def step_run_extraction(context, call_id):
    # Run the actual extraction tool
    context.result = extract_timing(context.vtt_path)

@then('I should detect exactly {count:d} searches')
def step_verify_search_count(context, count):
    actual = context.result['total_searches']
    assert actual == count, f"Expected {count} searches, got {actual}"

@then('search #{num:d} should have')
def step_verify_search_properties(context, num):
    search = context.result['searches'][num-1]
    for row in context.table:
        property_name = row['property']
        expected_value = row['value']

        actual_value = search[property_name]

        # Type conversion based on property
        if 'seconds' in property_name:
            expected_value = float(expected_value)

        assert actual_value == expected_value, \
            f"Search {num} {property_name}: expected {expected_value}, got {actual_value}"

@then('final 9.1 assessment should be {status}')
def step_verify_final_assessment(context, status):
    actual = context.result['final_9_1_assessment']['status']
    assert actual == status, f"Expected {status}, got {actual}"
```

### Step 3: Run Tests (Should FAIL)

```bash
cd /home/user/sample20calls
behave tests/features/timing_extraction.feature

# Expected output:
# Feature: Search Duration Extraction from VTT Transcripts
#   Scenario: call_17 - Search with multiple patterns and check-in
#     Given I have the call_17 VTT transcript ... passed
#     When I run extract_timing.py on call_17 ... passed
#     Then I should detect exactly 2 searches ... passed
#     And search #2 should have ... FAILED
#       AssertionError: Search 2 duration_seconds: expected 69.71, got 26.9
```

### Step 4: Fix the Tool

Now you know EXACTLY what needs to work. Fix `extract_timing.py` to:
1. Detect line 25 "Сейчас я посмотрю, подойдет ли он на хавейл. Минуту, пожалуйста." as search start
2. NOT treat line 32 "Сейчас посмотрим" as new search start (it has concrete info)
3. Detect line 30 as check-in, not new search
4. End search at line 32 when concrete info delivered

### Step 5: Run Tests Until They Pass

```bash
# Fix tool, run test, iterate
behave tests/features/timing_extraction.feature

# When all pass:
# Feature: Search Duration Extraction from VTT Transcripts
#   Scenario: call_17 - Search with multiple patterns and check-in ... passed
#   5 scenarios (5 passed)
#   23 steps (23 passed)
```

### Step 6: Regression Testing

```bash
# Run on ALL calls with ground truth
for call in call_02 call_03 call_04 call_07 call_08 call_09 call_10 call_17; do
    echo "Testing $call..."
    behave tests/features/timing_extraction.feature --name "$call"
done
```

---

## Definition of Done

- [ ] BDD feature file created with all edge cases
- [ ] Step definitions implemented
- [ ] Test fixtures created (call_17 expected output)
- [ ] All tests run and FAIL (proving they test the right thing)
- [ ] Tool fixed to make tests pass
- [ ] Regression tests pass for call_02, call_08, call_09, call_10
- [ ] Re-run extraction on call_17 and verify output matches manual calculation
- [x] Update `sonnet_haiku_blind_core_decisions.json` (call_10 and call_17 upgraded to HIGH)
- [ ] Document the fix in tool README

---

## Expected Outcome

After fixing the tool:

**call_17 Ground Truth** (corrected):
```json
{
  "final_9_1_assessment": {
    "criterion": "9.1 - Long Information Search",
    "status": "VIOLATION",
    "grade_impact": 9
  }
}
```

**call_17 Golden Decision** (updated):
```json
{
  "call_id": "call_17",
  "golden_source": "Ground Truth",
  "confidence": "high",
  "reason": "Ground truth extraction confirms 69.71s search (VIOLATION)",
  "notes": "Tool fixed to correctly detect search announcement with multiple patterns. Search duration verified: 00:02:02.082 to 00:03:11.792 = 69.71s.",
  "ground_truth_validated": true
}
```

**Impact**:
- call_10 upgraded from MEDIUM → HIGH (manual verification: multiple violations 46.16s, 51.12s)
- call_17 upgraded from MEDIUM → HIGH (manual verification: 69.71s violation, tool failed)
- **20/20 HIGH confidence (100%)**
- Tool reliability must be improved (call_17 failure documented)
- Future edge cases prevented through regression tests

---

## References

- **Manual Analysis**: This task document, "Manual Analysis" section
- **Call Transcript**: `/home/user/sample20calls/calls/call_17/transcript-2.vtt`
- **Current Tool**: `/home/user/sample20calls/scripts/extract_timing.py`
- **Grading Config**: `/home/user/sample20calls/config/phase1_grading_config.json`
- **Golden Decisions**: `/home/user/sample20calls/phase1_analysis/sonnet_haiku_blind_core_decisions.json`

---

## Notes

This is a perfect example of why **ground truth tools must be tested rigorously**. The tool is SUPPOSED to be the source of truth, but if it has bugs, it becomes the source of ERROR. BDD ensures:

1. **Behavior is documented** - future developers know what MUST work
2. **Regression is prevented** - fixing call_17 won't break call_02
3. **Confidence is justified** - we KNOW the tool works because tests prove it
4. **Edge cases are preserved** - weird patterns like "Сейчас посмотрим" in info delivery are documented forever

**This is the right way to build reliable tooling.**

---

## Update 2025-11-19: Manual Verification Completed

**Status**: Golden dataset updated before tool fix

**Actions Taken**:
1. Manually analyzed call_17 transcript - confirmed 69.71s violation
2. Manually analyzed call_10 transcript - confirmed 46.16s and 51.12s violations  
3. Updated golden dataset: call_10 and call_17 → HIGH confidence
4. Result: **20/20 HIGH confidence (100%)**

**Tool Status**:
- call_17: Tool FAILED (detected 26.9s instead of 69.71s) - BDD tests required
- call_10: Tool SUCCEEDED (detected 46.2s and 51.1s) - regression tests should pass

**Next Steps**:
- Implement BDD tests as specified above
- Fix tool to pass call_17 test
- Verify regression tests still pass for call_02, call_08, call_09, call_10
