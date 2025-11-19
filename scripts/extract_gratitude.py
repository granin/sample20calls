#!/usr/bin/env python3
"""
Extract gratitude phrase detection ground truth for criterion 9.3 (No Thank You for Waiting).

This tool checks if operators thanked customers after information searches longer than 10 seconds.

Usage:
    python scripts/extract_gratitude.py <call_dir>
    python scripts/extract_gratitude.py calls/call_08

Output: JSON with gratitude detection for each search
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


# Gratitude phrase patterns (Russian)
GRATITUDE_PATTERNS = [
    r"спасибо\s+за\s+ожидание",  # "спасибо за ожидание"
    r"благодар[юя]\s+(вас\s+)?за\s+ожидание",  # "благодарю за ожидание"
    r"спасибо,?\s+что\s+подождали",  # "спасибо что подождали"
    r"спасибо,?\s+что\s+ждали",  # "спасибо что ждали"
    r"благодар[юя],?\s+что\s+подождали",  # "благодарю что подождали"
]

# Gratitude requirement threshold (seconds)
GRATITUDE_THRESHOLD = 10.0


def parse_vtt_timestamp(ts_str: str) -> float:
    """Convert VTT timestamp to seconds (HH:MM:SS,mmm format)."""
    ts_str = ts_str.replace(',', '.')
    parts = ts_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(parts[0])


def find_gratitude_in_window(text: str, speaker: str, window_start: float, window_end: float,
                               utterances: List[Dict], search_end_idx: int) -> Optional[Dict]:
    """
    Find gratitude phrase in time window after search ends.

    Args:
        text: Search end utterance text
        speaker: Speaker of search end utterance
        window_start: Start of search window (seconds)
        window_end: End of search window (seconds)
        utterances: All utterances
        search_end_idx: Index of search end utterance

    Returns:
        Dict with gratitude details if found, None otherwise
    """
    # First check the search end utterance itself (common pattern: "Спасибо за ожидание. Вот результат...")
    text_lower = text.lower()
    for pattern in GRATITUDE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return {
                "gratitude_found": True,
                "gratitude_phrase": match.group(0),
                "gratitude_timestamp": ms_to_timestamp(int(window_end * 1000)),
                "time_after_search": 0.0,
                "location": "same_utterance",
                "full_text": text
            }

    # Check next few AGENT utterances within 10s window
    for i in range(search_end_idx + 1, min(search_end_idx + 5, len(utterances))):
        utt = utterances[i]

        # Only check AGENT utterances
        if utt['speaker'] != 'AGENT':
            continue

        # Stop if beyond 10s window
        if utt['start'] > window_end + 10.0:
            break

        text_lower = utt['text'].lower()
        for pattern in GRATITUDE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return {
                    "gratitude_found": True,
                    "gratitude_phrase": match.group(0),
                    "gratitude_timestamp": ms_to_timestamp(int(utt['start'] * 1000)),
                    "time_after_search": utt['start'] - window_end,
                    "location": "next_utterance",
                    "full_text": utt['text']
                }

    return None


def ms_to_timestamp(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS.mmm format."""
    from datetime import timedelta
    seconds = ms / 1000.0
    return str(timedelta(seconds=seconds))[:-3] if seconds < 3600 else str(timedelta(seconds=seconds))[:-3]


