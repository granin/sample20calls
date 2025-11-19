# QUICK REFERENCE - 17 GRADING CRITERIA
## Russian Contact Center Evaluation System (СО 2024 ВТМ)

---

## GRADE 10 - EXCELLENCE (Baseline Quality)

### 10.2 - Script Work
**Rule**: Information provided per script, strict adherence when required, logical presentation when flexible

**Violation**: Information not per script, illogical presentation, script requirements not met

**Detection**: Check greeting format, information delivery matches approved script, logical flow

**Confidence**: HIGH

---

### 10.3 - Dialogue Management
**Rule**: Ability to listen AND hear customer, building rapport, dialogue creation not just info delivery, all questions logically connected and sequential, proper opening/closing, not giving conversation control to customer

**Violation**: Not listening to customer, no rapport building, questions disconnected, improper opening/closing, lost conversation control

**Detection**: Customer name usage, rapport indicators, conversation flow, opening/closing phrases

**Confidence**: HIGH

---

### 10.6 - Information Completeness
**Rule**: Correct, accurate, complete project information, confident command of additional information, fast search for needed information

**Violation**: Incomplete information, uncertainty, slow information retrieval

**Detection**: Check if core information was provided, note any gaps

**Confidence**: MEDIUM (partial without project config)

---

## GRADE 9 - MINOR ISSUES

### 9.1 - Long Information Search
**Rule**: Standard question answer within 3 seconds, complex/database lookup max 40 seconds. Timer START when operator announces search, END when operator begins delivering information. Returns to customer don't reset timer (total search duration counted).

**Thresholds**:
- 0-40s: PASS
- 40-45s: FLAG for improvement only (NO score reduction)
- >45s: VIOLATION (score reduction)

**Violation**: Search >45 seconds

**Detection**: Find search announcement ("Сейчас посмотрю", "Минутку"), measure silence/search duration until info delivery starts

**Confidence**: HIGH

---

### 9.3 - No Thank You for Waiting
**Rule**: Not thanking customer for waiting after information search completion, even if operator returned to customer every 40 seconds during search

**Violation**: Search completed but no gratitude expressed

**Detection**: Look for "(спасибо|благодарю).*(ожидани|подождал|ждал)" within 5s after search

**Confidence**: HIGH

---

## GRADE 7 - PROCESS VIOLATIONS

### 7.1 - Script Violations
**Rule**: Question sequence followed, information priority maintained, script conditions met, greeting/closing technique followed, required questions asked. Applies when strict question order required by script. Only violations explicitly stated in project documentation count.

**Violation**: Sequence wrong, priorities violated, conditions not met, greeting/closing wrong, required questions missing

**Detection**: Check greeting phrase structure, question order, closing format, customer orientation questions

**Confidence**: HIGH

---

### 7.2 - Echo Method Not Used ⭐ CRITICAL
**Rule**: When recording ANY customer contact data (name/full name/ФИО, address, phone number, email address, other contact info), operator must use Echo method = Read data back to customer for verification

**Violation**: Contact data collected without repeat-back confirmation

**Detection**: 
1. Find contact data collection moments (word-level JSON)
2. Check for operator repeat within 10 seconds
3. Check for confirmation request ("Верно?", "Правильно?")
4. Check for customer confirmation ("Да", "Верно")

**Confidence**: VERY_HIGH (requires word-level JSON timestamps)

**Example**:
- CORRECT: "Ваш номер 912-778-1421, верно?" → Customer: "Да"
- VIOLATION: Customer: "Алексей" → Operator: "Хорошо, Алексей" (no confirmation)

---

### 7.3 - 5-Second Timing Rules
**Rule**: 
A) Operator presentation AFTER 5 seconds from call start (violation)
B) Not disconnecting call within 5 seconds after conversation end

**Violation**: Intro >5s from start OR disconnect >5s after end

**Detection**: 
- Intro: First operator speech timestamp from 0:00.000
- Outro: Time from last speech to call end

**Confidence**: HIGH

---

### 7.4 - Interruption Without Apology
**Rule**: Impolite attitude: interrupting/cutting off customer speech. Exception: operator says "Извините, что перебиваю вас" (Sorry for interrupting you)

**Violation**: Cuts off customer without apology

**Detection**: 
1. Find overlapping speech (operator starts while customer speaking)
2. Check for apology within 3 seconds
3. Look for "(извинит|простит).*(перебил|перебива)"

**Confidence**: HIGH

---

## GRADE 6 - CRITICAL ISSUES

### 6.1 - Critical Silence / Customer Hangup
**Rule**: Long search/silence resulted in customer hanging up. Operator searching >40 seconds, customer didn't wait, customer ended call first. OR call received but customer didn't wait for operator answer.

**Timing**:
- 0-40s: OK
- 40-45s: FLAG only (no reduction)
- >45s: Violation if customer hangs up

**Violation**: Search >45s + customer terminated call

**Detection**: Check silence duration, who ended call (customer vs operator)

**Confidence**: HIGH

---

## GRADE 5 - INCOMPLETE WORK

### 5.1 - Incomplete Information Provision
**Rule**: Incomplete information provision. Missing mandatory information: addresses, operating hours/schedule, phone numbers, additional required information, incident number, booking/reservation number, not reading all required information

**Violation**: Core required information missing

**Detection**: Check if addresses, hours, phone numbers, incident/booking numbers provided

**Confidence**: MEDIUM (need project config for complete validation)

---

## GRADE 4 - CUSTOMER HANDLING

### 4.1 - Difficult Customer Handling
**Rule**: Cannot handle difficult customers. Includes inability to handle: difficult/rude customers, overly talkative customers, slow/deliberate customers, rushed/hurried customers, other non-standard customer types, cannot defuse customer negativity, emotional tone decline.

