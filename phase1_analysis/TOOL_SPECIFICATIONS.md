# Tool Specifications for Ground Truth Extraction

## Overview

This document provides detailed technical specifications for building the tool suite that will extract ground truth from transcripts and improve Sonnet grading accuracy.

---

## Tool 1: `scripts/extract_timing.py`

### Purpose
Extract search duration ground truth for criterion 9.1 (Long Information Search).

### Inputs
1. `transcript-2.vtt` - VTT format transcript with timestamps
2. `paragraphs-2.json` - Paragraph-level segmentation with word-level timing

### Output Format
```json
{
  "call_id": "call_08",
  "total_searches": 5,
  "searches": [
    {
      "search_number": 1,
      "start_timestamp": "00:00:27.869",
      "start_line_number": 32,
      "start_phrase": "Минутку, пожалуйста",
      "start_speaker": "AGENT",
      "end_timestamp": "00:02:03.930",
      "end_line_number": 44,
      "end_phrase": "Спасибо за ожидание, а уточните, пожалуйста",
      "end_speaker": "AGENT",
      "duration_seconds": 96.061,
      "duration_formatted": "1m 36.0s",
      "check_ins": [
        {
          "timestamp": "00:00:56.793",
          "phrase": "Спасибо. Заждание ещё минут, пожалуйста",
          "line_number": 38
        },
        {
          "timestamp": "00:02:00.850",
          "phrase": "А его?",
          "speaker": "CUSTOMER",
          "note": "Customer impatience signal"
        }
      ],
      "assessment": {
        "status": "VIOLATION",
        "threshold_applied": "complex_question_40s",
        "flag_window": false,
        "exceeds_threshold_by": 56.061,
        "grade_impact": 9,
        "coaching_note": "Search exceeded 45s threshold (96s total). Customer showed impatience at 2:00."
      }
    }
  ],
  "summary": {
    "total_duration_all_searches": 180.5,
    "longest_search": 96.061,
    "violations_count": 1,
    "flag_count": 0,
    "pass_count": 4
  }
}
```

### Algorithm

#### Step 1: Identify Search Announcements
**Search phrases (Russian, regex patterns):**
```python
SEARCH_PATTERNS = [
    r"\b(минут[ауеы]?|минуточк[ауеы]?)\b",          # "минуту", "минуточку"
    r"\b(секунд[ауеы]?|секундочк[ауеы]?)\b",        # "секунду"
    r"\b(сейчас|щас)\s+(посмотр[юу]|провер[юу]|уточн[юу])",  # "сейчас посмотрю"
    r"\b(подожд[иеу]те|ждите)\b",                   # "подождите"
    r"\b(давайте|дайте)\s+(я\s+)?посмотр",          # "давайте посмотрю"
]
```

**Speaker filter**: Only AGENT search announcements count (customer waiting ≠ search)

#### Step 2: Identify Answer Delivery End Point
**Filler words to skip (not substantive):**
```python
FILLER_WORDS = [
    "вот",      # here/well
    "так",      # so
    "итак",     # so/thus
    "ну",       # well
    "значит",   # means
    "хорошо",   # okay
    "да",       # yes (when not answering question)
]
```

**Substantive answer indicators:**
```python
ANSWER_PATTERNS = [
    r"\b(есть|нашел|нашла|вижу)\b",                    # "есть", "нашел"
    r"\b(информация|данные|результат)\b",              # "информация"
    r"\b(размер|цена|адрес|телефон|номер)\b",         # domain-specific
    r"\b(спасибо\s+за\s+ожидание)\b",                 # gratitude phrase
]
```

**Logic**:
1. Start from search announcement timestamp
2. Scan forward until AGENT speaks again
3. Skip filler words at start of AGENT utterance
4. Find first word matching ANSWER_PATTERNS OR first content word not in FILLER_WORDS
5. Use that word's timestamp as answer delivery endpoint

#### Step 3: Check-in Detection
**Check-in phrase patterns:**
```python
CHECKIN_PATTERNS = [
    r"(еще|ещё)\s+(немного|чуть-чуть|секунд)",        # "еще немного"
    r"(почти|практически)\s+(готов|нашел)",           # "почти готово"
    r"(продолжаю|ищу|смотрю)",                        # "продолжаю искать"
]
```

