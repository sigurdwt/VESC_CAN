import can
import csv
import struct
import time
import vesc_utils
from collections import deque

CAN_INTERFACE = 'can0'
MAX_LEN = 2000


def main():
    VESC_IDs = [0x50, 0x51, 0x52, 0x53, 0x60, 0x61, 0x62, 0x63]  
    bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

    #Define a dictionary to store all logged data from each VESC
    vesc_data = {
        vesc_id: {
            'time': deque(maxlen=MAX_LEN),
            'current': deque(maxlen=MAX_LEN),
            'rpm': deque(maxlen=MAX_LEN),
            'duty': deque(maxlen=MAX_LEN),
            'mos_temp': deque(maxlen=MAX_LEN),
            'motor_temp': deque(maxlen=MAX_LEN),
            'input_current': deque(maxlen=MAX_LEN),
            'pid_pos': deque(maxlen=MAX_LEN),
            'tachometer': deque(maxlen=MAX_LEN),
            'voltage': deque(maxlen=MAX_LEN)
        }
        for vesc_id in VESC_IDs
    }

    try:
        while True:
            msg = bus.recv(timeout=0.1)
            if msg is None or len(msg.data) != 8:
                continue
            cmd, vesc_id = vesc_utils.extract_command_and_id(msg.arbitration_id)
            if vesc_id not in VESC_IDs:
                continue

            timestamp = time.time()

            if cmd == 0x09:  # STATUS
                rpm, current, duty = vesc_utils.parse_status(msg.data)
                vesc_data[vesc_id]['time'].append(timestamp)
                vesc_data[vesc_id]['current'].append(current)
                vesc_data[vesc_id]['rpm'].append(rpm)
                vesc_data[vesc_id]['duty'].append(duty)
                if vesc_id == 0x50:
                    print(f"VESC ID: {vesc_id}, RPM: {rpm}")
                # print(f"VESC ID: {vesc_id}, Time: {timestamp:.2f}, Current: {current:.1f} A, RPM: {rpm}, Duty: {duty:.2f}")

            elif cmd == 0x10:  # STATUS_4
                mos, motor, input_i, pid = vesc_utils.parse_status_4(msg.data)
                vesc_data[vesc_id]['mos_temp'].append(mos)
                vesc_data[vesc_id]['motor_temp'].append(motor)
                vesc_data[vesc_id]['input_current'].append(input_i)
                vesc_data[vesc_id]['pid_pos'].append(pid)
                # print(f"VESC ID: {vesc_id}, MOS Temp: {mos:.1f} C, Motor Temp: {motor:.1f} C, Input Current: {input_i:.1f} A, PID Pos: {pid:.2f}")

            elif cmd == 0x1B:  # STATUS_5
                tach, voltage = vesc_utils.parse_status_5(msg.data)
                vesc_data[vesc_id]['tachometer'].append(tach)
                vesc_data[vesc_id]['voltage'].append(voltage)
                # print(f"VESC ID: {vesc_id}, Tachometer: {tach}, Voltage: {voltage:.1f} V")

            else:
                continue
            
            id = 0x60
            if vesc_id == id and vesc_data[id]['input_current'] and vesc_data[id]['voltage']:
                current = vesc_data[id]['input_current'][-1]
                voltage = vesc_data[id]['voltage'][-1]
                power = current * voltage
                # print(f"VESC {id}: Effekt = {power:.1f} W (I={current:.1f} A, U={voltage:.1f} V)")
                # print ("\n")




    except KeyboardInterrupt:
        print("Avslutter...")

    finally:
        bus.shutdown()



if __name__ == "__main__":
    main()