**Violation**: Cannot adapt to customer type, shows frustration, tone declines

**Detection**: Text indicators of frustration, inability to redirect customer, lack of adaptation to customer pace

**Confidence**: LOW (text-based partial assessment only, full tone needs audio)

**Note**: Use text evidence where available, but acknowledge limitations without audio

---

## GRADE 3 - SERIOUS ISSUES

### 3.1 - Unresolved Customer Request
**Rule**: Expected information not offered. Results in: customer question unanswered, information request unfulfilled per script, customer loss, client conditions not met, customer emotional decline

**Violation**: Customer request not resolved by end of call

**Detection**: Track customer questions/requests, verify each was answered, check for workaround vs full resolution

**Confidence**: MEDIUM (borderline cases need manager review)

**Note**: If unclear whether workaround counts as resolution, FLAG for review

---

### 3.3 - Confidential Information Disclosure
**Rule**: Providing confidential information. Definition: information explicitly forbidden by script/instructions. Examples: office phone numbers, personal customer data without ID verification. Information operator knows but should not disclose

**Violation**: Disclosed forbidden information without authorization

**Detection**: 
- Patterns: "(офис|внутренн).*\\d{3}[-\\s]?\\d{3}[-\\s]?\\d{4}"
- Internal codes: "(код доступ|пароль|внутренн.*номер)"
- Check if customer ID verification performed before disclosure

**Confidence**: HIGH

---

### 3.6 - Unverified Information
**Rule**: Inaccurate/unreliable information provision. Includes: providing info 'from memory' when strict script adherence required, giving unverified information, knowingly giving wrong information, information doesn't match customer request but presented as correct

**Violation**: Gave info without system verification when required

**Detection**: 
- Check for search cues: "(сейчас.*посмотр|провер|уточн|найд.*информац)"
- If strict verification required but no search performed = violation

**Confidence**: MEDIUM (depends on whether strict verification applies)

---

## GRADE 2 - SERVICE FAILURE

### 2.1 - Call Dropout / Service Refusal
**Rule**: Call dropout by operator side, service refusal. Definition: employee unjustifiably refuses service despite having all necessary information, terminates dialogue with customer without reason

**Violation**: Operator refuses service or disconnects without valid reason

**Detection**: Check call termination pattern, look for refusal phrases, verify who ended call

**Confidence**: HIGH

---

## GRADE 1 - GROSS MISCONDUCT

### 1.1 - Rudeness / Profanity / Yelling
**Rule**: Rudeness during conversation, harshness detected, harsh interruption of customer, profanity/obscene language, yelling/shouting. Also applies DURING TRANSFER. Definition: gross violations detected: rudeness, harshness, harsh customer interruption, profanity, yelling

**Violation**: Operator uses profanity, yells, or shows harsh attitude

**Detection**: 
- Profanity: "(блять|хрен|черт|ебан|пизд)"
- Harsh language: "(отвали|отстань|надоел)"
- NOTE: Can detect text profanity, but harsh TONE requires audio

**Confidence**: LOW for tone, HIGH for text profanity

**Important**: Customer profanity is NOT a violation (only operator behavior matters)

---

## SCORING RULES

### Lowest Code Principle
If violations at multiple grades detected → final grade = MIN(all violation grades)

**Example**:
- Violations: [10, 9, 7, 3]
- Final grade = 3 (lowest)

### 40-45 Second Flag Window (Criterion 9.1)
- 0-40s: PASS
- 40-45s: FLAG for improvement (no score reduction)
- >45s: VIOLATION (score reduction applies)

### Confidence Thresholds
- **VERY_HIGH** (0.90+): Auto-grade, no review needed
- **HIGH** (0.75+): Auto-grade, no review needed
- **MEDIUM** (0.50+): Flag for manager review
- **LOW** (<0.50): Note indicators only, don't penalize

### Evidence Requirements
Every violation must include:
1. Criterion code (e.g., "7.2")
2. Timestamp (MM:SS.sss)
3. Evidence (transcript excerpt or description)
4. Confidence score (0.0-1.0)

---

## QUICK LOOKUP BY GRADE

```
Grade 10: 10.2, 10.3, 10.6
Grade 9:  9.1, 9.3
Grade 7:  7.1, 7.2, 7.3, 7.4
Grade 6:  6.1
Grade 5:  5.1
Grade 4:  4.1
Grade 3:  3.1, 3.3, 3.6
Grade 2:  2.1
Grade 1:  1.1
```

**Total: 17 criteria**

---

## DETECTION PRIORITIES

### Must Use Word-Level JSON:
- 7.2 (Echo method) - Requires millisecond precision

### VTT/SRT Sufficient:
- All other 16 criteria - Line-level timing adequate

### Text-Based Partial Only:
- 1.1 (Rudeness) - Can detect profanity, not tone
- 4.1 (Difficult customer) - Can detect text indicators, not tone decline

---

## COMMON PATTERNS

### Echo Method Violation (7.2)
**Customer**: "Мой номер 912-778-1421"
**Operator**: "Хорошо" ← VIOLATION (no repeat + confirmation)
**Correct**: "Итак, ваш номер 912-778-1421, верно?"

### Long Search Flag vs Violation (9.1)
- Search 42s: FLAG only (no score reduction)
- Search 47s: VIOLATION (score reduction)

### Unresolved Request Borderline (3.1)
**Customer**: "Сайт не работает"
**Operator**: "Давайте я оформлю вручную" ← FLAG for review (workaround vs resolution?)

---

*System: СО 2024 ВТМ v2024.09*  
*Scope: 17 transcript-assessable criteria*  
*Last Updated: 2025-11-19*
