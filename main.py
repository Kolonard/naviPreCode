
from measurment_device import measurment_device
from common import COM
import struct


com = COM()
md  = measurment_device()


def main():

    com.init_COM()
    buffer = bytearray()

    while True:  # Global while

        while True:  # One msg while

            byte = com.readByte()
            if not byte:
                break
            if byte != md.PREAMBLE[0:1]:
                break

            byte = com.readByte()
            if not byte:
                break
            if byte != md.PREAMBLE[1:2]:
                break

            buffer = com.readBuffer(9)

            crc16, timestamp, payload_len, msg_type = struct.unpack('<H I H B', buffer)
            payload = com.readBuffer(payload_len)
            if crc16 != md.crc16(buffer[2:] + payload):
                break

            md.parce(timestamp, msg_type, payload)

            md.imu.log()
            md.mgn.log()
            md.gnss.log()
            md.bar.log()


if __name__ == '__main__':
    main()
