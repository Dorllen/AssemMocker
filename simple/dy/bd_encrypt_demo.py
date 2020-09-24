from core.sisc_core.mocker import *
from util.sisc_core.inst_helper import InstHelper as IH


def sub_100369894(x0:Mem, x1:Mem):
    return x0 ^ x1

'''
  * frame #0: 0x0000000102455878 XXXXX`___lldb_unnamed_symbol19941$$XXXXX + 1556
    frame #1: 0x0000000102455dc8 XXXXX`___lldb_unnamed_symbol19945$$XXXXX + 248
    frame #2: 0x0000000102455c34 XXXXX`___lldb_unnamed_symbol19944$$XXXXX + 444
    frame #3: 0x000000010245835c XXXXX`___lldb_unnamed_symbol19955$$XXXXX + 564
    frame #4: 0x0000000102454904 XXXXX`___lldb_unnamed_symbol19938$$XXXXX + 96
'''
def sub_100369264(x0:Mem, x1:Mem, x2:Mem, x25_f_path):
    _x0 = x0
    _x1 = x1
    _x2 = x2

    w8, w9, w10, w11 = Mem.mem_read(x1, 4) # *(x1)

    w8, w9, w10, w11 = IH.rev(w8), IH.rev(w9), IH.rev(w10), IH.rev(w11)

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

    w11 = -4 # 1 - 0xa # -9 # 1 - (w8 >> 1) # 1 - 0xa => 0xfffffffc. 可以理解为-9

    w15 = 1
    w14 = 0x1ce
    x12 = x0 + 0x18 # 表示 x0 + 0x18 地址
    # w24, w26, w27, w28 已知
    # x16内容： lldb_mem_0x10c6d9cb0.txt
    # x25 = 0x..d8f8. 且读这块内存至少是 0x2000
    # "lldb_mem_0x10cf1acc8.txt"
    x25 = Mem.read_file(x25_f_path) #
    while True:
        #loc_100369364
        w8 = w27 >> 0x18
        # lldb_mem_0x10c6d9cb0.txt $x16
        # lldb_mem_0x10cf1acc8.txt $x25
        w6 = x25.w[w8 << 2]
        w8 = IH.ubfx(w26, 16, 8)
        # 0x10cf1b0c8 $x10
        x10 = x25 + 0x400 # 0x..dcf8 都是计算x19后的结果，以x25为基准偏移，+偏移0x400
        w22 = x10.w[w8 << 2]
        w8 = IH.ubfx(w28, 0x8, 0x8)

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
        w0 = IH.ubfx(w28, 0x10, 8)
        w0 = x10.w[w0 << 2]
        w2 = IH.ubfx(w24, 8, 8)
        w2 = x30.w[w2 << 2]
        w17 = w0 ^ w17
        w17 = w17 ^ w2
        w0 = w27 & 0xFF
        w0 = x8.w[w0 << 2]
        w17 = w17 ^ w0
        w0 = w28 >> 0x18
        w0 = x25.w[w0 << 2]
        w2 = IH.ubfx(w24, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w22 = w17 ^ w22
        w17 = w2 ^ w0
        w0 = IH.ubfx(w27, 8, 8)
        w0 = x30.w[w0 << 2]
        w17 = w17 ^ w0
        w0 = w26 & 0xFF
        w0 = x8.w[w0 << 2]
        w2 = w24 >> 0x18
        w2 = x25.w[w2 << 2]
        w17 = w17 ^ w0
        w0 = IH.ubfx(w27, 0x10, 8)
        w10 = x10.w[w0 << 2]

        w0, w25 = Mem.mem_read(x12, 2)
        w24 = w17 ^ w0
        w10 = w10 ^ w2
        w17 = IH.ubfx(w26, 8, 8)
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
            w14 = IH.ubfx(w22, 0x10, 8)
            x12 = x11 + 0x400
            w14 = x12.w[w14 << 2]
            w15 = IH.ubfx(w24, 8, 8)

            x16 = x12 + 0x400
            w15 = x16.w[w15 << 2]

            w17 = x17.w[sp_0xa0_0x90 << 2]
            w0 = w22 >> 0x18
            w0 = x11.w[w0 << 2]
            w1 = IH.ubfx(w24, 0x10, 8)
            w1 = x12.w[w1 << 2]
            w2 = IH.ubfx(w25, 8, 8)
            w2 = x16.w[w2 << 2]
            w3 = w24 >> 0x18
            w3 = x11.w[w3 << 2]
            w4 = IH.ubfx(w25, 0x10, 8)
            w4 = x12.w[w4 << 2]
            w5 = IH.ubfx(w6, 8, 8)
            w5 = x16.w[w5 << 2]
            w7 = w25 >> 0x18
            w11 = x11.w[w7 << 2]
            w7 = IH.ubfx(w6, 0x10, 8)
            w12 = x12.w[w7 << 2]
            w7 = IH.ubfx(w22, 8, 8)
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
            w11 = w13 >> 0x10
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
        w26 = IH.ubfx(w22, 0x10, 8)
        x10 = x17 + 0x400
        w0 = x10.w[w26 << 2]
        w26 = IH.ubfx(w24, 8, 8)
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
        w2 = IH.ubfx(w24, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w0 = w2 ^ w0
        w2 = IH.ubfx(w25, 8, 8)
        w2 = x30.w[w2 << 2]
        w0 = w0 ^ w2
        w2 = w6 & 0xFF
        w2 = x8.w[w2 << 2]
        w0 = w0 ^ w2
        w26 = w0 ^ w26
        w0 = w24 >> 0x18
        w0 = x17.w[w0 << 2]
        w2 = IH.ubfx(w25, 0x10, 8)
        w2 = x10.w[w2 << 2]
        w0 = w2 ^ w0
        w2 = IH.ubfx(w6, 8, 8)
        w2 = x30.w[w2 << 2]
        w0 = w0 ^ w2
        w2 = w22 & 0xFF
        w2 = x8.w[w2 << 2]
        w0 = w0 ^ w2

        w2, w13 = Mem.mem_read(x12 + 0x10, 2)
        w28 = w0 ^ w2
        w0 = w25 >> 0x18
        w17 = x17.w[w0 << 2]
        w0 = IH.ubfx(w6, 0x10, 8)
        w10 = x10.w[w0 << 2]
        w10 = w10 ^ w17
        w17 = IH.ubfx(w22, 8, 8)
        w17 = x30.w[w17 << 2]
        w10 = w10 ^ w17
        w17 = w24 & 0xFF
        w8 = x8.w[w17 << 2]
        w8 = w10 ^ w8
        w24 = w8 ^ w13
        w11 += 1
        x12 += 0x20

def sub_100369CD0(x0, x1, x2, x3):
    x19 = x3
    x24 = x2 >> 4
    x22 = x1
    x20 = x0
    x21 = x20 + 0x1E4
    while x24 != 0:
        x1 = sub_100369894(x21, x22)
        x0 = sub_100369264(x0, x1, x1, x25_f_path)
        x19[:len(x0)] = x0
        x19 += 0x10
        x24 -= 1
        x22 += 0x10

def sub_100369A78(x0, x1, x2, x3, x4, x5, x6):
    x19 = x6
    x20 = x5
    x21 = x4
    x22 = x3
    x23 = x2
    x0 = Mem.create(0x10)
    return sub_100369CD0(x0, x22, x21, x20)


if __name__ == '__main__':
    import os
    lldb_file_path = "simple/dy/lldb_result"
    # x0_path = os.path.join(lldb_file_path, "lldb_mem_0x16f7ee7c0.txt")
    # x1_path = os.path.join(lldb_file_path, "lldb_mem_0x16f7ee9a4.txt")
    # x0, x1 = Mem.read_file(x0_path), Mem.read_file(x1_path)
    x0_text = '''
0x16eb467c0: ba a2 70 4f ea 6b a6 fc 97 22 62 a6 68 73 0b d5  ��pO�k��."b�hs.�
0x16eb467d0: b9 e7 ff 65 53 8c 59 99 c4 ae 3b 3f ac dd 30 ea  ���eS.Y.Į;?��0�
0x16eb467e0: 3e 76 3e 63 6d fa 67 fa a9 54 5c c5 05 89 6c 2f  >v>cm�g�T\�..l/
0x16eb467f0: 2b 1d 99 37 46 e7 fe cd ef b3 a2 08 ea 3a ce 27  +..7F���ﳢ.�:�'
0x16eb46800: e7 9a 19 b4 a1 7d e7 79 4e ce 45 71 a4 f4 8b 56  �..��}�yN�Eq��.V
0x16eb46810: 56 d3 a6 99 f7 ae 41 e0 b9 60 04 91 1d 94 8f c7  VӦ.�A�`.....�
0x16eb46820: 90 77 84 ca 67 d9 c5 2a de b9 c1 bb c3 2d 4e 7c  .w.�g��*޹���-N|
0x16eb46830: 80 59 5c a5 e7 80 99 8f 39 39 58 34 fa 14 16 48  .Y\��...99X4�..H
0x16eb46840: d2 74 a6 62 35 f4 3f ed 0c cd 67 d9 f6 d9 71 91  �t�b5�?�.�g���q.
0x16eb46850: 53 36 93 da 66 c2 ac 37 6a 0f cb ee 9c d6 ba 7f  S6.�f¬7j.��.ֺ.
0x16eb46860: 81 e8 65 18 e7 2a c9 2f 8d 25 02 c1 11 f3 b8 be  .�e.�*�/.%.�.�
0x16eb46870: 9d 81 69 c5 1c 8f d2 c6 fd bf bb 02 e3 48 97 82  ..i�..���.�H..
0x16eb46880: 17 27 c6 c0 77 35 14 a3 cc 78 f8 bc 88 6c e5 ce  .'��w5.��x�.l��
0x16eb46890: d2 51 b3 dd c5 f4 06 f6 2a 71 86 97 e2 a7 88 07  �Q����.�*q..�..
0x16eb468a0: d0 78 b2 9e 6d de eb 4c 0f 60 e1 0d cd 45 32 ab  �x�.m��L.`�.�E2�
0x16eb468b0: 81 e8 65 18 e7 2a c9 2f 8d 25 02 c1 11 f3 b8 be  .�e.�*�/.%.�.�
'''
    x0 = Mem.read_text(x0_text)

    x1_text = '''
0x16eb469a4: 35 51 d6 43 ed de 11 ea 5b 90 a3 72 5a 0b 22 db  5Q�C��.�[.�rZ."�
'''
    x1 = Mem.read_text(x1_text)
    x1_v0_text = '''
0x129e995d0: 1f 8b 08 00 00 00 00 00 00 13 6d 53 4f 6f d3 30  ..........mSOo�0
    '''
    x1_v0 = Mem.read_text(x1_v0_text)
    x1 = sub_100369894(x1, x1_v0)
    print("sub_100369894:", Mem.merge_arr_to_int(x1.to_list()))
    x25_f_path = os.path.join(lldb_file_path, "lldb_mem_0x10985acc8.txt")
    # 总结：x25是固定内容
    # x25 = Mem.read_file(os.path.join(lldb_file_path, "lldb_mem_0x10cf1acc8.txt"))
    # x25_ = Mem.read_file(x25_f_path)
    # lx25 = x25.to_list()
    # lx25_ = x25_.to_list()
    # print(lx25)
    # print(lx25_)
    # lx25len = min(len(lx25), len(lx25_))
    # print(lx25_[:lx25len] == lx25[:lx25len])

    # x0至少177长度
    value = sub_100369264(x0, x1, x1, x25_f_path) # 得到 symbol19944 br x8的结果di
    vv = Mem.merge_arr_to_int(value.to_list())
    # print(value)
    print("sub_100369264:", vv)

    r_text = '''
0x16eb469a4: 73 05 de 30 46 65 c0 a2 6d 76 1e 6e 42 a7 5f e0  s.�0Fe��mv.nB�_�
'''
    rr = Mem.merge_arr_to_int(Mem.read_text(r_text).to_list()[:16])
    print(rr, vv == rr)

