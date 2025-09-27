import sys
import datetime
from pathlib import Path

# === File paths ===
USER_FILE      = Path('user.txt')
TASK_FILE      = Path('tasks.txt')
TASK_OVERVIEW  = Path('task_overview.txt')
USER_OVERVIEW  = Path('user_overview.txt')

# ==== Utility Functions ==== 

def ensure_file(path: Path):
    """
    Ensure that the given file exists; create an empty file if not.
    """
    if not path.exists():
        path.write_text('')


def parse_date(date_str: str) -> datetime.date:
    """
    Parse a date string in common formats into a date object.
    Raises ValueError if no format matches.
    """
    for fmt in ('%Y-%m-%d', '%d %b %Y', '%d %B %Y'):
        try:
            return datetime.datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{date_str}'")


def parse_task_line(line: str) -> dict:
    """
    Convert a CSV line from TASK_FILE into a task dictionary.
    Fields: username, title, description, assigned_date, due_date, complete
    """
    parts = [p.strip() for p in line.strip().split(',', 5)]
    if len(parts) != 6:
        raise ValueError(f"Malformed task line: {line!r}")
    username, title, desc, assigned_str, due_str, complete_str = parts
    return {
        'username': username.lower(),
        'title': title,
        'description': desc,
        'assigned': parse_date(assigned_str),
        'due': parse_date(due_str),
        'complete': complete_str.lower() == 'yes'
    }


def load_users() -> dict:
    """
    Read USER_FILE and return a dict mapping username -> password.
    Exits if file is missing.
    """
    ensure_file(USER_FILE)
    users = {}
    for line in USER_FILE.read_text().splitlines():
        if not line or ',' not in line:
            continue
        user, pwd = [x.strip() for x in line.split(',', 1)]
        users[user.lower()] = pwd
    return users


def save_user(username: str, password: str):
    """
    Append a new user record to USER_FILE.
    """
    with USER_FILE.open('a') as f:
        f.write(f"{username},{password}\n")


def load_tasks() -> list:
    """
    Read TASK_FILE, parse each line, and return a list of task dicts.
    """
    ensure_file(TASK_FILE)
    tasks = []
    for line in TASK_FILE.read_text().splitlines():
        if not line.strip():
            continue
        try:
            tasks.append(parse_task_line(line))
        except ValueError:
            continue
    return tasks


def save_tasks(tasks: list):
    """
    Overwrite TASK_FILE with the given list of task dicts.
    """
    lines = []
    for t in tasks:
        assigned = t['assigned'].isoformat()
        due      = t['due'].isoformat()
        complete = 'Yes' if t['complete'] else 'No'
        lines.append(f"{t['username']},{t['title']},{t['description']},{assigned},{due},{complete}")
    TASK_FILE.write_text("\n".join(lines) + ("\n" if lines else ""))

# ==== Authentication ==== 

def authenticate(users: dict) -> str:
    """
    Prompt for credentials until a valid (username,password) is entered.
    Returns the authenticated username.
    """
    print("Please log in to the Task Manager (admin/users).")
    while True:
        usr = input("Username: ").strip().lower()
        pwd = input("Password: ").strip()
        if users.get(usr) == pwd:
            print(f"\nWelcome, {usr}!\n")
            return usr
        else:
            print("Invalid credentials, please try again.\n")

# ==== Task Management Functions ==== 

def reg_user(users: dict, current_user: str):
    """
    Register a new user (admin only). Checks for duplicates and confirms password.
    """
    if current_user != 'admin':
        print("Permission denied: only 'admin' may register users.\n")
        return
    print("=== Register New User ===")
    while True:
        new_usr = input("New username: ").strip().lower()
        if not new_usr:
            print("Username cannot be empty.")
        elif new_usr in users:
            print(f"Username '{new_usr}' exists; choose another.")
        else:
            break
    while True:
        new_pwd = input("Password: ").strip()
        confirm = input("Confirm password: ").strip()
        if not new_pwd:
            print("Password cannot be empty.")
        elif new_pwd != confirm:
            print("Passwords do not match.")
        else:
            break
    users[new_usr] = new_pwd
    save_user(new_usr, new_pwd)
    print(f"User '{new_usr}' registered successfully.\n")


