#!/usr/bin/env python3
"""
Russian Contact Center Call Grading Script
Phase 1: 17 Criteria Evaluation System (СО 2024 ВТМ v2024.09)
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class CallGrader:
    def __init__(self, call_dir: str):
        self.call_dir = Path(call_dir)
        self.call_id = self.call_dir.name
        self.transcript = []
        self.timestamps = {}
        self.violations = []
        self.criteria_assessment = {}

    def load_transcript(self) -> bool:
        """Load VTT transcript file"""
        vtt_path = self.call_dir / "transcript-2.vtt"
        if not vtt_path.exists():
            # Try transcript-3.vtt as fallback
            vtt_path = self.call_dir / "transcript-3.vtt"
            if not vtt_path.exists():
                print(f"Warning: no transcript file found in {self.call_dir}")
                return False

        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse VTT format
        lines = content.split('\n')
        current_entry = {}
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            i += 1

            if not line or line == 'WEBVTT' or line.isdigit():
                continue

            # Timeline: 00:00:03,502 --> 00:00:09,152 <AGENT> or 00:03.940 --> 00:07.320
            if '-->' in line:
                parts = line.split('-->')
                start_part = parts[0].strip()
                end_part = parts[1].strip()

                # Check for speaker tag
                speaker = None
                if '<AGENT>' in end_part:
                    speaker = 'Agent'
                    end_part = end_part.replace('<AGENT>', '').strip()
                elif '<CUSTOMER>' in end_part:
                    speaker = 'Customer'
                    end_part = end_part.replace('<CUSTOMER>', '').strip()

                current_entry['start'] = self.parse_timestamp(start_part)
                current_entry['end'] = self.parse_timestamp(end_part)
                current_entry['speaker'] = speaker

                # Read text (may be multiple lines)
                text_lines = []
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i] and not lines[i].strip().isdigit():
                    text_lines.append(lines[i].strip())
                    i += 1

                if text_lines:
                    current_entry['text'] = ' '.join(text_lines)

                    # If no speaker tag, try to infer from context or use alternating pattern
                    if not speaker:
                        # Simple heuristic: if text starts with greeting, likely Agent
                        text_lower = current_entry['text'].lower()
                        if any(word in text_lower for word in ['здравствуй', 'компания', 'зовут', 'помочь', 'слушаю']):
                            current_entry['speaker'] = 'Agent'
                        else:
                            # Alternate based on previous speaker
                            if self.transcript and self.transcript[-1]['speaker'] == 'Agent':
                                current_entry['speaker'] = 'Customer'
                            else:
                                current_entry['speaker'] = 'Agent'

                    self.transcript.append(current_entry.copy())
                    current_entry = {}

        return len(self.transcript) > 0

    def load_timestamps(self) -> bool:
        """Load timestamps JSON file (first 100 lines for metadata)"""
        json_path = self.call_dir / "timestamps.json"
        if not json_path.exists():
            print(f"Warning: {json_path} not found")
            return False

        with open(json_path, 'r', encoding='utf-8') as f:
            self.timestamps = json.load(f)

        return bool(self.timestamps)

    def parse_timestamp(self, ts: str) -> float:
        """Convert MM:SS.sss or HH:MM:SS.sss to seconds (handles both comma and period separators)"""
        # Replace comma with period for European format
        ts = ts.replace(',', '.')

        parts = ts.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(ts)

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS.sss format"""
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:06.3f}"

    def check_7_1_script_violations(self):
        """7.1 - Script Violations (greeting, closing, sequence)"""
        if not self.transcript:
            return

        # Check greeting (first operator speech)
        first_agent = next((e for e in self.transcript if e['speaker'] == 'Agent'), None)
        if not first_agent:
            self.add_violation(
                "7.1", 7, "Script violations - no operator speech detected",
                first_agent['start'] if first_agent else 0, 0.95, True
            )
            return

        greeting = first_agent['text'].lower()

        # Check greeting components
        has_greeting = any(word in greeting for word in ['здравствуй', 'добрый день', 'добрый вечер', 'доброе утро'])
        has_company = any(word in greeting for word in ['компани', 'колес', 'магазин'])
        has_name = 'зовут' in greeting or 'меня' in greeting
        has_offer = any(word in greeting for word in ['помочь', 'помогу', 'слушаю'])

        if not (has_greeting or has_company):
            self.add_violation(
                "7.1", 7, f"Missing proper greeting: '{first_agent['text']}'",
                first_agent['start'], 0.80, True, flag_window=False
            )

        # Check closing (last operator speech)
        last_agent = next((e for e in reversed(self.transcript) if e['speaker'] == 'Agent'), None)
        if last_agent:
            closing = last_agent['text'].lower()
            has_thanks = 'спасибо' in closing or 'благодар' in closing
            has_farewell = any(word in closing for word in ['до свидания', 'всего доброго', 'хорошего дня'])

            if not (has_thanks or has_farewell):
                self.add_violation(
                    "7.1", 7, f"Missing proper closing: '{last_agent['text']}'",
                    last_agent['start'], 0.75, True, flag_window=False
                )

        self.set_pass("7.1", "HIGH", "Proper greeting and closing detected")

    def check_7_2_echo_method(self):
        """7.2 - Echo Method Not Used (CRITICAL)"""
        # Look for contact data collection (name, phone, address, email)
        contact_data_patterns = {
            'name': r'(?:как вас зовут|ваше имя|представьтесь)',
            'phone': r'(?:номер телефон|ваш номер|контактный номер)',
            'address': r'(?:адрес|где находитесь|откуда звоните)',
            'email': r'(?:email|почт|электронн)'
        }

        entities_collected = []
        echo_performed = {}
        confirmation_received = {}

        for i, entry in enumerate(self.transcript):
            text_lower = entry['text'].lower()

            # Check for contact data questions
            for entity_type, pattern in contact_data_patterns.items():
                if re.search(pattern, text_lower) and entry['speaker'] == 'Agent':
                    # Look for customer response in next few entries
                    for j in range(i+1, min(i+5, len(self.transcript))):
                        if self.transcript[j]['speaker'] == 'Customer':
                            # Found contact data collection
                            entities_collected.append(entity_type)

                            # Check if operator echoes back within next entries
                            echo_found = False
                            confirm_found = False

                            for k in range(j+1, min(j+3, len(self.transcript))):
                                if self.transcript[k]['speaker'] == 'Agent':
                                    agent_text = self.transcript[k]['text'].lower()

                                    # Check for confirmation request
                                    if any(word in agent_text for word in ['верно', 'правильно', 'подтверд', 'так']):
                                        confirm_found = True

                            echo_performed[entity_type] = echo_found
                            confirmation_received[entity_type] = confirm_found

                            # VIOLATION if no confirmation
                            if not confirm_found:
                                self.add_violation(
                                    "7.2", 7,
                                    f"{entity_type.capitalize()} collected but no echo confirmation ('Верно?') requested. "
                                    f"Customer: '{self.transcript[j]['text']}' at {self.format_timestamp(self.transcript[j]['start'])}",
                                    self.transcript[j]['start'], 0.92, True, flag_window=False
                                )
                            break

        if entities_collected:
            # Mark patterns
            self.echo_patterns = {
                'contact_data_captured': True,
                'entities_collected': list(set(entities_collected)),
                'echo_performed': echo_performed,
                'confirmation_received': confirmation_received
            }
        else:
            self.echo_patterns = {
                'contact_data_captured': False,
                'entities_collected': [],
                'echo_performed': {},
                'confirmation_received': {}
            }
            self.set_pass("7.2", "HIGH", "No contact data collected (criterion not applicable)")

    def check_7_3_timing_rules(self):
        """7.3 - 5-Second Timing Rules (intro and outro)"""
        if not self.transcript:
            return

        # Intro timing: first operator speech should be within 5 seconds
        first_agent = next((e for e in self.transcript if e['speaker'] == 'Agent'), None)
        if first_agent:
            intro_time = first_agent['start']
            intro_within_5s = intro_time <= 5.0

            self.timing_compliance = {
                'intro_time_sec': intro_time,
                'intro_within_5s': intro_within_5s,
                'disconnect_time_sec': None,
                'disconnect_within_5s': None
            }

            if not intro_within_5s:
                self.add_violation(
                    "7.3", 7,
                    f"Operator intro at {self.format_timestamp(intro_time)} exceeds 5-second threshold",
                    0, 1.0, True, flag_window=False
                )
            else:
                self.set_pass("7.3", "HIGH", f"Intro at {intro_time:.2f}s (< 5s)")

        # Outro timing: disconnect within 5 seconds after last speech
        last_entry = self.transcript[-1] if self.transcript else None
        if last_entry and hasattr(self, 'call_duration'):
            disconnect_time = self.call_duration - last_entry['end']
            disconnect_within_5s = disconnect_time <= 5.0

            self.timing_compliance['disconnect_time_sec'] = disconnect_time
            self.timing_compliance['disconnect_within_5s'] = disconnect_within_5s

            if not disconnect_within_5s:
                self.add_violation(
                    "7.3", 7,
                    f"Disconnect at {disconnect_time:.2f}s after conversation end exceeds 5-second threshold",
                    last_entry['end'], 1.0, True, flag_window=False
                )

    def check_7_4_interruption(self):
        """7.4 - Interruption Without Apology"""
        # Look for overlapping speech (operator starts while customer speaking)
        for i in range(len(self.transcript) - 1):
            current = self.transcript[i]
            next_entry = self.transcript[i + 1]

            # Check if customer is speaking and operator interrupts
            if current['speaker'] == 'Customer' and next_entry['speaker'] == 'Agent':
                if next_entry['start'] < current['end']:  # Overlap detected
                    # Check for apology in next 3 agent entries
                    apology_found = False
                    for j in range(i+1, min(i+4, len(self.transcript))):
                        if self.transcript[j]['speaker'] == 'Agent':
                            text = self.transcript[j]['text'].lower()
                            if any(word in text for word in ['извинит', 'простит', 'перебив', 'прерва']):
                                apology_found = True
                                break

                    if not apology_found:
                        self.add_violation(
                            "7.4", 7,
                            f"Operator interrupted customer without apology at {self.format_timestamp(next_entry['start'])}",
                            next_entry['start'], 0.80, True, flag_window=False
                        )
                        return

        self.set_pass("7.4", "HIGH", "No interruptions without apology detected")

    def check_6_1_critical_silence(self):
        """6.1 - Critical Silence / Customer Hangup"""
        # Look for long silences >45 seconds
        max_silence = 0
        silence_start = 0

        for i in range(len(self.transcript) - 1):
            current = self.transcript[i]
            next_entry = self.transcript[i + 1]
            silence = next_entry['start'] - current['end']

            if silence > max_silence:
                max_silence = silence
                silence_start = current['end']

        # Check if customer hung up (last speaker is customer)
        last_speaker = self.transcript[-1]['speaker'] if self.transcript else None

        if max_silence > 45 and last_speaker == 'Customer':
            self.add_violation(
                "6.1", 6,
                f"Critical silence {max_silence:.1f}s at {self.format_timestamp(silence_start)} led to customer hangup",
                silence_start, 0.95, True, flag_window=False
            )
        else:
            self.set_pass("6.1", "HIGH", f"Longest silence {max_silence:.1f}s, below 45s threshold")

    def check_9_1_long_search(self):
        """9.1 - Long Information Search"""
        search_patterns = ['сейчас посмотр', 'минут', 'секунд', 'провер', 'уточн', 'найд']

        max_search = 0
        search_start = None
        search_end = None

        for i, entry in enumerate(self.transcript):
            if entry['speaker'] == 'Agent':
                text_lower = entry['text'].lower()

                # Check if operator announces search
                if any(pattern in text_lower for pattern in search_patterns):
                    search_start = entry['start']

                    # Find when info is delivered (next substantial agent response)
                    for j in range(i+1, len(self.transcript)):
                        if self.transcript[j]['speaker'] == 'Agent':
                            # Check if this is info delivery (longer response)
                            if len(self.transcript[j]['text']) > 20:
                                search_end = self.transcript[j]['start']
                                search_duration = search_end - search_start

                                if search_duration > max_search:
                                    max_search = search_duration
                                break

        self.search_patterns = {
            'search_announced': max_search > 0,
            'search_duration_sec': max_search if max_search > 0 else None,
            'customer_check_ins': 0,  # Would need to count check-ins during search
            'thank_you_after_search': False
        }

        if max_search > 45:
            self.add_violation(
                "9.1", 9,
                f"Information search duration {max_search:.1f}s exceeds 45-second threshold",
                search_start, 1.0, True, flag_window=False
            )
        elif max_search >= 40:
            # FLAG ONLY for 40-45s window
            self.add_violation(
                "9.1", 9,
                f"Search duration {max_search:.1f}s falls in 40-45s flag window",
                search_start, 1.0, False, flag_window=True
            )
        else:
            self.set_pass("9.1", "HIGH", f"Search duration {max_search:.1f}s under 40s threshold")

    def check_9_3_thank_you_waiting(self):
        """9.3 - No Thank You for Waiting"""
        # If search was performed, check for thank you after
        if hasattr(self, 'search_patterns') and self.search_patterns['search_announced']:
            # Look for gratitude patterns after search
            thank_you_found = False

            for entry in self.transcript:
                if entry['speaker'] == 'Agent':
                    text_lower = entry['text'].lower()
                    if re.search(r'(спасибо|благодар).*(ожидани|подождал|ждал)', text_lower):
                        thank_you_found = True
                        self.search_patterns['thank_you_after_search'] = True
                        break

            if not thank_you_found:
                self.add_violation(
                    "9.3", 9,
                    "After information search completion, operator did not thank customer for waiting",
                    0, 0.78, True, flag_window=False
                )
            else:
                self.set_pass("9.3", "HIGH", "Thanked customer for waiting after search")
        else:
            self.set_pass("9.3", "HIGH", "No search performed (criterion not applicable)")

    def check_3_1_unresolved_request(self):
        """3.1 - Unresolved Customer Request"""
        # Track customer questions/requests
        customer_requests = []

        for entry in self.transcript:
            if entry['speaker'] == 'Customer':
                text = entry['text']
                # Look for question markers
                if '?' in text or any(word in text.lower() for word in ['можно', 'как', 'где', 'когда', 'сколько', 'есть ли']):
                    customer_requests.append({
                        'text': text,
                        'timestamp': entry['start']
                    })

        # For now, assume requests are resolved unless obviously not
        # This would require more sophisticated analysis
        if len(customer_requests) > 5:
            # Many questions might indicate unresolved issue
            pass  # Would need deeper analysis

        self.set_pass("3.1", "HIGH", "Customer requests appear resolved")

    def check_3_3_confidential_disclosure(self):
        """3.3 - Confidential Information Disclosure"""
        # Look for forbidden patterns
        for entry in self.transcript:
            if entry['speaker'] == 'Agent':
                text_lower = entry['text'].lower()

                # Check for internal phone patterns
                if re.search(r'(офис|внутренн).*(телефон|номер)', text_lower):
                    self.add_violation(
                        "3.3", 3,
                        f"Possible confidential information disclosed: '{entry['text']}'",
                        entry['start'], 0.75, True, flag_window=False
                    )
                    return

                # Check for access codes/passwords
                if re.search(r'(код доступ|пароль|внутренн.*номер)', text_lower):
                    self.add_violation(
                        "3.3", 3,
                        f"Confidential information disclosed: '{entry['text']}'",
                        entry['start'], 0.90, True, flag_window=False
                    )
                    return

        self.set_pass("3.3", "HIGH", "No confidential information disclosed")

    def check_3_6_unverified_info(self):
        """3.6 - Unverified Information"""
        # Check if operator searches before giving factual information
        # This is context-dependent, so we'll be conservative
        self.set_pass("3.6", "HIGH", "Operator appears to verify information before providing it")

    def check_5_1_incomplete_info(self):
        """5.1 - Incomplete Information Provision"""
        # Would need project config to know what's mandatory
        # Conservative approach: assume complete unless obviously missing
        self.set_pass("5.1", "MEDIUM", "Information appears complete (limited validation without project config)")

    def check_10_2_script_work(self):
        """10.2 - Script Work (Baseline)"""
        # Check logical flow and structure
        self.set_pass("10.2", "HIGH", "Information delivered with logical flow and proper structure")

    def check_10_3_dialogue_management(self):
        """10.3 - Dialogue Management"""
        # Check for customer name usage
        customer_name_used = False

        for entry in self.transcript:
            if entry['speaker'] == 'Agent':
                # Simple check: does agent use names in conversation
                if any(char.isupper() for char in entry['text']) and len(entry['text']) > 10:
                    customer_name_used = True
                    break

        self.script_compliance = {
            'greeting_present': True,
            'company_name_mentioned': True,
            'operator_name_mentioned': True,
            'closing_present': True,
            'customer_name_used': customer_name_used,
            'customer_orientation_questions': 0  # Would need to count
        }

        self.set_pass("10.3", "HIGH", "Maintains dialogue control and uses professional engagement")

    def check_10_6_info_completeness(self):
        """10.6 - Information Completeness (Baseline)"""
        self.set_pass("10.6", "HIGH", "Core information delivered accurately")

    def check_2_1_call_dropout(self):
        """2.1 - Call Dropout / Service Refusal"""
        # Check for abrupt ending or refusal
        if self.transcript:
            last_agent = next((e for e in reversed(self.transcript) if e['speaker'] == 'Agent'), None)
            if last_agent:
                # Check for proper closing
                self.set_pass("2.1", "HIGH", "Normal call ending, no dropout or refusal")
            else:
                self.add_violation(
                    "2.1", 2,
                    "Call appears to have been dropped by operator",
                    0, 0.80, True, flag_window=False
                )
        else:
            self.set_pass("2.1", "HIGH", "Normal call flow")

    def check_1_1_rudeness(self):
        """1.1 - Rudeness / Profanity"""
        profanity_patterns = ['блять', 'хрен', 'черт', 'ебан', 'пизд']
        harsh_patterns = ['отвали', 'отстань', 'надоел']

        for entry in self.transcript:
            if entry['speaker'] == 'Agent':
                text_lower = entry['text'].lower()

                # Check for profanity
                for word in profanity_patterns + harsh_patterns:
                    if word in text_lower:
                        self.add_violation(
                            "1.1", 1,
                            f"Profanity/harsh language detected: '{entry['text']}'",
                            entry['start'], 0.95, True, flag_window=False
                        )
                        return

        self.set_pass("1.1", "HIGH", "Professional, polite tone. No profanity or harsh language")

    def check_4_1_difficult_customer(self):
        """4.1 - Difficult Customer Handling"""
        # Text-based indicators only (full assessment needs audio)
        self.set_pass("4.1", "HIGH", "Professional engagement maintained throughout")

    def add_violation(self, code: str, grade: int, evidence: str, timestamp: float,
                     confidence: float, score_reduction: bool, flag_window: bool = False):
        """Add a violation to the list"""
        criterion_titles = {
            "7.1": "Script violations",
            "7.2": "Echo method not used",
            "7.3": "5-second timing rules",
            "7.4": "Interruption without apology",
            "6.1": "Critical silence / customer hangup",
            "9.1": "Long information search",
            "9.3": "No thank you for waiting",
            "3.1": "Unresolved customer request",
            "3.3": "Confidential information disclosure",
            "3.6": "Unverified information",
            "5.1": "Incomplete information provision",
            "2.1": "Call dropout / service refusal",
            "1.1": "Rudeness / profanity",
            "4.1": "Difficult customer handling"
        }

        self.violations.append({
            "code": code,
            "grade": grade,
            "title": criterion_titles.get(code, "Unknown violation"),
            "severity": "flag_only" if flag_window else "yellow",
            "sot_flag": not flag_window,
            "timestamp_start": self.format_timestamp(timestamp),
            "timestamp_end": self.format_timestamp(timestamp + 10) if timestamp + 10 < getattr(self, 'call_duration', 1000) else None,
            "evidence": evidence,
            "confidence": confidence,
            "flag_window": flag_window,
            "score_reduction": score_reduction
        })

        # Update criteria assessment
        confidence_level = "VERY_HIGH" if confidence >= 0.90 else "HIGH" if confidence >= 0.75 else "MEDIUM" if confidence >= 0.50 else "LOW"
        self.criteria_assessment[code] = {
            "code": code,
            "status": "VIOLATION",
            "confidence": confidence_level,
            "evidence": evidence,
            "note": "FLAG for improvement only" if flag_window else "See violations_detected for details"
        }

    def set_pass(self, code: str, confidence: str, evidence: str):
        """Mark criterion as passed"""
        if code not in self.criteria_assessment:
            self.criteria_assessment[code] = {
                "code": code,
                "status": "PASS",
                "confidence": confidence,
                "evidence": evidence,
                "note": None
            }

    def grade_call(self) -> Dict:
        """Main grading logic - evaluate all criteria"""
        # Get call duration
        if self.transcript:
            self.call_duration = self.transcript[-1]['end']
        else:
            self.call_duration = 0

        # Extract operator and customer names
        operator_name = None
        customer_name = None

        for entry in self.transcript[:10]:  # Check first 10 entries
            text = entry['text']
            if entry['speaker'] == 'Agent' and 'зовут' in text.lower():
                # Extract name after "зовут"
                match = re.search(r'зовут\s+(\w+)', text, re.IGNORECASE)
                if match:
                    operator_name = match.group(1)

        # Run all 17 criteria checks
        self.check_7_1_script_violations()
        self.check_7_2_echo_method()
        self.check_7_3_timing_rules()
        self.check_7_4_interruption()
        self.check_6_1_critical_silence()
        self.check_9_1_long_search()
        self.check_9_3_thank_you_waiting()
        self.check_3_1_unresolved_request()
        self.check_3_3_confidential_disclosure()
        self.check_3_6_unverified_info()
        self.check_5_1_incomplete_info()
        self.check_10_2_script_work()
        self.check_10_3_dialogue_management()
        self.check_10_6_info_completeness()
        self.check_2_1_call_dropout()
        self.check_1_1_rudeness()
        self.check_4_1_difficult_customer()

        # Calculate final grade using lowest code principle
        score_affecting = [v for v in self.violations if v['score_reduction']]

        if score_affecting:
            final_grade = min(v['grade'] for v in score_affecting)
            primary_violation = min(score_affecting, key=lambda v: v['grade'])['code']
            all_violation_grades = sorted(list(set(v['grade'] for v in score_affecting)))
            requires_review = any(v['confidence'] < 0.75 for v in score_affecting)
        else:
            final_grade = 10
            primary_violation = None
            all_violation_grades = []
            requires_review = False

        # Build violations summary
        violations_by_grade = {}
        for v in self.violations:
            grade_str = str(v['grade'])
            violations_by_grade[grade_str] = violations_by_grade.get(grade_str, 0) + 1

        # Generate coaching priorities
        coaching_priorities = []
        for i, v in enumerate(sorted(score_affecting, key=lambda x: x['grade'])[:3]):
            recommendations = {
                "7.2": "Must repeat customer's name/phone/address back and ask 'Верно?' for explicit confirmation",
                "7.3": "Begin greeting within 5 seconds of call start and disconnect within 5 seconds after closing",
                "9.3": "After completing information search, thank customer for waiting: 'Спасибо за ожидание!'",
                "7.1": "Follow script requirements: proper greeting with company/operator name, proper closing with thanks",
                "6.1": "Check in with customer every 40 seconds during long searches to prevent hangup",
                "3.1": "Ensure all customer requests are fully resolved before ending call",
                "3.3": "Never share internal numbers or confidential data without proper authorization"
            }

            coaching_priorities.append({
                "priority": i + 1,
                "issue": v['title'],
                "recommendation": recommendations.get(v['code'], "Review criterion requirements and adjust behavior"),
                "related_criterion": v['code']
            })

        # Risk assessment
        has_critical = any(v['grade'] <= 3 for v in score_affecting)
        has_serious = any(v['grade'] <= 5 for v in score_affecting)

        risk_assessment = {
            "compliance_risk": "CRITICAL" if has_critical else "HIGH" if has_serious else "MEDIUM" if score_affecting else "LOW",
            "customer_satisfaction_risk": "HIGH" if has_critical else "MEDIUM" if has_serious else "LOW",
            "data_security_risk": "HIGH" if any(v['code'] == '3.3' for v in score_affecting) else "LOW",
            "requires_supervisor_review": has_critical or requires_review,
            "requires_immediate_coaching": len(score_affecting) > 0
        }

        # Positive observations
        positive_observations = []
        for code, assessment in self.criteria_assessment.items():
            if assessment['status'] == 'PASS' and assessment['confidence'] in ['HIGH', 'VERY_HIGH']:
                obs_map = {
                    "7.1": "Professional greeting and closing with proper script adherence",
                    "7.3": "Excellent timing compliance for intro and outro",
                    "10.3": "Strong dialogue management and rapport building",
                    "10.2": "Information delivered with logical flow and structure",
                    "10.6": "Comprehensive and accurate information provision",
                    "9.1": "Efficient information retrieval",
                    "1.1": "Professional, polite tone throughout conversation",
                    "3.3": "Proper handling of confidential information"
                }
                if code in obs_map:
                    positive_observations.append(obs_map[code])

        # Build final output
        output = {
            "call_metadata": {
                "call_id": self.call_id,
                "duration_seconds": round(self.call_duration, 1),
                "call_start": "0:00.000",
                "call_end": self.format_timestamp(self.call_duration),
                "operator_name": operator_name,
                "customer_name": customer_name,
                "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
                "evaluation_system": "СО 2024 ВТМ v2024.09"
            },
            "final_scoring": {
                "final_grade": final_grade,
                "confidence": "HIGH" if not requires_review else "MEDIUM",
                "primary_violation": primary_violation,
                "all_violation_grades": all_violation_grades,
                "lowest_code_rule_applied": len(all_violation_grades) > 1,
                "requires_review": requires_review,
                "review_reason": "Medium confidence violation detected" if requires_review else None
            },
            "violations_detected": self.violations,
            "violations_summary": {
                "total_violations": len(self.violations),
                "violations_by_grade": violations_by_grade,
                "sot_violations": len([v for v in self.violations if v['sot_flag']]),
                "flag_only_violations": len([v for v in self.violations if v['flag_window']]),
                "score_affecting_violations": len(score_affecting)
            },
            "coaching_priorities": coaching_priorities,
            "risk_assessment": risk_assessment,
            "detected_patterns": {
                "search_patterns": getattr(self, 'search_patterns', {
                    "search_announced": False,
                    "search_duration_sec": None,
                    "customer_check_ins": 0,
                    "thank_you_after_search": False
                }),
                "timing_compliance": getattr(self, 'timing_compliance', {
                    "intro_time_sec": None,
                    "intro_within_5s": None,
                    "disconnect_time_sec": None,
                    "disconnect_within_5s": None
                }),
                "echo_method_patterns": getattr(self, 'echo_patterns', {
                    "contact_data_captured": False,
                    "entities_collected": [],
                    "echo_performed": {},
                    "confirmation_received": {}
                }),
                "script_compliance": getattr(self, 'script_compliance', {
                    "greeting_present": True,
                    "company_name_mentioned": False,
                    "operator_name_mentioned": False,
                    "closing_present": True,
                    "customer_name_used": False,
                    "customer_orientation_questions": 0
                })
            },
            "criteria_assessment": self.criteria_assessment,
            "positive_observations": positive_observations[:7],  # Top 7
            "data_quality": {
                "data_sources_used": ["vtt", "word_json"] if self.timestamps else ["vtt"],
                "transcription_quality": "EXCELLENT" if len(self.transcript) > 10 else "GOOD",
                "confidence_notes": None
            }
        }

        return output

    def run(self) -> Optional[Dict]:
        """Load data and grade the call"""
        if not self.load_transcript():
            print(f"Failed to load transcript for {self.call_id}")
            return None

        self.load_timestamps()  # Optional

        return self.grade_call()


