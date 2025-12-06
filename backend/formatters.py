# formatters.py - CORRECTED response formatting

from typing import List, Dict, Any, Optional
from datetime import datetime

# ============================================================================
# BASE FORMATTER
# ============================================================================

class BaseFormatter:
    """Base class for response formatters"""
    
    def format(self, results: List[Dict[str, Any]], context: Dict) -> str:
        raise NotImplementedError("Subclasses must implement format()")


# ============================================================================
# TIMETABLE FORMATTER (CORRECTED with batch support)
# ============================================================================

class TimetableFormatter(BaseFormatter):
    """Format timetable results in structured table format"""
    
    def format(self, results: List[Dict[str, Any]], context: Dict) -> str:
        """Format timetable as structured table"""
        if not results:
            return self._format_no_results(context)
        
        # Extract context
        class_batch_name = context.get('class_batch_name', 'Unknown')
        day = context.get('day', 'Unknown Day')
        day_full = self._get_full_day_name(day)
        
        # Determine if class or batch
        is_batch = context.get('class_batch_type') == 'batch'
        
        # Build header
        emoji = "📚" if not is_batch else "🔬"
        header = f"{emoji} Timetable – {class_batch_name} ({day_full})\n"
        header += "─" * 75 + "\n\n"
        
        # Build table rows
        rows = []
        for idx, entry in enumerate(results, 1):
            time_slot = self._format_time_slot(
                entry.get('start_time'),
                entry.get('end_time')
            )
            
            subject = entry.get('subject_name', 'N/A')
            classroom = entry.get('classroom_name', 'N/A')
            teacher = entry.get('teacher_name', 'Not Assigned')
            lesson_type = entry.get('lesson_type', 'lecture')
            
            # Determine audience
            if entry.get('batch_name'):
                audience = f"Batch: {entry.get('batch_name')}"
            elif entry.get('group_name'):
                audience = f"Batch: {entry.get('group_name')}"
            elif entry.get('class_name'):
                audience = f"Class: {entry.get('class_name')}"
            else:
                audience = "Class Lecture"
            
            # Format type emoji
            type_emoji = "🔬" if lesson_type.lower() == 'lab' else "📖"
            type_text = "Lab" if lesson_type.lower() == 'lab' else "Lecture"
            
            # Build row with number prefix
            row = f"{idx}️⃣  {time_slot}\n"
            row += f"    📚 {subject}\n"
            row += f"    👨‍🏫 {teacher}\n"
            row += f"    🏫 {classroom}\n"
            row += f"    {type_emoji} {type_text} | {audience}\n"
            
            rows.append(row)
        
        if not rows:
            return self._format_no_results(context)
        
        return header + "\n".join(rows)
    
    def _format_time_slot(self, start_time, end_time) -> str:
        """Format time slot"""
        if not start_time or not end_time:
            return "N/A"
        
        if hasattr(start_time, 'strftime'):
            start_str = start_time.strftime('%H:%M')
        else:
            start_str = str(start_time)[:5]
        
        if hasattr(end_time, 'strftime'):
            end_str = end_time.strftime('%H:%M')
        else:
            end_str = str(end_time)[:5]
        
        return f"⏰ {start_str} – {end_str}"
    
    def _get_full_day_name(self, day_code: str) -> str:
        """Convert day code to full name"""
        day_map = {
            'MON': 'Monday',
            'TUE': 'Tuesday',
            'WED': 'Wednesday',
            'THU': 'Thursday',
            'FRI': 'Friday',
            'SAT': 'Saturday',
            'SUN': 'Sunday',
        }
        return day_map.get(day_code, day_code)
    
    def _format_no_results(self, context: Dict) -> str:
        """Format message when no results found"""
        name = context.get('class_batch_name', 'that class/batch')
        day = context.get('day', 'that day')
        day_full = self._get_full_day_name(day)
        
        return f"📅 No timetable entries found for {name} on {day_full}.\n\n" \
               f"Please check:\n" \
               f"• Class/batch name format (e.g., 7CE-A for class, 7CE-A-3 for batch)\n" \
               f"• Day is correct (Monday-Saturday)\n" \
               f"• There are scheduled classes on this day"


