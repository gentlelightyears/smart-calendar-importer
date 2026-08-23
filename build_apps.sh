#!/bin/bash
cd /Users/jingzhang/Projects/calendar_events

# 1. 编译导入旅行日历的 Mac App
cat << 'EOF' > travel_app.scpt
set excelFile to choose file with prompt "请选择你的旅行计划 Excel 文件 (.xlsx):"
set posixPath to POSIX path of excelFile

try
    do shell script "/Users/jingzhang/Projects/calendar_events/venv/bin/python /Users/jingzhang/Projects/calendar_events/add_travel_schedule.py " & quoted form of posixPath
    display dialog "处理完成！Apple Calendar 应该已经弹出并询问你是否添加。" buttons {"太棒了!"} default button 1 with title "成功" with icon note
on error errMsg
    display dialog "出现错误: " & errMsg buttons {"OK"} default button 1 with title "错误" with icon stop
end try
EOF

osacompile -o "导入旅行日历.app" travel_app.scpt
rm travel_app.scpt

# 2. 编译导入文本课程表的 Mac App
cat << 'EOF' > class_app.scpt
set textFile to choose file with prompt "请选择包含排课时间的文本文件 (.txt):"
set posixPath to POSIX path of textFile

try
    do shell script "python3 /Users/jingzhang/Projects/calendar_events/add_class_schedule.py " & quoted form of posixPath
    display dialog "处理完成！Apple Calendar 应该已经弹出并询问你是否添加。" buttons {"太棒了!"} default button 1 with title "成功" with icon note
on error errMsg
    display dialog "出现错误: " & errMsg buttons {"OK"} default button 1 with title "错误" with icon stop
end try
EOF

osacompile -o "导入文本课程.app" class_app.scpt
rm class_app.scpt
