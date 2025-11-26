# Task Tracking - BDD Approach

This directory contains task specifications using **Behavior Driven Development (BDD)** methodology.

## Active Tasks

| ID | Title | Status | Priority | Files Affected |
|----|-------|--------|----------|----------------|
| [TASK-001](TASK_001_FIX_TIMING_EXTRACTION_EDGE_CASES.md) | Fix Timing Extraction Edge Cases | OPEN | HIGH | `scripts/extract_timing.py` |

## Quick Reference

### TASK-001: Fix Timing Extraction

**Problem**: Tool incorrectly detected call_17 search as 26.9s (PASS) when actual duration is 69.71s (VIOLATION)

**Root Cause**: Tool missed search announcement at line 25, incorrectly detected line 32 as search start

**Solution**: BDD test-driven fix using `behave` framework

**Key Edge Cases Documented**:
1. Multiple search patterns in same utterance
2. "Сейчас посмотрим" during information delivery (NOT a new search)
3. Agent check-ins during active search
4. Customer interruptions during search
5. Context-dependent pattern interpretation

**Expected Outcome**:
- call_17 correctly assessed as VIOLATION
- All regression tests pass (call_02, call_08, call_09, call_10)
- 19/20 HIGH confidence achieved (95%)

## BDD Workflow

```bash
# 1. Read the task specification
cat docs/tasks/TASK_001_FIX_TIMING_EXTRACTION_EDGE_CASES.md

# 2. Set up behave framework
pip install behave
mkdir -p tests/features/steps tests/fixtures

# 3. Write feature file (Gherkin)
# See task doc for complete feature specification

# 4. Write step definitions
# Implement Given/When/Then steps in Python

# 5. Run tests (should FAIL initially)
behave tests/features/timing_extraction.feature

# 6. Fix the tool
# Modify scripts/extract_timing.py

# 7. Run tests until they PASS
behave tests/features/timing_extraction.feature

# 8. Regression test all calls
behave tests/features/ --tags=@regression
```

## Why BDD?

1. **Documentation IS Tests** - Always up to date
2. **Prevents Regression** - Fix call_17 without breaking call_02
3. **Explicit Expectations** - No ambiguity about what "correct" means
4. **Knowledge Preservation** - Future developers see EXACTLY what must work
5. **Confidence in Tools** - Ground truth tools must be tested rigorously

## Task Template

Each task should include:
- [ ] Problem statement with evidence
- [ ] Root cause analysis
- [ ] All edge cases documented with examples
- [ ] BDD feature file (Gherkin)
- [ ] Expected test output
- [ ] Definition of done
- [ ] Impact assessment

## References

- **BDD Framework**: [behave documentation](https://behave.readthedocs.io/)
- **Gherkin Syntax**: Given/When/Then format
- **Project Config**: `/config/phase1_grading_config.json`
- **Golden Dataset**: `/phase1_analysis/sonnet_haiku_blind_core_decisions.json`