# ============================================================================
# WHERE IS BATCH FORMATTER (NEW)
# ============================================================================

class WhereIsBatchFormatter(BaseFormatter):
    """Format current location of batch"""
    
    def format(self, results: List[Dict[str, Any]], context: Dict) -> str:
        """Format current location"""
        if not results:
            batch_name = context.get('class_batch_name', 'this batch')
            return f"📍 {batch_name} is currently not in any scheduled class.\n\n" \
                   f"Possible reasons:\n" \
                   f"• Free period/break time\n" \
                   f"• No class scheduled right now\n" \
                   f"• Weekend/holiday"
        
        # Should only be one result for "right now"
        entry = results[0]
        
        batch_name = entry.get('batch_name', context.get('class_batch_name', 'Batch'))
        subject = entry.get('subject_name', 'N/A')
        classroom = entry.get('classroom_name', 'N/A')
        teacher = entry.get('teacher_name', 'Not specified')
        lesson_type = entry.get('lesson_type', 'lecture')
        start_time = entry.get('start_time')
        end_time = entry.get('end_time')
        
        # Format times
        if hasattr(start_time, 'strftime'):
            start_str = start_time.strftime('%H:%M')
        else:
            start_str = str(start_time)[:5] if start_time else 'N/A'
        
        if hasattr(end_time, 'strftime'):
            end_str = end_time.strftime('%H:%M')
        else:
            end_str = str(end_time)[:5] if end_time else 'N/A'
        
        type_emoji = "🔬" if lesson_type.lower() == 'lab' else "📖"
        type_text = "Lab Session" if lesson_type.lower() == 'lab' else "Lecture"
        
        response = f"📍 Current Location: {batch_name}\n"
        response += "─" * 50 + "\n\n"
        response += f"🏫 **Room:** {classroom}\n"
        response += f"{type_emoji} **Type:** {type_text}\n"
        response += f"📚 **Subject:** {subject}\n"
        response += f"👨‍🏫 **Teacher:** {teacher}\n"
        response += f"⏰ **Time:** {start_str} – {end_str}\n"
        
        return response


# ============================================================================
# ROOM AVAILABILITY FORMATTER (CORRECTED)
# ============================================================================

class RoomAvailabilityFormatter(BaseFormatter):
    """Format room availability results"""
    
    def format(self, all_rooms: List[Dict], occupied_rooms: List[str], context: Dict) -> str:
        """Format room availability"""
        time_info = context.get('time_info', {})
        start_time = time_info.get('start_time', 'N/A')
        end_time = time_info.get('end_time', 'N/A')
        day = time_info.get('day', 'Today')
        day_full = self._get_full_day_name(day)
        
        # Filter available rooms
        occupied_set = set(occupied_rooms)
        available_rooms = [
            room for room in all_rooms 
            if room.get('classroom_id') not in occupied_set
        ]
        
        # Build header
        time_range = self._format_time_range(start_time, end_time)
        header = f"🏫 Available Rooms – {day_full} {time_range}\n"
        header += "─" * 75 + "\n\n"
        
        # Classify rooms by type
        labs = [r for r in available_rooms if 'lab' in r.get('name', '').lower()]
        classrooms = [r for r in available_rooms if 'lab' not in r.get('name', '').lower()]
        
        # Build available list
        if available_rooms:
            if labs:
                header += "🔬 **LABS AVAILABLE:**\n"
                for room in labs:
                    room_name = room.get('name', room.get('short', 'Unknown'))
                    header += f"  ✅ {room_name}\n"
                header += "\n"
            
            if classrooms:
                header += "📚 **CLASSROOMS AVAILABLE:**\n"
                for room in classrooms:
                    room_name = room.get('name', room.get('short', 'Unknown'))
                    header += f"  ✅ {room_name}\n"
                header += "\n"
        else:
            header += "⚠️  No rooms available during this time slot.\n\n"
        
        # Build occupied list (first 5)
        if occupied_set:
            header += "❌ **OCCUPIED:**\n"
            for room_id in list(occupied_set)[:5]:
                room_info = next((r for r in all_rooms if r.get('classroom_id') == room_id), None)
                if room_info:
                    room_name = room_info.get('name', room_id)
                    header += f"  🚫 {room_name}\n"
            
            if len(occupied_set) > 5:
                header += f"  ... and {len(occupied_set) - 5} more\n"
            header += "\n"
        
        # Summary
        total_rooms = len(all_rooms)
        available_count = len(available_rooms)
        header += f"📊 **Summary:** {available_count} available out of {total_rooms} total rooms\n"
        
        return header
    
    def _format_time_range(self, start_time: str, end_time: str) -> str:
        """Format time range"""
        if start_time == 'N/A' or end_time == 'N/A':
            return ""
        
        start = start_time[:5] if len(start_time) >= 5 else start_time
        end = end_time[:5] if len(end_time) >= 5 else end_time
        
        return f"({start} – {end})"
    
    def _get_full_day_name(self, day_code: str) -> str:
        """Convert day code to full name"""
        day_map = {
            'MON': 'Monday',
            'TUE': 'Tuesday',
            'WED': 'Wednesday',
            'THU': 'Thursday',
            'FRI': 'Friday',
            'SAT': 'Saturday',
            'SUN': 'Sunday',
        }
        return day_map.get(day_code, day_code)


