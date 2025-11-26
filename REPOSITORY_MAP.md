# Phase 1 Golden Dataset Grading Project - Complete Repository Map

**Repository**: `/home/user/sample20calls/`  
**Status**: Phase 1 Golden Dataset Development  
**Date**: 2025-11-19  
**Scope**: 17 transcript-based grading criteria for Russian contact center calls (20 calls)

---

## 1. ROOT DIRECTORY STRUCTURE

```
/home/user/sample20calls/
├── README.md                          # Main entry point and quick start guide
├── TASK.md                            # Top-level instructions for agents
├── config/                            # Grading system configuration (4 files)
├── docs/                              # Documentation and guides (5 files)
├── calls/                             # Call data directories (20 calls)
├── phase1_analysis/                   # Analysis, comparisons, and task briefs
├── phase1_consolidated/               # Normalized gradings from all 4 sources
├── scripts/                           # CLI tools for ground truth extraction
└── .git/                              # Git repository metadata
```

---

## 2. CONFIGURATION FILES (`/config/`)

**Location**: `/home/user/sample20calls/config/`

### 2.1 Core Configuration Files

| File | Size | Purpose |
|------|------|---------|
| `phase1_grading_config.json` | 13 KB | **17-criteria specification** - Detection methods, thresholds, confidence levels for each criterion |
| `phase1_output_format_v2.json` | 19 KB | **JSON output schema** - Defines structure for grading results (call_metadata, violations_detected, risk_assessment, etc.) |
| `confidence_thresholds.json` | 12 KB | **Confidence rules** - When to auto-grade vs flag for review (VERY_HIGH, HIGH, MEDIUM, LOW) |
| `prompt_for_transcript_only_grading.txt` | 1.8 KB | **LLM grading prompt** - Instructions for Sonnet/Haiku/Opus to grade calls from transcripts only |

**Key Content**:
- `phase1_grading_config.json` contains 17 criteria across 7 grade categories:
  - Grade 1: Misconduct (1.1 - Rudeness/profanity)
  - Grade 2: Service Failures (2.1 - Call dropout/refusal)
  - Grade 3: Serious Problems (3.1, 3.3, 3.6)
  - Grade 4: Customer Handling (4.1 - Difficult customer)
  - Grade 5: Information (5.1 - Incomplete information)
  - Grade 6: Critical Issues (6.1 - Critical silence/hangup)
  - Grade 7: Protocol Compliance (7.1, 7.2, 7.3, 7.4)
  - Grade 9: Search Quality (9.1, 9.3)
  - Grade 10: Baseline Quality (10.2, 10.3, 10.6)

---

## 3. DOCUMENTATION (`/docs/`)

**Location**: `/home/user/sample20calls/docs/`

| File | Size | Purpose |
|------|------|---------|
| `PHASE1_SCOPE.md` | 7.4 KB | **Scope definition** - 17 criteria list, data sources, grading rules, confidence thresholds |
| `Quick_Reference_Grades_EN_PHASE1.md` | 12 KB | **Fast lookup reference** - One-page guide for all 17 criteria with detection methods |
| `Excel_Analysis_Summary_EN_PHASE1.md` | 13 KB | **Detailed system guide** - System structure, rules, Russian language patterns, implementation checklist |
| `PHASE1_PACKAGE_GUIDE.md` | 11 KB | **Workflow guide** - How to grade first call, LLM prompt usage, troubleshooting, success metrics |
| `phase1_comparison_to_full.md` | 12 KB | **Scope comparison** - What Phase 1 covers vs full 26-criteria system |

---

## 4. CALL DATA DIRECTORIES (`/calls/`)

**Location**: `/home/user/sample20calls/calls/`

### 4.1 Directory Structure

