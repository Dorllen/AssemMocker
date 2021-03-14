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
    def rev(arg, size=8):
        # rev: 0x000000006eb740dc -> 0x00000000dc40b76e 字节反转
        # 0x000000000039b100 -> 0x0000000000b13900
        # bstr = bin(arg).replace("0b", "")
        # while len(bstr) % 8 != 0:
        #     bstr = "0" + bstr
        # barr = re.findall("[01]{8}", bstr)
        # barr = [Int("0b" + i, 2) for i in barr]
        # barr.reverse()
        # return Mem.merge_arr_to_int(barr)

        s = f"%0.{size}x" % arg
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

    @staticmethod
    def orr(x0, x1):
        return x0 | x1

    @staticmethod
    def ror(x0, x1, size=4):
        """
        当x寄存器时，size=8; w寄存器时，size=4.默认w寄存器
        注： extr 指令 IH.extr(w10, w10, 0x13) = IH.ror(w10, 0x13)
        :param x0: 值
        :param x1: 位数
        :param size: 字节数
        :return:
        """
        x0 = x0 & ((2 << (size * 8 - 1)) -1)
        x0_0 = x0 << (size * 8 - x1)
        x0_1 = x0 >> x1
        return x0_0 | x0_1


    @staticmethod
    def bic(x0, x1):
        """
        x1与x0 位对应位置，如果bin_x1[]=0,则值为bin_x0[],否则为0
        (0x00000000b3bf9ede bic 0x0000000054a5e59f).w = 0xa31a1a40
        :param x0:
        :param x1:
        :return:
        """
        # x0 = x0 & ((2 << (size * 8 - 1)) -1)
        # x1 = x1 & ((2 << (size * 8 - 1)) -1)
        bx0 = bin(x0).replace("0b", "")
        bx1 = bin(x1).replace("0b", "")
        while len(bx1) < len(bx0):
            bx1 = "0" + bx1

        while len(bx0) < len(bx1):
            bx0 = "0" + bx0

        assert len(bx1) == len(bx0)
        _ = []
        for i in range(len(bx0)):
            if bx1[i] == "0":
                _.append(bx0[i])
            else:
                _.append("0")
        return int("0b" + "".join(_), 2)

    @staticmethod
    def sxtw(arg0):
        return arg0

    @staticmethod
    def sbfiz(arg0, arg1, arg2):
        """
        sbfiz(0x1, 2, 32) -> 0x4
        :param arg0:
        :param arg1:
        :param arg2:
        :return:
        """
        return (arg0 << arg1) & ((1 << arg2) - 1)



if __name__ == '__main__':
    # t = InstHelper.bic(0x00000000b3bf9ede, 0x0000000054a5e59f)
    t = InstHelper.ror(0x0000001254a5e59f, 11)
    print(hex(t))
    print(hex(0x7d529796 ^ t & 0xFF_FF_FF_FF))
