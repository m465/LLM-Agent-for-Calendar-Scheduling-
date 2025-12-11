import json
import os
from datetime import datetime
from dateutil import parser

DB_FILE = "calendar.json"

CURRENT_TIME_REF = datetime.now()

# --- Database Helpers ---
def load_calendar():
    if not os.path.exists(DB_FILE):
        return {"events": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_calendar(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_conflict(start_dt, end_dt):
    data = load_calendar()
    for evt in data["events"]:
        evt_start = parser.parse(evt["start_time"])
        evt_end = parser.parse(evt["end_time"])
        # Overlap logic
        if start_dt < evt_end and end_dt > evt_start:
            return True, evt["title"]
    return False, None

# --- The Actual Tools ---

def check_schedule(date_str: str):
    """List events for a specific date."""
    try:
        target_date = parser.parse(date_str).date()
    except:
        return "Error: Invalid date format."

    data = load_calendar()
    events = []
    for evt in data["events"]:
        evt_start = parser.parse(evt["start_time"])
        if evt_start.date() == target_date:
            events.append(f"{evt['start_time']} - {evt['title']}")
    
    if not events:
        return f"No events found on {target_date}."
    return "\n".join(events)

def get_next_meeting_with(person: str):
    """Find the next meeting with a specific person."""
    data = load_calendar()
    # Sort by time
    sorted_events = sorted(data["events"], key=lambda x: x["start_time"])
    
    for evt in sorted_events:
        evt_start = parser.parse(evt["start_time"])
        if evt_start > CURRENT_TIME_REF:
            if any(person.lower() in p.lower() for p in evt["participants"]):
                return json.dumps(evt)
    return f"No upcoming meetings found with {person}."

def block_time_slot(title: str, start_time: str, end_time: str):
    """Block a time slot if no conflict exists."""
    try:
        s_dt = parser.parse(start_time)
        e_dt = parser.parse(end_time)
    except:
        return "Error: Invalid time format."

    conflict, conflict_title = check_conflict(s_dt, e_dt)
    if conflict:
        return f"Failed: Conflict with '{conflict_title}'."

    data = load_calendar()
    new_event = {
        "id": f"evt-{len(data['events']) + 1:03d}",
        "title": title,
        "participants": ["User"],
        "start_time": s_dt.isoformat(),
        "end_time": e_dt.isoformat(),
        "location": "TBD"
    }
    data["events"].append(new_event)
    save_calendar(data)
    return f"Success: Blocked '{title}' from {s_dt} to {e_dt}."

# --- OpenAI Tool Definitions ---
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_schedule",
            "description": "Get schedule for a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date (YYYY-MM-DD)"}
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_meeting_with",
            "description": "Find next meeting with a person.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person": {"type": "string", "description": "Name of person"}
                },
                "required": ["person"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "block_time_slot",
            "description": "Block a time slot on the calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO format start"},
                    "end_time": {"type": "string", "description": "ISO format end"}
                },
                "required": ["title", "start_time", "end_time"]
            }
        }
    }
]