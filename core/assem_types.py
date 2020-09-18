from core.mocker import *


class Int(int):
    @staticmethod
    def num(value):
        return Int(value)

    @staticmethod
    def num64(value):
        if value > 0x7F_FFFFFF_FFFFFFFF: # 处理上溢
            value = -0x80_000000_00000000 + (value - 0x80_000000_00000000)
        elif -0x80_000000_00000000 > value:
            value = 0x7F_FFFFFF_FFFFFFFF + (value + 0x80_000000_00000001)
        return Int(value)

    @staticmethod
    def unum64(value):
        return Int.num(value & INT_Mask)

    @staticmethod
    def num32(value):
        assert isinstance(value, int)
        # if value > (INT_Mask_32 >> 1) - 1 or value < (INT_Mask_32 >> 1):
        if value > 0x7F_FF_FF_FF:
            value = -0x80_00_00_00 + (value - 0x80_00_00_00)
        elif -0x80_00_00_00 > value:
            value = 0x7F_FF_FF_FF + (value + 0x80_00_00_01)
        return Int.num(value)

    @staticmethod
    def unum32(value):
        return Int.num(value & INT_Mask_32)

    @staticmethod
    def num8(value):
        assert isinstance(value, int)
        if value > 0x7F:
            value = -0x80 + (value - 0x80)
        elif value < -2**7:
            value = 0x7F + (value + 0x81)
        else:
            pass
        return Int.num(value)

    @staticmethod
    def unum8(value):
        return Int.num(value & 0xFF)


    @staticmethod
    def signed2unsigned(value): # 有符号数转换无符号int. -0x63680835 -> 0xFFFFFFFF9C97F7CB。 无符号数不受影响
        return value & INT_Mask

    @staticmethod
    def toW(value):
        return Int.num32(value)

    @staticmethod
    def toQ(value):
        assert value <= 0, "待观察"
        return Int(value & INT_Mask_128)

    @staticmethod
    def toX(value):
        return Int.num64(value)

    @staticmethod
    def toUX(value):
        return Int.unum64(value)

    @staticmethod
    def toUW(value):
        return Int.unum32(value)

    def toHex(self):
        return hex(self)

    @classmethod
    def guess_is_int(cls, value):
        try:
            if isinstance(value, int):
                return True
            elif isinstance(value, str):
                if value.startswith("0x") or value.startswith("-0x"):
                    int(value, 16)
                    return True
                int(value)
                return True
            raise RuntimeError("未知类型[待处理]:"+value)
        except ValueError:
            pass


class Register(object):
    pass


class List(list):
    def toHexList(self, size=16):
        return [hex(i) for i in self[:size]]


class Position(object):
    pass


class BreakPoint(object):
    pass
