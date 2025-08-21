import can
import time

# Parametre
can_interface = 'can0'
#vesc_id = 0x52 #6
vesc_id = 0x6 #6

# CAN-ID for kommando (du sender data direkte, så dette er fast)
can_id = vesc_id

# Data: Duty cycle = 0.01 (tilsvarer 00 01 00 00)
drive_data = [0x00, 0x01, 0x00, 0x00] +[0x00] * 4 
stop_data  = [0x00] * 8

# Sett opp CAN-bus
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')

# Lag meldinger
drive_msg = can.Message(
    arbitration_id=can_id,
    data=bytearray(drive_data),
    is_extended_id=True
)

stop_msg = can.Message(
    arbitration_id=can_id,
    data=bytearray(stop_data),
    is_extended_id=True
)

try:
    print("Starter motor i 3 sekunder...")
    start_time = time.time()

    while time.time() - start_time < 3.0:
        bus.send(drive_msg)
        time.sleep(0.1)

    print("Stopper motor.")
    bus.send(stop_msg)

except can.CanError as e:
    print("CAN send error:", e)

finally:
    bus.shutdown()