**Check-ins do NOT reset timer** - they're tracked separately as `check_ins` array.

#### Step 4: Duration Calculation and Assessment
```python
def assess_search(duration_seconds: float) -> dict:
    if duration_seconds <= 40:
        return {
            "status": "PASS",
            "flag_window": False,
            "grade_impact": None
        }
    elif 40 < duration_seconds <= 45:
        return {
            "status": "FLAG",
            "flag_window": True,
            "grade_impact": 10,  # No score reduction
            "note": "40-45s window: flag for improvement, no penalty"
        }
    else:  # > 45
        return {
            "status": "VIOLATION",
            "flag_window": False,
            "grade_impact": 9,
            "note": f"Exceeds 45s threshold by {duration_seconds - 45:.1f}s"
        }
```

### Test Cases (Validate Against Expert Review)

**call_08:**
- Expected: Search 1 at 00:27-02:03 = 96.061s (VIOLATION)
- Check-ins: 00:56 ("еще минут"), 02:00 (customer "А его?")

**call_11:**
- Expected: Search at 00:36-01:35 = 57s (VIOLATION)
- Sonnet measured ~19s (WRONG), BLIND1 ~20s (WRONG), BLIND2 59s (CORRECT)

**call_13:**
- Expected: Search at 01:13-01:56 = 42.8s (FLAG, no violation)
- Sonnet marked FLAG correctly, BLIND1 missed, BLIND2 over-penalized

**call_07:**
- Expected: Search 2 at 07:34-08:35 = 60.8s (VIOLATION)
- Sonnet/BLIND2 correct, BLIND1 missed

### Usage Example
```bash
# Extract timing for call_08
python scripts/extract_timing.py \
  calls/call_08/transcript-2.vtt \
  calls/call_08/paragraphs-2.json \
  > phase1_analysis/ground_truth/call_08_timing.json

# Validate against grader
python scripts/validate_grading.py \
  --timing-truth phase1_analysis/ground_truth/call_08_timing.json \
  --grading phase1_consolidated/sonnet/call_08/CALL_08_GRADING.json \
  --criterion 9.1
```

---

## Tool 2: `scripts/extract_echo.py`

### Purpose
Extract echo method verification ground truth for criterion 7.2 (Echo Method Not Used).

### Inputs
1. `paragraphs-2.json` - Word-level timing and speaker diarization
2. (Optional) `transcript-2.vtt` - For context verification

### Output Format
```json
{
  "call_id": "call_08",
  "contact_data_collected": [
    {
      "data_type": "name_first",
      "timestamp": "00:00:08.168",
      "line_number": 8,
      "customer_phrase": "Здравствуйте, Дмитрий",
      "value_extracted": "Дмитрий",
      "echo_verification": {
        "operator_repeated": false,
        "repeat_timestamp": null,
        "repeat_phrase": null,
        "confirmation_requested": false,
        "confirmation_phrase": null,
        "customer_confirmed": false,
        "customer_confirmation": null,
        "time_between_collection_and_repeat": null,
        "assessment": "VIOLATION",
        "violation_reason": "Name collected but not repeated back to customer. Operator moved directly to next question without echo."
      }
    },
    {
      "data_type": "phone",
      "timestamp": "00:11:05.000",
      "line_number": 67,
      "customer_phrase": "912-345-6789",
      "value_extracted": "912-345-6789",
      "echo_verification": {
        "operator_repeated": true,
        "repeat_timestamp": "00:11:19.000",
        "repeat_phrase": "Бру-вер. Дмитрий Владимирович",
        "confirmation_requested": true,
        "confirmation_phrase": "верно?",
        "customer_confirmed": true,
        "customer_confirmation": "Да",
        "time_between_collection_and_repeat": 14.0,
        "assessment": "PASS",
        "violation_reason": null
      }
    }
  ],
  "summary": {
    "total_contact_fields": 4,
    "fields_echoed_correctly": 3,
    "fields_violated": 1,
    "violation_fields": ["name_first"],
    "overall_assessment": "VIOLATION",
    "policy_applied": "all_or_nothing",
    "note": "1/4 contact fields not echoed = violation per all-or-nothing rule"
  }
}
```

### Algorithm

