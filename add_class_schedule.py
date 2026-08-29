import re
import datetime
import sys
import subprocess
import hashlib
import os

def extract_dates(dates_str, current_year):
    dates = []
    
    month_groups = dates_str.split(';')
    parsed_any_old = False
    temp_dates = []
    for group in month_groups:
        group = group.strip()
        if not group: continue
        match = re.match(r'([A-Za-z.]+)\s*(.*)', group)
        if match:
            month_str, days_str = match.groups()
            month_str_clean = month_str.replace('.', '').strip()[:3]
            try:
                # If it contains a year, it's not the old format (e.g., Nov. 21, 28)
                if re.search(r'20\d{2}', days_str):
                    continue
                month_num = datetime.datetime.strptime(month_str_clean, "%b").month
                days = [int(re.sub(r'\D', '', d)) for d in days_str.split(',') if d.strip()]
                for day in days:
                    temp_dates.append(datetime.date(current_year, month_num, day))
                parsed_any_old = True
            except ValueError:
                pass
                
    if parsed_any_old:
        dates.extend(temp_dates)
        return dates
        
    en_matches = re.finditer(r'(?i)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(20\d{2}))?', dates_str)
    parsed_en = False
    for m in en_matches:
        try:
            month_str = m.group(1).title()
            month_num = datetime.datetime.strptime(month_str, "%b").month
            day = int(m.group(2))
            y = int(m.group(3)) if m.group(3) else current_year
            dates.append(datetime.date(y, month_num, day))
            parsed_en = True
        except ValueError:
            pass
            
    if parsed_en:
        return dates
        
    cn_matches = re.finditer(r'(?:(\d{4})年)?\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?', dates_str)
    for m in cn_matches:
        y = int(m.group(1)) if m.group(1) else current_year
        dates.append(datetime.date(y, int(m.group(2)), int(m.group(3))))
        
    if dates:
        return dates

    iso_matches = re.finditer(r'(?:(\d{4})[-/])?(\d{1,2})[-/](\d{1,2})', dates_str)
    for m in iso_matches:
        y = int(m.group(1)) if m.group(1) else current_year
        dates.append(datetime.date(y, int(m.group(2)), int(m.group(3))))
        
    return dates

def extract_times(time_str):
    time_str = time_str.upper().replace('.', '')
    m = re.search(r'(\d{1,2}:\d{2})\s*(AM|PM)?\s*[-~至]\s*(\d{1,2}:\d{2})\s*(AM|PM)?', time_str)
    if m:
        t1, p1, t2, p2 = m.groups()
        if not p1 and p2: p1 = p2
        if not p2 and p1: p2 = p1
        if not p1: p1 = 'AM'
        if not p2: p2 = 'AM'
        try:
            start = datetime.datetime.strptime(f"{t1} {p1}", "%I:%M %p").time()
            end = datetime.datetime.strptime(f"{t2} {p2}", "%I:%M %p").time()
            return start, end
        except:
            pass
            
    m2 = re.search(r'(\d{1,2}:\d{2})\s*[-~至]\s*(\d{1,2}:\d{2})', time_str)
    if m2:
        try:
            return datetime.datetime.strptime(m2.group(1), "%H:%M").time(), datetime.datetime.strptime(m2.group(2), "%H:%M").time()
        except:
            pass
    return None

def _create_events_list(title, location, time_str, dates_str, notes, current_year):
    parsed_dates = extract_dates(dates_str, current_year)
    if not parsed_dates:
        print(f"Skipping '{title}': Missing or unparsable dates.")
        return []
    
    times = extract_times(time_str) if time_str else None
    is_yearly = any(keyword in title.lower() for keyword in ["生日", "纪念日", "birthday", "anniversary"])
    
    created = []
    for d in parsed_dates:
        event = {
            'title': title,
            'location': location,
            'notes': notes,
            'is_all_day': times is None,
            'is_yearly': is_yearly
        }
        if times:
            event['start'] = datetime.datetime.combine(d, times[0])
            event['end'] = datetime.datetime.combine(d, times[1])
        else:
            event['start_date'] = d
            event['end_date'] = d + datetime.timedelta(days=1)
        created.append(event)
    return created

