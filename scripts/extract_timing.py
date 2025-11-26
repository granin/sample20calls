#!/usr/bin/env python3
"""
Extract search timing ground truth from VTT and word-level JSON transcripts.

This tool identifies search durations for criterion 9.1 (Long Information Search)
by analyzing operator search announcements and answer delivery timestamps.

Usage:
    python scripts/extract_timing.py <call_dir>
    python scripts/extract_timing.py calls/call_08

Output: JSON with search durations and assessments
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import timedelta


# Search announcement patterns (Russian)
SEARCH_PATTERNS = [
    r"минут[а-яё]{0,4}",  # "минуту", "минутку", "минуточку", "минутик"
    r"секунд[а-яё]{0,4}",  # "секунду", "секундочку"
    r"\b(сейчас|щас)\s+(посмотр|провер|уточн)",  # "сейчас посмотрю"
    r"подожд[а-яё]{0,3}",  # "подождите", "подожди"
    r"\b(давайте|дайте)\s+(я\s+)?посмотр",  # "давайте посмотрю"
]

# Filler words to skip when finding substantive answers
FILLER_WORDS = {
    "вот", "так", "итак", "ну", "значит", "хорошо", "да", "ага", "угу", "э", "эм"
}

# Substantive answer indicators
ANSWER_PATTERNS = [
    r"\b(есть|нашел|нашла|вижу|нашли)\b",  # "есть", "нашел"
    r"\b(информация|данные|результат)\b",  # "информация"
    r"\b(размер|цена|адрес|телефон|номер)\b",  # domain-specific
    r"спасибо\s+за\s+ожидание",  # gratitude phrase - marks end of search (MUST be full phrase)
]

# Check-in patterns (don't reset timer)
CHECKIN_PATTERNS = [
    r"(еще|ещё)\s+(немного|чуть-чуть|секунд|минут)",  # "еще немного"
    r"(почти|практически)\s+(готов|нашел)",  # "почти готово"
    r"(продолжаю|ищу|смотрю)",  # "продолжаю искать"
    r"спасибо\.?\s+(заждание|подождите)",  # "спасибо заждание" - check-in, not answer
]

# Time window for merging consecutive search announcements (seconds)
SEARCH_MERGE_WINDOW = 30.0


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


def ms_to_timestamp(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS.mmm format."""
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