#### Step 1: Identify Contact Data Collection
**Contact data types:**
```python
CONTACT_DATA_TYPES = {
    "name_first": [r"\b(меня\s+зовут|я\s+)?[А-ЯЁ][а-яё]+(?=\s|$)", r"как\s+(вас|тебя)\s+зовут"],
    "name_last": [r"\b(фамилия|отчество)\b", r"[А-ЯЁ][а-яё]+ович|[А-ЯЁ][а-яё]+овна"],
    "phone": [r"\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b", r"номер\s+телефона"],
    "email": [r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"],
    "city": [r"из\s+какого\s+города", r"\b(город|регион)\b"],
    "address": [r"адрес\s+доставки", r"улица.*дом.*квартира"],
    "inn": [r"\b\d{10,12}\b", r"ИНН"],
}
```

**Detection logic:**
1. Scan CUSTOMER utterances for contact data patterns
2. Note timestamp when customer provides data
3. Track data type and extracted value

#### Step 2: Verify 3-Step Echo Within 10-Second Window
**For each contact data item collected:**

```python
def verify_echo(contact_data, transcript_after_collection):
    """
    Verify echo method compliance within 10s window after collection.

    Returns: dict with echo verification details
    """
    # Step 1: Operator must repeat within 10s
    operator_repeat = find_operator_repeat(
        contact_data.value,
        transcript_after_collection,
        time_window=10.0
    )

    if not operator_repeat:
        return {
            "assessment": "VIOLATION",
            "violation_reason": "Contact data not repeated back to customer"
        }

    # Step 2: Operator must ask confirmation immediately after repeat
    confirmation_patterns = [r"верно\?", r"правильно\?", r"подтвержда(ю|ешь|ете)\?"]
    confirmation = find_pattern_near_timestamp(
        operator_repeat.end_timestamp,
        confirmation_patterns,
        max_gap=5.0  # Must be within same or next utterance
    )

    if not confirmation:
        return {
            "assessment": "VIOLATION",
            "violation_reason": "Contact data repeated but no confirmation requested"
        }

    # Step 3: Customer must confirm within 5s
    customer_confirmation_patterns = [r"\bда\b", r"\bверно\b", r"\bугу\b", r"\bправильно\b"]
    customer_confirm = find_customer_response(
        confirmation.timestamp,
        customer_confirmation_patterns,
        time_window=5.0
    )

    if not customer_confirm:
        return {
            "assessment": "VIOLATION",
            "violation_reason": "Confirmation requested but customer did not confirm"
        }

    # All 3 steps passed
    return {
        "assessment": "PASS",
        "violation_reason": null
    }
```

#### Step 3: All-or-Nothing Assessment
```python
def assess_overall_echo_compliance(contact_data_items):
    """Apply all-or-nothing rule for 7.2 assessment."""
    violated_fields = [
        item for item in contact_data_items
        if item.echo_verification.assessment == "VIOLATION"
    ]

    if len(violated_fields) > 0:
        return {
            "overall_assessment": "VIOLATION",
            "policy_applied": "all_or_nothing",
            "note": f"{len(violated_fields)}/{len(contact_data_items)} fields not echoed = violation"
        }
    else:
        return {
            "overall_assessment": "PASS",
            "policy_applied": "all_or_nothing"
        }
```

### Test Cases (Validate Against Expert Review)

**call_08:**
- Expected: Name "Дмитрий" at 00:08 NOT echoed (VIOLATION)
- Phone at 11:19 echoed correctly (PASS for this field)
- Overall: VIOLATION (all-or-nothing)

**call_01:**
- Expected: Name "Алексей" at 00:14 NOT echoed (VIOLATION)
- City "Усть-Катав" NOT echoed (VIOLATION)
- Phone echoed correctly (PASS for this field)
- Overall: VIOLATION

**call_20:**
- Expected: Name "Дмитрий" at 00:03 NOT echoed (VIOLATION)
- Sonnet/BLIND1 correct (VIOLATION), BLIND2 missed

---

## Tool 3: `scripts/extract_gratitude.py`

### Purpose
Extract gratitude phrase detection ground truth for criterion 9.3 (No Thank You for Waiting).

### Inputs
1. `transcript-2.vtt` - VTT transcript
2. `timing.json` - Output from `extract_timing.py` (list of searches)

