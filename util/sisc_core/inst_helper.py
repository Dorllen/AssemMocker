import re
from core.sisc_core.mocker import Int, Mem, ARM_DEFAULT_MASK, ARM_DEFAULT_MASK_SIZE

class InstHelper(object):

    @staticmethod
    def _get_mask(value):
        assert isinstance(value, int) and value <= ARM_DEFAULT_MASK_SIZE, f"value:{value}"
        return ARM_DEFAULT_MASK >> (ARM_DEFAULT_MASK_SIZE - value)

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
    def bfi(*args):
        # # 0x00000000922f5a80, 0x00000000e9ab4270, 0x20, 0x20 -> 0xe9ab4270922f5a80
        # 仅仅支持64位
        x0, x1, x2, x3 = args
        arg0_high = x0 & (ARM_DEFAULT_MASK << (0 if x2 + x3 >= ARM_DEFAULT_MASK_SIZE else x2 + x3))
        # print(hex(arg0_high), hex(ARM_DEFAULT_MASK << (0 if x2 + x3 >= ARM_DEFAULT_MASK_SIZE else x2 + x3)))
        arg0_low = x0 & ARM_DEFAULT_MASK >> (ARM_DEFAULT_MASK_SIZE - x3)
        # print(hex(arg0_low), hex(ARM_DEFAULT_MASK >> (ARM_DEFAULT_MASK_SIZE - x3)))
        arg0_mid = (x1 & InstHelper._get_mask(x3)) << x2
        # print(hex(arg0_mid), hex(InstHelper._get_mask(x3) << (x2 - x3)))
        return arg0_high | arg0_mid | arg0_low

    @staticmethod
    def rev(arg):
        # rev: 0x000000006eb740dc -> 0x00000000dc40b76e 字节反转
        # 0x000000000039b100 -> 0x0000000000b13900
        # bstr = bin(arg).replace("0b", "")
        # while len(bstr) % 8 != 0:
        #     bstr = "0" + bstr
        # barr = re.findall("[01]{8}", bstr)
        # barr = [Int("0b" + i, 2) for i in barr]
        # barr.reverse()
        # return Mem.merge_arr_to_int(barr)

        s = "%0.8x" % arg
        s = [s[_:_+2] for _ in range(0, len(s), 2)]
        s.reverse()
        return Int("0x" + "".join(s), 16)

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

    @staticmethod
    def tst(x0, x1):
        return x0 & x1

    @staticmethod
    def orn(x0, x1):
        # 0x00a060400a021040 orn 0x0000000102b6c950 -> 0xfffffffeff4b36ef
        # todo: 待测试
        1/0
        return x0 | ~x1

    @staticmethod
    def bzero(x0, x1):
        for _ in range(x1):
            x0[_] = 0
        return x0