def add_task(users: dict):
    """
    Prompt for task details, validate assignee (warn if unknown), and append to TASK_FILE.
    """
    print("=== Add New Task ===")
    assignee = input("Assign to (username): ").strip().lower()
    if assignee and assignee not in users:
        print(f"Warning: '{assignee}' not recognized.")
        if input("Proceed anyway? (y/n): ").strip().lower() != 'y':
            print("Task cancelled.\n")
            return
    title = input("Title: ").strip()
    desc  = input("Description: ").strip()
    while True:
        due_str = input("Due date (YYYY-MM-DD): ").strip()
        try:
            due = parse_date(due_str)
            break
        except ValueError as e:
            print(e)
    task = {
        'username': assignee,
        'title': title,
        'description': desc,
        'assigned': datetime.date.today(),
        'due': due,
        'complete': False
    }
    tasks = load_tasks() + [task]
    save_tasks(tasks)
    print("Task added successfully.\n")


def view_all():
    """
    Display every task with full details.
    """
    print("=== All Tasks ===")
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.\n")
        return
    for i, t in enumerate(tasks, 1):
        print(f"\nTask {i}:")
        print(f"  User     : {t['username']}")
        print(f"  Title    : {t['title']}")
        print(f"  Desc     : {t['description']}")
        print(f"  Assigned : {t['assigned']}")
        print(f"  Due      : {t['due']}")
        print(f"  Complete : {'Yes' if t['complete'] else 'No'}")
    print()  # blank line


def get_valid_task_number(max_idx: int) -> int:
    """
    Recursively prompt for a valid task number between 1 and max_idx, or -1 to cancel.
    """
    resp = input(f"Enter task number (1-{max_idx}) or -1 to return: ").strip()
    if resp == '-1':
        return -1
    if not resp.isdigit() or not (1 <= int(resp) <= max_idx):
        print("Invalid selection.")
        return get_valid_task_number(max_idx)
    return int(resp)


def view_mine(current_user: str):
    """
    Show tasks for current_user; allow marking complete or editing (if incomplete).
    """
    print(f"=== Your Tasks ({current_user}) ===")
    tasks = [t for t in load_tasks() if t['username'] == current_user]
    if not tasks:
        print("No tasks assigned to you.\n")
        return
    for i, t in enumerate(tasks, 1):
        print(f"[{i}] {t['title']} (Due: {t['due']}) - Complete: {'Yes' if t['complete'] else 'No'}")
    choice = get_valid_task_number(len(tasks))
    if choice == -1:
        return
    # Map back to full task list
    full = load_tasks()
    # find the nth occurrence in full list
    count = 0
    for idx, t in enumerate(full):
        if t['username'] == current_user:
            count += 1
            if count == choice:
                task_idx = idx
                break
    task = full[task_idx]
    if task['complete']:
        print("Task already complete; cannot edit.\n")
        return
    action = input("Enter 'c' to mark complete or 'e' to edit: ").strip().lower()
    if action == 'c':
        full[task_idx]['complete'] = True
    elif action == 'e':
        if input("Change assignee? (y/n): ").strip().lower() == 'y':
            full[task_idx]['username'] = input("New assignee: ").strip().lower()
        if input("Change due date? (y/n): ").strip().lower() == 'y':
            while True:
                try:
                    full[task_idx]['due'] = parse_date(input("New due date: ").strip())
                    break
                except ValueError as e:
                    print(e)
    else:
        print("Unknown action.")
        return
    save_tasks(full)
    print("Task updated.\n")


def view_completed():
    """
    Display only tasks marked complete.
    """
    print("=== Completed Tasks ===")
    tasks = [t for t in load_tasks() if t['complete']]
    if not tasks:
        print("No completed tasks.\n")
        return
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t['title']} (User: {t['username']}, Due: {t['due']})")
    print()