### Output Format
```json
{
  "call_id": "call_07",
  "searches": [
    {
      "search_number": 1,
      "duration_seconds": 22.7,
      "end_timestamp": "00:01:20.573",
      "gratitude_check": {
        "required": true,
        "rationale": "Search duration 22.7s > 10s threshold",
        "gratitude_found": false,
        "gratitude_phrase": null,
        "gratitude_timestamp": null,
        "time_after_search": null,
        "assessment": "VIOLATION",
        "violation_note": "Search completed without gratitude. Operator delivered answer directly ('Да, есть шины...') without thanking customer."
      }
    },
    {
      "search_number": 2,
      "duration_seconds": 60.8,
      "end_timestamp": "00:08:35.565",
      "gratitude_check": {
        "required": true,
        "rationale": "Search duration 60.8s > 10s threshold",
        "gratitude_found": true,
        "gratitude_phrase": "За ожидание",
        "gratitude_timestamp": "00:08:35.565",
        "time_after_search": 0.0,
        "assessment": "QUESTIONABLE",
        "violation_note": "Truncated gratitude ('За ожидание' missing 'Спасибо'). Acceptable per lenient interpretation, but borderline."
      }
    }
  ],
  "summary": {
    "total_searches": 2,
    "searches_requiring_gratitude": 2,
    "searches_with_gratitude": 1,
    "violations_count": 1,
    "overall_assessment": "VIOLATION",
    "note": "At least one search >10s completed without gratitude = violation"
  }
}
```

### Algorithm

#### Step 1: Filter Searches Requiring Gratitude
```python
def search_requires_gratitude(search_duration: float) -> bool:
    """Only searches >10s require explicit gratitude."""
    return search_duration > 10.0
```

#### Step 2: Detect Gratitude Phrases Within 5s After Search
**Acceptable gratitude patterns (Russian):**
```python
GRATITUDE_PATTERNS = [
    # Explicit (always acceptable)
    r"спасибо\s+за\s+(ожидание|терпение|время)",
    r"благодарю\s+за\s+(ожидание|терпение|что\s+подождали)",
    r"спасибо,?\s+что\s+подождали",

    # Embedded (acceptable if gratitude clear)
    r"спасибо[,\s]+(нашел|вот|итак)",
    r"благодарю[,\s]+",

    # Borderline (may be acceptable depending on context)
    r"за\s+ожидание",  # Truncated, missing "спасибо"
    r"спасибо\s+за\s+звонок",  # Generic, but may count
]

# NOT acceptable (no gratitude)
NON_GRATITUDE = [
    r"^вот$",
    r"^нашел$",
    r"^итак$",
    r"^так$",
]
```

**Detection logic:**
```python
def find_gratitude_after_search(search_end_timestamp, transcript, time_window=5.0):
    """
    Look for gratitude phrase within 5s after search ends.

    Returns: dict with gratitude details or None
    """
    search_end_time = parse_timestamp(search_end_timestamp)
    window_end_time = search_end_time + time_window

    # Scan AGENT utterances in window
    for utterance in transcript:
        if utterance.speaker != "AGENT":
            continue
        if not (search_end_time <= utterance.timestamp <= window_end_time):
            continue

        # Check for gratitude patterns
        for pattern in GRATITUDE_PATTERNS:
            match = re.search(pattern, utterance.text, re.IGNORECASE)
            if match:
                return {
                    "found": True,
                    "phrase": match.group(0),
                    "timestamp": utterance.timestamp,
                    "pattern_matched": pattern
                }

    return {"found": False}
```

#### Step 3: Multi-Search Handling
**Rule**: EACH search >10s requires SEPARATE gratitude.

```python
def assess_multi_search(searches_with_gratitude_check):
    """
    Check if operator thanked after EVERY search >10s.

    Violation if ANY search >10s lacks gratitude.
    """
    violations = [
        search for search in searches_with_gratitude_check
        if search.gratitude_check.required and not search.gratitude_check.gratitude_found
    ]

    if violations:
        return {
            "overall_assessment": "VIOLATION",
            "violations_count": len(violations),
            "note": f"{len(violations)} search(es) >10s completed without gratitude"
        }
    else:
        return {
            "overall_assessment": "PASS",
            "note": "All searches >10s followed by gratitude"
        }
```

### Test Cases (Validate Against Expert Review)

