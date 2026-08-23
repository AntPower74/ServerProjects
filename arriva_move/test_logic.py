import json
from datetime import datetime

with open('/root/orari-app/data.js', 'r') as f:
    js_content = f.read()
    json_str = js_content[js_content.find('['):js_content.rfind(']')+1]
    trips = json.loads(json_str)

def is_valid(trip, date_obj):
    month = date_obj.month
    day = date_obj.day
    day_of_week = (date_obj.weekday() + 1) % 7 # Python weekday: 0=Mon..6=Sun. We want 0=Sun.
    date_str = f"{day:02d}-{month:02d}"
    
    FESTIVITA = ["01-01", "06-01", "25-04", "01-05", "02-06", "15-08", "01-11", "08-12", "25-12", "26-12"]
    is_holiday = date_str in FESTIVITA or day_of_week == 0
    is_august_break = month == 8 and 3 <= day <= 23
    
    giorni = trip.get('_giorni', '')
    stagionalita = trip.get('_stagionalita', '')
    note = trip.get('_note', '')
    
    if 'A' in note and is_august_break: return False
    if 'J' in note and not is_august_break: return False
    if 'F' in note and date_str == '25-12': return True
    if '#' in note and date_str != '25-12': return False
    
    if stagionalita == 'FEST' and not is_holiday: return False
    if stagionalita == 'FER' and is_holiday: return False
    
    if giorni:
        if giorni == 'GG': return True
        if giorni == '12345' and (is_holiday or day_of_week == 6): return False
        if giorni == '123456' and is_holiday: return False
        if giorni == '6' and day_of_week != 6: return False
        if giorni == '78' and not is_holiday: return False
        
        week_str = '7' if day_of_week == 0 else str(day_of_week)
        if giorni.isdigit() and week_str not in giorni and not (is_holiday and '8' in giorni):
            return False
            
    return True

valid_today = [t for t in trips if is_valid(t, datetime(2026, 7, 19))]
print(f"Valid trips for July 19 (Sunday): {len(valid_today)}")

valid_monday = [t for t in trips if is_valid(t, datetime(2026, 7, 20))]
print(f"Valid trips for July 20 (Monday): {len(valid_monday)}")
