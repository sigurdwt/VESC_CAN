import can
import vesc_utils
import time
import argparse

parser = argparse.ArgumentParser(description="Eksempel på argument med defaultverdi.")

parser.add_argument('--wheel', type=str, default='BL', help="Wheel, ie. BL,BR,FR,FL (default: BL)")
parser.add_argument('--motor', type=str, default='Drive', help="Drive or swerve motor (default: Drive)")
parser.add_argument('--rpm', type=int, default='5000', help="ERPM (default: 5000)")

args = parser.parse_args()

drive_vesc_IDs = [0x50, 0x51, 0x52, 0x53]
swerve_vesc_IDs = [0x60, 0x61, 0x62, 0x63]

ID = 0
if args.motor == 'Drive':
    if args.wheel == 'FR':
        ID = drive_vesc_IDs[0]
    elif args.wheel == 'FL':
        ID = drive_vesc_IDs[1]
    elif args.wheel == 'BL':
        ID = drive_vesc_IDs[2]
    elif args.wheel == 'BR':
        ID = drive_vesc_IDs[3]
elif args.motor == 'Swerve':
    if args.wheel == 'FR':
        ID = swerve_vesc_IDs[0]
    elif args.wheel == 'FL':
        ID = swerve_vesc_IDs[1]
    elif args.wheel == 'BL':
        ID = swerve_vesc_IDs[2]
    elif args.wheel == 'BR':
        ID = swerve_vesc_IDs[3]

can_interface = 'can0'
bus = can.interface.Bus(channel=can_interface, bustype='socketcan')
VESC = vesc_utils.VESC(ID, bus)  # Initialize VESC with node ID and CAN bus



try:
    #Kjør i ett sekund  
    start_time = time.time()
    while time.time() - start_time < 1:
        try:
            # Les RPM fra VESC
            VESC.set_rpm(args.rpm)
            print(f"Sender RPM {args.rpm} til VESC  ({args.wheel}, {args.motor})")
        except RuntimeError as e:
            print(f"Feil ved sending av RPM til VESC ({args.wheel}, {args.motor}): {e}")
        time.sleep(0.1)

    

except RuntimeError as e:
    print(f"Feil ved sending av RPM til VESC  ({args.wheel}, {args.motor}): {e}")



except KeyboardInterrupt:
    print("\nAvbrutt av bruker.")
    bus.shutdown()

finally:
    bus.shutdown()
    print("Bus shutdown complete.")