# Task Manager (CLI)

A simple command-line task manager with file-based login.  
Register users, add tasks, and view tasks — all from your terminal.

> ⚠️ **Note:** This project stores passwords in plain text for learning/demo purposes.  
> Do **not** use real credentials. See **Security & Data** for safer options.

---

## ✨ Features

- User login (reads `user.txt`)
- Register new users (`r`)
- Add tasks (`a`)
- View all tasks (`va`)
- View only your tasks (`vm`)
- Clean, dependency-free Python

---
## Technical Improvements
- Database integration
- Web interface
- API development
- Unit test coverage
- Configuration management
---
## 🚀 Quick Start

```bash
# 1) Clone and enter the project
git clone https://github.com/<your-username>/task-manager-demo.git
cd task-manager-demo

# 2) (Optional) Create a virtual env
# python -m venv .venv
# source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate      # Windows

# 3) Seed data (edit as you like)
echo "admin,admin123" > user.txt
# Optionally create an empty tasks file
type NUL > tasks.txt  # Windows
# touch tasks.txt     # macOS/Linux

# 4) Run
python task_manager.py
