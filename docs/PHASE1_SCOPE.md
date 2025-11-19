# PHASE 1 GRADING SCOPE

## YOUR ASSIGNMENT

You are grading Russian contact center calls using the **17-criterion evaluation system** for protocol compliance and conversation quality.

This document defines what you will assess and the data sources available to you.

---

## THE 17 GRADING CRITERIA

### GRADE 7 - Process Violations (4 criteria)

**7.1 - Script Violations**
- Wrong greeting/closing format
- Question sequence not followed
- Required questions not asked

**7.2 - Echo Method Not Used** ⭐ CRITICAL
- When recording contact data (name, phone, address, email)
- Operator must repeat back AND ask for confirmation
- Example: "Ваш номер 912-778-1421, верно?"

**7.3 - 5-Second Timing Rules**
- Intro: Must start within 5 seconds of call start
- Outro: Must disconnect within 5 seconds after conversation ends

**7.4 - Interruption Without Apology**
- Cutting off customer mid-sentence
- OK if operator says "Извините, что перебиваю"

---

### GRADE 6 - Critical Issues (1 criterion)

**6.1 - Critical Silence / Customer Hangup**
- Silence >45 seconds causing customer to hang up
- Call received but customer didn't wait for operator

---

### GRADE 9 - Search Issues (2 criteria)

**9.1 - Long Information Search**
- Standard questions: Answer within 3 seconds
- Complex questions: Answer within 40 seconds
- **40-45 seconds: FLAG for improvement (NO score reduction)**
- **>45 seconds: Score reduction applies**
- Timer: From "Сейчас посмотрю" to information delivery start

**9.3 - No Thank You for Waiting**
- After search completes, must thank customer
- Required even if operator checked in during search

---

### GRADE 3 - Serious Issues (3 criteria)

**3.1 - Unresolved Customer Request**
- Customer question goes unanswered
- Customer need not met by end of call
- Workaround provided but root cause not resolved

**3.3 - Confidential Information Disclosure**
- Office phone numbers shared
- Internal codes/passwords disclosed
- Personal data given without ID verification

**3.6 - Unverified Information**
- Giving info "from memory" without system check
- Applies when strict verification required

---

### GRADE 5 - Incomplete Work (1 criterion)

**5.1 - Incomplete Information**
- Missing mandatory info: addresses, hours, phone numbers
- Booking/incident numbers not provided

---

### GRADE 10 - Baseline Quality (3 criteria)

**10.2 - Script Work**
- Information provided per approved script
- Logical presentation and flow

**10.3 - Dialogue Management**
- Uses customer name consistently
- Builds rapport, maintains conversation control
- Proper opening and closing

**10.6 - Information Completeness**
- Accurate project information delivered
- Confident command of details

---

### GRADE 2 - Service Failure (1 criterion)

**2.1 - Call Dropout / Service Refusal**
- Operator disconnects without reason
- Operator refuses service despite having information

---

### GRADE 1 - Gross Misconduct (1 criterion)

**1.1 - Rudeness / Profanity**
- Harsh language from operator
- Profanity or yelling
- Note: Can detect profanity in text, full tone assessment would need audio

---

### GRADE 4 - Customer Handling (1 criterion - Partial)

**4.1 - Difficult Customer Handling**
- Cannot handle rude/talkative/slow/rushed customers
- Note: Text shows behavior indicators, full assessment needs audio
- Use text evidence only, note limitations

---

## GRADING RULES

### 1. Lowest Code Principle
If violations at grades [9, 7, 5] detected → final grade = 5 (always lowest)

### 2. 40-45 Second Flag Window
- Search 0-40s: PASS
- Search 40-45s: FLAG for improvement (NO score reduction)
- Search >45s: VIOLATION (score reduction)

### 3. Confidence Levels
- **VERY_HIGH** (0.90+): Auto-grade, objective measurement
- **HIGH** (0.75+): Auto-grade, clear pattern
- **MEDIUM** (0.50+): Flag for manager review
- **LOW** (<0.50): Note indicators only, don't penalize

