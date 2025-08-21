import tkinter as tk
import can
from vesc_utils import VESC

# --- VESC-konfigurasjon ---
can_interface = 'can0'
vesc1_id = 0x52  # Første VESC
vesc2_id = 0x06  # Andre VESC

# Sett opp CAN-bus
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')

# Lag VESC-instansene
vesc1 = VESC(vesc1_id, bus)
vesc2 = VESC(vesc2_id, bus)

# --- Funksjon for å sende strøm ---
def send_loop():
    # Hent verdier fra sliderne
    value_1 = slider1.get()
    value_2 = slider2.get()

    # Send via VESC-klassen
    vesc1.set_rpm(value_1)  # Bruk RPM for første VESC
    vesc2.set_rpm(value_2)  # Bruk RPM for andre VESC

    # Kjør denne funksjonen igjen etter 100 ms
    root.after(100, send_loop)

# --- GUI ---
root = tk.Tk()
root.title("To VESC-kontrollere via vesc_utils")

slider1 = tk.Scale(root, from_=0, to=15000, orient=tk.HORIZONTAL,
                   label="VESC 0x52 – Set rpm",
                   length=400)
slider1.set(0)
slider1.pack(padx=20, pady=20)

slider2 = tk.Scale(root, from_=0, to=15000, orient=tk.HORIZONTAL,
                   label="VESC 0x06 – Set rpm",
                   length=400)
slider2.set(0)
slider2.pack(padx=20, pady=20)

# Start sende-loop
root.after(100, send_loop)

# Shutdown CAN når vinduet lukkes
def on_close():
    print("Stopper...")
    bus.shutdown()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
