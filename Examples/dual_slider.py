import tkinter as tk
import can
import struct

# VESC-konfigurasjon
can_interface = 'can0'
vesc1_id = 0x52  # Første VESC
vesc2_id = 0x06  # Andre VESC
cmd = 0x03       # 0-set duty, 1-set current, 2-set brake, 3-set RPM

can_id_1 = (cmd << 8) | vesc1_id
can_id_2 = (cmd << 8) | vesc2_id

# Sett opp CAN-bus
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')


def send_loop():
    # Hent verdier fra sliderne
    value_1 = slider1.get()
    value_2 = slider2.get()

    # Pakk og send til VESC 1
    data1 = struct.pack('>I', value_1) + bytes(4)
    msg1 = can.Message(arbitration_id=can_id_1, data=data1, is_extended_id=True)
    try:
        bus.send(msg1, timeout=0.0)
    except can.CanError as e:
        print("CAN send error to VESC 1:", e)
        
    # Pakk og send til VESC 2
    data2 = struct.pack('>I', value_2) + bytes(4)
    msg2 = can.Message(arbitration_id=can_id_2, data=data2, is_extended_id=True)
    try:
        bus.send(msg2, timeout=0.0)
    except can.CanError as e:
        print("CAN send error to VESC 2:", e)

    root.after(100, send_loop)

    

# GUI
root = tk.Tk()
root.title("To VESC-kontrollere")

slider1 = tk.Scale(root, from_=0, to=15000, orient=tk.HORIZONTAL,
                   label="VESC 0x52 – Set Current (mA)",
                   length=400)
slider1.set(0)
slider1.pack(padx=20, pady=20)

slider2 = tk.Scale(root, from_=0, to=15000, orient=tk.HORIZONTAL,
                   label="VESC 0x06 – Set Current (mA)",
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