```
/calls/
├── call_01/ through call_20/     (20 directories)
└── Each call_XX/ contains:
    ├── transcript-2.vtt           (Transcript in WebVTT format with speaker labels)
    ├── transcript-2.srt           (Transcript in SubRip format)
    ├── paragraphs-2.json          (Paragraph-level segmentation)
    ├── sentences-2.json           (Sentence-level segmentation)
    ├── timestamps-2.json          (Word-level timing data)
    ├── CALL_XX_TASK.md            (Call-specific instructions)
    └── CALL_XX_BLIND.json         (BLIND1 reference grading)
    └── CALL_XX_BLIND2.json        (BLIND2 reference grading, if exists)
```

### 4.2 Sample Call Examples

#### **CALL_01** (Small call: 60 KB total)
- Files present: transcript-2.vtt, transcript-2.srt, paragraphs-2.json, sentences-2.json, timestamps.json, CALL_01_TASK.md
- BLIND1: `CALL_01_BLIND.json`
- BLIND2: `CALL_01_BLIND2.json`
- Estimated duration: ~80 seconds

#### **CALL_10** (Large call: 829 KB total)
- Files present: transcript-2.vtt, transcript-2.srt, paragraphs-2.json (273 KB), sentences-2.json (309 KB), timestamps-2.json (184 KB), CALL_10_TASK.md
- BLIND1: `CALL_10_BLIND.json`
- BLIND2: `CALL_10_BLIND2.json`
- Estimated duration: ~400 seconds

#### **CALL_15** (Medium call: 138 KB total)
- Files present: transcript-2.vtt, transcript-2.srt, paragraphs-2.json, sentences-2.json, timestamps-2.json, CALL_15_TASK.md
- BLIND1: `CALL_15_BLIND.json`
- BLIND2: `CALL_15_BLIND2.json`
- Estimated duration: ~100 seconds

### 4.3 Data Format Summary

| File Type | Format | Purpose | Example Size |
|-----------|--------|---------|--------------|
| `transcript-X.vtt` | WebVTT | Formatted transcript with timecodes | 3-23 KB |
| `transcript-X.srt` | SubRip | Alternative transcript format | 3-23 KB |
| `paragraphs-X.json` | JSON | Speech segments by paragraph | 35-273 KB |
| `sentences-X.json` | JSON | Speech segments by sentence | 41-309 KB |
| `timestamps-X.json` | JSON | Word-level timing data (millisecond precision) | 23-184 KB |
| `CALL_XX_TASK.md` | Markdown | Call-specific grading instructions | 1-3 KB |

**Complete File Counts**:
- VTT transcripts: 20 files
- SRT transcripts: 20 files
- Total call data: 20 directories with consistent structure

---

## 5. PHASE 1 ANALYSIS (`/phase1_analysis/`)

**Location**: `/home/user/sample20calls/phase1_analysis/`

### 5.1 Documentation Files

| File | Size | Purpose |
|------|------|---------|
| `PHASE1_GOLDEN_REVIEW_TASK.md` | 12.6 KB | **Golden dataset task description** - Explains 4 grading waves (Sonnet, Haiku, BLIND1, BLIND2) and comparison methodology |
| `NEXT_AGENT_TASK_BRIEF.md` | 14.8 KB | **Next phase mission** - Describes systematic improvements to achieve 18/20 golden labels; tool roadmap; timing extraction needs |
| `TOOL_SPECIFICATIONS.md` | 28.2 KB | **Detailed tool specs** - 5-tool implementation roadmap for timing extraction and consistency checking |
| `DELIVERABLE_A_SPEC_AMBIGUITIES_AND_IMPROVEMENTS.md` | 21.7 KB | **Specification analysis** - Identified ambiguities in grading criteria and proposed improvements |
| `DELIVERABLE_B_FIELD_STABILITY_ANALYSIS.md` | 13.6 KB | **Field stability report** - Analysis of which criteria fields are stable across graders |
| `DELIVERABLE_C_GOLDEN_DECISIONS_REFINED.md` | 15.2 KB | **Golden decisions** - Refined ground truth decisions for each call based on 3-way analysis |
| `DELIVERABLE_D_REVISED_PROMPT_STRATEGY.md` | 24.2 KB | **Prompt strategy** - Recommendations for improving LLM prompt to increase grading consistency |