# ============================================================================
# NATURAL LANGUAGE FORMATTER (For Student Info)
# ============================================================================

class NaturalLanguageFormatter(BaseFormatter):
    """Format results in natural conversational language"""
    
    async def format(self, results: List[Dict[str, Any]], context: Dict, gemini_client) -> str:
        """Use Gemini to format results naturally"""
        import json
        from google.genai import types
        
        user_message = context.get('user_message', '')
        query_context = context.get('context', '')
        
        format_prompt = f"""Convert this database result into natural, conversational language.

User asked: "{user_message}"
Context: {query_context}

Database Results:
{json.dumps(results[:10], indent=2, default=str)}

FORMATTING RULES:
1. Start with a summary (e.g., "I found X matching Person(s):")
2. Present key information in natural sentences
3. For multiple results, use a concise list format
4. Highlight relevant details based on the user's query
5. Don't include null/empty fields
6. Don't mention technical column names
7. Keep it conversational and easy to read
8. Remove ** present before and after any details presenr in response(name, enrollment, phone mumber, email...),  so that response in end should be natural without **

Formatted Response:"""

        try:
            formatted_response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=format_prompt,
                config=types.GenerateContentConfig(temperature=0.5, max_output_tokens=1024)
            )
            return formatted_response.text.strip()
        except Exception as e:
            # Fallback to simple formatting
            print(f"Formatting error: {e}")
            return self._simple_format(results, user_message)
    
    def _simple_format(self, results: List[Dict], query: str) -> str:
        """Simple fallback formatting"""
        if not results:
            return "No results found."
        
        if len(results) == 1:
            result = results[0]
            response = "I found the following information:\n\n"
            for key, value in result.items():
                if value and key not in ['user_id', 'id', 'timetable_id']:
                    response += f"• {key.replace('_', ' ').title()}: {value}\n"
            return response
        else:
            return f"I found {len(results)} matching records. Please be more specific."


# ============================================================================
# FORMATTER FACTORY
# ============================================================================

def get_formatter(query_type: str) -> BaseFormatter:
    """Get appropriate formatter for query type"""
    from query_router import QueryType
    
    formatter_map = {
        QueryType.TIMETABLE_VIEW: TimetableFormatter(),
        QueryType.BATCH_TIMETABLE: TimetableFormatter(),
        QueryType.WHERE_IS_BATCH: WhereIsBatchFormatter(),
        QueryType.ROOM_AVAILABILITY: RoomAvailabilityFormatter(),
        QueryType.STUDENT_INFO: NaturalLanguageFormatter(),
        QueryType.TEACHER_INFO: NaturalLanguageFormatter(),
    }
    
    return formatter_map.get(query_type, NaturalLanguageFormatter())