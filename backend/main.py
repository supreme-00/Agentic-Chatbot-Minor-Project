# main.py - COMPLETE FIXED VERSION with hardcoded SQL for all queries

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from db import fetch_query_async, get_pool
import json
import re
import os
from typing import Dict, Optional
import asyncio

from schema_context import get_day_binary
from query_router import detect_query_type, QueryType, build_query_context

# Initialize Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyCpYyHLymA3er4k1l4A1OWXk2YLCl9S3Go"))

app = FastAPI(title="Ganpat University AI Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HARDCODED SQL BUILDERS
# ============================================================================

def build_person_lookup_sql(person_info: Dict) -> Optional[str]:
    """Build SQL for person lookup - CASE INSENSITIVE"""
    id_type = person_info.get('type')
    id_value = person_info.get('value')
    
    if not id_type or not id_value:
        return None
    
    # Clean the value
    id_value_clean = id_value.strip()
    
    if id_type == 'student_enrollment':
        return f"""
SELECT 
    'student' as person_type,
    enrollment_no,
    name_of_student as name,
    branch,
    semester,
    class,
    student_phone_no as phone,
    parents_phone_no as parent_phone,
    student_gnu_mail_id as email,
    gender,
    hosteller_commuters,
    batch
FROM student_enrollment_information
WHERE enrollment_no = '{id_value_clean}'
LIMIT 1;
"""
    
    elif id_type == 'teacher_id':
        return f"""
SELECT 
    'teacher' as person_type,
    user_id as employee_id,
    tt_display_full_name as name,
    email_id as email,
    short
FROM teacher_enrollment_info
WHERE user_id = '{id_value_clean}'
LIMIT 1;
"""
    
    elif id_type == 'phone':
        return f"""
SELECT 
    'student' as person_type,
    enrollment_no,
    name_of_student as name,
    branch,
    semester,
    class,
    student_phone_no as phone,
    parents_phone_no as parent_phone,
    student_gnu_mail_id as email
FROM student_enrollment_information
WHERE student_phone_no = '{id_value_clean}'
   OR parents_phone_no = '{id_value_clean}'
LIMIT 10;
"""
    
    elif id_type == 'email':
        return f"""
SELECT 
    'student' as person_type,
    enrollment_no,
    name_of_student as name,
    student_phone_no as phone,
    parents_phone_no as parent_phone,
    student_gnu_mail_id as email
FROM student_enrollment_information
WHERE LOWER(student_gnu_mail_id) LIKE LOWER('%{id_value_clean}%')
   OR LOWER(student_personal_mail_id) LIKE LOWER('%{id_value_clean}%')
LIMIT 10;
"""
    
    elif id_type == 'name':
        # CASE INSENSITIVE name search
        name_lower = id_value_clean.lower()
        name_parts = name_lower.split()
        
        if len(name_parts) == 1:
            # Single name - search anywhere in name
            return f"""
SELECT 
    'student' as person_type,
    enrollment_no,
    name_of_student as name,
    branch,
    semester,
    class,
    student_phone_no as phone,
    parents_phone_no as parent_phone,
    student_gnu_mail_id as email,
    gender
FROM student_enrollment_information
WHERE LOWER(name_of_student) LIKE LOWER('%{name_parts[0]}%')
ORDER BY name_of_student
LIMIT 10;
"""
        else:
            # Multiple words - try exact match first, then partial
            full_name = ' '.join(name_parts)
            first_name = name_parts[0]
            last_name = name_parts[-1]
            return f"""
SELECT 
    'student' as person_type,
    enrollment_no,
    name_of_student as name,
    branch,
    semester,
    class,
    student_phone_no as phone,
    parents_phone_no as parent_phone,
    student_gnu_mail_id as email,
    gender
FROM student_enrollment_information
WHERE LOWER(name_of_student) LIKE LOWER('%{full_name}%')
   OR (LOWER(name_of_student) LIKE LOWER('%{first_name}%') 
       AND LOWER(name_of_student) LIKE LOWER('%{last_name}%'))
ORDER BY 
    CASE WHEN LOWER(name_of_student) LIKE LOWER('%{full_name}%') THEN 0 ELSE 1 END,
    name_of_student
LIMIT 10;
"""
    
    return None


def build_teacher_search_sql(name: str) -> str:
    """Build SQL to search teachers"""
    name_lower = name.lower().strip()
    return f"""
SELECT 
    'teacher' as person_type,
    user_id as employee_id,
    tt_display_full_name as name,
    email_id as email,
    short
FROM teacher_enrollment_info
WHERE LOWER(tt_display_full_name) LIKE LOWER('%{name_lower}%')
ORDER BY tt_display_full_name
LIMIT 10;
"""


def build_batch_timetable_sql(batch_name: str, day_binary: str) -> str:
    """
    Build SQL for batch timetable - EXACT pattern from Query_explanation.txt
    """
    return f"""
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
WHERE b.name = '{batch_name}'
  AND c.days = '{day_binary}'
ORDER BY p.start_time;
"""


def build_where_is_batch_sql(batch_name: str) -> str:
    """
    Build SQL for "where is batch right now" - EXACT pattern from Query_explanation.txt
    """
    return f"""
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
    c.period,
    c.days AS day_binary,
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
WHERE b.name = '{batch_name}'
  AND CURRENT_TIME BETWEEN p.start_time AND p.end_time;
"""


def build_free_rooms_now_sql() -> str:
    """Build SQL for free rooms right now - EXACT pattern from Query_explanation.txt"""
    return """
SELECT 
    c.classroom_id,
    c.name AS classroom_name
FROM classroom c
WHERE c.classroom_id NOT IN (
    SELECT s.classroom_id
    FROM session s
    WHERE CURRENT_TIME BETWEEN s.start_time::time AND s.end_time::time
);
"""


def build_free_rooms_time_sql(start_time: str, end_time: str) -> str:
    """Build SQL for free rooms in time range - EXACT pattern from Query_explanation.txt"""
    return f"""
SELECT 
    c.classroom_id,
    c.name AS classroom_name
FROM classroom c
WHERE c.classroom_id NOT IN (
    SELECT s.classroom_id
    FROM session s
    WHERE s.start_time::time < '{end_time}'::time
      AND s.end_time::time > '{start_time}'::time
);
"""


# ============================================================================
# RESPONSE FORMATTERS (Natural Language)
# ============================================================================

def format_student_response(results: list) -> str:
    """Format student info in natural language"""
    if not results:
        return "No student found with that information."
    
    if len(results) == 1:
        s = results[0]
        name = s.get('name', 'Unknown')
        enrollment = s.get('enrollment_no', 'N/A')
        branch = s.get('branch', 'N/A')
        semester = s.get('semester', 'N/A')
        class_name = s.get('class', 'N/A')
        phone = s.get('phone')
        parent_phone = s.get('parent_phone')
        email = s.get('email', 'N/A')
        gender = s.get('gender', '')
        
        # Gender prefix
        prefix = "He" if gender and gender.lower() == 'm' else "She" if gender and gender.lower() == 'f' else "They"
        
        response = f"I found **{name}** (Enrollment: {enrollment}).\n\n"
        response += f"{prefix} is a student in **{branch}**, currently in **Semester {semester}**, Class **{class_name}**.\n\n"
        
        # Phone handling with parent fallback
        if phone and str(phone).strip():
            response += f"📱 Phone: {phone}\n"
        elif parent_phone and str(parent_phone).strip():
            response += f"📱 Phone: Student's number not listed, but parent's number is **{parent_phone}**\n"
        else:
            response += f"📱 Phone: Not available\n"
        
        response += f"📧 Email: {email}\n"
        
        return response
    
    else:
        response = f"I found **{len(results)} students** matching your query:\n\n"
        for i, s in enumerate(results[:5], 1):
            name = s.get('name', 'Unknown')
            enrollment = s.get('enrollment_no', 'N/A')
            class_name = s.get('class', 'N/A')
            response += f"{i}. **{name}** - {enrollment} ({class_name})\n"
        
        if len(results) > 5:
            response += f"\n...and {len(results) - 5} more. Please be more specific."
        
        return response


def format_teacher_response(results: list) -> str:
    """Format teacher info in natural language"""
    if not results:
        return "No teacher found with that information."
    
    if len(results) == 1:
        t = results[0]
        name = t.get('name', 'Unknown')
        emp_id = t.get('employee_id', 'N/A')
        email = t.get('email', 'N/A')
        
        response = f"I found **{name}** (Employee ID: {emp_id}).\n\n"
        response += f"📧 Email: {email}\n"
        
        return response
    
    else:
        response = f"I found **{len(results)} teachers** matching your query:\n\n"
        for i, t in enumerate(results[:5], 1):
            name = t.get('name', 'Unknown')
            emp_id = t.get('employee_id', 'N/A')
            response += f"{i}. **{name}** (ID: {emp_id})\n"
        
        return response


def format_timetable_response(results: list, context: Dict) -> str:
    """Format timetable in structured but readable format"""
    if not results:
        batch_name = context.get('class_batch_name', 'this batch')
        day = context.get('day', 'today')
        return f"📅 No classes scheduled for **{batch_name}** on **{day}**.\n\nPlease check the batch name format (e.g., 7CE-A-2) and day."
    
    batch_name = context.get('class_batch_name', results[0].get('batch_name', 'Unknown'))
    day = context.get('day', 'Today')
    
    # Day name mapping
    day_names = {'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 
                 'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'}
    day_full = day_names.get(day, day)
    
    response = f"📚 **Timetable for {batch_name}** ({day_full})\n"
    response += "━" * 40 + "\n\n"
    
    for i, entry in enumerate(results, 1):
        start = entry.get('start_time')
        end = entry.get('end_time')
        subject = entry.get('subject_name', 'N/A')
        classroom = entry.get('classroom_name', 'N/A')
        lesson_type = entry.get('lesson_type', 'lecture')
        
        # Format time
        if hasattr(start, 'strftime'):
            start_str = start.strftime('%H:%M')
        else:
            start_str = str(start)[:5] if start else 'N/A'
        
        if hasattr(end, 'strftime'):
            end_str = end.strftime('%H:%M')
        else:
            end_str = str(end)[:5] if end else 'N/A'
        
        type_emoji = "🔬" if 'lab' in str(lesson_type).lower() else "📖"
        type_text = "Lab" if 'lab' in str(lesson_type).lower() else "Lecture"
        
        response += f"**{i}. {start_str} - {end_str}**\n"
        response += f"   {type_emoji} {subject}\n"
        response += f"   🏫 {classroom} ({type_text})\n\n"
    
    return response


def format_where_is_batch_response(results: list, context: Dict) -> str:
    """Format current location of batch"""
    batch_name = context.get('class_batch_name', 'this batch')
    
    if not results:
        return f"📍 **{batch_name}** is not in any scheduled class right now.\n\n" \
               f"This could mean:\n" \
               f"• It's a free period or break\n" \
               f"• No class is scheduled at this time\n" \
               f"• It's outside college hours"
    
    entry = results[0]
    subject = entry.get('subject_name', 'N/A')
    classroom = entry.get('classroom_name', 'N/A')
    lesson_type = entry.get('lesson_type', 'lecture')
    start = entry.get('start_time')
    end = entry.get('end_time')
    
    if hasattr(start, 'strftime'):
        start_str = start.strftime('%H:%M')
    else:
        start_str = str(start)[:5] if start else 'N/A'
    
    if hasattr(end, 'strftime'):
        end_str = end.strftime('%H:%M')
    else:
        end_str = str(end)[:5] if end else 'N/A'
    
    type_text = "Lab" if 'lab' in str(lesson_type).lower() else "Lecture"
    type_emoji = "🔬" if 'lab' in str(lesson_type).lower() else "📖"
    
    response = f"📍 **{batch_name}** is currently in:\n\n"
    response += f"🏫 **Room:** {classroom}\n"
    response += f"{type_emoji} **Subject:** {subject}\n"
    response += f"📋 **Type:** {type_text}\n"
    response += f"⏰ **Time:** {start_str} - {end_str}\n"
    
    return response


def format_free_rooms_response(results: list) -> str:
    """Format free rooms list"""
    if not results:
        return "🏫 No rooms are available at this time. All rooms are currently occupied."
    
    # Separate labs and classrooms
    labs = [r for r in results if 'lab' in r.get('classroom_name', '').lower()]
    classrooms = [r for r in results if 'lab' not in r.get('classroom_name', '').lower()]
    
    response = f"🏫 **Available Rooms** ({len(results)} total)\n"
    response += "━" * 35 + "\n\n"
    
    if labs:
        response += "🔬 **Labs:**\n"
        for room in labs:
            response += f"   ✅ {room.get('classroom_name', 'Unknown')}\n"
        response += "\n"
    
    if classrooms:
        response += "📚 **Classrooms:**\n"
        for room in classrooms:
            response += f"   ✅ {room.get('classroom_name', 'Unknown')}\n"
    
    return response


# ============================================================================
# MAIN CHAT ENDPOINT
# ============================================================================

@app.post("/chat")
async def chat(request: Request):
    """Main chat endpoint with hardcoded SQL"""
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return {"reply": "Please send a message."}

        detected_type = detect_query_type(user_message)
        print(f"🔍 Detected: {detected_type}")

        context = build_query_context(user_message, detected_type)
        print(f"📋 Context: {context}")

        # === GREETING ===
        if detected_type == QueryType.GREETING:
            return {"reply": "Hello! 👋 I'm your Ganpat University assistant.\n\nI can help you with:\n• Student/Teacher information\n• Batch timetables\n• Room availability\n\nWhat would you like to know?"}

        # === GENERAL QUERY ===
        if detected_type == QueryType.GENERAL:
            try:
                prompt = f"""You are Ganpat University's assistant providing accurate information.

        FACTS ABOUT GANPAT UNIVERSITY (GUNI):

        BASIC INFORMATION:
        - Full Name: Ganpat University (GUNI)
        - Type: State Private University (not-for-profit, philanthropic)
        - Location: North Gujarat, India
        - Established: April 12, 2005 (through Gujarat State Legislature Act No. 19 of 2005)
        - Recognition: University Grants Commission (UGC) recognized
        - NAAC Grade: A Grade
        - Campus: Over 300 acres in Ganpat Vidyanagar (high-tech education campus)
        - Mission: "Social Upliftment through Education"

        ADDRESS:
        Ganpat University, Ganpat Vidyanagar, Mehsana-Gozaria Highway, North Gujarat, India, PIN - 384012

        LEADERSHIP & MANAGEMENT:
        - Patron-in-Chief & President: Padma Shri Dr. Ganpat Patel (Indian-American scientist, entrepreneur, philanthropist)
        - Founded by: Large number of industrialists, technocrats, and businessmen
        - Governed by: Board of Governors (as per university Act and rules/regulations)

        COLLEGES & INSTITUTES:
        - U. V. Patel College of Engineering (UVPCE)
        - Shree S. K. Patel College of Pharmaceutical Education and Research
        - V. M. Patel Institute of Management
        - Acharya Motibhai Patel Institute of Computer Studies
        - Faculties: Computer Technology, Management Studies & Research, Architecture, Nursing, Sciences, Social Science & Humanities, Maritime Studies, Agricultural Sciences, Polytechnic

        PROGRAMS OFFERED:
        Diploma, Undergraduate, Postgraduate, and Research programs across multiple disciplines

        INDUSTRY COLLABORATIONS & CENTRES OF EXCELLENCE:
        - Over 20 industry-supported Centres of Excellence
        - Japan-India Institute for Manufacturing (JIM) - collaboration with Maruti Suzuki & Government of Japan
        - Bosch-Rexroth for automation
        - IBM for emerging technologies
        - Recognized as Centre for Entrepreneurship Development (CED) nodal institute by Government of Gujarat
        - Supports "Start-up India" initiative

        FACILITIES & CAMPUS LIFE:
        - Modern hostel facilities
        - Sports tournaments and cultural programs
        - Hosts academic conferences and workshops
        - Vibrant student life with modern amenities

        RULES FOR ANSWERING:
        1. Answer directly in 1-5 sentences based on the question.
        2. Use ONLY the facts above when answering about Ganpat University.
        3. For non-university questions, give brief, helpful general answers.
        4. Do NOT greet unless the user greets first.
        5. Do NOT ask "How can I help?" or similar phrases.
        6. Do NOT mention you are an AI or assistant.
        7. Do NOT repeat the user's question.
        8. Provide ONLY the final answer - clear and concise.

        User's question: {user_message}

        Answer:"""
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,  # Very low for consistent factual answers
                        max_output_tokens=350,
                        top_p=0.9,
                        top_k=40
                    )
                )
                
                if response and hasattr(response, "text") and response.text:
                    reply = response.text.strip()
                    
                    # Clean up common AI phrases that might slip through
                    unwanted_phrases = [
                        "As an AI", "I'm an AI", "As a language model",
                        "I am an assistant", "As an assistant",
                        "According to the information provided",
                        "Based on the facts above"
                    ]
                    
                    for phrase in unwanted_phrases:
                        reply = reply.replace(phrase, "").strip()
                    
                    # Remove leading colons or dashes if present
                    reply = reply.lstrip(":- ").strip()
                    
                    if reply:
                        return {"reply": reply}
                
                return {"reply": "I'm not sure how to answer that. Could you rephrase your question?"}
                
            except Exception as e:
                print(f"Error in general query: {str(e)}")
                return {"reply": "Sorry, I encountered an error. Please try asking again."}
        # === PERSON LOOKUP ===
        if detected_type == QueryType.PERSON_LOOKUP:
            person_info = context.get('person_identifier', {})
            print(f"👤 Person info: {person_info}")
            
            sql = build_person_lookup_sql(person_info)
            if not sql:
                return {"reply": "Please provide a name, enrollment number, phone, or email to search."}
            
            print(f"📊 SQL: {sql[:100]}...")
            
            try:
                results = await fetch_query_async(sql)
                print(f"✅ Found {len(results)} results")
            except Exception as e:
                print(f"❌ DB Error: {e}")
                return {"reply": f"Database error: {e}"}
            
            # If no student found and searching by name, try teachers
            if not results and person_info.get('type') == 'name':
                print("🔄 Searching teachers...")
                teacher_sql = build_teacher_search_sql(person_info.get('value', ''))
                try:
                    results = await fetch_query_async(teacher_sql)
                    print(f"✅ Found {len(results)} teachers")
                    if results:
                        return {"reply": format_teacher_response(results), "result_count": len(results)}
                except Exception as e:
                    print(f"❌ Teacher search error: {e}")
            
            if not results:
                return {"reply": "No matching person found. Please check:\n• Name spelling (try full name)\n• Enrollment number (11 digits for students)\n• Try with different search terms"}
            
            # Format response based on type
            if results[0].get('person_type') == 'teacher':
                return {"reply": format_teacher_response(results), "result_count": len(results)}
            return {"reply": format_student_response(results), "result_count": len(results)}

        # === BATCH TIMETABLE ===
        if detected_type == QueryType.BATCH_TIMETABLE:
            batch_name = context.get('class_batch_name')
            day = context.get('day')
            
            if not batch_name:
                return {"reply": "Please specify a batch name (e.g., 7CE-A-2)."}
            
            if not day:
                return {"reply": f"Please specify a day for {batch_name}'s timetable (e.g., Monday, Tuesday)."}
            
            day_binary = get_day_binary(day)
            sql = build_batch_timetable_sql(batch_name, day_binary)
            
            print(f"📊 Timetable SQL for {batch_name} on {day}")
            
            try:
                results = await fetch_query_async(sql)
                print(f"✅ Found {len(results)} entries")
            except Exception as e:
                print(f"❌ DB Error: {e}")
                return {"reply": f"Database error: {e}"}
            
            return {"reply": format_timetable_response(results, context), "result_count": len(results)}

        # === WHERE IS BATCH ===
        if detected_type == QueryType.WHERE_IS_BATCH:
            batch_name = context.get('class_batch_name')
            
            if not batch_name:
                return {"reply": "Please specify a batch name (e.g., 7CE-A-2)."}
            
            sql = build_where_is_batch_sql(batch_name)
            
            print(f"📍 Where is {batch_name}")
            
            try:
                results = await fetch_query_async(sql)
                print(f"✅ Found {len(results)} entries")
            except Exception as e:
                print(f"❌ DB Error: {e}")
                return {"reply": f"Database error: {e}"}
            
            return {"reply": format_where_is_batch_response(results, context)}

        # === ROOM AVAILABILITY ===
        if detected_type == QueryType.ROOM_AVAILABILITY:
            time_info = context.get('time_info', {})
            
            if time_info.get('is_now', True):
                sql = build_free_rooms_now_sql()
            else:
                start = time_info.get('start_time', '00:00:00')
                end = time_info.get('end_time', '23:59:59')
                sql = build_free_rooms_time_sql(start, end)
            
            print(f"🏫 Room availability query")
            
            try:
                results = await fetch_query_async(sql)
                print(f"✅ Found {len(results)} free rooms")
            except Exception as e:
                print(f"❌ DB Error: {e}")
                return {"reply": f"Database error: {e}"}
            
            return {"reply": format_free_rooms_response(results), "result_count": len(results)}

        # === CLASS TIMETABLE (Fallback) ===
        if detected_type == QueryType.TIMETABLE_VIEW:
            return {"reply": "For timetables, please specify a batch like **7CE-A-2** with a day.\n\nExample: 'Timetable of 7CE-A-2 for Monday'"}

        return {"reply": "I couldn't understand your request. Try asking about:\n• Student/Teacher details\n• Batch timetables\n• Free classrooms"}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"reply": "Something went wrong. Please try again.", "error": str(e)}


@app.get("/")
async def root():
    return {"message": "Ganpat University Chatbot", "version": "4.0 - Complete Fix"}


@app.get("/health")
async def health_check():
    try:
        await fetch_query_async("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


@app.on_event("startup")
async def startup():
    await get_pool()
    print("✅ Server started - All queries hardcoded")


@app.on_event("shutdown")
async def shutdown():
    from db import close_pool
    await close_pool()