### 5.2 Comparison and Analysis JSON Files

| File | Lines | Purpose |
|------|-------|---------|
| `sonnet_haiku_blind1_comparison.json` | 3,201 | **3-way comparison** - Detailed field-by-field comparison of Sonnet, Haiku, and BLIND1 gradings for all 20 calls |
| `sonnet_haiku_blind_core_decisions.json` | 149 | **Summary of core decisions** - Consolidated view of key differing decisions across graders |

### 5.3 BLIND2 Task Files Subdirectory

**Location**: `/home/user/sample20calls/phase1_analysis/blind2_tasks/`

```
blind2_tasks/
├── BLIND2_TASK_call_01.md
├── BLIND2_TASK_call_02.md
├── BLIND2_TASK_call_06.md
├── BLIND2_TASK_call_07.md
├── BLIND2_TASK_call_08.md
├── BLIND2_TASK_call_09.md
├── BLIND2_TASK_call_10.md
├── BLIND2_TASK_call_11.md
├── BLIND2_TASK_call_12.md
├── BLIND2_TASK_call_13.md
├── BLIND2_TASK_call_14.md
├── BLIND2_TASK_call_15.md
├── BLIND2_TASK_call_16.md
├── BLIND2_TASK_call_17.md
├── BLIND2_TASK_call_18.md
├── BLIND2_TASK_call_19.md
└── BLIND2_TASK_call_20.md
```

**Note**: 17 task files present (calls 3, 4, 5 excluded - likely no BLIND2 needed for those)

---

## 6. PHASE 1 CONSOLIDATED GRADINGS (`/phase1_consolidated/`)

**Location**: `/home/user/sample20calls/phase1_consolidated/`

### 6.1 Directory Structure

```
/phase1_consolidated/
├── sonnet/              (20 calls - Sonnet model gradings)
├── haiku/               (20 calls - Haiku model gradings)
├── blind1/              (20 calls - First blind pass, Codex/GPT)
├── blind2/              (17 calls - Second blind pass, more constrained)
├── analysis_3way_per_call.json      (72.9 KB)
├── analysis_3way_per_field.json     (4.2 KB)
├── compact_3way_summary.json        (21.0 KB)
├── summary_3way_field_stats.json    (9.4 KB)
├── summary_3way_field_stats.csv     (1.6 KB)
├── matrix_3way_patterns.csv         (5.3 KB)
├── report_3way_comparison.html      (50.6 KB)
└── report_3way_charts.html          (11.8 KB)
```

### 6.2 Grading Output Files by Model

#### **Sonnet Gradings** (`/sonnet/`)
- **Count**: 20 files (call_01 through call_20)
- **Format**: `CALL_XX_GRADING.json`
- **Size**: ~10 KB per file
- **Content**: Full JSON grading output following `phase1_output_format_v2.json` schema
- **Examples**:
  - `/home/user/sample20calls/phase1_consolidated/sonnet/call_01/CALL_01_GRADING.json`
  - `/home/user/sample20calls/phase1_consolidated/sonnet/call_20/CALL_20_GRADING.json`

#### **Haiku Gradings** (`/haiku/`)
- **Count**: 20 files (call_01 through call_20)
- **Format**: `CALL_XX_HAIKU.json`
- **Size**: ~11 KB per file
- **Content**: Full JSON grading output using same schema
- **Source**: Haiku cost-optimized model (normalized from `/tmp/phase1_haiku`)

#### **BLIND1 Gradings** (`/blind1/`)
- **Count**: 20 files (call_01 through call_20)
- **Format**: `CALL_XX_BLIND.json`
- **Size**: ~9-10 KB per file
- **Content**: First independent blind grading pass (Codex/GPT)
- **Dual location**: 
  - Normalized: `/phase1_consolidated/blind1/call_XX/CALL_XX_BLIND.json`
  - Original: `/calls/call_XX/CALL_XX_BLIND.json`

