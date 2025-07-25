import tkinter as tk
import threading
import pyautogui
import time
import json
import keyboard
import os

# === Globals ===
positions = []
clicking = False
click_interval = 0.5
holding_click = False
hold_key = "left"  # Default till vänsterklick


# Profile folder
script_dir = os.path.dirname(os.path.abspath(__file__))
profile_dir = os.path.join(script_dir, "profiles")
os.makedirs(profile_dir, exist_ok=True)

def get_profile_path(profile_name):
    return os.path.join(profile_dir, f"{profile_name}.json")

# === Tkinter Root & Styling ===
root = tk.Tk()
root.title("LucceLito's Auto-Cliccer")
root.geometry("330x750")
root.configure(bg="#2e2e2e")  # Dark background
root.resizable(False, False)

def center_window(window, width=320, height=110):
    # Get main window position and size
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    
    # Calculate position to center the popup over root
    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)
    
    # Set the geometry of the popup
    window.geometry(f"{width}x{height}+{x}+{y}")


# === Status Label ===
status_label = tk.Label(root, text="", fg="lightgray", bg="#2e2e2e",
                        anchor="center", font=("Segoe UI", 11, "bold"))
status_label.pack(fill="x", padx=10, pady=5)

def update_status(message, color="lightgray"):
    status_label.config(text=message, fg=color)


# === Position Listbox ===
listbox = tk.Listbox(root, width=45, height=10, bg="#3b3b3b", fg="white",
                     selectbackground="#575757", selectforeground="white",
                     font=("Segoe UI", 10))
listbox.pack(pady=5)

def update_position_list():
    listbox.delete(0, tk.END)
    for idx, pos in enumerate(positions):
        listbox.insert(tk.END, f"{idx+1}: {pos}")

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
        update_status("Please add at least one click position.", "orange")
        return
    if not clicking:
        clicking = True
        threading.Thread(target=click_loop, daemon=True).start()
        update_status("Clicking started.", "#4CAF50")

def stop_clicking():
    global clicking
    clicking = False
    update_status("Clicking stopped.", "#f44336")

def hold_click_loop():
    global holding_click
    if not positions:
        update_status("Please add at least one click position.", "orange")
        holding_click = False
        return

    pos = positions[0]
    pyautogui.moveTo(pos)

    if hold_key.lower() == "left":
        pyautogui.mouseDown()
    else:
        keyboard.press(hold_key)

    update_status(f"Holding '{hold_key.upper()}' at {pos}. Press F9 to release.", "#FF9800")

    while holding_click:
        time.sleep(0.1)

    if hold_key.lower() == "left":
        pyautogui.mouseUp()
    else:
        keyboard.release(hold_key)

    update_status(f"Released '{hold_key.upper()}'.", "#f44336")

def set_hold_key():
    def validate_key(keyname):
        # Allow any string key, or "left" for mouse
        return True, "" if keyname else (False, "Key cannot be empty.")

    val = modal_input("Set Hold Key", "Enter key to hold (e.g. A, space, left):", validate_key)
    if val:
        global hold_key
        hold_key = val.lower()
        update_status(f"Hold key set to '{hold_key.upper()}'.", "#4CAF50")

def start_holding_click():
    global holding_click
    if holding_click:
        update_status("Already holding.", "orange")
        return
    holding_click = True
    threading.Thread(target=hold_click_loop, daemon=True).start()

def stop_holding_click():
    global holding_click
    holding_click = False

# === Position Management ===
def add_position():
    update_status("Move mouse to position in 2 seconds...", "#2196F3")
    time.sleep(2)
    pos = pyautogui.position()
    positions.append(pos)
    update_position_list()
    update_status(f"Added position: {pos}", "#4CAF50")

def delete_selected_position():
    selected = listbox.curselection()
    if selected:
        del positions[selected[0]]
        update_position_list()
        update_status("Selected position removed.", "#4CAF50")
    else:
        update_status("No position selected to remove.", "orange")

def clear_positions():
    positions.clear()
    update_position_list()
    update_status("All positions cleared.", "#4CAF50")