### 4. Evidence Required
Every violation needs:
- Criterion code (e.g., "7.2")
- Timestamp (MM:SS.sss)
- Evidence (quote from transcript)
- Confidence score (0.0-1.0)

---

## YOUR DATA SOURCES

### What You Have:

**VTT/SRT Transcripts**
- Line-level timestamps (±0.5 second accuracy)
- Speaker diarization (Agent/Customer)
- Full conversation text
- Sufficient for most criteria

**Word-Level JSON** (for criterion 7.2 only)
- Millisecond-precision timestamps
- Required for echo method detection
- Enables 10-second window tracking

### What You Don't Have:

**Audio Features**
- Pitch variance, WPM, SNR
- Affects 1 criterion: Some aspects of 4.1 (tone detection)
- Use text evidence where available

---

## ASSESSMENT APPROACH

### For Each Call:

1. **Load transcript** (VTT/SRT + word-level JSON)
2. **Check all 17 criteria** systematically
3. **Collect violations** with confidence scores
4. **Apply lowest code rule** to HIGH/VERY_HIGH violations
5. **Flag MEDIUM confidence** for manager review
6. **Generate coaching** with specific timestamps

### Confidence-Based Decisions:

**AUTO-GRADE** (No review needed):
- 7.1, 7.2, 7.3, 7.4 (VERY_HIGH/HIGH)
- 9.1, 9.3 (HIGH)
- 6.1 (HIGH)
- 2.1, 3.3 (HIGH)
- 10.2, 10.3 (HIGH)

**FLAG FOR REVIEW** (Manager confirms):
- 3.1 (MEDIUM - borderline cases)
- 3.6 (MEDIUM - if strict verification unclear)
- 5.1 (MEDIUM - without project config)

**NOTE ONLY** (Don't penalize):
- 1.1 (LOW - text profanity detected but tone unclear)
- 4.1 (LOW - text indicators only)

---

## OUTPUT FORMAT

Return JSON with these sections:

1. **call_metadata** - Basic call info
2. **final_scoring** - Grade, confidence, violations
3. **violations_detected** - Array with evidence
4. **violations_summary** - Stats by grade
5. **coaching_priorities** - Ranked improvements
6. **risk_assessment** - Compliance/satisfaction/security
7. **detected_patterns** - Search/timing/echo/script
8. **criteria_assessment** - Status per criterion
9. **positive_observations** - What operator did well
10. **data_quality** - Sources used, confidence notes

See `phase1_output_format_v2.json` for complete schema and examples.

---

## CRITICAL REMINDERS

✓ Check all 17 criteria on every call
✓ Use lowest code principle for final grade
✓ 40-45s search = flag only (no score reduction)
✓ Every violation needs timestamp + evidence
✓ Auto-grade HIGH confidence, flag MEDIUM for review
✓ Echo method (7.2) requires word-level JSON precision
✓ Customer profanity ≠ violation (only operator rudeness)
✓ Provide specific, actionable coaching recommendations

---

## EXPECTED COVERAGE

With transcript data alone, you can assess:
- **Process violations** (Grade 7): 100% coverage
- **Critical issues** (Grade 6): 100% coverage
- **Search issues** (Grade 9): 67% coverage (2 of 3)
- **Serious issues** (Grade 3): Partial coverage (3 criteria)
- **Baseline quality** (Grade 10): Partial coverage (3 criteria)
- **Service failures** (Grades 1-2): 100% coverage

**Overall**: Reliable grading for protocol compliance and conversation quality.

---

## GETTING STARTED

1. Read `PHASE1_PACKAGE_GUIDE.md` for workflow
2. Review `Quick_Reference_Grades_EN_PHASE1.md` for quick lookup
3. Use `prompt_for_transcript_only_grading.txt` for LLM grading
4. Check example outputs in `phase1_output_format_v2.json`
5. Start grading calls in the `calls/` directory

**Questions?** See `PHASE1_PACKAGE_GUIDE.md` troubleshooting section.

---

*Evaluation System: СО 2024 ВТМ v2024.09*  
*Scope: Transcript-based protocol compliance grading*  
*Last Updated: 2025-11-19*
