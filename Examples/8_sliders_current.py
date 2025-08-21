import tkinter as tk
import can
from vesc_utils import VESC

# --- Innstillinger ---
can_interface = 'can0'
MAX_CURRENT_DRIVE = 50000   # i milliampere (50A)
MAX_CURRENT_SWERVE = 10000  # i milliampere (10A)

# --- CAN-bus ---
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')

# --- VESC-IDer (hex) ---
vesc_ids = {
    "FR Drive (0x50)": 0x50,
    "FR Swerve (0x60)": 0x60,
    "FL Drive (0x51)": 0x51,
    "FL Swerve (0x61)": 0x61,
    "BL Drive (0x52)": 0x52,
    "BL Swerve (0x62)": 0x62,
    "BR Drive (0x53)": 0x53,
    "BR Swerve (0x63)": 0x63
}

# --- Opprett VESC-instansene og sliders ---
vescs = {}
sliders = {}

root = tk.Tk()
root.title("VESC-kontroller for 8 motorer")

for name, vesc_id in vesc_ids.items():
    vescs[vesc_id] = VESC(vesc_id, bus)

    # Bruk forskjellige grenser for swerve og drive
    if "Swerve" in name:
        current_limit = MAX_CURRENT_SWERVE
    else:
        current_limit = MAX_CURRENT_DRIVE

    slider = tk.Scale(
        root,
        from_=-current_limit,
        to=current_limit,
        orient=tk.HORIZONTAL,
        label=f"{name} – Set current (mA)",
        length=400
    )
    slider.set(0)
    slider.pack(padx=15, pady=10)
    sliders[vesc_id] = slider

# --- Nullstill alle sliders ---
def reset_all_currents():
    for slider in sliders.values():
        slider.set(0)

reset_button = tk.Button(root, text="Nullstill alle motorstrømmer", command=reset_all_currents, bg="lightgray")
reset_button.pack(pady=15)

# --- Send-loop ---
def send_loop():
    for vesc_id, vesc in vescs.items():
        current = sliders[vesc_id].get()
        vesc.set_current(current)
    root.after(100, send_loop)

# --- Lukk og stopp bus ---
def on_close():
    print("Stopper...")
    bus.shutdown()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# --- Start loop ---
root.after(100, send_loop)
root.mainloop()