def load_vtt(vtt_path: Path) -> List[Dict]:
    """Parse VTT file into list of utterances."""
    utterances = []
    with open(vtt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and WEBVTT header
        if not line or line == 'WEBVTT':
            i += 1
            continue

        # Check if this is a sequence number
        if line.isdigit():
            seq = int(line)
            i += 1

            # Next line should be timestamp
            if i < len(lines):
                timestamp_line = lines[i].strip()
                match = re.match(r'([\d:,]+)\s*-->\s*([\d:,]+)\s*<(\w+)>', timestamp_line)
                if match:
                    start_ts, end_ts, speaker = match.groups()
                    i += 1

                    # Next line(s) are the text
                    text_lines = []
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                        text_lines.append(lines[i].strip())
                        i += 1

                    text = ' '.join(text_lines)
                    utterances.append({
                        'seq': seq,
                        'start': parse_vtt_timestamp(start_ts),
                        'end': parse_vtt_timestamp(end_ts),
                        'speaker': speaker,
                        'text': text,
                        'line_number': seq
                    })
        else:
            i += 1

    return utterances


def extract_gratitude(call_dir: Path) -> Dict:
    """Extract gratitude phrase detection from transcript and timing data."""

    call_id = call_dir.name
    vtt_path = call_dir / 'transcript-2.vtt'

    if not vtt_path.exists():
        return {"error": f"VTT file not found: {vtt_path}"}

    # Load transcript
    utterances = load_vtt(vtt_path)

    # Try to load timing data from extract_timing.py output
    timing_path = call_dir.parent.parent / 'phase1_analysis' / 'ground_truth' / f'{call_id}_timing.json'

    if timing_path.exists():
        with open(timing_path, 'r', encoding='utf-8') as f:
            timing_data = json.load(f)
    else:
        # If timing data not available, return error asking user to run extract_timing first
        return {
            "error": f"Timing data not found: {timing_path}",
            "note": f"Run extract_timing.py first: python3 scripts/extract_timing.py {call_dir}"
        }

    if 'error' in timing_data:
        return timing_data

    # Check gratitude for each search
    searches_with_gratitude = []

    for search in timing_data.get('searches', []):
        search_duration = search['duration_seconds']
        end_timestamp_str = search['end_timestamp']
        end_line = search['end_line_number']

        # Find the utterance by line number
        search_end_utt = None
        search_end_idx = None
        for idx, utt in enumerate(utterances):
            if utt['line_number'] == end_line:
                search_end_utt = utt
                search_end_idx = idx
                break

        if not search_end_utt:
            # Fallback: parse timestamp
            end_ts = parse_vtt_timestamp(end_timestamp_str)
        else:
            end_ts = search_end_utt['start']

        # Determine if gratitude is required
        gratitude_required = search_duration > GRATITUDE_THRESHOLD

        if gratitude_required:
            # Look for gratitude phrase
            gratitude_result = find_gratitude_in_window(
                search_end_utt['text'] if search_end_utt else "",
                'AGENT',
                0,  # Not used
                end_ts,
                utterances,
                search_end_idx if search_end_idx else 0
            )

            if gratitude_result:
                assessment = "PASS"
                violation_note = None
            else:
                assessment = "VIOLATION"
                violation_note = f"Search duration {search_duration:.1f}s requires gratitude, but none found after answer delivery."
        else:
            # Gratitude not required for short searches
            gratitude_result = {
                "gratitude_found": False,
                "gratitude_phrase": None,
                "gratitude_timestamp": None,
                "time_after_search": None,
                "location": None,
                "full_text": None
            }
            assessment = "PASS"
            violation_note = None

        searches_with_gratitude.append({
            "search_number": search['search_number'],
            "duration_seconds": search_duration,
            "end_timestamp": end_timestamp_str,
            "end_phrase": search.get('end_phrase', ''),
            "gratitude_check": {
                "required": gratitude_required,
                "rationale": f"Search duration {search_duration:.1f}s {'>' if gratitude_required else '<='} {GRATITUDE_THRESHOLD}s threshold",
                "gratitude_found": gratitude_result.get('gratitude_found', False) if gratitude_result else False,
                "gratitude_phrase": gratitude_result.get('gratitude_phrase') if gratitude_result else None,
                "gratitude_timestamp": gratitude_result.get('gratitude_timestamp') if gratitude_result else None,
                "time_after_search": gratitude_result.get('time_after_search') if gratitude_result else None,
                "location": gratitude_result.get('location') if gratitude_result else None,
                "assessment": assessment,
                "violation_note": violation_note
            }
        })

    # Overall assessment
    violations = [s for s in searches_with_gratitude if s['gratitude_check']['assessment'] == 'VIOLATION']

    summary = {
        "total_searches": len(searches_with_gratitude),
        "searches_requiring_gratitude": len([s for s in searches_with_gratitude if s['gratitude_check']['required']]),
        "searches_with_gratitude": len([s for s in searches_with_gratitude if s['gratitude_check']['gratitude_found']]),
        "violations": len(violations),
        "violation_search_numbers": [s['search_number'] for s in violations]
    }

    return {
        "call_id": call_id,
        "searches": searches_with_gratitude,
        "summary": summary,
        "final_9_3_assessment": {
            "criterion": "9.3 - No Thank You for Waiting",
            "status": "VIOLATION" if len(violations) > 0 else "PASS",
            "grade_impact": 9 if len(violations) > 0 else 10,
            "violations_found": len(violations),
            "note": f"{len(violations)} search(es) without required gratitude" if len(violations) > 0 else "All searches properly acknowledged"
        }
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_gratitude.py <call_dir>", file=sys.stderr)
        print("Example: python extract_gratitude.py calls/call_08", file=sys.stderr)
        sys.exit(1)

    call_dir = Path(sys.argv[1])

    if not call_dir.exists():
        print(f"Error: Directory not found: {call_dir}", file=sys.stderr)
        sys.exit(1)

    result = extract_gratitude(call_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
