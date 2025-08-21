import tkinter as tk
import can
from vesc_utils import VESC

# --- Innstillinger ---
can_interface = 'can0'
MAX_RPM = 15000     #ERPM

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
    slider = tk.Scale(
        root,
        from_=-MAX_RPM,
        to=MAX_RPM,
        orient=tk.HORIZONTAL,
        label=f"{name} – Set rpm",
        length=400
    )
    slider.set(0)
    slider.pack(padx=15, pady=10)
    sliders[vesc_id] = slider

# --- Send-loop ---
def send_loop():
    for vesc_id, vesc in vescs.items():
        rpm = sliders[vesc_id].get()
        vesc.set_rpm(rpm)
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