def load_paragraphs(para_path: Path) -> Dict:
    """Load paragraphs-2.json file."""
    with open(para_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_search_announcement(text: str, speaker: str) -> bool:
    """Check if utterance is a search announcement."""
    if speaker != 'AGENT':
        return False

    text_lower = text.lower()

    # First check if this is a check-in (not a new search)
    if is_checkin(text_lower, speaker):
        return False

    # Then check if it matches search patterns
    for pattern in SEARCH_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_checkin(text: str, speaker: str) -> bool:
    """Check if utterance is a check-in (doesn't end search)."""
    if speaker != 'AGENT':
        return False

    text_lower = text.lower()
    for pattern in CHECKIN_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def find_substantive_answer(utterances: List[Dict], search_idx: int) -> Optional[Dict]:
    """Find the first substantive answer after a search announcement."""

    # Scan forward from search announcement
    for i in range(search_idx + 1, len(utterances)):
        utt = utterances[i]

        # Only look at AGENT utterances
        if utt['speaker'] != 'AGENT':
            continue

        text_lower = utt['text'].lower()

        # Check if this is another search announcement (continuation, not answer)
        if is_search_announcement(utt['text'], 'AGENT'):
            continue

        # Check if this is just a check-in (doesn't end search)
        if is_checkin(text_lower, 'AGENT'):
            continue

        # Check for substantive answer patterns
        for pattern in ANSWER_PATTERNS:
            if re.search(pattern, text_lower):
                return utt

        # Check if first word is NOT filler (indicates substantive answer)
        words = text_lower.split()
        if words:
            first_word = words[0].strip('.,!?;:')
            if first_word not in FILLER_WORDS:
                # Found substantive answer
                return utt

    return None


def assess_search(duration_seconds: float) -> Dict:
    """Assess search duration against thresholds."""
    if duration_seconds <= 40:
        return {
            "status": "PASS",
            "threshold_applied": "40s",
            "flag_window": False,
            "grade_impact": None,
            "coaching_note": "Search within acceptable duration"
        }
    elif 40 < duration_seconds <= 45:
        return {
            "status": "FLAG",
            "threshold_applied": "40-45s flag window",
            "flag_window": True,
            "grade_impact": 10,  # No score reduction
            "coaching_note": "40-45s window: flag for improvement, no penalty per spec"
        }
    else:  # > 45
        return {
            "status": "VIOLATION",
            "threshold_applied": "45s",
            "flag_window": False,
            "grade_impact": 9,
            "exceeds_threshold_by": round(duration_seconds - 45, 3),
            "coaching_note": f"Exceeds 45s threshold by {duration_seconds - 45:.1f}s (Grade 9)"
        }


def extract_timing(call_dir: Path) -> Dict:
    """Extract search timing from transcript files."""

    call_id = call_dir.name
    vtt_path = call_dir / 'transcript-2.vtt'
    para_path = call_dir / 'paragraphs-2.json'

    if not vtt_path.exists():
        return {"error": f"VTT file not found: {vtt_path}"}

    # Load transcripts
    utterances = load_vtt(vtt_path)

    # Find all search announcements first
    search_announcements = []
    for i, utt in enumerate(utterances):
        if is_search_announcement(utt['text'], utt['speaker']):
            search_announcements.append((i, utt))

    # Merge consecutive search announcements within SEARCH_MERGE_WINDOW
    merged_searches = []
    i = 0
    while i < len(search_announcements):
        idx, utt = search_announcements[i]
        start_idx = idx
        start_utt = utt

        # Check if next announcement is within merge window (likely continuation)
        while i + 1 < len(search_announcements):
            next_idx, next_utt = search_announcements[i + 1]
            time_diff = next_utt['start'] - utt['start']

            if time_diff <= SEARCH_MERGE_WINDOW:
                # This is likely a continuation, skip it
                i += 1
                utt = next_utt  # Update to check next one
            else:
                break

        merged_searches.append((start_idx, start_utt))
        i += 1

    # Now process each merged search
    searches = []
    for i, utt in merged_searches:
            # Find answer delivery
            answer = find_substantive_answer(utterances, i)

            if answer:
                duration_seconds = answer['start'] - utt['start']

                # Find any check-ins between search and answer
                check_ins = []
                for j in range(i + 1, utterances.index(answer)):
                    check_utt = utterances[j]
                    if is_checkin(check_utt['text'], check_utt['speaker']):
                        check_ins.append({
                            "timestamp": ms_to_timestamp(int(check_utt['start'] * 1000)),
                            "phrase": check_utt['text'],
                            "line_number": check_utt['seq']
                        })
                    elif check_utt['speaker'] == 'CUSTOMER':
                        # Customer speaking during search (potential impatience)
                        check_ins.append({
                            "timestamp": ms_to_timestamp(int(check_utt['start'] * 1000)),
                            "phrase": check_utt['text'],
                            "speaker": "CUSTOMER",
                            "line_number": check_utt['seq'],
                            "note": "Customer spoke during search (potential impatience)"
                        })

                assessment = assess_search(duration_seconds)

                searches.append({
                    "search_number": len(searches) + 1,
                    "start_timestamp": ms_to_timestamp(int(utt['start'] * 1000)),
                    "start_line_number": utt['seq'],
                    "start_phrase": utt['text'],
                    "start_speaker": utt['speaker'],
                    "end_timestamp": ms_to_timestamp(int(answer['start'] * 1000)),
                    "end_line_number": answer['seq'],
                    "end_phrase": answer['text'],
                    "end_speaker": answer['speaker'],
                    "duration_seconds": round(duration_seconds, 3),
                    "duration_formatted": f"{int(duration_seconds // 60)}m {duration_seconds % 60:.1f}s" if duration_seconds >= 60 else f"{duration_seconds:.1f}s",
                    "check_ins": check_ins,
                    "assessment": assessment
                })

    # Generate summary
    summary = {
        "total_duration_all_searches": round(sum(s['duration_seconds'] for s in searches), 3),
        "longest_search": round(max((s['duration_seconds'] for s in searches), default=0), 3),
        "violations_count": sum(1 for s in searches if s['assessment']['status'] == 'VIOLATION'),
        "flag_count": sum(1 for s in searches if s['assessment']['status'] == 'FLAG'),
        "pass_count": sum(1 for s in searches if s['assessment']['status'] == 'PASS')
    }

    return {
        "call_id": call_id,
        "total_searches": len(searches),
        "searches": searches,
        "summary": summary,
        "final_9_1_assessment": {
            "criterion": "9.1 - Long Information Search",
            "status": "VIOLATION" if summary['violations_count'] > 0 else ("FLAG" if summary['flag_count'] > 0 else "PASS"),
            "grade_impact": 9 if summary['violations_count'] > 0 else (10 if summary['flag_count'] > 0 else 10),
            "flag_for_coaching": summary['flag_count'] > 0 or summary['violations_count'] > 0
        }
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_timing.py <call_dir>", file=sys.stderr)
        print("Example: python extract_timing.py calls/call_08", file=sys.stderr)
        sys.exit(1)

    call_dir = Path(sys.argv[1])

    if not call_dir.exists():
        print(f"Error: Directory not found: {call_dir}", file=sys.stderr)
        sys.exit(1)

    result = extract_timing(call_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
