import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from datetime import datetime
import zipfile
import json
import csv

SETTINGS_FILE = "organizer_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("language") == "en":
                data["language"] = "English"
            elif data.get("language") == "hi":
                data["language"] = "Hindi"
            elif data.get("language") == "te":
                data["language"] = "Telugu"
            return data

    return {"language": "English", "password": "1234", "size_limit": 100}

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

settings = load_settings()

file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz"]
}

translations = {
    "English": {
        "select_folder": "Select a folder to organize its files:",
        "organize": "Organize Files",
        "organize_date": "Organize by Date",
        "browse": "Browse",
        "preview": "Preview",
        "undo": "Undo",
        "add_category": "Add Category",
        "success": "Files organized successfully!",
        "undo_success": "Files restored to original location!",
        "undo_empty": "Nothing to undo!",
        "warning": "Please select a folder first!",
        "wrong_password": "Wrong password!",
        "enter_password": "Enter password:"
    },
    "Hindi": {
        "select_folder": "फ़ोल्डर चुनें:",
        "organize": "फ़ाइल व्यवस्थित करें",
        "organize_date": "तारीख अनुसार व्यवस्थित करें",
        "browse": "ब्राउज़",
        "preview": "पूर्वावलोकन",
        "undo": "पूर्ववत",
        "add_category": "श्रेणी जोड़ें",
        "success": "फ़ाइलें सफलतापूर्वक व्यवस्थित हुईं!",
        "undo_success": "फ़ाइलें मूल स्थान पर लौटा दी गईं!",
        "undo_empty": "पूर्ववत करने के लिए कुछ नहीं!",
        "warning": "कृपया पहले फ़ोल्डर चुनें!",
        "wrong_password": "गलत पासवर्ड!",
        "enter_password": "पासवर्ड दर्ज करें:"
    },
    "Telugu": {
        "select_folder": "ఫోల్డర్ ఎంచుకోండి:",
        "organize": "ఫైళ్ళను సజావుగా చేయండి",
        "organize_date": "తేదీ ప్రకారం సజావుగా చేయండి",
        "browse": "బ్రౌజ్",
        "preview": "ప్రివ్యూ",
        "undo": "అన్‌డూ",
        "add_category": "కొత్త వర్గం జోడించండి",
        "success": "ఫైళ్ళు విజయవంతంగా సజావుగా చేయబడ్డాయి!",
        "undo_success": "ఫైళ్ళు అసలు స్థానానికి పునరుద్ధరించబడ్డాయి!",
        "undo_empty": "అన్‌డూ చేయడానికి ఏమీ లేదు!",
        "warning": "దయచేసి ముందుగా ఫోల్డర్ ఎంచుకోండి!",
        "wrong_password": "తప్పు పాస్‌వర్డ్!",
        "enter_password": "పాస్‌వర్డ్ నమోదు చేయండి:"
    }
}

undo_history = {}

def organize_files(folder_path, sort_by_date=False):
    if not folder_path:
        messagebox.showwarning("Warning", translations[settings["language"]]["warning"])
        return

    pwd = simpledialog.askstring("Password", translations[settings["language"]]["enter_password"], show='*')
    if pwd != settings["password"]:
        messagebox.showerror("Error", translations[settings["language"]]["wrong_password"])
        return

    global undo_history
    undo_history = {}  

    files_moved = {}
    file_list = os.listdir(folder_path)
    total_files = len(file_list)
    progress["maximum"] = total_files

    for idx, file_name in enumerate(file_list, start=1):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isdir(file_path):
            continue

        ext = os.path.splitext(file_name)[1].lower()
        moved = False

        if os.path.getsize(file_path) > settings["size_limit"] * 1024 * 1024:
            zip_path = file_path + ".zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(file_path, arcname=file_name)
            os.remove(file_path)
            continue

        for folder, extensions in file_types.items():
            if ext in extensions:
                if sort_by_date:
                    date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    folder = os.path.join(folder, date.strftime("%Y-%m"))
                dest_folder = os.path.join(folder_path, folder)
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                base, extension = os.path.splitext(file_name)
                new_name = file_name
                counter = 1
                while os.path.exists(os.path.join(dest_folder, new_name)):
                    new_name = f"{base}_{counter}{extension}"
                    counter += 1

                new_path = os.path.join(dest_folder, new_name)
                shutil.move(file_path, new_path)
                undo_history[file_name] = file_path
                files_moved.setdefault(folder, 0)
                files_moved[folder] += 1
                moved = True
                break

        if not moved:
            others_folder = os.path.join(folder_path, "Others")
            if not os.path.exists(others_folder):
                os.makedirs(others_folder)
            new_path = os.path.join(others_folder, file_name)
            shutil.move(file_path, new_path)
            undo_history[file_name] = file_path
            files_moved.setdefault("Others", 0)
            files_moved["Others"] += 1

        progress["value"] = idx
        root.update_idletasks()

    for item in os.listdir(folder_path):
        sub_folder = os.path.join(folder_path, item)
        if os.path.isdir(sub_folder) and not os.listdir(sub_folder):
            os.rmdir(sub_folder)

    with open("organize_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Files"])
        for k, v in files_moved.items():
            writer.writerow([k, v])

    summary = "\n".join([f"{k}: {v} files" for k, v in files_moved.items()])
    messagebox.showinfo("Success", f"{translations[settings['language']]['success']}\n\n{summary}")

