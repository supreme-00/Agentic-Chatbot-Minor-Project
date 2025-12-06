# query_router.py - FIXED: Better detection for names and queries

from typing import Dict, Optional
from datetime import datetime
import re

class QueryType:
    STUDENT_INFO = "STUDENT_INFO"
    TEACHER_INFO = "TEACHER_INFO"
    PERSON_LOOKUP = "PERSON_LOOKUP"
    TIMETABLE_VIEW = "TIMETABLE_VIEW"
    BATCH_TIMETABLE = "BATCH_TIMETABLE"
    WHERE_IS_BATCH = "WHERE_IS_BATCH"
    ROOM_AVAILABILITY = "ROOM_AVAILABILITY"
    GENERAL = "GENERAL"
    GREETING = "GREETING"


def detect_query_type(user_message: str) -> str:
    """Detect query type with IMPROVED name detection"""
    msg_lower = user_message.lower().strip()
    msg_original = user_message.strip()
    
    # Greeting patterns (highest priority)
    greeting_patterns = [
        r'^(hi|hello|hey|heyy|greetings|good morning|good afternoon|good evening|namaste)\b',
        r'^(thanks|thank you|bye|goodbye|tata)\b',
    ]
    for pattern in greeting_patterns:
        if re.search(pattern, msg_lower):
            return QueryType.GREETING
    
    # Room availability (check before timetable)
    room_patterns = [
        r'(free|available|empty|vacant|unoccupied).*(classroom|room|lab)',
        r'(classroom|room|lab).*(free|available|empty|vacant)',
        r'which.*(classroom|room|lab).*(available|free)',
    ]
    for pattern in room_patterns:
        if re.search(pattern, msg_lower):
            return QueryType.ROOM_AVAILABILITY
    
    # "Where is batch" patterns
    where_batch_patterns = [
        r'where\s+(is|are)',
        r'(current|now|right now).*(location|place|room)',
        r'(batch|class).*(right now|currently|now)',
        r'location\s+of',
    ]
    for pattern in where_batch_patterns:
        if re.search(pattern, msg_lower):
            # Check if batch/class name present
            if re.search(r'\d+[a-z]{2,3}-[a-z](-\d+)?', msg_lower):
                return QueryType.WHERE_IS_BATCH
    
    # Batch timetable (has format like 7CE-A-3)
    if re.search(r'\d+[a-z]{2,3}-[a-z]-\d+', msg_lower):
        return QueryType.BATCH_TIMETABLE
    
    # Class timetable (has format like 7CE-A or mentions timetable/schedule)
    if re.search(r'\d+[a-z]{2,3}-[a-z]\b', msg_lower):
        return QueryType.TIMETABLE_VIEW
    
    if re.search(r'(timetable|schedule|time\s*table)', msg_lower):
        return QueryType.TIMETABLE_VIEW
    
    # PERSON LOOKUP - IMPROVED DETECTION
    # Check for person-related keywords FIRST
    person_keywords = [
        r'\b(detail|details|info|information)\b',
        r'\b(who\s+is|who\'s)\b',
        r'\btell\s+me\s+about\b',
        r'\babout\s+[A-Z][a-z]+',
        r'\b(fetch|show|get|find|search)\b.*\b(student|teacher|person|name)\b',
        r'\b(student|teacher|professor|faculty)\b.*\b(detail|info|name)\b',
        r'\bphone\s*(number|no)?\b',
        r'\bemail\b',
        r'\benrollment\b',
    ]
    
    has_person_keyword = False
    for pattern in person_keywords:
        if re.search(pattern, msg_lower):
            has_person_keyword = True
            break
    
    # If has person keyword, check what identifier is present
    if has_person_keyword:
        # Check for enrollment (11 digits)
        if re.search(r'\b\d{11}\b', msg_lower):
            return QueryType.PERSON_LOOKUP
        
        # Check for teacher ID (5-6 digits)
        if re.search(r'\b\d{5,6}\b', msg_lower):
            return QueryType.PERSON_LOOKUP
        
        # Check for phone (10 digits)
        if re.search(r'\b\d{10}\b', msg_lower):
            return QueryType.PERSON_LOOKUP
        
        # Check for ANY name (single word that looks like a name)
        # Extract potential names - words after "of", "is", or standalone capitalized
        name_after_keyword = re.search(r'(?:of|is|about|for|named?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)', msg_lower)
        if name_after_keyword:
            potential_name = name_after_keyword.group(1).strip()
            # Filter out common non-name words
            non_names = ['student', 'teacher', 'professor', 'faculty', 'person', 'the', 'a', 'an', 'class', 'batch']
            if potential_name.lower() not in non_names and len(potential_name) >= 2:
                return QueryType.PERSON_LOOKUP
        
        # Check for capitalized name in original message
        if re.search(r'\b[A-Z][a-z]+\b', msg_original):
            return QueryType.PERSON_LOOKUP
        
        # Even without capitalization, if person keyword present, try lookup
        return QueryType.PERSON_LOOKUP
    
    # Check for just a number (enrollment/phone)
    if re.search(r'\b\d{10,11}\b', msg_lower):
        return QueryType.PERSON_LOOKUP
    
    # Check for just a name with common query patterns
    simple_name_patterns = [
        r'^(details?\s+of|info\s+of|about)\s+\w+',
        r'^who\s+is\s+\w+',
        r'^find\s+\w+',
        r'^search\s+\w+',
    ]
    for pattern in simple_name_patterns:
        if re.search(pattern, msg_lower):
            return QueryType.PERSON_LOOKUP
    
    return QueryType.GENERAL


