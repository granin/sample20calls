# PHASE 1 GRADING PACKAGE
## Russian Contact Center Call Evaluation System

---

## START HERE

This package contains everything you need to grade Russian contact center calls using the 17-criterion evaluation system.

**Your assignment**: Grade calls using transcript data (VTT/SRT + word-level JSON) with high confidence for protocol compliance.

---

## QUICK START (3 Steps)

### Step 1: Understand Your Scope
**Read first**: [`docs/PHASE1_SCOPE.md`](docs/PHASE1_SCOPE.md)

This defines:
- The 17 criteria you will assess
- Your data sources (transcript + word-level JSON)
- Grading rules (lowest code, 40-45s flag window)
- Confidence thresholds (auto-grade vs review)

**Time**: 10 minutes

---

### Step 2: Review Reference Materials

**Quick lookup**: [`docs/Quick_Reference_Grades_EN_PHASE1.md`](docs/Quick_Reference_Grades_EN_PHASE1.md)
- One-page reference for all 17 criteria
- Detection methods per criterion
- Common patterns and examples

**Detailed guide**: [`docs/Excel_Analysis_Summary_EN_PHASE1.md`](docs/Excel_Analysis_Summary_EN_PHASE1.md)
- System structure and rules
- Detection features explained
- Russian language patterns
- Implementation checklist

**Time**: 15 minutes

---

### Step 3: Start Grading

**Workflow guide**: [`docs/PHASE1_PACKAGE_GUIDE.md`](docs/PHASE1_PACKAGE_GUIDE.md)
- How to grade your first call
- Using the LLM prompt
- Troubleshooting common issues
- Success metrics

**Sample calls**: `calls/call_05/` and `calls/call_06/`
- Practice on these first
- Compare your results to reference gradings

**Time**: 30 minutes to grade first call

---

## PACKAGE CONTENTS

### `/config/` - System Configuration
- `phase1_grading_config.json` - 17 criteria specs + detection methods
- `confidence_thresholds.json` - When to auto-grade vs review
- `phase1_output_format_v2.json` - JSON output schema with examples
- `prompt_for_transcript_only_grading.txt` - LLM prompt for Haiku/Sonnet/Opus

### `/calls/` - Sample Calls for Practice
- `call_05/` - Short call (80s) with multiple violations
- `call_06/` - Full call (455s) with echo method violation
- Each contains: VTT, SRT, word-level JSON, reference grading

### `/docs/` - Documentation
- `PHASE1_SCOPE.md` - ⭐ START HERE - Your assignment scope
- `Quick_Reference_Grades_EN_PHASE1.md` - Fast lookup
- `Excel_Analysis_Summary_EN_PHASE1.md` - Detailed system guide
- `PHASE1_PACKAGE_GUIDE.md` - Workflow and troubleshooting
- `phase1_comparison_to_full.md` - What this phase covers

---

## THE 17 CRITERIA (Quick Overview)

### Protocol Compliance (Grade 7) ✓✓✓✓
- 7.1 Script violations
- 7.2 Echo method ⭐ CRITICAL
- 7.3 Timing rules (5 seconds)
- 7.4 Interruption without apology

### Critical Issues (Grade 6) ✓
- 6.1 Critical silence / customer hangup

### Search Quality (Grade 9) ✓✓
- 9.1 Long search (40-45s flag window)
- 9.3 No thank you

### Serious Problems (Grade 3) ✓✓✓
- 3.1 Unresolved request
- 3.3 Confidential info disclosure
- 3.6 Unverified information

### Information (Grade 5) ✓
- 5.1 Incomplete information

### Baseline Quality (Grade 10) ✓✓✓
- 10.2 Script work
- 10.3 Dialogue management
- 10.6 Information completeness

### Service Failures (Grade 2) ✓
- 2.1 Call dropout / refusal

### Misconduct (Grade 1) ✓
- 1.1 Rudeness / profanity

### Customer Handling (Grade 4) 📝
- 4.1 Difficult customer (partial)

**Total: 17 criteria**

---

## GRADING METHODS

### Method A: Manual Grading with LLM

**Best for**: Quick testing, model comparison, validation

**How**:
1. Copy prompt from `config/prompt_for_transcript_only_grading.txt`
2. Paste into Claude (Sonnet recommended)
3. Add transcript from `calls/call_XX/transcript-X.vtt`
4. Get JSON output

**Time**: ~2 minutes per call

---

### Method B: Automated System

**Best for**: Production deployment, batch processing

