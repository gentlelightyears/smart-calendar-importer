#!/bin/bash
cd /Users/jingzhang/Projects/calendar_events

APP_NAME="Smart Calendar Importer.app"
PNG_PATH="/Users/jingzhang/.gemini/antigravity-ide/brain/88a1f723-9f2c-4160-a878-a8443b212fc5/calendar_icon_1787463568694.png"

# 1. Write the unified AppleScript
cat << 'EOF' > unified_app.scpt
set dialogResult to display dialog "Welcome to Smart Calendar Importer! / 欢迎使用！\n\nPlease choose the file type to import:\n请选择要导入的内容：" buttons {"Cancel (取消)", "Text (.txt)", "Excel (.xlsx)"} default button 3 with title "Smart Calendar Importer" with icon note

if button returned of dialogResult is "Excel (.xlsx)" then
    set excelFile to choose file with prompt "Please select your Travel Plan Excel file (.xlsx):\n请选择你的旅行计划表格:" of type {"org.openxmlformats.spreadsheetml.sheet", "xls", "xlsx"}
    set posixPath to POSIX path of excelFile
    try
        do shell script "/Users/jingzhang/Projects/calendar_events/venv/bin/python /Users/jingzhang/Projects/calendar_events/add_travel_schedule.py " & quoted form of posixPath
        display dialog "Success! Apple Calendar should have opened.\n处理完成！请在日历中确认添加。" buttons {"Awesome! (太棒了)"} default button 1 with title "Success (成功)" with icon note
    on error errMsg
        display dialog "Error / 出现错误: " & errMsg buttons {"OK"} default button 1 with title "Error (错误)" with icon stop
    end try
else if button returned of dialogResult is "Text (.txt)" then
    set textFile to choose file with prompt "Please select your Class Schedule text file (.txt):\n请选择包含排课时间的文本文件:" of type {"public.plain-text", "txt"}
    set posixPath to POSIX path of textFile
    try
        do shell script "python3 /Users/jingzhang/Projects/calendar_events/add_class_schedule.py " & quoted form of posixPath
        display dialog "Success! Apple Calendar should have opened.\n处理完成！请在日历中确认添加。" buttons {"Awesome! (太棒了)"} default button 1 with title "Success (成功)" with icon note
    on error errMsg
        display dialog "Error / 出现错误: " & errMsg buttons {"OK"} default button 1 with title "Error (错误)" with icon stop
    end try
end if
EOF

# 2. Compile to .app
osacompile -o "$APP_NAME" unified_app.scpt
rm unified_app.scpt

# 3. Process icon
mkdir MyIcon.iconset
sips -z 16 16     "$PNG_PATH" --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     "$PNG_PATH" --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     "$PNG_PATH" --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     "$PNG_PATH" --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   "$PNG_PATH" --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   "$PNG_PATH" --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   "$PNG_PATH" --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   "$PNG_PATH" --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   "$PNG_PATH" --out MyIcon.iconset/icon_512x512.png
sips -z 1024 1024 "$PNG_PATH" --out MyIcon.iconset/icon_512x512@2x.png

iconutil -c icns MyIcon.iconset
rm -rf MyIcon.iconset

# 4. Inject icon into .app bundle
cp MyIcon.icns "$APP_NAME/Contents/Resources/applet.icns"
rm MyIcon.icns

# 5. Force Finder to refresh the icon
touch "$APP_NAME"
touch "$APP_NAME/Contents/Resources/applet.icns"

# Clean up old apps
rm -rf "导入旅行日历.app"
rm -rf "导入文本课程.app"

echo "Unified App created successfully with custom icon!"
