#!/bin/bash
#
# Batch extract ground truth for all 20 calls
# Runs extract_timing.py and extract_gratitude.py on each call
#
# Usage: bash scripts/batch_extract_ground_truth.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/phase1_analysis/ground_truth"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Batch Ground Truth Extraction ==="
echo "Output directory: $OUTPUT_DIR"
echo ""

# Counter for successes and failures
timing_success=0
timing_fail=0
gratitude_success=0
gratitude_fail=0

# Process each call
for call_num in $(seq -w 1 20); do
    call_id="call_$call_num"
    call_dir="$REPO_ROOT/calls/$call_id"

    if [ ! -d "$call_dir" ]; then
        echo "⚠️  $call_id: Directory not found, skipping"
        continue
    fi

    echo "Processing $call_id..."

    # Extract timing (9.1)
    timing_output="$OUTPUT_DIR/${call_id}_timing.json"
    if python3 "$SCRIPT_DIR/extract_timing.py" "$call_dir" > "$timing_output" 2>&1; then
        # Check if output has searches
        search_count=$(jq -r '.total_searches // 0' "$timing_output")
        if [ "$search_count" -gt 0 ]; then
            echo "  ✓ Timing: $search_count searches detected"
            ((timing_success++))
        else
            echo "  ⚠️  Timing: No searches detected (may need manual review)"
            ((timing_fail++))
        fi
    else
        echo "  ✗ Timing: Extraction failed"
        ((timing_fail++))
    fi

    # Extract gratitude (9.3)
    gratitude_output="$OUTPUT_DIR/${call_id}_gratitude.json"
    if python3 "$SCRIPT_DIR/extract_gratitude.py" "$call_dir" > "$gratitude_output" 2>&1; then
        violations=$(jq -r '.summary.violations // 0' "$gratitude_output")
        if [ "$violations" -gt 0 ]; then
            echo "  ✓ Gratitude: $violations violation(s) detected"
        else
            echo "  ✓ Gratitude: PASS (no violations)"
        fi
        ((gratitude_success++))
    else
        echo "  ✗ Gratitude: Extraction failed"
        ((gratitude_fail++))
    fi

    echo ""
done

echo "=== Batch Extraction Complete ==="
echo ""
echo "Timing extraction (9.1):"
echo "  Success: $timing_success calls"
echo "  Failed/No searches: $timing_fail calls"
echo ""
echo "Gratitude extraction (9.3):"
echo "  Success: $gratitude_success calls"
echo "  Failed: $gratitude_fail calls"
echo ""
echo "Output files saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  1. Review calls with no searches detected (may need word-level parsing)"
echo "  2. Run validation: python3 scripts/validate_grading.py"
echo "  3. Generate consolidated grading context for Sonnet"
