# Task Manager (CLI)

A simple command-line task manager with file-based login.  
Register users, add tasks, and view tasks — all from your terminal.

> ⚠️ **Note:** Passwords are stored in plain text for learning/demo purposes.  
> Do **not** use real credentials. See **Security & Data** for safer options.

---

## 📦 Project Files

- `task_manager.py` — **v1 (basic)**: login, register, add task, view all, view mine.
- `task-manager - Practical task - Part 3.py` — **v2 (enhanced/admin)**: everything in v1 **plus**:
  - Auto-creates missing data files
  - Flexible date parsing (`YYYY-MM-DD`, `01 Jan 2025`, `01 January 2025`)
  - Admin-only: register users, view completed, delete, generate reports, display stats
  - Edit/mark complete flow for “my tasks”
  - Writes `task_overview.txt` and `user_overview.txt`

Data files:
- `user.txt` (credentials as `username,password`)
- `tasks.txt` (tasks as `assignee, title, description, assigned_date, due_date, complete`)
- Generated (v2): `task_overview.txt`, `user_overview.txt`

---

## ✨ Features

- User login (reads `user.txt`)
- Register users (`r`)
- Add tasks (`a`)
- View all tasks (`va`)
- View only your tasks (`vm`)
- **v2 admin**: `vc` (view done), `del` (delete), `gr` (generate reports), `ds` (display stats)
- Clean, dependency-free Python (standard library only)

---

## 🚀 Quick Start

```bash
# 1) Clone and enter the project
git clone https://github.com/<your-username>/task-manager-demo.git
cd task-manager-demo

# 2) (Optional) Create a virtual env
# python -m venv .venv
# .venv\Scripts\activate      # Windows
# source .venv/bin/activate   # macOS/Linux

# 3) Seed data (edit as you like)
echo admin,admin123> user.txt
type NUL > tasks.txt  # Windows
# touch tasks.txt     # macOS/Linux

# 4a) Run v1 (basic)
python task_manager.py

# 4b) Run v2 (enhanced/admin)
python "task-manager - Practical task - Part 3.py"

