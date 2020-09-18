from core.lldb.lldb_mocker import *
from util.file_util import FileUtil

def test():
    # v = Register("x12")
    # RegisterFactory.register(v)
    # r = RegisterFactory.find_r("x12")
    # r = "12323"
    #
    # a = NilSymbol(0)
    # print(repr(a))
    # print(a + 1)
    # print(str(a))
    # print(hex(a))

    # p = Position()
    # p.name = "xxx"
    # print(p.name)
    # p.a = "123", 444
    # print(p.name)
    # print(p.a)

    # print(SymbolFactory.convert_int_2_list(888, 8, 1))
    # print(SymbolFactory.convert_int_2_list(256, 2, 0))
    #
    # print(Int.num32(-1))
    # print(Int.num64(-1))
    # print((Int.num32(-1) + 1).toHex())
    # print(hex(-2 & INT_Mask))
    # a = 256
    # print([b for b in a.to_bytes(8, "little")])
    # print(SymbolFactory.convert_int_2_list(0x8881, 8, 0))
    # print(SymbolFactory.convert_int_2_list_raw(0x8881, 8, 0))
    # print(hex(SymbolFactory.convert_list_2_int([0, 0, 0, 0, 0, 0, 136, 129], 0)))

    # print(Int.get_bits_size(0xFFFE))
    # # print(Int.get_bits_size(0xFFFF))
    # # print(Int.get_bits_size(0xFF))
    # # print(0b1101)
    # # print(Int.get_bits_size(0b111))
    # # print(Int.get_bits_size(0xFF))
    # # print((0b111 << (Int.get_bits_size(0xFF) - Int.get_bits_size(0b111))).to_bytes(8, "little"))
    # # print(ARM_DEFAULT_MASK_SIZE)
    #
    # print(hex(Int.get_mask(16)))
    # print(hex(Int.get_mask(ARM_DEFAULT_MASK_SIZE // 2)))
    # R.register(Register("x0", 0x1BCDEF1234567890))
    # print(Op.bfi("x0", 0xFFFF, 32, 16))
    # print(hex(R.r("x0").g_value()))

    # r1 = Register("x28", 0x000000006367ffff)
    # R.register(r1)
    # r2 = Register("x23", 0x00000000fc9e19b6)
    # R.register(r2)
    # cpsr = CPSRRegister(value=0x60000000)
    # R.register(cpsr)
    # print(Op.cmp("w28", "w23")) # 0000
    # arg0 = -2
    # arg1 = -1
    # if arg0 < arg1:
    #     print("N1")
    # else:
    #     print("N0")
    #
    # if Int.toUW(arg0) - Int.toUW(arg1):
    #     print("C0")
    # else:
    #     print("C1")
    #
    # if (INT_Mask_32 >> 1) - 1 > arg0 - arg1 > -(INT_Mask_32 >> 1) :
    #     print("V0", arg0 - arg1)
    # else:
    #     print("V1", arg0 - arg1, (INT_Mask_32 >> 1) - 1 > arg0 - arg1, arg0 - arg1 > -(INT_Mask_32 >> 1))
    # # print(cpsr.toNZCV())
    # #
    # # print(Int.toUW(-128).toHex())
    # print(Int.toUW(-3).toHex())
    # print(Int.toW(-0xFFFF_FFFE).toHex())
    # print(Int.toX(-3))

    Op.ubfx("", 0x0202e21f29, 21, 5) # 17


def test_main():
    f1 = FunctionFactory.create_function(FileUtil.read_file("./lldb_sub_103CE4E48.txt"))
    # F.dumps(f1)
    registers = Parser.load_register_from_lldb_text("./tmp/lldb_registers.txt")
    # 取 dumpM [($sp - 0x330), 4096] 还要更大..
    # 更新：建议 dumpM ($sp - 0x380)
    # mems = Parser.load_mem_from_lldb_text("./tmp/lldb_mem_0x16dcb8680.txt")
    mems = Parser.load_mem_from_lldb_text("./tmp/lldb_mem_0x1701f4680.txt")
    arm = ARMEleciron().init_environment(registers, mems, [f1])
    R.r("pc").s_value(f1.func_address)  # pc修复
    # <+20036>: mem read ($x5 + 0xc0) => mem read ($sp + 0x208 + 0xc0)
    # mem_0x10bb45100_line20036 = Parser.load_mem_from_lldb_text("./tmp/lldb_mem_0x010bb45100.txt") # 20036 [x9]
    mem_0x10bb45100_line20036 = Parser.load_mem_from_lldb_text("./tmp/lldb_mem_0x1094f1100.txt")  # 20036 [x9]
    arm.init_mems(mem_0x10bb45100_line20036)
    # <+1540>：mem read $sp - 24
    mem_0x1701f4668_line1540 = Parser.load_mem_from_lldb_text("./tmp/lldb_mem_0x1701f4668.txt")
    arm.init_mems(mem_0x1701f4668_line1540)
    # <+464> -> <+476> -> <+492> -> <+1252 -> <+2508> -> <+42060>: 是返回位置
    # 20200812测试 0x103CE4E48 ：dumpM 0x1701f39b0（$sp-0x1000） 0x3096
    # 20200815测试：共有5处放0x28... 观察前4处：0x170030e38($sp+0x488) > 0x170030d20 > 0x170030560 > 0x170030bc8、
    #   1. 0x170030e38 + 0x860 是单个值取位置。 lldb_func_symbol482833$$Aweme_348.txt <+324>
    # BP.register(OpCodePosition('Op.and_("w9", "w9", 0x80000000)')) # 断点到：+25492
    # BP.register(OpCodePosition('Op.cmp("w10", R.r("w9") >> 26)'))
    # BP.register(OpCodePosition('Op.stur("x3", (R.r("x8") - 0xd0).ptr)'))
    # BP.register(OpLineNoPosition("1540"))
    # BP.register(OpLineNoPosition("27964"))
    arm.start()
