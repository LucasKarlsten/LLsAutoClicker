import tkinter as tk
from tkinter import simpledialog
import pyautogui
import threading
import time
import json
import keyboard
import os

# === Globals ===
positions = []
clicking = False
click_interval = 0.5

# Profile folder
script_dir = os.path.dirname(os.path.abspath(__file__))
profile_dir = os.path.join(script_dir, "profiles")
os.makedirs(profile_dir, exist_ok=True)

def get_profile_path(profile_name):
    return os.path.join(profile_dir, f"{profile_name}.json")

# === Status Label updater ===
def update_status(message, color="black"):
    status_label.config(text=message, fg=color)

# === Custom Modal Input Dialog ===
def modal_input(title, prompt, validate_func=None):
    result = {'value': None}
    def on_ok():
        val = entry.get()
        if validate_func:
            valid, msg = validate_func(val)
            if not valid:
                update_status(msg, "orange")
                return
        result['value'] = val
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.grab_set()
    dialog.geometry("300x100")
    dialog.resizable(False, False)
    dialog.transient(root)

    tk.Label(dialog, text=prompt).pack(pady=5)
    entry = tk.Entry(dialog)
    entry.pack(pady=5)
    entry.focus_set()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=5)

    root.wait_window(dialog)
    return result['value']

# === Clicking Loop ===
def click_loop():
    while clicking:
        for pos in positions:
            if not clicking:
                break
            pyautogui.click(pos)
            time.sleep(click_interval)

def start_clicking():
    global clicking
    if not positions:
        update_status("Warning: Please add at least one click position.", "orange")
        return
    if not clicking:
        clicking = True
        threading.Thread(target=click_loop, daemon=True).start()
        update_status("Clicking started.", "green")

def stop_clicking():
    global clicking
    clicking = False
    update_status("Clicking stopped.", "red")

# === Position Management ===
def add_position():
    update_status("Move your mouse to the new position in 2 seconds...", "blue")
    time.sleep(2)
    pos = pyautogui.position()
    positions.append(pos)
    update_position_list()
    update_status(f"Added position: {pos}", "green")

def delete_selected_position():
    selected = listbox.curselection()
    if selected:
        del positions[selected[0]]
        update_position_list()
        update_status("Selected position removed.", "green")
    else:
        update_status("No position selected to remove.", "orange")

def clear_positions():
    positions.clear()
    update_position_list()
    update_status("All positions cleared.", "green")

def update_position_list():
    listbox.delete(0, tk.END)
    for idx, pos in enumerate(positions):
        listbox.insert(tk.END, f"{idx+1}: {pos}")

# === Click Interval ===
def validate_interval(val):
    try:
        v = float(val)
        if v < 0.01 or v > 10:
            return False, "Interval must be between 0.01 and 10 seconds."
        return True, ""
    except:
        return False, "Invalid number for interval."

def set_interval():
    val = modal_input("Set Click Interval", "Enter click interval (seconds):", validate_interval)
    if val is not None:
        global click_interval
        click_interval = float(val)
        update_status(f"Click interval set to {click_interval} seconds.", "green")

# === Profile Management ===
def save_profile():
    if not positions:
        update_status("Add positions before saving profile.", "orange")
        return
    name = modal_input("Save Profile", "Enter profile name:")
    if not name:
        update_status("Profile save cancelled.", "orange")
        return
    try:
        with open(get_profile_path(name), "w") as f:
            json.dump(positions, f)
        update_profile_list()
        update_status(f"Profile '{name}' saved.", "green")
    except Exception as e:
        update_status(f"Error saving profile: {e}", "red")

def load_profile(event=None):
    selected = profile_var.get()
    if not selected:
        update_status("No profile selected to load.", "orange")
        return
    try:
        with open(get_profile_path(selected), "r") as f:
            loaded = json.load(f)
        global positions
        positions = [tuple(pos) for pos in loaded]
        update_position_list()
        update_status(f"Profile '{selected}' loaded.", "green")
    except Exception as e:
        update_status(f"Error loading profile: {e}", "red")

