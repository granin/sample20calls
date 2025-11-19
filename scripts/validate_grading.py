#!/usr/bin/env python3
"""
Validate grader accuracy against ground truth extractions.

Compares Sonnet, BLIND1, and BLIND2 grading outputs against ground truth
from extract_timing.py and extract_gratitude.py.

Usage:
    python scripts/validate_grading.py <call_id>
    python scripts/validate_grading.py call_07 call_08 call_12

Output: Validation report showing which graders matched ground truth
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_ground_truth(call_id: str, repo_root: Path) -> Dict:
    """Load ground truth data for a call."""
    timing_path = repo_root / 'phase1_analysis' / 'ground_truth' / f'{call_id}_timing.json'
    gratitude_path = repo_root / 'phase1_analysis' / 'ground_truth' / f'{call_id}_gratitude.json'

    gt = {'call_id': call_id}

    if timing_path.exists():
        with open(timing_path, 'r') as f:
            gt['timing'] = json.load(f)
    else:
        gt['timing'] = None

    if gratitude_path.exists():
        with open(gratitude_path, 'r') as f:
            gt['gratitude'] = json.load(f)
    else:
        gt['gratitude'] = None

    return gt


def load_grader_output(call_id: str, grader: str, repo_root: Path) -> Dict:
    """Load grader output for a call."""
    grader_paths = {
        'sonnet': repo_root / 'phase1_consolidated' / 'sonnet' / call_id / f'{call_id.upper()}_GRADING.json',
        'blind1': repo_root / 'phase1_consolidated' / 'blind1' / call_id / f'{call_id.upper()}_BLIND.json',
        'blind2': repo_root / 'phase1_consolidated' / 'blind2' / call_id / f'{call_id.upper()}_BLIND2.json',
    }

    grader_path = grader_paths.get(grader)

    if grader_path and grader_path.exists():
        with open(grader_path, 'r') as f:
            return json.load(f)
    return None


def compare_criterion(grader_assessment: str, ground_truth_status: str) -> bool:
    """
    Compare grader assessment against ground truth.

    Returns: True if match, False if mismatch
    """
    # Normalize assessments
    grader_norm = grader_assessment.upper() if grader_assessment else "UNKNOWN"
    gt_norm = ground_truth_status.upper() if ground_truth_status else "UNKNOWN"

    # Handle various assessment formats
    if "VIOLATION" in grader_norm:
        grader_norm = "VIOLATION"
    elif "BORDERLINE" in grader_norm or "FLAG" in grader_norm:
        grader_norm = "BORDERLINE"
    elif "PASS" in grader_norm or "N/A" in grader_norm:
        grader_norm = "PASS"

    if "VIOLATION" in gt_norm:
        gt_norm = "VIOLATION"
    elif "FLAG" in gt_norm or "BORDERLINE" in gt_norm:
        gt_norm = "BORDERLINE"
    elif "PASS" in gt_norm:
        gt_norm = "PASS"

    return grader_norm == gt_norm


def validate_call(call_id: str, repo_root: Path) -> Dict:
    """Validate all graders against ground truth for a call."""

    # Load ground truth
    gt = load_ground_truth(call_id, repo_root)

    # Load grader outputs
    graders = {}
    for grader_name in ['sonnet', 'blind1', 'blind2']:
        graders[grader_name] = load_grader_output(call_id, grader_name, repo_root)

    validation = {
        'call_id': call_id,
        'ground_truth': {},
        'grader_accuracy': {}
    }

    # Extract ground truth assessments
    if gt['timing'] and 'final_9_1_assessment' in gt['timing']:
        validation['ground_truth']['9.1'] = gt['timing']['final_9_1_assessment']['status']
    else:
        validation['ground_truth']['9.1'] = None

    if gt['gratitude'] and 'final_9_3_assessment' in gt['gratitude']:
        validation['ground_truth']['9.3'] = gt['gratitude']['final_9_3_assessment']['status']
    else:
        validation['ground_truth']['9.3'] = None

    # Compare each grader
    for grader_name, grader_data in graders.items():
        # Handle different key names (criteria_assessment vs criteria_assessments)
        if not grader_data:
            validation['grader_accuracy'][grader_name] = {
                '9.1': {'status': 'NO_DATA', 'match': False},
                '9.3': {'status': 'NO_DATA', 'match': False},
                'overall': 'NO_DATA'
            }
            continue

        criteria = grader_data.get('criteria_assessment') or grader_data.get('criteria_assessments')
        if not criteria:
            validation['grader_accuracy'][grader_name] = {
                '9.1': {'status': 'NO_DATA', 'match': False},
                '9.3': {'status': 'NO_DATA', 'match': False},
                'overall': 'NO_DATA'
            }
            continue

        grader_results = {}

        # Check 9.1
        if '9.1' in criteria and validation['ground_truth']['9.1']:
            # Try different field names (status, assessment)
            grader_9_1 = criteria['9.1'].get('status') or criteria['9.1'].get('assessment', 'UNKNOWN')
            match_9_1 = compare_criterion(grader_9_1, validation['ground_truth']['9.1'])
            grader_results['9.1'] = {
                'grader_status': grader_9_1,
                'match': match_9_1
            }
        else:
            grader_results['9.1'] = {'grader_status': 'N/A', 'match': None}

        # Check 9.3
        if '9.3' in criteria and validation['ground_truth']['9.3']:
            # Try different field names (status, assessment)
            grader_9_3 = criteria['9.3'].get('status') or criteria['9.3'].get('assessment', 'UNKNOWN')
            match_9_3 = compare_criterion(grader_9_3, validation['ground_truth']['9.3'])
            grader_results['9.3'] = {
                'grader_status': grader_9_3,
                'match': match_9_3
            }
        else:
            grader_results['9.3'] = {'grader_status': 'N/A', 'match': None}

        # Calculate overall accuracy
        matches = [r['match'] for r in grader_results.values() if r['match'] is not None]
        if matches:
            accuracy = sum(matches) / len(matches) * 100
            grader_results['overall_accuracy'] = f"{accuracy:.0f}%"
            grader_results['correct'] = sum(matches)
            grader_results['total'] = len(matches)
        else:
            grader_results['overall_accuracy'] = "N/A"

        validation['grader_accuracy'][grader_name] = grader_results

    return validation


def print_validation_report(validations: List[Dict]):
    """Print human-readable validation report."""

    print("\n" + "=" * 80)
    print("GRADER VALIDATION REPORT - Ground Truth Comparison")
    print("=" * 80 + "\n")

    for val in validations:
        call_id = val['call_id']
        gt = val['ground_truth']

        print(f"Call: {call_id}")
        print(f"  Ground Truth:")
        print(f"    9.1 (Long Search): {gt.get('9.1', 'N/A')}")
        print(f"    9.3 (Gratitude):   {gt.get('9.3', 'N/A')}")
        print()

        print(f"  Grader Accuracy:")
        for grader_name in ['sonnet', 'blind1', 'blind2']:
            grader_results = val['grader_accuracy'][grader_name]

            if grader_results.get('overall_accuracy') == 'NO_DATA':
                print(f"    {grader_name.upper()}: NO DATA")
                continue

            overall = grader_results.get('overall_accuracy', 'N/A')
            correct = grader_results.get('correct', 0)
            total = grader_results.get('total', 0)

            print(f"    {grader_name.upper()}: {overall} ({correct}/{total} criteria match)")

            for criterion in ['9.1', '9.3']:
                if criterion in grader_results and 'grader_status' in grader_results[criterion]:
                    if grader_results[criterion]['match'] is not None:
                        match = "✓" if grader_results[criterion]['match'] else "✗"
                        status = grader_results[criterion]['grader_status']
                        print(f"      {criterion}: {match} ({status})")

        print("\n" + "-" * 80 + "\n")

    # Summary statistics
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80 + "\n")

    for grader_name in ['sonnet', 'blind1', 'blind2']:
        total_correct = 0
        total_criteria = 0

        for val in validations:
            grader_results = val['grader_accuracy'][grader_name]
            if 'correct' in grader_results:
                total_correct += grader_results['correct']
                total_criteria += grader_results['total']

        if total_criteria > 0:
            accuracy = (total_correct / total_criteria) * 100
            print(f"{grader_name.upper()}: {accuracy:.1f}% accuracy ({total_correct}/{total_criteria} criteria)")
        else:
            print(f"{grader_name.upper()}: No data")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_grading.py <call_id> [<call_id> ...]", file=sys.stderr)
        print("Example: python validate_grading.py call_07 call_08 call_12", file=sys.stderr)
        sys.exit(1)

    call_ids = sys.argv[1:]
    repo_root = Path(__file__).parent.parent

    validations = []
    for call_id in call_ids:
        validation = validate_call(call_id, repo_root)
        validations.append(validation)

    # Print report
    print_validation_report(validations)

    # Also save JSON
    output_path = repo_root / 'phase1_analysis' / 'ground_truth' / 'validation_report.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(validations, f, ensure_ascii=False, indent=2)

    print(f"Detailed JSON report saved to: {output_path}")


if __name__ == '__main__':
    main()