def undo_last_action():
    if not undo_history:
        messagebox.showinfo("Undo", translations[settings["language"]]["undo_empty"])
        return

    for file_name, original_path in undo_history.items():
        for root_dir, _, files in os.walk(folder_entry.get()):
            if file_name in files:
                current_path = os.path.join(root_dir, file_name)
                shutil.move(current_path, original_path)
                break

    messagebox.showinfo("Undo", translations[settings["language"]]["undo_success"])
    undo_history.clear()

def preview_files(folder_path):
    if not folder_path:
        messagebox.showwarning("Warning", translations[settings["language"]]["warning"])
        return

    counts = {folder: 0 for folder in file_types}
    counts["Others"] = 0

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isdir(file_path):
            continue
        ext = os.path.splitext(file_name)[1].lower()
        matched = False
        for folder, extensions in file_types.items():
            if ext in extensions:
                counts[folder] += 1
                matched = True
                break
        if not matched:
            counts["Others"] += 1

    summary = "\n".join([f"{k}: {v} files" for k, v in counts.items()])
    messagebox.showinfo("Preview", f"Files will be organized as:\n\n{summary}")

def add_category():
    new_window = tk.Toplevel(root)
    new_window.title(translations[settings["language"]]["add_category"])

    tk.Label(new_window, text="Category Name:").pack(pady=5)
    category_entry = tk.Entry(new_window)
    category_entry.pack(pady=5)

    tk.Label(new_window, text="Extensions (comma separated):").pack(pady=5)
    ext_entry = tk.Entry(new_window)
    ext_entry.pack(pady=5)

    def save_category():
        category = category_entry.get().strip()
        extensions = [e.strip().lower() for e in ext_entry.get().split(",")]
        if category and extensions:
            file_types[category] = extensions
            messagebox.showinfo("Success", f"Category '{category}' added!")
            new_window.destroy()

    tk.Button(new_window, text="Save", command=save_category).pack(pady=10)

def select_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)

def change_language(lang):
    settings["language"] = lang
    save_settings(settings)
    label.config(text=translations[lang]["select_folder"])
    organize_btn.config(text=translations[lang]["organize"])
    date_btn.config(text=translations[lang]["organize_date"])
    browse_btn.config(text=translations[lang]["browse"])
    preview_btn.config(text=translations[lang]["preview"])
    undo_btn.config(text=translations[lang]["undo"])
    category_btn.config(text=translations[lang]["add_category"])

root = tk.Tk()
root.title("File Organizer Pro")
root.geometry("650x400")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")

label = tk.Label(root, text=translations[settings["language"]]["select_folder"], font=("Arial", 12))
label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=5)

folder_entry = tk.Entry(frame, width=50)
folder_entry.pack(side=tk.LEFT, padx=5)

browse_btn = tk.Button(frame, text=translations[settings["language"]]["browse"], command=select_folder)
browse_btn.pack(side=tk.LEFT)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

preview_btn = tk.Button(btn_frame, text=translations[settings["language"]]["preview"], command=lambda: preview_files(folder_entry.get()))
preview_btn.grid(row=0, column=0, padx=10)

organize_btn = tk.Button(btn_frame, text=translations[settings["language"]]["organize"], font=("Arial", 12, "bold"), bg="green", fg="white", command=lambda: organize_files(folder_entry.get()))
organize_btn.grid(row=0, column=1, padx=10)

date_btn = tk.Button(btn_frame, text=translations[settings["language"]]["organize_date"], bg="blue", fg="white", command=lambda: organize_files(folder_entry.get(), sort_by_date=True))
date_btn.grid(row=0, column=2, padx=10)

undo_btn = tk.Button(btn_frame, text=translations[settings["language"]]["undo"], bg="orange", fg="black", command=undo_last_action)
undo_btn.grid(row=0, column=3, padx=10)

category_btn = tk.Button(root, text=translations[settings["language"]]["add_category"], command=add_category)
category_btn.pack(pady=5)

progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=10)

lang_menu = ttk.Combobox(root, values=list(translations.keys()))
lang_menu.set(settings["language"])
lang_menu.pack()
lang_menu.bind("<<ComboboxSelected>>", lambda e: change_language(lang_menu.get()))

root.mainloop()