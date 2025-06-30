import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
import threading
import time
import json
import keyboard  # pip install keyboard
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
positions_file = os.path.join(script_dir, "positions.json")

# === Global Variables ===
positions = []  # List of (x, y) tuples
clicking = False
click_interval = 0.5
positions_file = "positions.json"

# === Click Loop ===
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
        messagebox.showwarning("No Positions", "Please add at least one click position.")
        return
    if not clicking:
        clicking = True
        threading.Thread(target=click_loop, daemon=True).start()

def stop_clicking():
    global clicking
    clicking = False

# === Position Handling ===
def add_position():
    time.sleep(2)  # Give user time to move mouse
    pos = pyautogui.position()
    positions.append(pos)
    update_position_list()

def update_position_list():
    listbox.delete(0, tk.END)
    for idx, pos in enumerate(positions):
        listbox.insert(tk.END, f"{idx+1}: {pos}")

def delete_selected_position():
    selected = listbox.curselection()
    if selected:
        del positions[selected[0]]
        update_position_list()

def clear_positions():
    positions.clear()
    update_position_list()

def save_positions():
    with open(positions_file, "w") as f:
        json.dump(positions, f)
    messagebox.showinfo("Saved", f"Positions saved to {positions_file}")

def load_positions():
    global positions
    try:
        with open(positions_file, "r") as f:
            positions = [tuple(pos) for pos in json.load(f)]
        update_position_list()
        messagebox.showinfo("Loaded", "Positions loaded from file.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not load from file:\n{e}")

# === Interval Setting ===
def set_interval():
    global click_interval
    try:
        value = simpledialog.askfloat("Click Interval", "Enter interval in seconds (e.g. 0.5):", minvalue=0.01, maxvalue=10)
        if value is not None:
            click_interval = value
    except:
        pass

# === Hotkey (F8) Toggle ===
def toggle_clicking_hotkey():
    global clicking
    if clicking:
        stop_clicking()
    else:
        start_clicking()

keyboard.add_hotkey('f8', toggle_clicking_hotkey)

# === GUI ===
root = tk.Tk()
root.title("Advanced Auto Clicker")
root.geometry("400x500")

# Start/Stop Buttons
tk.Button(root, text="Start (F8)", bg="lightgreen", command=start_clicking).pack(pady=5)
tk.Button(root, text="Stop", bg="tomato", command=stop_clicking).pack(pady=5)

# Interval Setting
tk.Button(root, text="Set Click Interval", command=set_interval).pack(pady=5)

# Position Controls
tk.Button(root, text="Add Position (2s to move mouse)", command=lambda: threading.Thread(target=add_position, daemon=True).start()).pack(pady=5)
tk.Button(root, text="Remove Selected Position", command=delete_selected_position).pack(pady=5)
tk.Button(root, text="Clear All Positions", command=clear_positions).pack(pady=5)

# Position List Display
listbox = tk.Listbox(root, width=40, height=10)
listbox.pack(pady=5)

# Save / Load Buttons
tk.Button(root, text="Save Positions", command=save_positions).pack(pady=5)
tk.Button(root, text="Load Positions", command=load_positions).pack(pady=5)

# Instruction
tk.Label(root, text="Press F8 at any time to Start/Stop").pack(pady=10)

# Footer / Credit
tk.Label(root, text="Made by LucceLito & ChatGPT", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)

# Run the GUI
root.mainloop()