def extract_person_identifier(query: str) -> Dict[str, Optional[str]]:
    """Extract person identifier - IMPROVED for case-insensitive and single names"""
    query_stripped = query.strip()
    query_lower = query_stripped.lower()
    
    # Enrollment: 11 digits
    enrollment_match = re.search(r'\b(\d{11})\b', query_stripped)
    if enrollment_match:
        return {'type': 'student_enrollment', 'value': enrollment_match.group(1)}
    
    # Teacher ID: 5-6 digits
    teacher_id_match = re.search(r'\b(\d{5,6})\b', query_stripped)
    if teacher_id_match:
        return {'type': 'teacher_id', 'value': teacher_id_match.group(1)}
    
    # Phone: 10 digits
    phone_match = re.search(r'\b(\d{10})\b', query_stripped)
    if phone_match:
        return {'type': 'phone', 'value': phone_match.group(1)}
    
    # Email
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query_stripped)
    if email_match:
        return {'type': 'email', 'value': email_match.group(1)}
    
    # NAME extraction - IMPROVED
    # Common non-name words to filter
    stop_words = {
        'details', 'detail', 'info', 'information', 'of', 'about', 'for', 
        'who', 'is', 'the', 'a', 'an', 'student', 'teacher', 'professor',
        'faculty', 'person', 'find', 'search', 'show', 'get', 'fetch',
        'phone', 'number', 'email', 'enrollment', 'name', 'named'
    }
    
    # Try to extract name after common prefixes
    name_patterns = [
        r'(?:details?\s+of|info\s+of|about|for|who\s+is|who\'s|named?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)',
        r'(?:find|search|show|get|fetch)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, query_lower)
        if match:
            potential_name = match.group(1).strip()
            # Remove stop words from beginning
            words = potential_name.split()
            filtered_words = [w for w in words if w.lower() not in stop_words]
            if filtered_words:
                name = ' '.join(filtered_words)
                if len(name) >= 2:
                    return {'type': 'name', 'value': name}
    
    # Try to find capitalized words in original (proper nouns)
    capitalized = re.findall(r'\b([A-Z][a-z]+)\b', query_stripped)
    non_name_caps = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 
                     'Saturday', 'Sunday', 'Computer', 'Engineering', 'Science'}
    filtered_caps = [w for w in capitalized if w not in non_name_caps]
    if filtered_caps:
        return {'type': 'name', 'value': ' '.join(filtered_caps)}
    
    # Last resort: find any word that could be a name (after removing stop words)
    words = re.findall(r'\b([a-zA-Z]{2,})\b', query_lower)
    name_words = [w for w in words if w not in stop_words and len(w) >= 3]
    if name_words:
        return {'type': 'name', 'value': name_words[-1]}  # Take last meaningful word
    
    return {'type': None, 'value': None}


