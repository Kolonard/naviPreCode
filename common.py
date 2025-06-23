import serial
import serial.tools.list_ports


class COM():
    BAUDRATE = 115200
    DEFAULT_WIN11_BUFF_LEN = 4098
    TIME_OUT = 0.5

    def __init__(self, baudrate=BAUDRATE):
        self.COM        = None
        self.baudrate   = baudrate

    def init_COM(self):
        available_ports = self.__list_com_ports()

        if not available_ports:
            print("No COM ports found.")
            input()

        print("Available COM ports:")
        for i, (port, desc) in enumerate(available_ports):
            print(f"{i + 1}: {port} - {desc}")

        port_index = int(input("Select COM port by number: ")) - 1
        self.COM = serial.Serial(available_ports[port_index][0], self.baudrate, timeout=self.TIME_OUT)

    def readByte(self) -> bytearray:
        return self.COM.read(1)

    def readBuffer(self, buff_len=DEFAULT_WIN11_BUFF_LEN):
        try:
            return bytearray(self.COM.read(buff_len))
        except serial.SerialException as e:
            print(f"COM error: {e}")

    def __list_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]