#### **BLIND2 Gradings** (`/blind2/`)
- **Count**: 17 files (calls with significant Sonnet/BLIND1 disagreement)
- **Format**: `CALL_XX_BLIND2.json`
- **Size**: ~9-10 KB per file
- **Calls present**: 01, 02, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
- **Calls missing**: 03, 04, 05 (likely no disagreement requiring third pass)
- **Content**: Second blind pass with more constrained instructions and higher thinking effort

### 6.3 Analysis Output Files

| File | Size | Content |
|------|------|---------|
| `analysis_3way_per_call.json` | 72.9 KB | Detailed per-call comparison of Sonnet vs Haiku vs BLIND1 across all 17 criteria |
| `analysis_3way_per_field.json` | 4.2 KB | Per-field summary showing agreement/disagreement patterns |
| `compact_3way_summary.json` | 21.0 KB | Compact summary of 3-way analysis for all calls |
| `summary_3way_field_stats.json` | 9.4 KB | Statistical summary of field-level agreement |
| `summary_3way_field_stats.csv` | 1.6 KB | CSV version of field statistics |
| `matrix_3way_patterns.csv` | 5.3 KB | Pattern matrix for comparison analysis |
| `report_3way_comparison.html` | 50.6 KB | Interactive HTML report of 3-way comparison |
| `report_3way_charts.html` | 11.8 KB | HTML charts for visualization |

---

## 7. SCRIPTS (`/scripts/`)

**Location**: `/home/user/sample20calls/scripts/`

### 7.1 Tools Available

| File | Type | Purpose | Status |
|------|------|---------|--------|
| `extract_timing.py` | Python (executable) | **Ground truth extraction for criterion 9.1** (Long search detection) | Implemented, ~60% success rate |
| `README.md` | Markdown | Documentation for timing extraction tool | Up-to-date |

### 7.2 Extract Timing Tool Details

**Location**: `/home/user/sample20calls/scripts/extract_timing.py`

**Purpose**: Extract search duration ground truth for criterion 9.1 (Long Information Search)

**Usage**:
```bash
python3 scripts/extract_timing.py calls/call_XX
```

**Output Structure**:
```json
{
  "call_id": "call_08",
  "searches": [
    {
      "search_num": 1,
      "start_time": "00:00:27.869",
      "start_phrase": "Минутку, пожалуйста",
      "end_time": "00:02:03.930",
      "end_phrase": "Спасибо за ожидание",
      "duration_seconds": 96.061,
      "status": "VIOLATION (>45s)"
    }
  ]
}
```

**Validation Results**:
- call_08: 96.061s violation - DETECTED ✓
- call_07: 60.836s violation (search 2) - DETECTED ✓
- call_12: Searches - DETECTED ✓
- call_11, 13, 01: Failed - Poor VTT diarization

**Success Rate**: 50-60% automatic detection; 40-50% require manual review

**Known Limitations**:
1. VTT granularity (multi-turn blocks)
2. Limited search phrase coverage
3. Diarization quality dependency

**Planned Tools** (per TOOL_SPECIFICATIONS.md):
- Tool 2: Echo method (7.2) verification
- Tool 3: Interruption timing (7.4) verification
- Tool 4: Confidence assessment helper
- Tool 5: Batch consistency checker

---

## 8. ROOT-LEVEL FILES

| File | Size | Purpose |
|------|------|---------|
| `README.md` | 7.7 KB | **Main entry point** - Quick start (3 steps), package contents, 17 criteria overview, grading methods, key concepts, success metrics, validation workflow, troubleshooting |
| `TASK.md` | 5.6 KB | **Agent task instructions** - Repository scope, folder structure, assumptions, grading workflow (4 steps), human interaction patterns, safety guardrails |

---

## 9. DATA SUMMARY AND STATISTICS