def parse_weekly_schedule(text):
    events = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    period_match = re.search(r'Period:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*to\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})', text)
    if not period_match:
        return events
        
    start_date_str = period_match.group(1)
    end_date_str = period_match.group(2)
    
    start_date = datetime.datetime.strptime(start_date_str, "%b %d, %Y").date()
    end_date = datetime.datetime.strptime(end_date_str, "%b %d, %Y").date()
    
    day_map = {
        'monday': 0, 'mondays': 0,
        'tuesday': 1, 'tuesdays': 1,
        'wednesday': 2, 'wednesdays': 2,
        'thursday': 3, 'thursdays': 3,
        'friday': 4, 'fridays': 4,
        'saturday': 5, 'saturdays': 5,
        'sunday': 6, 'sundays': 6
    }
    
    for line in lines:
        if line.startswith("Period:"): continue
        
        # fix common typos
        line = line.replace('69m', '6pm')
        
        parts = line.split(',', 1)
        if len(parts) < 2: continue
        
        time_part = parts[0].strip()
        event_part = parts[1].strip()
        
        if event_part.lower().startswith('event:'):
            event_title = event_part[6:].strip()
        else:
            event_title = event_part
            
        day_str = time_part.split(' ')[0].lower()
        if day_str not in day_map:
            continue
            
        target_weekday = day_map[day_str]
        
        time_match = re.search(r'(\d{1,2}(?::\d{2})?)\s*(am|pm)?\s*-\s*(\d{1,2}(?::\d{2})?)\s*(am|pm)?', time_part, re.IGNORECASE)
        start_time = None
        end_time = None
        if time_match:
            t1, p1, t2, p2 = time_match.groups()
            if not p1 and p2: p1 = p2
            if not p2 and p1: p2 = p1
            if not p1: p1 = 'am'
            if not p2: p2 = 'am'
            
            def to_time(t, p):
                if ':' not in t: t += ':00'
                if p.lower() == 'pm' and not t.startswith('12'):
                    h, m = t.split(':')
                    t = f"{int(h)+12}:{m}"
                elif p.lower() == 'am' and t.startswith('12'):
                    h, m = t.split(':')
                    t = f"00:{m}"
                return datetime.datetime.strptime(t, "%H:%M").time()
                
            try:
                start_time = to_time(t1, p1)
                end_time = to_time(t2, p2)
            except Exception as e:
                pass
                
        curr = start_date
        while curr.weekday() != target_weekday:
            curr += datetime.timedelta(days=1)
            
        while curr <= end_date:
            event = {
                'title': event_title,
                'location': '',
                'notes': '',
                'is_all_day': start_time is None,
                'is_yearly': False
            }
            if start_time:
                event['start'] = datetime.datetime.combine(curr, start_time)
                event['end'] = datetime.datetime.combine(curr, end_time)
            else:
                event['start_date'] = curr
                event['end_date'] = curr + datetime.timedelta(days=1)
                
            events.append(event)
            curr += datetime.timedelta(days=7)
            
    return events

