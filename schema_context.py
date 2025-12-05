# schema_context.py - FINAL CORRECTED VERSION

from typing import Dict, List, Optional

# ============================================================================
# TIMETABLE SCHEMA
# ============================================================================

TIMETABLE_SCHEMA = """
## TIMETABLE SYSTEM SCHEMA:

Use these EXACT query patterns from Query_explanation.txt:

### BATCH TIMETABLE PATTERN:
```sql
SELECT 
    b.name AS batch_name,
    s.name AS subject_name,
    l.lesson_type,
    c.period,
    c.days,
    cr.name AS classroom_name,
    p.start_time,
    p.end_time
FROM batch b
JOIN "group" g ON g.class_id = b.class_id
JOIN lesson l ON g.group_id::text = ANY(
    string_to_array(trim(both '{{}}' from l.group_ids), ',')
)
JOIN card c ON c.lesson_id = l.lesson_id
JOIN subject s ON s.subject_id = l.subject_id
JOIN classroom cr ON cr.classroom_id = ANY(
    string_to_array(trim(both '{{}}' from l.classroom_ids), ',')
)
JOIN periods p ON p.period = c.period
WHERE b.name = 'BATCH_NAME'
  AND c.days = 'BINARY_DAY';
```

### WHERE IS BATCH PATTERN:
```sql
WITH today_binary AS (
    SELECT CASE 
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Monday%' THEN '100000'
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Tuesday%' THEN '010000'
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Wednesday%' THEN '001000'
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Thursday%' THEN '000100'
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Friday%' THEN '000010'
        WHEN TO_CHAR(CURRENT_DATE, 'Day') ILIKE 'Saturday%' THEN '000001'
    END AS day_code
)
SELECT 
    b.name AS batch_name,
    s.name AS subject_name,
    l.lesson_type,
    cr.name AS classroom_name,
    p.start_time,
    p.end_time
FROM batch b
JOIN "group" g ON g.class_id = b.class_id
JOIN lesson l ON g.group_id::text = ANY(
    string_to_array(trim(both '{{}}' from l.group_ids), ',')
)
JOIN card c ON c.lesson_id = l.lesson_id
JOIN today_binary tb ON c.days = tb.day_code
JOIN subject s ON s.subject_id = l.subject_id
JOIN classroom cr ON cr.classroom_id = ANY(
    string_to_array(trim(both '{{}}' from l.classroom_ids), ',')
)
JOIN periods p ON p.period = c.period
WHERE b.name = 'BATCH_NAME'
  AND CURRENT_TIME BETWEEN p.start_time AND p.end_time;
```

### FREE CLASSROOMS PATTERN:
```sql
-- Free rooms at specific time
SELECT c.classroom_id, c.name AS classroom_name
FROM classroom c
WHERE c.classroom_id NOT IN (
    SELECT s.classroom_id
    FROM session s
    WHERE s.start_time::time < 'END_TIME'::time
      AND s.end_time::time > 'START_TIME'::time
);

-- Free rooms RIGHT NOW
SELECT c.classroom_id, c.name AS classroom_name
FROM classroom c
WHERE c.classroom_id NOT IN (
    SELECT s.classroom_id
    FROM session s
    WHERE CURRENT_TIME BETWEEN s.start_time::time AND s.end_time::time
);
```

## IMPORTANT:
- Days: Monday='100000', Tuesday='010000', Wednesday='001000', Thursday='000100', Friday='000010', Saturday='000001'
- Arrays: Use string_to_array(trim(both '{{}}' from column), ',')
- Always include lesson_type in timetable queries
"""

# ============================================================================
# STUDENT/TEACHER SCHEMA
# ============================================================================

STUDENT_SCHEMA = """
## PERSON LOOKUP SCHEMA:

### STUDENT INFO:
```sql
SELECT 
    sei.enrollment_no,
    sei.name_of_student,
    sei.branch,
    sei.semester,
    sei.class,
    sei.batch,
    sei.gender,
    sei.student_phone_no,
    sei.parents_phone_no,
    sei.student_gnu_mail_id,
    ui.full_name,
    ui.email_id,
    ui.mobile_no,
    ui.address,
    ui.city
FROM student_enrollment_information sei
LEFT JOIN user_info ui ON sei.user_id::text = ui.user_id::text
WHERE sei.enrollment_no = 'ENROLLMENT'
   OR sei.name_of_student ILIKE '%NAME%'
   OR sei.student_phone_no = 'PHONE'
LIMIT 10;
```

### TEACHER INFO:
```sql
SELECT 
    tt_display_full_name,
    email_id,
    user_id as employee_id
FROM teacher_enrollment_info
WHERE tt_display_full_name ILIKE '%NAME%'
   OR email_id ILIKE '%EMAIL%'
   OR user_id = 'EMPLOYEE_ID'
LIMIT 10;
```

## CRITICAL NOTES:
- Enrollment: 11 digits (student) or 5-6 digits (teacher)
- Use ::text cast for user_id joins to avoid type mismatch
- Search students first, then teachers if no results
- Return top 10 matches for ambiguous queries
"""

CLASSROOM_SCHEMA = """
## ROOM AVAILABILITY:

Use session table patterns from Query_explanation.txt (shown in TIMETABLE_SCHEMA above).
"""

# ============================================================================
# DAY MAPPING
# ============================================================================

DAY_TO_BINARY = {
    'MON': '100000', 'MONDAY': '100000',
    'TUE': '010000', 'TUESDAY': '010000',
    'WED': '001000', 'WEDNESDAY': '001000',
    'THU': '000100', 'THURSDAY': '000100',
    'FRI': '000010', 'FRIDAY': '000010',
    'SAT': '000001', 'SATURDAY': '000001',
}

BINARY_TO_DAY = {
    '100000': 'Monday', '010000': 'Tuesday', '001000': 'Wednesday',
    '000100': 'Thursday', '000010': 'Friday', '000001': 'Saturday',
}

def get_schema_for_query_type(query_type: str) -> str:
    """Return schema for query type"""
    schema_map = {
        'TIMETABLE_VIEW': TIMETABLE_SCHEMA,
        'BATCH_TIMETABLE': TIMETABLE_SCHEMA,
        'WHERE_IS_BATCH': TIMETABLE_SCHEMA,
        'ROOM_AVAILABILITY': CLASSROOM_SCHEMA,
        'STUDENT_INFO': STUDENT_SCHEMA,
        'TEACHER_INFO': STUDENT_SCHEMA,
        'PERSON_LOOKUP': STUDENT_SCHEMA,
        'GENERAL': '',
        'GREETING': '',
    }
    return schema_map.get(query_type, '')


def get_day_binary(day_name: Optional[str]) -> str:
    """Convert day to binary, with safe handling of None"""
    if not day_name:
        # Default to Friday if no day specified
        return '000010'
    return DAY_TO_BINARY.get(day_name.upper(), '000010')


def get_day_name(binary: str) -> str:
    """Convert binary to day name"""
    return BINARY_TO_DAY.get(binary, 'Unknown')


def get_current_day_binary() -> str:
    """Get current day as binary code"""
    from datetime import datetime
    day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    day_name = day_names[datetime.now().weekday()]
    return get_day_binary(day_name)