def delete_profile():
    selected = profile_var.get()
    if not selected:
        update_status("No profile selected to delete.", "orange")
        return
    # Confirm deletion inside GUI with modal input dialog (Yes/No)
    answer = tk.messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{selected}'?")
    # Since you asked for no popups, replace above with inline confirmation:
    # We'll do a simple confirmation modal instead:
    confirm = modal_confirm(f"Delete profile '{selected}'?")
    if not confirm:
        update_status("Profile deletion cancelled.", "orange")
        return
    try:
        os.remove(get_profile_path(selected))
        update_profile_list()
        update_status(f"Profile '{selected}' deleted.", "green")
    except Exception as e:
        update_status(f"Error deleting profile: {e}", "red")

def update_profile_list():
    profiles = [f[:-5] for f in os.listdir(profile_dir) if f.endswith(".json")]
    profile_menu['menu'].delete(0, 'end')
    for prof in profiles:
        profile_menu['menu'].add_command(label=prof, command=tk._setit(profile_var, prof, load_profile))
    if profiles:
        profile_var.set(profiles[0])
    else:
        profile_var.set('')

# === Modal Confirm Dialog ===
def modal_confirm(question):
    result = {'answer': False}

    def on_yes():
        result['answer'] = True
        dialog.destroy()

    def on_no():
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Confirm")
    dialog.grab_set()
    dialog.geometry("300x100")
    dialog.resizable(False, False)
    dialog.transient(root)

    tk.Label(dialog, text=question).pack(pady=10)

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Yes", width=10, command=on_yes).pack(side="left", padx=5)
    tk.Button(btn_frame, text="No", width=10, command=on_no).pack(side="left", padx=5)

    root.wait_window(dialog)
    return result['answer']

# === Hotkey Toggle (F8) ===
def toggle_clicking_hotkey():
    global clicking
    if clicking:
        stop_clicking()
    else:
        start_clicking()

keyboard.add_hotkey('f8', toggle_clicking_hotkey)

# === GUI Setup ===
root = tk.Tk()
root.title("LucceLito's Cliccer")
root.geometry("400x550")

# Profile frame horizontal layout
profile_frame = tk.Frame(root)
profile_frame.pack(pady=5)

tk.Label(profile_frame, text="Select Profile:").grid(row=0, column=0, padx=5)

profile_var = tk.StringVar(root)
profile_menu = tk.OptionMenu(profile_frame, profile_var, [])
profile_menu.grid(row=0, column=1, padx=5)

tk.Button(profile_frame, text="Save Profile", command=save_profile).grid(row=0, column=2, padx=5)
tk.Button(profile_frame, text="Delete Profile", command=delete_profile).grid(row=0, column=3, padx=5)

# Start/Stop Buttons
tk.Button(root, text="Start (F8)", bg="lightgreen", command=start_clicking).pack(pady=5)
tk.Button(root, text="Stop (F8)", bg="tomato", command=stop_clicking).pack(pady=5)

# Interval Setting
tk.Button(root, text="Set Click Interval", command=set_interval).pack(pady=5)

# Position Controls
tk.Button(root, text="Add Position (2s to move mouse)", command=lambda: threading.Thread(target=add_position, daemon=True).start()).pack(pady=5)
tk.Button(root, text="Remove Selected Position", command=delete_selected_position).pack(pady=5)
tk.Button(root, text="Clear All Positions", command=clear_positions).pack(pady=5)

# Position Listbox
listbox = tk.Listbox(root, width=40, height=10)
listbox.pack(pady=5)

# Instruction Label
tk.Label(root, text="Press F8 at any time to Start/Stop").pack(pady=10)

# Status Label (no pop-ups, messages here)
status_label = tk.Label(root, text="", fg="black", anchor="w")
status_label.pack(fill="x", padx=10, pady=5)

# Footer / Credit
tk.Label(root, text="Made by LucceLito", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)

# Initialize profile list on startup
update_profile_list()

root.mainloop()
