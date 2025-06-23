import struct


class measurment_device():
    HEADER_LEN   = 11
    HEADER_FMT   = '< H H I H B'
    PREAMBLE     = b'\xCC\xCC'

    def __init__(self):
        self.imu    = inertial_module_unit('imu')
        self.mgn    = magnetometer('mgn')
        self.gnss   = GNSS_reciever('gnss')
        self.bar    = barometer('bar')

    def parce(self, time_mark, type, buffer):

        match type:
            case DEP_TYPES.IMU:
                self.imu.parce(time_mark, buffer)
            case DEP_TYPES.MAG:
                self.mgn.parce(time_mark, buffer)
                pass
            case DEP_TYPES.GNSS:
                self.gnss.parce(time_mark, buffer)
            case DEP_TYPES.BAR:
                self.bar.parce(time_mark, buffer)

    def crc16(  self,
                data:       bytearray,
                mask:       int         = 0x1021,
                init_valie: int         = 0xFFFF)   -> int:

        def updcrc( crc:  int, c:  int) -> int:
            c <<= 8
            for _ in range(8):
                if (crc ^ c) & 0x8000:
                    crc = (crc << 1) ^ mask
                else:
                    crc <<= 1
                crc &= 0xFFFF
                c <<= 1
            return crc

        crc = init_valie
        for byte in data:
            crc = updcrc(crc, byte)

        return crc


class measurment():

    def __init__(self, name=''):
        self.payload = None
        self.time_mark = None
        self.name = name
        self.last_tmark = None

    def parce(self, time_mark, buffer):
        self.time_mark  = time_mark
        self.payload    = buffer
        self.parce_payload(buffer)

    def parce_payload(self, buffer):
        pass

    def log(self):
        if self.last_tmark != self.time_mark:
            print(f"[{self.name}] tMark= {self.time_mark} ", end="")
            self._log()
            self.last_tmark = self.time_mark

    def _log(self):
        pass


class inertial_module_unit(measurment):
    FMT = '< I h 3h 3h h'
    GRS_SF  = 16.4
    ACC_SF  = 2048

    def __init__(self, name=''):
        super().__init__(name)
        self.time   = None
        self.state  = None
        self.grs    = [None] * 3
        self.acc    = [None] * 3
        self.tmp    = None

    def parce_payload(self, buffer):
        temp = struct.unpack(self.FMT, buffer)
        self.time   = temp[0]
        self.state  = temp[1]
        self.grs    = [val / self.GRS_SF for val in temp[2:5]]
        self.acc    = [val / self.ACC_SF for val in temp[5:8]]
        self.grs[0], self.grs[1], self.grs[2] = -self.grs[0], self.grs[2], self.grs[1]
        self.acc[0], self.acc[1], self.acc[2] = -self.acc[0], self.acc[2], self.acc[1]
        self.tmp    = temp[8]   / 132.48 + 25

    def _log(self):
        def fmt(v):
            return "[" + ", ".join(f"{x:.3f}" for x in v) + "]"
        print(f"state={self.state} tmp={self.tmp:.3f} grs={fmt(self.grs)} acc={fmt(self.acc)}")


class magnetometer(measurment):
    FMT = '< I H 3i'

    def __init__(self, name=''):
        super().__init__(name)
        self.time   = None
        self.state  = None
        self.mgn    = [None] * 3

    def parce_payload(self, buffer):
        temp = struct.unpack(self.FMT, buffer)
        self.time  = temp[0]
        self.state = temp[1]
        self.mgn   = temp[2:]

    def _log(self):
        print(f"state= {self.state} mgn={self.mgn}")


class GNSS_reciever(measurment):

    def __init__(self, name=''):
        super().__init__(name)
        self.NMEA = None

    def parce_payload(self, buffer):
        self.NMEA = buffer.decode('ascii')

    def _log(self):
        print(f"NMEA= {self.NMEA}")


class barometer(measurment):
    FMT = '< I I'

    def __init__(self, name=''):
        super().__init__(name)
        self.tmp = None
        self.prs = None

    def parce_payload(self, buffer):
        temp = struct.unpack(self.FMT, buffer)
        self.tmp = temp[0]
        self.prs = temp[1]

    def _log(self):
        print(f"temp= {self.tmp} prs={self.prs}")


class DEP_TYPES():
    IMU  = 4
    MAG  = 6
    BAR  = 5
    GNSS = 8