def delete_task():
    """
    Allow admin to delete any task by its number.
    """
    print("=== Delete Task ===")
    tasks = load_tasks()
    if not tasks:
        print("No tasks to delete.\n")
        return
    for i, t in enumerate(tasks, 1):
        print(f"[{i}] {t['title']} (User: {t['username']})")
    choice = get_valid_task_number(len(tasks))
    if choice == -1:
        return
    del tasks[choice - 1]
    save_tasks(tasks)
    print("Task deleted.\n")


def generate_reports(users: dict):
    """
    Create task_overview.txt and user_overview.txt with summary statistics.
    """
    today = datetime.date.today()
    tasks = load_tasks()
    total     = len(tasks)
    completed = sum(t['complete'] for t in tasks)
    incomplete= total - completed
    overdue   = sum((not t['complete'] and t['due'] < today) for t in tasks)
    pct_incomp= (incomplete/total*100) if total else 0
    pct_over  = (overdue/total*100) if total else 0
    # Write task overview
    TASK_OVERVIEW.write_text("""
Total tasks         : {total}
Completed           : {completed}
Incomplete          : {incomplete}
Overdue             : {overdue}
% Incomplete        : {pct_incomp:.2f}
% Overdue           : {pct_over:.2f}
""".format(**locals()))
    # Write user overview
    lines = [f"Total users       : {len(users)}", f"Total tasks       : {total}"]
    for u in users:
        utasks = [t for t in tasks if t['username'] == u]
        utot   = len(utasks)
        upct   = (utot/total*100) if total else 0
        ucomp  = sum(t['complete'] for t in utasks)
        uin    = utot - ucomp
        uov    = sum((not t['complete'] and t['due'] < today) for t in utasks)
        lines.append(f"\nUser: {u}")
        lines.append(f"  Tasks assigned     : {utot}")
        lines.append(f"  % of all tasks     : {upct:.2f}")
        lines.append(f"  % complete         : {(ucomp/utot*100) if utot else 0:.2f}")
        lines.append(f"  % incomplete       : {(uin/utot*100)  if utot else 0:.2f}")
        lines.append(f"  % overdue          : {(uov/utot*100)  if utot else 0:.2f}")
    USER_OVERVIEW.write_text("\n".join(lines)+"\n")
    print("Reports generated.\n")


def display_stats(users: dict):
    """
    Print report files to screen, generating them if missing.
    """
    if not TASK_OVERVIEW.exists() or not USER_OVERVIEW.exists():
        generate_reports(users)
    print("=== Task Overview ===")
    print(TASK_OVERVIEW.read_text())
    print("=== User Overview ===")
    print(USER_OVERVIEW.read_text())

# ==== Main Loop ==== 

def main():
    users = load_users()
    current = authenticate(users)
    while True:
        # Build menu dynamically based on role
        if current == 'admin':
            options = ['r','a','va','vm','vc','del','gr','ds','e']
            prompt = ('''Select one of the following options: 
r - register 
a - add task 
va - view all 
vm - view mine 
vc - view done 
del - delete 
gr - reports 
ds - stats
e - exit
: ''')
        else:
            options = ['a','va','vm','e']
            prompt = ('''Select one of the following options: 
a - add 
va - view all 
vm - view mine 
e - exit
: ''')
        choice = input(prompt).strip().lower()
        if choice not in options:
            print("Invalid option.\n")
            continue
        if choice == 'r':  reg_user(users, current)
        if choice == 'a':  add_task(users)
        if choice == 'va': view_all()
        if choice == 'vm': view_mine(current)
        if choice == 'vc': view_completed()  if current=='admin' else print("No permission.\n")
        if choice == 'del': delete_task()     if current=='admin' else print("No permission.\n")
        if choice == 'gr': generate_reports(users) if current=='admin' else print("No permission.\n")
        if choice == 'ds': display_stats(users)   if current=='admin' else print("No permission.\n")
        if choice == 'e':
            print("Goodbye!")
            sys.exit(0)

if __name__ == '__main__':
    main()
