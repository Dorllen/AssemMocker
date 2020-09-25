import re
from core.sisc_core.mocker import Int, Mem


class InstHelper(object):

    @staticmethod
    def ubfx(*args):
        assert len(args) == 3, args
        arg1, arg2, arg3 = args
        assert isinstance(arg2, int) and isinstance(arg3, int)
        bin_list = list(bin(arg1).replace("0b", ""))
        bin_list.reverse()
        bin_values = bin_list[arg2:arg2 + arg3]
        bin_values.reverse()
        bin_value = "".join(bin_values) or "0"
        return Int("0b" + bin_value, 2)

    @staticmethod
    def rev(arg):
        # rev: 0x000000006eb740dc -> 0x00000000dc40b76e 字节反转
        bstr = bin(arg).replace("0b", "")
        while len(bstr) % 8 != 0:
            bstr = "0" + bstr
        barr = re.findall("[01]{8}", bstr)
        barr = [Int("0b" + i, 2) for i in barr]
        barr.reverse()
        return Mem.merge_arr_to_int(barr)

    @staticmethod
    def memcpy(x0, x1, x2):
        if isinstance(x1, Mem):
            x1 = x1.to_list()[:x2]
        if isinstance(x0, Mem):
            x0[:] = x1
            return x0
        assert isinstance(x0, list)
        x0[:x2] = x1
        return x0
