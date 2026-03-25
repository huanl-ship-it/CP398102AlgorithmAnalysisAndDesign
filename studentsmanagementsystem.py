import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from pathlib import Path


# ---------- 数据文件路径（关键修改） ----------
def get_data_file():
    """获取数据文件路径（用户目录，避免exe只读问题）"""
    home = Path.home()
    app_dir = home / "StudentManager"
    app_dir.mkdir(exist_ok=True)
    return app_dir / "students.json"


DATA_FILE = get_data_file()
FILE_NAME = str(DATA_FILE)


# ---------- Windows 单实例 ----------
if os.name == "nt":
    import tempfile
    import msvcrt

    lockfile_path = Path(tempfile.gettempdir()) / "student_manager.lock"
    try:
        lockfile = open(str(lockfile_path), "w")
        msvcrt.locking(lockfile.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        messagebox.showerror("Error", "程序已在运行，不能重复启动。")
        sys.exit(0)


# ---------- 数据处理 ----------
def load_data():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


students = load_data()


# ---------- 功能 ----------
def clear_inputs():
    entry_name.delete(0, tk.END)
    entry_lastname.delete(0, tk.END)
    entry_birthplace.delete(0, tk.END)
    gender_var.set("Female")
    entry_phone.delete(0, tk.END)
    entry_emergency.delete(0, tk.END)
    entry_emergency_phone.delete(0, tk.END)


def get_input():
    return {
        "name": entry_name.get(),
        "lastname": entry_lastname.get(),
        "birthplace": entry_birthplace.get(),
        "gender": gender_var.get(),
        "phone": entry_phone.get(),
        "emergency_contact": entry_emergency.get(),
        "emergency_phone": entry_emergency_phone.get()
    }


def add_student():
    student = get_input()
    if not student["name"].strip() or not student["lastname"].strip():
        messagebox.showerror("Error", "Name and Lastname are required!")
        return
    students.append(student)
    save_data(students)
    messagebox.showinfo("Success", "Student added!")
    clear_inputs()


def update_student():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter the name to update!")
        return
    for s in students:
        if s["name"] == name:
            s.update(get_input())
            save_data(students)
            messagebox.showinfo("Success", "Updated!")
            clear_inputs()
            return
    messagebox.showerror("Error", "Not found!")


def delete_student():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Name is required!")
        return

    global students
    original_count = len(students)
    students = [s for s in students if s["name"] != name]

    if len(students) < original_count:
        save_data(students)
        messagebox.showinfo("Success", "Deleted!")
    else:
        messagebox.showerror("Error", "Not found!")


def search_student():
    name_query = entry_name.get().strip().lower()
    lastname_query = entry_lastname.get().strip().lower()

    headers = ["Name", "Lastname", "Birthplace", "Gender", "Phone", "Emergency Contact", "Emergency Phone"]
    rows = []

    for s in students:
        if name_query and name_query not in s["name"].lower():
            continue
        if lastname_query and lastname_query not in s["lastname"].lower():
            continue

        rows.append((
            s.get("name", ""),
            s.get("lastname", ""),
            s.get("birthplace", ""),
            s.get("gender", ""),
            s.get("phone", ""),
            s.get("emergency_contact", ""),
            s.get("emergency_phone", "")
        ))

    if not rows:
        result = "No result"
    else:
        widths = [max(len(str(row[i])) for row in rows + [tuple(headers)]) for i in range(len(headers))]
        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+\n"

        result = sep
        result += "| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |\n"
        result += sep

        for row in rows:
            result += "| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |\n"
        result += sep

    text_output.config(state='normal')
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state='disabled')


# ---------- GUI ----------
root = tk.Tk()
root.title("Student Manager")
root.geometry("820x720")
root.resizable(True, True)

# Grid weight for responsive layout
root.grid_columnconfigure(0, weight=0, minsize=160)
root.grid_columnconfigure(1, weight=1)
for r in range(0, 11):
    root.grid_rowconfigure(r, weight=0)
root.grid_rowconfigure(10, weight=1)

labels = ["Name", "Lastname", "Birthplace", "Gender", "Phone", "Emergency Contact", "Emergency Phone"]

entries = []
gender_var = tk.StringVar(value="Female")

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, padx=5, pady=3, sticky="w")

    if label == "Gender":
        tk.OptionMenu(root, gender_var, "Female", "Male", "Other").grid(row=i, column=1, sticky="ew")
    else:
        entry = tk.Entry(root)
        entry.grid(row=i, column=1, sticky="ew")
        entries.append(entry)

(entry_name, entry_lastname, entry_birthplace,
 entry_phone, entry_emergency, entry_emergency_phone) = entries


# 按钮
tk.Button(root, text="Add", command=add_student, bg="#6a9fff").grid(row=7, column=0, sticky="ew")
tk.Button(root, text="Update", command=update_student, bg="#59c4a1").grid(row=7, column=1, sticky="ew")
tk.Button(root, text="Delete", command=delete_student, bg="#f56d6d").grid(row=8, column=0, sticky="ew")
tk.Button(root, text="Search", command=search_student, bg="#8f9bff").grid(row=8, column=1, sticky="ew")
tk.Button(root, text="Clear", command=clear_inputs, bg="#aaaaaa").grid(row=9, column=0, sticky="ew")
tk.Button(root, text="Exit", command=root.destroy, bg="#2f2f2f").grid(row=9, column=1, sticky="ew")


# 输出框
text_output = tk.Text(root)
text_output.grid(row=10, column=0, columnspan=2, sticky="nsew")
text_output.config(state='disabled')


root.mainloop()