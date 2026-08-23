tell application "Calendar"
	set deletedCount to 0
	set allCalendars to calendars
	repeat with aCalendar in allCalendars
		try
			set targetEvents to (every event of aCalendar whose summary is "Saturday Morning Clinic (14 Sessions)")
			repeat with anEvent in targetEvents
				delete anEvent
				set deletedCount to deletedCount + 1
			end repeat
		end try
	end repeat
	save
	return "Deleted " & deletedCount & " old events."
end tell