**call_07:**
- Expected: Search 1 (22.7s) NO gratitude (VIOLATION)
- Expected: Search 2 (60.8s) truncated "За ожидание" (questionable, BLIND2 marked VIOLATION)
- Overall: VIOLATION

**call_14:**
- Expected: Search (37s) NO gratitude (VIOLATION)
- Sonnet/BLIND2 correct, BLIND1 too lenient

**call_20:**
- Expected: Two searches without gratitude (VIOLATION × 2)
- Sonnet caught both, BLIND1 hallucinated gratitude

**call_12:**
- Expected: Searches 20-25s, borderline for gratitude requirement
- Sonnet PASS (reasonable for brief searches), BLIND2 VIOLATION (strict)

---

## Tool 4: `scripts/validate_grading.py`

### Purpose
Compare grader assessments against extracted ground truth and produce accuracy scores.

### Inputs
1. `--timing-truth call_XX_timing.json` - Ground truth timing
2. `--echo-truth call_XX_echo.json` - Ground truth echo verification
3. `--gratitude-truth call_XX_gratitude.json` - Ground truth gratitude
4. `--sonnet CALL_XX_GRADING.json` - Sonnet grading
5. `--blind1 CALL_XX_BLIND.json` - BLIND1 grading
6. `--blind2 CALL_XX_BLIND2.json` - BLIND2 grading

### Output Format
```json
{
  "call_id": "call_08",
  "ground_truth": {
    "7.2_status": "VIOLATION",
    "9.1_status": "VIOLATION",
    "9.3_status": "PASS",
    "final_grade": 7
  },
  "grader_accuracy": {
    "sonnet": {
      "7.2": {"grader_status": "VIOLATION", "correct": true, "score": 1.0},
      "9.1": {"grader_status": "PASS", "correct": false, "score": 0.0},
      "9.3": {"grader_status": "PASS", "correct": true, "score": 1.0},
      "final_grade": {"grader_grade": 7, "correct": true, "score": 1.0},
      "overall_score": 0.75,
      "accuracy_pct": 75.0
    },
    "blind1": {
      "7.2": {"grader_status": "VIOLATION", "correct": true, "score": 1.0},
      "9.1": {"grader_status": "PASS", "correct": false, "score": 0.0},
      "9.3": {"grader_status": "PASS", "correct": true, "score": 1.0},
      "final_grade": {"grader_grade": 7, "correct": true, "score": 1.0},
      "overall_score": 0.75,
      "accuracy_pct": 75.0
    },
    "blind2": {
      "7.2": {"grader_status": "PASS", "correct": false, "score": 0.0},
      "9.1": {"grader_status": "VIOLATION", "correct": true, "score": 1.0},
      "9.3": {"grader_status": "PASS", "correct": true, "score": 1.0},
      "final_grade": {"grader_grade": 9, "correct": false, "score": 0.0},
      "overall_score": 0.50,
      "accuracy_pct": 50.0
    }
  },
  "recommendation": {
    "best_grader": "sonnet",
    "best_score": 0.75,
    "tied": ["sonnet", "blind1"],
    "golden_source": "sonnet",
    "rationale": "Sonnet and BLIND1 tied at 75% accuracy, but Sonnet has more detailed evidence. Use Sonnet with note that 9.1 also violated."
  },
  "discrepancies": [
    {
      "criterion": "9.1",
      "ground_truth": "VIOLATION (96s search)",
      "sonnet": "PASS (measured 3.2s - measurement error)",
      "blind1": "PASS (missed violation)",
      "blind2": "VIOLATION (correct)",
      "note": "Sonnet and BLIND1 both missed 96s search. BLIND2 most accurate on timing."
    },
    {
      "criterion": "7.2",
      "ground_truth": "VIOLATION (name not echoed)",
      "sonnet": "VIOLATION (correct)",
      "blind1": "VIOLATION (correct)",
      "blind2": "PASS (missed violation at call start)",
      "note": "BLIND2 only looked at formal data collection later, missed initial name violation."
    }
  ]
}
```

