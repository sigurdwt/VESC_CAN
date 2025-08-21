# py

import struct
import can
import time


COMM_SET_DUTY = 0x00
COMM_SET_CURRENT = 0x01
COMM_SET_BRAKE = 0x02
COMM_SET_RPM = 0x03
COMM_PING = 0x11

COMM_STATUS_1 =  0x09
COMM_STATUS_2 =  0x0E
COMM_STATUS_3 =  0x0F
COMM_STATUS_4 =  0x10
COMM_STATUS_5 =  0x1B


class VESC:
    # Kommando-koder (fra VESC firmware)



    def __init__(self, vesc_id: int, bus: can.Bus):
        """
        Oppretter en VESC-instans bundet til én fysisk enhet (via vesc_id).
        """
        self.vesc_id = vesc_id
        self.bus = bus

    def _build_can_id(self, cmd: int) -> int:
        """
        Lager VESC CAN-ID fra kommando og enhets-ID.
        CAN ID = (cmd << 8) | vesc_id
        """
        return (cmd << 8) | self.vesc_id

    @staticmethod
    def _encode_float32(value: float) -> bytes:
        """
        Pakk 4-byte float (big-endian) + 4-byte padding = 8 byte.
        """
        return struct.pack('>f', value) + bytes(4)

    @staticmethod
    def _encode_int32(value: int) -> bytes:
        """
        Pakk 4-byte signed int (big-endian) + 4-byte padding = 8 byte.
        """
        return struct.pack('>i', value)

    def _send(self, cmd: int, data: bytes):
        """
        Intern funksjon for å sende CAN-melding.
        """
        can_id = self._build_can_id(cmd)
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        try:
            self.bus.send(msg)
        except can.CanError as e:
            print(f"Feil ved sending til VESC {self.vesc_id}: {e}")

    def set_current(self, current_ma: int):
        """
        Setter strøm i ampere.
        """
        data = self._encode_int32(current_ma)
        self._send(self.COMM_SET_CURRENT, data)

    def set_duty(self, duty_cycle: float):
        """
        Setter duty cycle [-1.0, 1.0].
        """
        data = self._encode_float32(duty_cycle)
        self._send(self.COMM_SET_DUTY, data)

    def set_brake(self, brake_current: float):
        """
        Setter bremsekraft i ampere.
        """
        data = self._encode_float32(brake_current)
        self._send(self.COMM_SET_BRAKE, data)

    def set_rpm(self, rpm: int):
        """
        Setter ønsket RPM.
        """
        data = self._encode_int32(rpm)
        self._send(self.COMM_SET_RPM, data)

    def ping(self):
        self._send(self.COMM_PING, bytes(8))
        timeout = 1
        start = time.time()
        while time.time() - start < timeout:
            resp = self.bus.recv(timeout=timeout - (time.time() - start))
            if resp and resp.arbitration_id == 0x1200:
                if (resp.data[0] & 0xFF) == self.vesc_id:
                    return True
        return None

   

def parse_status(data):
    rpm = struct.unpack_from(">i", data, 0)[0]
    current = struct.unpack_from(">h", data, 4)[0] / 10.0
    duty = struct.unpack_from(">h", data, 6)[0] / 1000.0
    return rpm, current, duty

def parse_status_2(data):
    # Int32 @0: amp-hours (forbruk), Int32 @4: amp-hours charged (regen)
    ah = struct.unpack_from(">i", data, 0)[0] / 10000.0
    ah_ch = struct.unpack_from(">i", data, 4)[0] / 10000.0
    return ah, ah_ch

def parse_status_3(data):
    # Int32 @0: watt-hours (forbruk), Int32 @4: watt-hours charged (regen)
    wh = struct.unpack_from(">i", data, 0)[0] / 10000.0
    wh_ch = struct.unpack_from(">i", data, 4)[0] / 10000.0
    return wh, wh_ch

def parse_status_4(data):
    mos_temp = struct.unpack_from(">h", data, 0)[0] / 10.0
    motor_temp = struct.unpack_from(">h", data, 2)[0] / 10.0
    input_current = struct.unpack_from(">h", data, 4)[0] / 10.0
    pid_pos = struct.unpack_from(">h", data, 6)[0] / 50.0
    return mos_temp, motor_temp, input_current, pid_pos

def parse_status_5(data):
    tach = struct.unpack_from(">i", data, 0)[0]
    voltage = struct.unpack_from(">h", data, 4)[0] / 10.0
    return tach, voltage

def extract_command_and_id(arb_id):
    vesc_id = arb_id & 0xFF
    cmd = (arb_id >> 8) & 0xFF
    return cmd, vesc_id


#Make a function thtat takes in a can msg and returns the correct data
def parse_vesc_status(msg): 
    vesc_data = {
        vesc_id: {
            'time': None,
            'current': 0.0,
            'rpm': 0,
            'duty': 0.0,
            'mos_temp': 0.0,
            'motor_temp': 0.0,
            'input_current': 0.0,
            'pid_pos': 0.0,
            'tachometer': 0,
            'voltage': 0.0,
            'amp_hours': 0.0,
            'amp_hours_charged': 0.0,
            'watt_hours': 0.0,
            'watt_hours_charged': 0.0,
        }
    }

    cmd, vesc_id = extract_command_and_id(msg.arbitration_id)
    vesc_data[vesc_id]['time'] = time.time()

    if cmd == COMM_STATUS_1:  # STATUS
        rpm, current, duty = parse_status(msg.data)
        vesc_data[vesc_id]['current'] = current
        vesc_data[vesc_id]['rpm'] = rpm
        vesc_data[vesc_id]['duty'] = duty

  
    elif cmd == COMM_STATUS_2:  # STATUS_2
        ah, ah_ch = parse_status_2(msg.data)
        vesc_data[vesc_id]['amp_hours'] = ah
        vesc_data[vesc_id]['amp_hours_charged'] = ah_ch
        

    elif cmd == COMM_STATUS_3:  # STATUS_3
        wh, wh_ch = parse_status_3(msg.data)
        vesc_data[vesc_id]['watt_hours'] = wh
        vesc_data[vesc_id]['watt_hours_charged'] = wh_ch


    elif cmd == COMM_STATUS_4:  # STATUS_4
        mos, motor, input_i, pid = parse_status_4(msg.data)
        vesc_data[vesc_id]['mos_temp'] = mos
        vesc_data[vesc_id]['motor_temp'] = motor
        vesc_data[vesc_id]['input_current'] = input_i
        vesc_data[vesc_id]['pid_pos'] = pid


    elif cmd == COMM_STATUS_5:  # STATUS_5
        tach, voltage = parse_status_5(msg.data)
        vesc_data[vesc_id]['tachometer'] = tach
        vesc_data[vesc_id]['voltage'] = voltage



 