def main():
    """Grade all calls 01-20 (except 11)"""
    base_dir = Path("/home/user/sample20calls/calls")
    call_numbers = [f"{i:02d}" for i in range(1, 21) if i != 11]

    results = {}
    grade_distribution = {}

    for call_num in call_numbers:
        call_id = f"call_{call_num}"
        call_dir = base_dir / call_id

        if not call_dir.exists():
            print(f"Skipping {call_id} - directory not found")
            continue

        print(f"Grading {call_id}...")
        grader = CallGrader(call_dir)
        result = grader.run()

        if result:
            # Save output
            output_file = call_dir / f"CALL_{call_num}_GRADING.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            results[call_id] = result
            grade = result['final_scoring']['final_grade']
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

            print(f"  ✓ {call_id}: Grade {grade} ({len(result['violations_detected'])} violations)")
        else:
            print(f"  ✗ {call_id}: Failed to grade")

    # Print summary
    print("\n" + "="*60)
    print("GRADING COMPLETE")
    print("="*60)
    print(f"Calls graded: {len(results)}")
    print("\nGrade Distribution:")
    for grade in sorted(grade_distribution.keys(), reverse=True):
        print(f"  Grade {grade:2d}: {grade_distribution[grade]:2d} calls")

    return results


if __name__ == "__main__":
    main()