### Usage Example
```bash
# Validate call_08
python scripts/validate_grading.py \
  --timing-truth phase1_analysis/ground_truth/call_08_timing.json \
  --echo-truth phase1_analysis/ground_truth/call_08_echo.json \
  --gratitude-truth phase1_analysis/ground_truth/call_08_gratitude.json \
  --sonnet phase1_consolidated/sonnet/call_08/CALL_08_GRADING.json \
  --blind1 phase1_consolidated/blind1/call_08/CALL_08_BLIND.json \
  --blind2 phase1_consolidated/blind2/call_08/CALL_08_BLIND2.json \
  > phase1_analysis/grader_accuracy/call_08_comparison.json
```

---

## Tool 5: `scripts/generate_consolidated_context.py`

### Purpose
Generate single-file grading context for Sonnet that includes all necessary information plus pre-computed ground truth.

### Inputs
1. `calls/call_XX/` - Call directory
2. `phase1_analysis/ground_truth/call_XX_*.json` - Pre-computed ground truth

### Output
Single markdown file with ALL context Sonnet needs:

```markdown
# GRADING CONTEXT FOR CALL_XX

## TRANSCRIPT
[Full VTT content]

## PRE-COMPUTED TIMING DATA (Use this for 9.1 grading)
```json
{
  "searches": [...]
}
```

**Instructions for 9.1:**
- Search 1: 96s (VIOLATION - exceeds 45s threshold)
- Do NOT re-measure manually, use provided timing data
- Grade: 9 (violation applies)

## PRE-COMPUTED ECHO DATA (Use this for 7.2 grading)
```json
{
  "contact_data_collected": [...]
}
```

**Instructions for 7.2:**
- Name "Дмитрий" collected at 00:08, NOT echoed (VIOLATION)
- Phone collected at 11:19, echoed correctly (PASS for this field)
- Overall: VIOLATION (all-or-nothing rule - 1/4 fields not echoed)

## PRE-COMPUTED GRATITUDE DATA (Use this for 9.3 grading)
```json
{
  "searches": [...]
}
```

**Instructions for 9.3:**
- All searches >10s had gratitude (PASS)

## GRADING SPEC
[Criteria 7.2, 9.1, 9.3 with examples from Deliverable D]

## YOUR TASK
Grade this call using the 17-criteria system.
For criteria 7.2, 9.1, 9.3: USE PRE-COMPUTED DATA ABOVE.
For other criteria: Grade as usual from transcript.
```

### Usage
```bash
python scripts/generate_consolidated_context.py \
  --call-id call_08 \
  --output consolidated/call_08_context.md
```

Then use with Sonnet:
```bash
claude --model sonnet < consolidated/call_08_context.md
```

---

## Testing Strategy

### Phase 1: Unit Tests for Each Tool

**`test_extract_timing.py`:**
```python
def test_call_08_96s_search():
    """Verify tool detects 96s search in call_08."""
    result = extract_timing("calls/call_08/transcript-2.vtt", "calls/call_08/paragraphs-2.json")
    assert result["searches"][0]["duration_seconds"] == pytest.approx(96.061, abs=1.0)
    assert result["searches"][0]["assessment"]["status"] == "VIOLATION"

def test_call_13_flag_window():
    """Verify tool correctly identifies 40-45s flag window."""
    result = extract_timing("calls/call_13/transcript-2.vtt", "calls/call_13/paragraphs-2.json")
    assert 40 < result["searches"][0]["duration_seconds"] < 45
    assert result["searches"][0]["assessment"]["flag_window"] == True
    assert result["searches"][0]["assessment"]["grade_impact"] == 10  # No score reduction
```

**`test_extract_echo.py`:**
```python
def test_call_08_name_violation():
    """Verify tool detects name not echoed in call_08."""
    result = extract_echo("calls/call_08/paragraphs-2.json")
    name_item = [item for item in result["contact_data_collected"] if item["data_type"] == "name_first"][0]
    assert name_item["echo_verification"]["assessment"] == "VIOLATION"
    assert name_item["echo_verification"]["operator_repeated"] == False
```

### Phase 2: Integration Tests Against Expert Review

**`test_validate_against_expert_review.py`:**
```python
def test_call_07_matches_expert_review():
    """Verify tools produce same findings as expert review for call_07."""
    # Load expert review finding from golden decisions JSON
    expert_finding = load_expert_finding("call_07")
    assert expert_finding["golden_source"] == "BLIND2"
    assert "60.8s search" in expert_finding["transcript_evidence"]

    # Run tools
    timing = extract_timing("calls/call_07/...")
    gratitude = extract_gratitude("calls/call_07/...", timing)

    # Verify tools match expert review
    assert timing["searches"][1]["duration_seconds"] == pytest.approx(60.8, abs=1.0)
    assert timing["searches"][1]["assessment"]["status"] == "VIOLATION"
    assert gratitude["searches"][0]["gratitude_check"]["assessment"] == "VIOLATION"
```

