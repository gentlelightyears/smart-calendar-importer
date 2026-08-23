# Smart Calendar Importer 智能日历助手

Welcome to the **Smart Calendar Importer**! This project provides tools to automatically parse your schedules (both plain text class schedules and complex Excel travel itineraries) and import them directly into your Apple Calendar.

欢迎来到 **智能日历助手**！本项目提供了一套完整的自动化工具，可以将你的纯文本排课表或复杂的 Excel 旅行计划表，一键导入到 Apple Calendar 中。

---

## 🚀 The Easiest Way: Use the Mac App / 最简单的方法：使用 Mac App

We highly recommend using the built-in macOS App for a seamless, click-and-go experience. No terminal required!

强烈建议你使用随附的 Mac 应用程序，无需敲打代码，只需双击鼠标即可完美导入！

**How to use / 使用步骤:**
1. Locate the **`Smart Calendar Importer.app`** in this folder. It has a beautiful AI-generated custom icon!
   (找到文件夹里带有精美专属图标的 `Smart Calendar Importer.app`。)
2. Double click the app. / 双击打开。
3. A dialog will prompt you to choose what you want to import: **Class Schedule (.txt)** or **Travel Plan (.xlsx)**.
   (应用会弹窗询问你要导入的内容：排课文本 或 旅行计划表格。)
4. Select your file, and wait a few seconds. Apple Calendar will automatically pop up with all your events prepared. Click "Add All" and make sure an iCloud calendar is selected!
   (选中你的文件，稍等几秒，Apple Calendar 就会自动弹出。在弹窗里选择你的 iCloud 日历并点击“添加全部”即可！)

> **Pro Tip / 小贴士:** You can drag the `Smart Calendar Importer.app` into your Mac's bottom Dock for quick access! / 你可以把这个 App 拖拽到 Mac 最下方的程序坞 (Dock) 里，以后想用点一下就搞定！

---

## 💻 Developer Guide: Using the CLI / 开发者指南：使用终端脚本

If you prefer using the command line, the raw Python scripts are completely at your disposal.
如果你喜欢使用 Terminal 终端，可以直接调用底层的 Python 脚本。

### 1. Add Class Schedule from Text / 从纯文本导入课程表
Used for adding simple lists of dates, times, and classes. (用于批量添加简单的日期、时间和课程列表文本。)

**Usage / 用法:**
1. Put your schedule text inside `schedule_input.txt` (recommend clearing old content first).
   (把排期文本粘贴到 `schedule_input.txt` 中。)
2. Run in Terminal / 在终端中运行:
   ```bash
   python3 ~/Projects/calendar_events/add_class_schedule.py ~/Projects/calendar_events/schedule_input.txt
   ```
*(Note: This script prevents duplicates! If run again on the same text, it updates existing events instead of creating copies. / 此脚本具备防重复功能！多次运行会自动更新而不会重复创建。)*

### 2. Add Travel Itinerary from Excel / 从 Excel 表格导入旅行计划
Parses multi-tab Google Spreadsheets (downloaded as `.xlsx`) and automatically bundles flight, lodging, and notes into the Calendar event's description field.
(解析多 Tab 的旅行表格，自动将航班、住宿和备注信息打包进日历的“备注”中。)

**Usage / 用法:**
1. Ensure your `.xlsx` file is saved in the folder (e.g., `Trip Plan.xlsx`).
2. This script uses a virtual environment for the Pandas library. Run it with:
   (此脚本依赖 Pandas 库，请使用专用的 venv 运行：)
   ```bash
   ~/Projects/calendar_events/venv/bin/python ~/Projects/calendar_events/add_travel_schedule.py "~/Projects/calendar_events/Trip Plan.xlsx"
   ```

### 3. Bulk Delete Calendar Events / 批量删除指定的日历事件
If you made a mistake or want to wipe out an entire class series by its name.
(如果你不小心加错，想一键删除某个名称的所有课程时使用。)

**Usage / 用法:**
1. Run the following command (replace `"Event Name"` with the exact title you want to delete):
   (运行以下命令，把最后引号里的名字换成你想删除的准确名称：)
   ```bash
   python3 ~/Projects/calendar_events/delete_calendar_events.py "Event Name"
   ```
2. If prompted, click "OK" to allow Terminal access to your Calendar. (如果系统请求访问日历权限，请允许)。

---
*Keep this document handy for future reference! / 你可以将此文档保存在这里，以便日后随时查阅。*
