import sys
import subprocess

if len(sys.argv) < 2:
    print("❌ 错误: 请提供要删除的日历事件的标题。")
    print('用法示例: python3 ~/delete_calendar_events.py "你的事件标题"')
    sys.exit(1)

title = sys.argv[1]
print(f"⏳ 正在搜索并删除所有标题为 '{title}' 的日历事件...")

applescript = f'''
tell application "Calendar"
    set deletedCount to 0
    set allCalendars to calendars
    repeat with aCalendar in allCalendars
        try
            set targetEvents to (every event of aCalendar whose summary is "{title}")
            repeat with anEvent in targetEvents
                delete anEvent
                set deletedCount to deletedCount + 1
            end repeat
        end try
    end repeat
    save
    return "✅ 成功删除了 " & deletedCount & " 个事件。"
end tell
'''

result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
print(result.stdout.strip())
