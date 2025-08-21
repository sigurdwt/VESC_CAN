import tkinter as tk
import can
import struct

# VESC-konfigurasjon
can_interface = 'can0'
vesc_id = 0x52
cmd = 0x03 #0-set duty, 1-set current, 2-set brake, 3-set RPM

can_id = (cmd << 8) | vesc_id  # COMM_SET_DUTY

# Sett opp CAN-bus
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')


def send_loop():
    # Pakk og send duty cycle som 4-byte float
    value = slider.get()
    data = struct.pack('>I', value)
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
    try:
        bus.send(msg)
    except can.CanError as e:
        print("CAN send error:", e)
    root.after(100, send_loop)  # kall igjen om 100 ms

# GUI
root = tk.Tk()
root.title("VESC Duty Control")

slider = tk.Scale(root, from_=0, to=15000, orient=tk.HORIZONTAL,
                  label="Set Current (mA)", 
                  length=400)
slider.set(0)
slider.pack(padx=20, pady=40)

# Start sende-loop
root.after(100, send_loop)

# Shutdown CAN når vinduet lukkes
def on_close():
    print("Stopper...")
    bus.shutdown()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