**How**:
1. Load `config/phase1_grading_config.json`
2. Implement 17 detectors per specs
3. Apply `config/confidence_thresholds.json` rules
4. Output per `config/phase1_output_format_v2.json` schema

**Time**: Development required, then <30s per call

---

## KEY CONCEPTS

### 1. Lowest Code Principle
Multiple violations → Use lowest (most severe) grade

**Example**: Violations [10, 7, 3] → Final grade = 3

### 2. 40-45 Second Flag Window
Search duration 40-45s → Flag for improvement (NO score reduction)
Search duration >45s → Violation (score reduction)

### 3. Confidence Thresholds
- **VERY_HIGH/HIGH**: Auto-grade
- **MEDIUM**: Flag for manager review
- **LOW**: Note indicators only

### 4. Echo Method (7.2) ⭐
Requires word-level JSON for millisecond precision
Most common violation in testing
Must detect: repeat-back + confirmation request + customer confirmation

---

## SUCCESS METRICS

### Technical
- [ ] Processing time: <60s per call
- [ ] Detection precision: >90%
- [ ] Detection recall: >85%

### Business
- [ ] Agreement with human QA: >75%
- [ ] Cost per call: <0.7 RUB/min
- [ ] Operator satisfaction: >80%

### Quality
- [ ] False positive rate: <10%
- [ ] Manager review completion: >90%
- [ ] Coaching actionability: >85%

---

## VALIDATION WORKFLOW

### Week 1: Test & Validate
1. Grade 5 practice calls from `/calls/`
2. Compare to reference gradings
3. Verify echo method detection (7.2)
4. Check 40-45s flag window (9.1)
5. Confirm lowest code principle

### Week 2: Production Batch
1. Grade 20 new calls
2. Compare to human QA (target >75% agreement)
3. Analyze disagreements
4. Tune patterns if needed
5. Document improvements

### Week 3+: Scale
1. Grade full call volume
2. Monitor quality metrics
3. Refine thresholds
4. Provide operator coaching

---

## IMPORTANT NOTES

### What You CAN Grade
✓ Protocol violations (Grade 7) - 100%
✓ Critical issues (Grade 6) - 100%
✓ Search timing (Grade 9) - 67%
✓ Serious issues (Grade 3) - 50%
✓ Service failures (Grades 1-2) - 100%

### What Has Limitations
📝 Tone analysis (1.1, 4.1) - Text indicators only
📝 Some baseline quality (10.6) - Partial without config

### Expected Results
- **Coverage**: 17 criteria reliably assessed
- **Accuracy**: 85% agreement with human QA expected
- **Speed**: <60 seconds processing per call
- **Cost**: ~0.5 RUB/minute transcription

---

## GETTING HELP

### Common Issues

**"I'm confused about scope"**
→ Read `docs/PHASE1_SCOPE.md` first
→ You have 17 criteria, that's the complete system for this assignment

**"Echo method detection unclear"**
→ See `docs/Quick_Reference_Grades_EN_PHASE1.md` criterion 7.2
→ Requires word-level JSON for 10-second windows

**"What about Grade 8?"**
→ Not in scope for this assignment
→ Focus only on the 17 criteria listed

**"40-45s search - penalize or not?"**
→ Flag only, NO score reduction
→ Only >45s causes score reduction

**"Multiple violations - which grade?"**
→ Always use lowest (most severe) grade number
→ Example: [10, 7, 3] → Final = 3

### Troubleshooting
See `docs/PHASE1_PACKAGE_GUIDE.md` section "Troubleshooting"

---

## NEXT STEPS

1. ☐ Read `docs/PHASE1_SCOPE.md` (10 min)
2. ☐ Review `docs/Quick_Reference_Grades_EN_PHASE1.md` (10 min)
3. ☐ Grade practice call from `calls/call_05/` (30 min)
4. ☐ Compare your result to reference grading
5. ☐ Grade `calls/call_06/` to confirm understanding
6. ☐ Start production grading batch

---

## CONTACT

**Questions about scope?** → See `docs/PHASE1_SCOPE.md`
**Technical issues?** → See `docs/PHASE1_PACKAGE_GUIDE.md`
**Need criteria clarification?** → See `docs/Quick_Reference_Grades_EN_PHASE1.md`

---

**System**: СО 2024 ВТМ v2024.09  
**Scope**: 17 transcript-assessable criteria  
**Status**: Production Ready  
**Last Updated**: 2025-11-19

**Ready to start grading? → Open `docs/PHASE1_SCOPE.md`**