### 9.1 Call Coverage
- **Total calls**: 20 (call_01 through call_20)
- **All calls have**: VTT, SRT, JSON transcripts, word-level timing
- **All calls graded by**: Sonnet, Haiku, BLIND1
- **BLIND2 coverage**: 17 of 20 calls (85%)
- **Call size range**: 60 KB (call_01) to 829 KB (call_10)

### 9.2 Grading Coverage
```
Grading Model   Complete Gradings   JSON Files
─────────────────────────────────────────────
Sonnet          20/20 (100%)        20 files
Haiku           20/20 (100%)        20 files
BLIND1          20/20 (100%)        20 files
BLIND2          17/20 (85%)         17 files
───────────────────────────────────────────
```

### 9.3 Documentation Files
- **Config files**: 4 (JSON specs + LLM prompt)
- **Docs files**: 5 (guides and references)
- **Analysis files**: 7 markdown (deliverables, task briefs)
- **Call tasks**: 20 (one per call)
- **BLIND2 tasks**: 17 (subset of calls)
- **Total markdown**: 34 files

### 9.4 Analysis Output
- **3-way comparison**: 6 JSON files + 2 HTML reports + 2 CSV files
- **Per-call JSON**: 80 grading files (20 Sonnet + 20 Haiku + 20 BLIND1 + 17 BLIND2)
- **Total grading data**: ~90 MB across all formats

### 9.5 Criteria Coverage
- **Total criteria defined**: 17 (transcript-based only)
- **Grade categories**: 8 (Grades 1, 2, 3, 4, 5, 6, 7, 9, 10)
- **Criteria per grade**:
  - Grade 1: 1
  - Grade 2: 1
  - Grade 3: 3
  - Grade 4: 1
  - Grade 5: 1
  - Grade 6: 1
  - Grade 7: 4
  - Grade 9: 2
  - Grade 10: 3

---

## 10. KEY FINDINGS FROM ANALYSIS

### 10.1 Golden Dataset Status
- **High confidence**: 12/20 calls (60%)
- **Medium confidence**: 8/20 calls (40%)
- **Target**: 18/20 calls (90%) after improvements

### 10.2 Root Cause Analysis
**Why graders disagree:**
1. **BLIND1 (Codex single session)**: Context rot → measurement errors (calls 07, 11, 13)
2. **BLIND2 (Codex per-call, high thinking)**: Most accurate on timing (9.1), but missed some 7.2 violations
3. **Sonnet (general understanding)**: Best comprehension, but timing measurement errors on 9.1

**Key Finding**: Sonnet needs **tool assistance** for timing precision, not just better prompts.

### 10.3 Critical Violations Found
- **Echo method (7.2)**: Most common violation
- **Long search timing (9.1)**: Measurement inconsistencies among graders
- **Protocol compliance (7.1-7.4)**: High detection confidence

---

## 11. USAGE PATTERNS

### 11.1 For Grading New Calls
1. Copy call data to `calls/call_XX/`
2. Create `calls/call_XX/CALL_XX_TASK.md`
3. Use `config/prompt_for_transcript_only_grading.txt` with Sonnet
4. Output to `phase1_consolidated/sonnet/call_XX/CALL_XX_GRADING.json`

### 11.2 For Analysis
1. Reference `phase1_consolidated/` for all 4 model gradings
2. Check `analysis_3way_per_call.json` for disagreements
3. Review `DELIVERABLE_*.md` files for findings

### 11.3 For Tool Development
1. Reference `scripts/extract_timing.py` as model implementation
2. Read `TOOL_SPECIFICATIONS.md` for full roadmap
3. Test against calls in `phase1_consolidated/blind2/` (BLIND2 has best timing accuracy)

---

## 12. FILE LOCATIONS REFERENCE

### Absolute Paths to Key Files

**Configuration**:
- `/home/user/sample20calls/config/phase1_grading_config.json`
- `/home/user/sample20calls/config/phase1_output_format_v2.json`
- `/home/user/sample20calls/config/confidence_thresholds.json`
- `/home/user/sample20calls/config/prompt_for_transcript_only_grading.txt`