### Phase 3: End-to-End Validation

Run full pipeline on all 20 calls and verify golden decisions match expert review:

```bash
#!/bin/bash
# test_full_pipeline.sh

for call_id in call_{01..20}; do
    echo "Processing $call_id..."

    # Extract ground truth
    python scripts/extract_timing.py calls/$call_id/transcript-2.vtt calls/$call_id/paragraphs-2.json > truth/timing.json
    python scripts/extract_echo.py calls/$call_id/paragraphs-2.json > truth/echo.json
    python scripts/extract_gratitude.py calls/$call_id/transcript-2.vtt truth/timing.json > truth/gratitude.json

    # Validate graders
    python scripts/validate_grading.py \
        --timing-truth truth/timing.json \
        --echo-truth truth/echo.json \
        --gratitude-truth truth/gratitude.json \
        --sonnet phase1_consolidated/sonnet/$call_id/CALL_${call_id^^}_GRADING.json \
        --blind1 phase1_consolidated/blind1/$call_id/CALL_${call_id^^}_BLIND.json \
        --blind2 phase1_consolidated/blind2/$call_id/CALL_${call_id^^}_BLIND2.json \
        > validation/$call_id.json

    # Compare to expert review
    python scripts/compare_to_expert_review.py \
        validation/$call_id.json \
        phase1_analysis/sonnet_haiku_blind_core_decisions.json \
        --call-id $call_id
done

echo "Pipeline validation complete. Check validation/*.json for results."
```

---

## Success Criteria

**Tool 1 (extract_timing.py) passes when:**
- ✅ Detects 96s search in call_08 (currently missed by Sonnet/BLIND1)
- ✅ Detects 57s search in call_11 (currently missed by Sonnet/BLIND1)
- ✅ Detects 42.8s FLAG in call_13 (currently Sonnet correct, BLIND1 missed)
- ✅ Detects 60.8s search in call_07 (currently BLIND2 correct, BLIND1 missed)

**Tool 2 (extract_echo.py) passes when:**
- ✅ Detects name violation in call_08 at 00:08 (Sonnet/BLIND1 correct, BLIND2 missed)
- ✅ Detects name violation in call_01 (partial echo pattern)
- ✅ Detects name violation in call_20 (Sonnet correct, BLIND2 missed)

**Tool 3 (extract_gratitude.py) passes when:**
- ✅ Detects missing gratitude in call_07 search 1 (BLIND2 correct, Sonnet/BLIND1 missed)
- ✅ Detects missing gratitude in call_14 (Sonnet/BLIND2 correct, BLIND1 missed)
- ✅ Detects both missing gratitudes in call_20 (Sonnet correct)

**Tool 4 (validate_grading.py) passes when:**
- ✅ Produces accuracy scores matching expert review findings
- ✅ Identifies call_07, call_11 as BLIND2 best (most accurate timing)
- ✅ Identifies call_13, call_14, call_20 as Sonnet best (most comprehensive)
- ✅ Identifies call_08 as hybrid (Sonnet best overall despite 9.1 miss)

**Tool 5 (generate_consolidated_context.py) passes when:**
- ✅ Sonnet grading with consolidated context matches ground truth on 9.1, 9.3, 7.2
- ✅ No manual timing measurement needed (pre-computed data used)
- ✅ Grading accuracy improves from ~70% to >90%

---

## Implementation Priority

**Week 1:**
1. `extract_timing.py` (highest impact - fixes 9.1 disagreements)
2. `validate_grading.py` (needed to verify tool 1 works)

**Week 2:**
3. `extract_echo.py` (medium impact - verifies 7.2)
4. `extract_gratitude.py` (medium impact - verifies 9.3)

**Week 3:**
5. `generate_consolidated_context.py` (integration - puts it all together)
6. End-to-end testing and validation

**Deliverable**: Production-ready tool suite for ground truth extraction and Sonnet grading assistance.
