from core.sisc_core.mocker import *
from util.sisc_core.inst_helper import InstHelper

def sub_100369264(x0:Mem, x1:Mem, x2:Mem, x25_f_path):
    _x0 = x0
    _x1 = x1
    _x2 = x2

    w8, w9, w10, w11 = Mem.mem_read(x1, 4) # *(x1)

    w8, w9, w10, w11 = InstHelper.rev(w8), InstHelper.rev(w9), InstHelper.rev(w10), InstHelper.rev(w11)

    w12, w13 = Mem.mem_read(x0, 2) # *(x0)

    w27 = w12 ^ w8 # main
    w26 = w13 ^ w9 # main

    w8, w9 = Mem.mem_read(x0 + 0x8, 2)

    w28 = w8 ^ w10 # main
    w24 = w9 ^ w11 # main

    w8 = 0xa # *([X0,#0x1E0])
    w9 = w8 >> 1
    w9 = w9 - 1
    w9 = w9 << 3 # 0x20
    sp_0xa0_0x99 = w9
    w9 = w9 + 0x8 # 存到 *(SP,#0xA0+var_90)
    sp_0xa0_0x90 = w9

    w11 = -9 # 1 - (w8 >> 1) # 1 - 0xa => 0xfffffffc. 可以理解为-9

    w15 = 1
    w14 = 0x1ce
    x12 = x0 + 0x18 # 表示 x0 + 0x18 地址
    # w24, w26, w27, w28 已知
    # x16内容： /Users/pengdongneng/PycharmProjects/secrets/pythonDemo/ios/Nt_ARM/Nt_LLDB/tmp/lldb_mem_0x10c6d9cb0.txt
    # x25 = 0x..d8f8. 且读这块内存至少是 0x2000
    # "/Users/pengdongneng/PycharmProjects/secrets/pythonDemo/ios/Nt_ARM/Nt_LLDB/tmp/lldb_mem_0x10cf1acc8.txt"
    x25 = Mem.read_file(x25_f_path) #
    while True:
        #loc_100369364
        w8 = w27 >> 0x18
        # lldb_mem_0x10c6d9cb0.txt $x16
        # lldb_mem_0x10cf1acc8.txt $x25
        w6 = x25.w[w8 << 2]
        w8 = InstHelper.ubfx(w26, 16, 8)
        # 0x10cf1b0c8 $x10
        x10 = x25 + 0x400 # 0x..dcf8 都是计算x19后的结果，以x25为基准偏移，+偏移0x400
        w22 = x10.w[w8 << 2]
        w8 = InstHelper.ubfx(w28, 0x8, 0x8)

        x30 = x10 + 0x400 # 0x..e0f8
        w0 = x30.w[w8 << 2]
        w2 = w24 & 0xFF
        x8 = x30 + 0x400 # 0x..e4f8
        w17 = x8.w[w2 << 2]
        w2 = w22 ^ w6
        w0 = w2 ^ w0
        w2 = w26 >> 0x18
        w17 = w0 ^ w17
        w0, w22 = Mem.mem_read(x12 - 8, 2) # *(x12 - 8) # 刚好 0x18 - 0x8 -> 0x10，因为前参数取的是0 ~ 0x10。而在这个循环总共处理x0 + 0x10 ~ 0x10 + 0x30的数据。
        w6 = w17 ^ w0
        w17 = x25.w[w2 << 2]
        w0 = InstHelper.ubfx(w28, 0x10, 8)
        w0 = x10.w[w0 << 2]
        w2 = InstHelper.ubfx(w24, 8, 8)
        w2 = x30.w[w2 << 2]
        w17 = w0 ^ w17
        w17 = w17 ^ w2
        w0 = w27 & 0xFF
        w0 = x8.w[w0 << 2]
        w17 = w17 ^ w0
        w0 = w28 >> 0x18
        w0 = x25.w[w0 << 2]
        w2 = InstHelper.ubfx(w24, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w22 = w17 ^ w22
        w17 = w2 ^ w0
        w0 = InstHelper.ubfx(w27, 8, 8)
        w0 = x30.w[w0 << 2]
        w17 = w17 ^ w0
        w0 = w26 & 0xFF
        w0 = x8.w[w0 << 2]
        w2 = w24 >> 0x18
        w2 = x25.w[w2 << 2]
        w17 = w17 ^ w0
        w0 = InstHelper.ubfx(w27, 0x10, 8)
        w10 = x10.w[w0 << 2]

        w0, w25 = Mem.mem_read(x12, 2)
        w24 = w17 ^ w0
        w10 = w10 ^ w2
        w17 = InstHelper.ubfx(w26, 8, 8)
        w17 = x30.w[w17 << 2]
        w10 = w10 ^ w17
        w17 = w28 & 0xFF
        w17 = x8.w[w17 << 2]
        w10 = w10 ^ w17
        w25 = w10 ^ w25
        w26 = w6 >> 0x18
        if w11 == 0:
            x17 = _x0 # [SP,#0xA0+var_88]. c0 a7 ca 6c 01
            x8 = sp_0xa0_0x99 # [SP,#0xA0+var_98]
            x8 = x17 + (x8 << 2) #

            x11 = x25 + 0x1000 #0x1000 = 0x400 * 4;  Mem.read_file("") # ldp [x10] # ida:0x100369720. x11 = 0x..e8f8
            w13 = x11.w[w26 << 2]
            w14 = InstHelper.ubfx(w22, 0x10, 8)
            x12 = x11 + 0x400
            w14 = x12.w[w14 << 2]
            w15 = InstHelper.ubfx(w24, 8, 8)

            x16 = x11 + 0x400
            w15 = x16.w[w15 << 2]

            w17 = x17.w[sp_0xa0_0x90 << 2]
            w0 = w22 > 0x18
            w0 = x11.w[w0 << 2]
            w1 = InstHelper.ubfx(w24, 0x10, 8)
            w1 = x12.w[w1 << 2]
            w2 = InstHelper.ubfx(w25, 8, 8)
            w2 = x16.w[w2 << 2]
            w3 = w24 >> 0x18
            w3 = x11.w[w3 << 2]
            w4 = InstHelper.ubfx(w24, 0x10, 8)
            w4 = x12.w[w4 << 2]
            w5 = InstHelper.ubfx(w6, 8, 8)
            w5 = x16.w[w5 << 2]
            w7 = w25 >> 0x18
            w11 = x11.w[w7 << 2]
            w7 = InstHelper.ubfx(w6, 0x10, 8)
            w12 = x12.w[w7 << 2]
            w7 = InstHelper.ubfx(w22, 8, 8)
            w16 = x16.w[w7 << 2]

            x9 = x16 + 0x400
            w10 = w25 & 0xFF
            w10 = x9.w[w10 << 2]
            w6 = w6 & 0xFF
            w6 = x9.w[w6 << 2]
            w7 = w22 & 0xFF
            w7 = x9.w[w7 << 2]
            w19 = w24 & 0xFF
            w9 = x9.w[w19 << 2]
            w13 = w14 ^ w13
            w13 = w13 ^ w15
            w10 = w13 ^ w10

            w13, w14 = Mem.mem_read(x8 + 0x24, 2)# *(x8 + 0x24)
            w8 = Mem.mem_read(x8 + 0x2c)# *(x8 + 0x2c)
            w10 = w10 ^ w17
            w15 = w10 >> 0x18

            x17 = Mem.create(0x10)
            x17[0] = w15
            w15 = w10 >> 0x10
            x17[1] = w15
            w15 = w10 >> 8
            x17[2] = w15

            w15 = w1 ^ w0
            w15 = w15 ^ w2
            w15 = w15 ^ w6
            w13 = w15 ^ w13
            w15 = w4 ^ w3
            w15 = w15 ^ w5
            w15 = w15 ^ w7
            w14 = w15 ^ w14
            x17[3] = w10
            w10 = w13 >> 0x18
            x17[4] = w10
            w10 = w12 ^ w11
            w11 = w13 > 0x10
            x17[5] = w11
            w11 = w13 >> 8
            x17[6] = w11
            x17[7] = w13
            w11 = w14 >> 0x18
            x17[8] = w11
            w10 = w10 ^ w16
            w11 = w14 >> 0x10
            x17[9] = w11
            w9 = w10 ^ w9
            w10 = w14 >> 8
            x17[0xa] = w10
            x17[0xb] = w14

            w8 = w9 ^ w8
            w9 = w8 >> 0x18
            x17[0xc] = w9
            w9 = w8 >> 0x10
            x17[0xd] = w9
            w9 = w8 >> 8
            x17[0xe] = w9
            x17[0xf] = w8
            return x17

        # lldb_mem_0x10cf1acc8.txt $x25
        # x10 是个固定值
        x17 = x25 # 实际上是一样的
        w2 = x25.w[w26 << 2]
        w26 = InstHelper.ubfx(w22, 0x10, 8)
        x10 = x17 + 0x400
        w0 = x10.w[w26 << 2]
        w26 = InstHelper.ubfx(w24, 8, 8)
        w26 = x30.w[w26 << 2]
        w27 = w25 & 0xFF
        w27 = x8.w[w27 << 2]
        w0 = w0 ^ w2
        w0 = w0 ^ w26
        w0 = w0 ^ w27

        w2, w26 = Mem.mem_read(x12 + 8, 2)
        w27 = w0 ^ w2
        w0 = w22 >> 0x18
        w0 = x17.w[w0 << 2]
        w2 = InstHelper.ubfx(w24, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w0 = w2 ^ w0
        w2 = InstHelper.ubfx(w25, 8, 8)
        w2 = x30.w[w2 << 2]
        w0 = w0 ^ w2
        w2 = w6 & 0xFF
        w2 = x8.w[w2 << 2]
        w0 = w0 ^ w2
        w26 = w0 ^ w26
        w0 = w24 >> 0x18
        w0 = x17.w[w0 << 2]
        w2 = InstHelper.ubfx(w25, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w0 = w2 ^ w0
        w2 = InstHelper.ubfx(w6, 8, 8)
        w2 = x30.w[w2 << 2]
        w0 = w0 ^ w2
        w2 = w22 & 0xFF
        w2 = x8.w[w2 << 2]
        w0 = w0 ^ w2

        w2, w13 = Mem.mem_read(x12 + 0x10, 2)
        w28 = w0 ^ w2
        w0 = w25 >> 0x18
        w17 = x17.w[w0 << 2]
        w0 = InstHelper.ubfx(w6, 0x10, 8)
        w10 = x10.w[w0 << 2]
        w10 = w10 ^ w17
        w17 = InstHelper.ubfx(w22, 8, 8)
        w17 = x30.w[w17 << 2]
        w10 = w10 ^ w17
        w17 = w24 & 0xFF
        w8 = x8.w[w17 << 2]
        w8 = w10 ^ w8
        w24 = w8 ^ w13
        w11 += 1
        x12 += 0x20


if __name__ == '__main__':
    import os
    lldb_file_path = "simple/dy/lldb_result"
    x0_path = os.path.join(lldb_file_path, "lldb_mem_0x16f7ee7c0.txt")
    x1_path = os.path.join(lldb_file_path, "lldb_mem_0x16f7ee9a4.txt")
    x25_f_path = os.path.join(lldb_file_path, "lldb_mem_0x10985acc8.txt")
    x0, x1 = Mem.read_file(x0_path), Mem.read_file(x1_path)
    value = sub_100369264(x0, x1, x1, x25_f_path)
    print(value, Mem.merge_arr_to_int(value.to_list()))