**Documentation**:
- `/home/user/sample20calls/docs/PHASE1_SCOPE.md`
- `/home/user/sample20calls/docs/Quick_Reference_Grades_EN_PHASE1.md`
- `/home/user/sample20calls/docs/PHASE1_PACKAGE_GUIDE.md`

**Sample Call Data**:
- `/home/user/sample20calls/calls/call_01/` (small call)
- `/home/user/sample20calls/calls/call_10/` (large call)
- `/home/user/sample20calls/calls/call_15/` (medium call)

**Consolidated Gradings**:
- `/home/user/sample20calls/phase1_consolidated/sonnet/call_01/CALL_01_GRADING.json`
- `/home/user/sample20calls/phase1_consolidated/haiku/call_01/CALL_01_HAIKU.json`
- `/home/user/sample20calls/phase1_consolidated/blind1/call_01/CALL_01_BLIND.json`
- `/home/user/sample20calls/phase1_consolidated/blind2/call_01/CALL_01_BLIND2.json`

**Analysis Files**:
- `/home/user/sample20calls/phase1_analysis/PHASE1_GOLDEN_REVIEW_TASK.md`
- `/home/user/sample20calls/phase1_analysis/NEXT_AGENT_TASK_BRIEF.md`
- `/home/user/sample20calls/phase1_analysis/TOOL_SPECIFICATIONS.md`
- `/home/user/sample20calls/phase1_consolidated/analysis_3way_per_call.json`
- `/home/user/sample20calls/phase1_consolidated/compact_3way_summary.json`

**Scripts**:
- `/home/user/sample20calls/scripts/extract_timing.py`
- `/home/user/sample20calls/scripts/README.md`

---

## 13. RELATED GRADING FILES IN /calls/

**Location**: Individual call directories also contain reference gradings

Each `calls/call_XX/` may contain:
- `CALL_XX_BLIND.json` - Original BLIND1 output (also mirrored in `phase1_consolidated/blind1/`)
- `CALL_XX_BLIND2.json` - BLIND2 output for selected calls (also mirrored in `phase1_consolidated/blind2/`)

These are provided for reference during comparison analysis.

---

## SUMMARY TABLE: Complete File Inventory

| Category | Location | Count | Key Files |
|----------|----------|-------|-----------|
| **Configuration** | `/config/` | 4 | phase1_grading_config.json, confidence_thresholds.json |
| **Documentation** | `/docs/` | 5 | PHASE1_SCOPE.md, Quick_Reference_Grades_EN_PHASE1.md |
| **Call Data** | `/calls/call_XX/` | 20 | transcript-2.vtt, paragraphs-2.json, sentences-2.json |
| **Analysis** | `/phase1_analysis/` | 9 markdown + 2 JSON | DELIVERABLE_*.md, TOOL_SPECIFICATIONS.md |
| **BLIND2 Tasks** | `/phase1_analysis/blind2_tasks/` | 17 | BLIND2_TASK_call_XX.md |
| **Sonnet Gradings** | `/phase1_consolidated/sonnet/` | 20 | CALL_XX_GRADING.json |
| **Haiku Gradings** | `/phase1_consolidated/haiku/` | 20 | CALL_XX_HAIKU.json |
| **BLIND1 Gradings** | `/phase1_consolidated/blind1/` | 20 | CALL_XX_BLIND.json |
| **BLIND2 Gradings** | `/phase1_consolidated/blind2/` | 17 | CALL_XX_BLIND2.json |
| **Analysis Output** | `/phase1_consolidated/` | 8 | 3-way comparison, reports, stats |
| **Scripts** | `/scripts/` | 2 | extract_timing.py, README.md |
| **Root** | `/` | 2 | README.md, TASK.md |
| **TOTAL** | All | **~170 files** | See sections above |

---

**Last Updated**: 2025-11-19  
**Repository Status**: Active Phase 1 Golden Dataset Development
