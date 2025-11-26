#!/usr/bin/env python3
"""
Generate consolidated grading context for Sonnet.

This tool creates a single Markdown file containing:
- Full transcript
- Pre-computed timing assessments (9.1)
- Pre-computed gratitude assessments (9.3)
- Clear grading instructions

Usage:
    python scripts/generate_consolidated_context.py <call_dir>
    python scripts/generate_consolidated_context.py calls/call_08 > grading_context_call_08.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


def load_ground_truth(call_id: str, repo_root: Path) -> Dict:
    """Load ground truth data for a call."""
    timing_path = repo_root / 'phase1_analysis' / 'ground_truth' / f'{call_id}_timing.json'
    gratitude_path = repo_root / 'phase1_analysis' / 'ground_truth' / f'{call_id}_gratitude.json'

    gt = {'call_id': call_id}

    if timing_path.exists():
        with open(timing_path, 'r', encoding='utf-8') as f:
            gt['timing'] = json.load(f)
    else:
        gt['timing'] = None

    if gratitude_path.exists():
        with open(gratitude_path, 'r', encoding='utf-8') as f:
            gt['gratitude'] = json.load(f)
    else:
        gt['gratitude'] = None

    return gt


def load_transcript(call_dir: Path) -> str:
    """Load VTT transcript."""
    vtt_path = call_dir / 'transcript-2.vtt'

    if not vtt_path.exists():
        return "ERROR: Transcript not found"

    with open(vtt_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_context(call_dir: Path) -> str:
    """Generate consolidated grading context as Markdown."""

    call_id = call_dir.name
    repo_root = call_dir.parent.parent

    # Load data
    transcript = load_transcript(call_dir)
    gt = load_ground_truth(call_id, repo_root)

    # Build Markdown context
    md = []

    # Header
    md.append(f"# Grading Context for {call_id.upper()}")
    md.append("")
    md.append("**Instructions**: Use the pre-computed timing and gratitude assessments below for criteria 9.1 and 9.3. Grade all other criteria normally by reading the transcript.")
    md.append("")
    md.append("---")
    md.append("")

    # Pre-computed assessments
    md.append("## PRE-COMPUTED ASSESSMENTS (Use These for 9.1 and 9.3)")
    md.append("")

    # Criterion 9.1 (Long Information Search)
    md.append("### Criterion 9.1 - Long Information Search")
    md.append("")

    if gt['timing']:
        timing = gt['timing']
        assessment = timing.get('final_9_1_assessment', {})

        md.append(f"**STATUS**: {assessment.get('status', 'UNKNOWN')}")
        md.append(f"**GRADE IMPACT**: {assessment.get('grade_impact', 'N/A')}")
        md.append("")

        if timing.get('total_searches', 0) > 0:
            md.append(f"**SEARCHES DETECTED**: {timing['total_searches']}")
            md.append("")

            # List searches
            for search in timing.get('searches', []):
                duration = search['duration_seconds']
                status = search['assessment']['status']

                md.append(f"- **Search #{search['search_number']}**: {duration:.1f}s → {status}")
                md.append(f"  - Start: {search['start_timestamp']} - \"{search['start_phrase']}\"")
                md.append(f"  - End: {search['end_timestamp']} - \"{search['end_phrase']}\"")

                if search.get('check_ins'):
                    md.append(f"  - Check-ins: {len(search['check_ins'])}")
                    for ci in search['check_ins']:
                        md.append(f"    - {ci['timestamp']}: {ci['phrase']}")

                md.append("")
        else:
            md.append("**NO SEARCHES DETECTED**")
            md.append("")
            md.append("⚠️ Tool did not detect any searches. This may be due to:")
            md.append("- Poor VTT diarization (multi-turn blocks)")
            md.append("- Unusual search phrase variations")
            md.append("- Actually no searches in this call")
            md.append("")
            md.append("**ACTION**: Manually review transcript and grade 9.1 by reading carefully.")
            md.append("")
    else:
        md.append("**ERROR**: Timing data not available. Run extract_timing.py first.")
        md.append("")

    # Criterion 9.3 (No Thank You for Waiting)
    md.append("### Criterion 9.3 - No Thank You for Waiting")
    md.append("")

    if gt['gratitude']:
        gratitude = gt['gratitude']
        assessment = gratitude.get('final_9_3_assessment', {})

        md.append(f"**STATUS**: {assessment.get('status', 'UNKNOWN')}")
        md.append(f"**GRADE IMPACT**: {assessment.get('grade_impact', 'N/A')}")
        md.append("")

        summary = gratitude.get('summary', {})
        md.append(f"**SEARCHES REQUIRING GRATITUDE**: {summary.get('searches_requiring_gratitude', 0)}")
        md.append(f"**GRATITUDE PHRASES DETECTED**: {summary.get('searches_with_gratitude', 0)}")
        md.append(f"**VIOLATIONS**: {summary.get('violations', 0)}")
        md.append("")

        if summary.get('violations', 0) > 0:
            md.append("**VIOLATION DETAILS**:")
            for search in gratitude.get('searches', []):
                gc = search.get('gratitude_check', {})
                if gc.get('assessment') == 'VIOLATION':
                    md.append(f"- Search #{search['search_number']} ({search['duration_seconds']:.1f}s): {gc.get('violation_note', 'No gratitude detected')}")
            md.append("")
    else:
        md.append("**ERROR**: Gratitude data not available. Run extract_gratitude.py first.")
        md.append("")

    md.append("---")
    md.append("")

    # Grading instructions
    md.append("## GRADING INSTRUCTIONS")
    md.append("")
    md.append("1. **For Criterion 9.1**: Use the pre-computed STATUS and GRADE IMPACT above. Copy the evidence from search details.")
    md.append("2. **For Criterion 9.3**: Use the pre-computed STATUS and GRADE IMPACT above. Copy the violation details if any.")
    md.append("3. **For all other criteria** (7.1, 7.2, 7.3, 7.4, etc.): Grade normally by reading the transcript below.")
    md.append("4. **Calculate final grade**: Apply the \"lowest code\" principle - final grade = minimum of all violation grades.")
    md.append("")
    md.append("---")
    md.append("")

    # Full transcript
    md.append("## FULL TRANSCRIPT")
    md.append("")
    md.append("```")
    md.append(transcript)
    md.append("```")
    md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("## VALIDATION")
    md.append("")
    md.append(f"After completing your grading, validate using:")
    md.append(f"```bash")
    md.append(f"python3 scripts/validate_grading.py {call_id}")
    md.append(f"```")
    md.append("")

    return "\n".join(md)


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_consolidated_context.py <call_dir>", file=sys.stderr)
        print("Example: python generate_consolidated_context.py calls/call_08", file=sys.stderr)
        sys.exit(1)

    call_dir = Path(sys.argv[1])

    if not call_dir.exists():
        print(f"Error: Directory not found: {call_dir}", file=sys.stderr)
        sys.exit(1)

    context = generate_context(call_dir)
    print(context)


if __name__ == '__main__':
    main()