def extract_class_or_batch_name(query: str) -> Dict[str, Optional[str]]:
    """Extract class/batch name"""
    query_upper = query.upper()
    
    # Batch: 7CE-A-3
    batch_match = re.search(r'(\d+[A-Z]{2,3}-[A-Z]-\d+)', query_upper)
    if batch_match:
        return {'type': 'batch', 'name': batch_match.group(1)}
    
    # Class: 7CE-A
    class_match = re.search(r'(\d+[A-Z]{2,3}-[A-Z])\b', query_upper)
    if class_match:
        return {'type': 'class', 'name': class_match.group(1)}
    
    return {'type': None, 'name': None}


def extract_day_from_query(query: str) -> Optional[str]:
    """Extract day from query"""
    query_lower = query.lower()
    days_map = {
        'monday': 'MON', 'mon': 'MON',
        'tuesday': 'TUE', 'tue': 'TUE',
        'wednesday': 'WED', 'wed': 'WED',
        'thursday': 'THU', 'thu': 'THU',
        'friday': 'FRI', 'fri': 'FRI',
        'saturday': 'SAT', 'sat': 'SAT',
        'today': get_current_day(),
        'tomorrow': get_tomorrow_day(),
    }
    
    for day_name, day_code in days_map.items():
        if day_name in query_lower:
            return day_code
    return None


def get_current_day() -> str:
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    return days[datetime.now().weekday()]


def get_tomorrow_day() -> str:
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    return days[(datetime.now().weekday() + 1) % 7]


def parse_time_from_query(query: str) -> Optional[Dict]:
    """Extract time from query"""
    query_lower = query.lower()
    result = {'start_time': None, 'end_time': None, 'is_now': False}
    
    if re.search(r'(right now|currently|now|at present)', query_lower):
        result['is_now'] = True
        return result
    
    # Time patterns
    times = []
    for match in re.finditer(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', query_lower):
        time_str = match.group(0)
        normalized = normalize_time(time_str)
        if normalized:
            times.append(normalized)
    
    if len(times) >= 2:
        result['start_time'] = times[0]
        result['end_time'] = times[1]
    elif len(times) == 1:
        result['start_time'] = times[0]
        result['end_time'] = add_hours(times[0], 1)
    
    return result if result['start_time'] or result['is_now'] else None


def normalize_time(time_str: str) -> Optional[str]:
    time_str = time_str.strip().lower()
    
    match = re.match(r'(\d{1,2})\s*(am|pm)', time_str)
    if match:
        hour = int(match.group(1))
        period = match.group(2)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:00:00"
    
    match = re.match(r'(\d{1,2}):(\d{2})\s*(am|pm)?', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3)
        if period:
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
        return f"{hour:02d}:{minute:02d}:00"
    
    return None


def add_hours(time_str: str, hours: int) -> str:
    try:
        from datetime import datetime, timedelta
        t = datetime.strptime(time_str, "%H:%M:%S")
        return (t + timedelta(hours=hours)).strftime("%H:%M:%S")
    except:
        return time_str


def build_query_context(user_message: str, detected_type: str) -> Dict:
    """Build context for query"""
    context = {
        'query_type': detected_type,
        'user_message': user_message,
        'detected_at': datetime.now().isoformat(),
    }
    
    if detected_type == QueryType.PERSON_LOOKUP:
        context['person_identifier'] = extract_person_identifier(user_message)
    
    elif detected_type == QueryType.ROOM_AVAILABILITY:
        time_info = parse_time_from_query(user_message)
        context['time_info'] = time_info if time_info else {'is_now': True}
    
    elif detected_type in [QueryType.TIMETABLE_VIEW, QueryType.BATCH_TIMETABLE, QueryType.WHERE_IS_BATCH]:
        cb = extract_class_or_batch_name(user_message)
        context['class_batch_type'] = cb['type']
        context['class_batch_name'] = cb['name']
        context['day'] = extract_day_from_query(user_message)
        if not context['day'] and detected_type == QueryType.WHERE_IS_BATCH:
            context['day'] = get_current_day()
    
    return context