# === Click Interval ===
def validate_interval(val):
    try:
        v = float(val)
        if v < 0.01 or v > 10:
            return False, "Interval must be between 0.01 and 10 seconds."
        return True, ""
    except:
        return False, "Invalid number for interval."

def modal_input(title, prompt, validate_func=None):
    result = {'value': None}
    def on_ok(event=None):
        val = entry.get()
        if validate_func:
            valid, msg = validate_func(val)
            if not valid:
                update_status(msg, "orange")
                return
        result['value'] = val
        dialog.destroy()

    def on_cancel(event=None):
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.grab_set()
    center_window(dialog, 320, 110)
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.configure(bg="#2e2e2e")

    tk.Label(dialog, text=prompt, bg="#2e2e2e", fg="lightgray", font=("Segoe UI", 10)).pack(pady=8)

    entry = tk.Entry(dialog, font=("Segoe UI", 11))
    entry.pack(pady=5)
    entry.focus_set()
    entry.bind("<Return>", on_ok)
    entry.bind("<Escape>", on_cancel)

    btn_frame = tk.Frame(dialog, bg="#2e2e2e")
    btn_frame.pack(pady=5)

    ok_btn = tk.Button(btn_frame, text="OK", width=10, command=on_ok,
                       bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                       activebackground="#45a049", activeforeground="white")
    ok_btn.pack(side="left", padx=8)

    cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel,
                           bg="#f44336", fg="white", font=("Segoe UI", 10, "bold"),
                           activebackground="#d32f2f", activeforeground="white")
    cancel_btn.pack(side="left", padx=8)

    root.wait_window(dialog)
    return result['value']

def set_interval():
    val = modal_input("Set Click Interval", "Enter click interval (Seconds):", validate_interval)
    if val is not None:
        global click_interval
        click_interval = float(val)
        update_status(f"Click interval set to {click_interval} seconds.", "#4CAF50")

# === Profile Management ===
def get_profile_path(profile_name):
    return os.path.join(profile_dir, f"{profile_name}.json")

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
        update_status(f"Profile '{name}' saved.", "#4CAF50")
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
        update_status(f"Profile '{selected}' loaded.", "#4CAF50")
    except Exception as e:
        update_status(f"Error loading profile: {e}", "red")

def modal_confirm(question):
    result = {'answer': False}

    def on_yes(event=None):
        result['answer'] = True
        dialog.destroy()

    def on_no(event=None):
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Confirm")
    dialog.grab_set()
    center_window(dialog, 320, 110)
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.configure(bg="#2e2e2e")

    tk.Label(dialog, text=question, bg="#2e2e2e", fg="lightgray",
             font=("Segoe UI", 11, "bold")).pack(pady=20)

    btn_frame = tk.Frame(dialog, bg="#2e2e2e")
    btn_frame.pack(pady=5)

    yes_btn = tk.Button(btn_frame, text="Yes", width=10, command=on_yes,
                        bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                        activebackground="#45a049", activeforeground="white")
    yes_btn.pack(side="left", padx=8)
    yes_btn.bind("<Return>", on_yes)

    no_btn = tk.Button(btn_frame, text="No", width=10, command=on_no,
                       bg="#f44336", fg="white", font=("Segoe UI", 10, "bold"),
                       activebackground="#d32f2f", activeforeground="white")
    no_btn.pack(side="left", padx=8)
    no_btn.bind("<Return>", on_no)

    root.wait_window(dialog)
    return result['answer']

def delete_profile():
    selected = profile_var.get()
    if not selected:
        update_status("No profile selected to delete.", "orange")
        return
    confirm = modal_confirm(f"Delete profile '{selected}'?")
    if not confirm:
        update_status("Profile deletion cancelled.", "orange")
        return
    try:
        os.remove(get_profile_path(selected))
        update_profile_list()
        update_status(f"Profile '{selected}' deleted.", "#4CAF50")
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

# === Hotkey Toggle (F8) ===
def toggle_clicking_hotkey():
    global clicking
    if clicking:
        stop_clicking()
    else:
        start_clicking()