def parse_schedule(text):
    if text.strip().startswith("Period:"):
        return parse_weekly_schedule(text)
        
    events = []
    blocks = re.split(r'\n\s*\n', text.strip())
    current_year = datetime.datetime.now().year
    
    for block in blocks:
        lines = [line for line in block.strip().split('\n') if line.strip()]
        if not lines: continue
        
        has_attrs = False
        if len(lines) > 1:
            for line in lines[1:]:
                if re.search(r'(?i)^(?:location|地点|📍|time|时间|🕥|dates?|日期|📅|notes?|备注|📝)[:：]', line.strip()):
                    has_attrs = True
                    break
        
        if not has_attrs and len(lines) > 1:
            all_independent = True
            for line in lines:
                if not extract_dates(line, current_year):
                    all_independent = False
                    break
            
            if all_independent:
                for line in lines:
                    if "：" in line or ":" in line:
                        parts = re.split(r'[:：]', line, maxsplit=1)
                        if extract_dates(parts[0], current_year):
                            events.extend(_create_events_list(parts[1].strip(), "", "", parts[0], "", current_year))
                        elif extract_dates(parts[1], current_year):
                            events.extend(_create_events_list(parts[0].strip(), "", "", parts[1], "", current_year))
                        else:
                            events.extend(_create_events_list(parts[0].strip(), "", "", line, "", current_year))
                    else:
                        events.extend(_create_events_list(line.strip(), "", "", line, "", current_year))
                continue
                
        # Normal block processing
        if len(lines) == 1:
            line = lines[0]
            if "：" in line or ":" in line:
                parts = re.split(r'[:：]', line, maxsplit=1)
                if extract_dates(parts[0], current_year):
                    events.extend(_create_events_list(parts[1].strip(), "", "", parts[0], "", current_year))
                elif extract_dates(parts[1], current_year):
                    events.extend(_create_events_list(parts[0].strip(), "", "", parts[1], "", current_year))
                else:
                    events.extend(_create_events_list(parts[0].strip(), "", "", line, "", current_year))
            else:
                events.extend(_create_events_list(line.strip(), "", "", line, "", current_year))
        else:
            title = lines[0].strip()
            location = ""
            time_str = ""
            dates_str = ""
            notes_str = ""
            
            for line in lines[1:]:
                if re.search(r'(?i)^(?:location|地点|📍)[:：]?\s*', line):
                    location = re.split(r'(?i)^(?:location|地点|📍)[:：]?\s*', line, maxsplit=1)[-1].strip()
                elif re.search(r'(?i)^(?:time|时间|🕥)[:：]?\s*', line):
                    time_str = re.split(r'(?i)^(?:time|时间|🕥)[:：]?\s*', line, maxsplit=1)[-1].strip()
                elif re.search(r'(?i)^(?:dates?|日期|📅)[:：]?\s*', line):
                    dates_str = re.split(r'(?i)^(?:dates?|日期|📅)[:：]?\s*', line, maxsplit=1)[-1].strip()
                elif re.search(r'(?i)^(?:notes?|备注|📝)[:：]?\s*', line):
                    notes_str += re.split(r'(?i)^(?:notes?|备注|📝)[:：]?\s*', line, maxsplit=1)[-1].strip() + "\n"
                else:
                    notes_str += line.strip() + "\n"
                    
            if not dates_str:
                if ":" in title or "：" in title:
                    parts = re.split(r'[:：]', title, maxsplit=1)
                    if extract_dates(parts[0], current_year):
                        dates_str = parts[0]
                        title = parts[1].strip()
                    elif extract_dates(parts[1], current_year):
                        dates_str = parts[1]
                        title = parts[0].strip()
                    else:
                        dates_str = title
                else:
                    dates_str = title
                    
            events.extend(_create_events_list(title, location, time_str, dates_str, notes_str, current_year))
                    
    return events

def generate_ics(events, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:-//Python Event Parser//EN\n")
        for e in events:
            f.write("BEGIN:VEVENT\n")
            if e['is_all_day']:
                uid_str = f"{e['title']}_{e['start_date'].isoformat()}"
                uid = hashlib.md5(uid_str.encode('utf-8')).hexdigest() + "@local.calendar"
                f.write(f"UID:{uid}\n")
                f.write(f"SUMMARY:{e['title']}\n")
                f.write(f"DTSTART;VALUE=DATE:{e['start_date'].strftime('%Y%m%d')}\n")
                f.write(f"DTEND;VALUE=DATE:{e['end_date'].strftime('%Y%m%d')}\n")
            else:
                uid_str = f"{e['title']}_{e['start'].isoformat()}"
                uid = hashlib.md5(uid_str.encode('utf-8')).hexdigest() + "@local.calendar"
                f.write(f"UID:{uid}\n")
                f.write(f"SUMMARY:{e['title']}\n")
                f.write(f"DTSTART:{e['start'].strftime('%Y%m%dT%H%M%S')}\n")
                f.write(f"DTEND:{e['end'].strftime('%Y%m%dT%H%M%S')}\n")
                
            if e.get('is_yearly'):
                f.write("RRULE:FREQ=YEARLY\n")
                
            if e.get('location'):
                f.write(f"LOCATION:{e['location']}\n")
                
            if e.get('notes'):
                encoded_notes = e['notes'].strip().replace('\n', '\\n')
                f.write(f"DESCRIPTION:{encoded_notes}\n")
                
            f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")

if __name__ == "__main__":
    import argparse
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_ics = os.path.join(script_dir, "schedule.ics")
    
    parser = argparse.ArgumentParser(description="Parse class schedule text and generate .ics file")
    parser.add_argument("input_file", help="Text file containing the schedule")
    parser.add_argument("--out", default=default_ics, help="Output .ics file name")
    
    args = parser.parse_args()
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading {args.input_file}: {e}")
        sys.exit(1)
        
    events = parse_schedule(text)
    if not events:
        print(f"No events parsed from {args.input_file}. Check format.")
        sys.exit(1)
        
    generate_ics(events, args.out)
    print(f"Generated {args.out} with {len(events)} events.")
    
    if sys.platform == 'darwin':
        subprocess.run(['open', args.out])
