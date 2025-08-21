import can
import struct
import time
import socket
import vesc_utils

# HOST = "10.0.254.170"  # IP-adresse Skøyen
HOST = "192.168.86.224"  # IP-adresse fredrikstad
PORT = 5005

CAN_INTERFACE = 'can0'
VESC_IDs = [0x50, 0x51, 0x52, 0x53, 0x60, 0x61, 0x62, 0x63]


def stream_data():
    bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    try:
        while True:
            msg = bus.recv(timeout=0.01)
            if msg is None or len(msg.data) != 8:
                continue

            cmd, vesc_id = vesc_utils.extract_command_and_id(msg.arbitration_id)
            if vesc_id not in VESC_IDs:
                continue

            timestamp = time.time()

            if cmd == 0x09:
                rpm, current, duty = vesc_utils.parse_status(msg.data)
                payload = f"{timestamp},{vesc_id},{rpm},{current:.2f},{duty:.3f}\n"
                sock.sendall(payload.encode('utf-8'))

    except KeyboardInterrupt:
        print("Avslutter strømming...")

    finally:
        bus.shutdown()
        sock.close()
        


if __name__ == "__main__":
    stream_data()
