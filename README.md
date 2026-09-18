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

#### Text Format / 文本格式

One event = one block. **The first line is the title**; the lines below it are optional attributes. Blank lines separate events.
（一个事件 = 一个块。**第一行就是标题**，下面几行是可选属性。事件之间用空行分隔。）

```
October Goal Setting Conferences with Ms. Ogawa
Date: Oct 5, 2026
Time: 2:55pm - 3:15pm
Location: Montclaire Elementary School, Room 16
Notes: Bring the goal sheet
```

| Line / 行 | Labels / 标签 | Examples / 示例 |
| --- | --- | --- |
| Title / 标题 | none, or `Topic:` `Title:` `Subject:` `Event:` `主题:` `标题:` `事件:` | first line of the block / 块的第一行 |
| Date / 日期 | `Date:` `Dates:` `日期:` `📅` | `Oct 5, 2026` · `Nov. 21, 28; Dec. 5` · `2026年10月5日` · `10/5` |
| Time / 时间 | `Time:` `时间:` `🕥` | `2:55pm - 3:15pm` · `14:00-15:00` |
| Location / 地点 | `Location:` `地点:` `📍` | `Room 16` |
| Notes / 备注 | `Notes:` `备注:` `📝` | unlabelled extra lines land here too / 没有标签的多余行也会进备注 |

**Good to know / 小贴士:**
- No `Time:` line → an all-day event. / 没有时间行就是全天事件。
- One `Date:` line can create several events: `Date: Nov. 21, 28; Dec. 5` → 3 events. / 一行日期可以生成多个事件。
- The date may also sit on the `Time:` line: `Time: Monday Oct 5, 2026; 2:55pm - 3:15pm`. / 日期也可以直接写在时间行里。
- `–` and `—` work as well as `-`, so pasting straight from email or Google Calendar is fine. / 从邮件或 Google Calendar 直接粘贴的破折号也能识别。
- Times are floating local time. Timezone text like `(Pacific Time - Los Angeles)` is ignored, not converted. / 生成的是无时区的本地时间，`(Pacific Time)` 这类文字会被忽略，不做换算。
- A title containing 生日 / 纪念日 / birthday / anniversary repeats every year. / 标题含这些词会自动设为每年重复。
- Edited the text and re-running changes nothing in Calendar? It does now — each run bumps `SEQUENCE`, which is how a client is told "same event, newer version". Without it Calendar silently ignores a UID it already holds. / 改完文本重跑却没反应？现在每次生成都会递增 `SEQUENCE`，告诉日历“同一事件的新版本”；没有它时日历会直接忽略已存在的 UID。
- Apple Calendar geocodes the `Location:` text. If it matches a real place, it shows that place's own name and drops any extra words, so put a room or suite number in `Notes:` instead. / Apple Calendar 会对地点做地理编码，匹配到真实地点后会用官方名称替换原文，多余文字会被丢掉 —— 房间号请写在备注里。

#### Weekly Recurring Format / 周期性排课格式

If the text starts with `Period:`, each following line is a weekday rule repeated across the whole range. Note the comma between the time and the event name.
（如果文本以 `Period:` 开头，后面每行都是一条按周重复的规则，覆盖整个日期区间。注意时间和事件名之间要用逗号分隔。）

```
Period: Sep 1, 2026 to Dec 18, 2026
Monday 3pm-4pm, Event: Soccer
Wednesday 5-6pm, Chess Club
```

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
