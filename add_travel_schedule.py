import pandas as pd
import datetime
import hashlib
import sys
import subprocess
import os

def clean_value(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def process_excel(file_path):
    xls = pd.ExcelFile(file_path)
    events = []
    
    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            continue
            
        for index, row in df.iterrows():
            date_val = None
            
            # Find the date column (could be 'Date' or 'Unnamed: 0')
            for col in df.columns:
                val = row[col]
                if isinstance(val, pd.Timestamp):
                    date_val = val.to_pydatetime()
                    break
                    
            if not date_val:
                continue
                
            title = f"Trip: {sheet_name}"
            location = ""
            notes_lines = []
            
            time_val = None
            
            # Extract details
            for col in df.columns:
                val = row[col]
                if pd.isna(val) or isinstance(val, pd.Timestamp):
                    continue
                
                col_name = str(col).strip().lower()
                
                if col_name == 'time' and isinstance(val, datetime.time):
                    time_val = val
                elif 'lodging' in col_name and not location:
                    location = str(val).strip()
                    
                # Add everything to notes except the date
                if not col_name.startswith('unnamed'):
                    notes_lines.append(f"{str(col).strip()}: {str(val).strip()}")
                else:
                    notes_lines.append(str(val).strip())
                    
            description = "\\n".join(notes_lines).replace("\n", "\\n").replace("\r", "")
            location_escaped = location.replace("\n", " ").replace("\r", "")
            
            # Construct event dictionary
            event = {
                'title': title,
                'location': location_escaped,
                'description': description,
                'date': date_val,
                'time': time_val
            }
            events.append(event)
            
    return events

def generate_ics(events, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:-//Python Travel Parser//EN\n")
        
        for e in events:
            f.write("BEGIN:VEVENT\n")
            
            # Generate UID
            dt_str = e['date'].strftime("%Y%m%d")
            uid = hashlib.md5(f"{e['title']}_{dt_str}".encode('utf-8')).hexdigest() + "@local.travel"
            f.write(f"UID:{uid}\n")
            
            f.write(f"SUMMARY:{e['title']}\n")
            if e['location']:
                f.write(f"LOCATION:{e['location']}\n")
            if e['description']:
                f.write(f"DESCRIPTION:{e['description']}\n")
                
            if e['time']:
                # Specific time event
                start_dt = datetime.datetime.combine(e['date'].date(), e['time'])
                # Assuming events are roughly 1 hour long if no end time is specified
                end_dt = start_dt + datetime.timedelta(hours=1)
                
                start_str = start_dt.strftime("%Y%m%dT%H%M%S")
                end_str = end_dt.strftime("%Y%m%dT%H%M%S")
                
                f.write(f"DTSTART:{start_str}\n")
                f.write(f"DTEND:{end_str}\n")
            else:
                # All-day event
                start_str = e['date'].strftime("%Y%m%d")
                end_dt = e['date'] + datetime.timedelta(days=1)
                end_str = end_dt.strftime("%Y%m%d")
                
                f.write(f"DTSTART;VALUE=DATE:{start_str}\n")
                f.write(f"DTEND;VALUE=DATE:{end_str}\n")
                
            f.write("END:VEVENT\n")
            
        f.write("END:VCALENDAR\n")

if __name__ == "__main__":
    import argparse
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_ics = os.path.join(script_dir, "travel_schedule.ics")
    
    parser = argparse.ArgumentParser(description="Parse travel schedule Excel and generate .ics file")
    parser.add_argument("input_file", help="Excel file containing the travel schedule")
    parser.add_argument("--out", default=default_ics, help="Output .ics file name")
    args = parser.parse_args()
    
    events = process_excel(args.input_file)
    if not events:
        print("No valid events found in spreadsheet.")
        sys.exit(1)
        
    generate_ics(events, args.out)
    print(f"Generated {args.out} with {len(events)} travel events.")
    
    if sys.platform == 'darwin':
        print("Opening in Calendar...")
        subprocess.run(['open', args.out])