keyboard.add_hotkey('f8', toggle_clicking_hotkey)
keyboard.add_hotkey('f9', lambda: stop_holding_click() if holding_click else start_holding_click())


# === GUI Layout ===

# Profile frame for profile management
profile_frame = tk.Frame(root, bg="#2e2e2e")
profile_frame.pack(pady=10)

profile_var = tk.StringVar(root)
tk.Label(profile_frame, text="Select Profile:", bg="#2e2e2e", fg="lightgray", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)

profile_menu = tk.OptionMenu(profile_frame, profile_var, ())
profile_menu.config(bg="#444", fg="white", activebackground="#575757", activeforeground="white", font=("Segoe UI", 10))
profile_menu.grid(row=0, column=1, padx=5)

btn_style = {
    "bg": "#444", "fg": "white", "activebackground": "#575757",
    "activeforeground": "white", "font": ("Segoe UI", 10, "bold"),
    "width": 20, "height": 1,
}

# Group buttons in frames for clarity

# Clicking controls frame
click_frame = tk.LabelFrame(root, text="Click Controls", fg="lightgray", bg="#2e2e2e", font=("Segoe UI", 11, "bold"))
click_frame.pack(pady=8, fill="x", padx=10)

# Rad 1
click_row1 = tk.Frame(click_frame, bg="#2e2e2e")
click_row1.pack(fill="x", padx=5)

# Rad 2
click_row2 = tk.Frame(click_frame, bg="#2e2e2e")
click_row2.pack(fill="x", padx=5, pady=(5, 0))


tk.Button(click_row1, text="Start (F8)", command=start_clicking,
          bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), width=9).pack(side="left", padx=5, pady=8)
tk.Button(click_row1, text="Stop (F8)", command=stop_clicking,
          bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"), width=9).pack(side="left", padx=5, pady=8)
tk.Button(click_row1, text="Set Interval", command=set_interval,
          bg="#00BCD4", fg="white", font=("Segoe UI", 11, "bold"), width=9).pack(side="left", padx=5, pady=8)
tk.Button(click_row2, text="Set Hold Key", command=set_hold_key,
          bg="#9C27B0", fg="white", font=("Segoe UI", 11, "bold"), width=12).pack(side="left", padx=20, pady=8)
tk.Button(click_row2, text="Hold Key (F9)", command=lambda: stop_holding_click() if holding_click else start_holding_click(),
          bg="#FF9800", fg="white", font=("Segoe UI", 11, "bold"), width=12).pack(side="right", padx=20, pady=8)

# Position management frame
pos_frame = tk.LabelFrame(root, text="Positions", fg="lightgray", bg="#2e2e2e", font=("Segoe UI", 11, "bold"))
pos_frame.pack(pady=8, fill="x", padx=10)

tk.Button(pos_frame, text="Add Position (2s to move mouse)", command=lambda: threading.Thread(target=add_position, daemon=True).start(), **btn_style).pack(pady=5, padx=10, fill="x")
tk.Button(pos_frame, text="Remove Selected Position", command=delete_selected_position, **btn_style).pack(pady=5, padx=10, fill="x")
tk.Button(pos_frame, text="Clear All Positions", command=clear_positions, **btn_style).pack(pady=5, padx=10, fill="x")

# Profile management frame
profile_mgmt_frame = tk.LabelFrame(root, text="Profiles", fg="lightgray", bg="#2e2e2e", font=("Segoe UI", 11, "bold"))
profile_mgmt_frame.pack(pady=8, fill="x", padx=10)

tk.Button(profile_mgmt_frame, text="Save Profile", command=save_profile, **btn_style).pack(pady=5, padx=10, fill="x")
tk.Button(profile_mgmt_frame, text="Delete Profile", command=delete_profile, **btn_style).pack(pady=5, padx=10, fill="x")

# Credits label
credits = tk.Label(root, text="Made by LucceLito and ChatGPT", bg="#2e2e2e", fg="gray", font=("Segoe UI", 9, "italic"))
credits.pack(side="bottom", pady=6)

# Initialize profile list & position list
update_profile_list()
update_position_list()

root.mainloop()
