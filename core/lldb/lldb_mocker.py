import re
import logging
from util.lldb.lldb_misc_util import LLDBParser as Parser

from core.assem_types import Int as MockerInt
from core.assem_types import Register as MockerRegister
from core.assem_types import List as MockerList
from core.assem_types import Position as MockerPosition
from core.assem_types import BreakPoint as MockerBreakPoint

from core.mocker import *
from core.lldb import *


class Int(MockerInt):
    def __add__(self, other):
        if SymbolFactory.is_symbol(other):
            if not SymbolFactory.is_rw(other):
                raise ValueError("不支持此种Symbol类型")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__add__(other)) # 去掉Int.MASK 掩码. 如Adds需要根据判断的

    def __sub__(self, other):
        if SymbolFactory.is_symbol(other):
            if not SymbolFactory.is_rw(other):
                raise ValueError("不支持此种Symbol类型")
        elif isinstance(other, Register):
            other = other.g_value()
        # value = self & INT_Mask
        # return Int(value - other) # 尝试用无符号去做操作。已验证：-1 - 1 == -2 情况
        return Int(super().__sub__(other))

    def __xor__(self, other):
        if SymbolFactory.is_symbol(other):
            raise ValueError("此中计算方式暂时拒绝[待观察]")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__xor__(other))

    def __rshift__(self, other):
        if SymbolFactory.is_symbol(other):
            raise ValueError("此中计算方式暂时拒绝[待观察]")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__rshift__(other))

    def __lshift__(self, other):
        if SymbolFactory.is_symbol(other):
            raise ValueError("此中计算方式暂时拒绝[待观察]")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__lshift__(other))

    def __and__(self, other):
        if SymbolFactory.is_symbol(other):
            raise ValueError("此中计算方式暂时拒绝[待观察]")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__and__(other))

    def __or__(self, other):
        if SymbolFactory.is_symbol(other):
            raise ValueError("此中计算方式暂时拒绝[待观察]")
        elif isinstance(other, Register):
            other = other.g_value()
        return Int(super().__or__(other))

    def to_r(self, r_name: str): # todo: 不建议用！！！
        # 模拟to register
        return RegisterFactory.find_r(r_name).s_value(self)

    @classmethod
    def get_mask(cls, value):
        # 0x20 -> 32位 -> 0xFF_FF_FF_FF
        assert isinstance(value, int) and value <= ARM_DEFAULT_MASK_SIZE, f"value:{value}"
        return ARM_DEFAULT_MASK >> (ARM_DEFAULT_MASK_SIZE - value)

    @classmethod
    def get_bits_size(cls, value):
        # 必须是0xFF格式
        value = value & ARM_DEFAULT_MASK
        tmp_a = 0
        tmp_b = 1
        while True:
            if tmp_b << tmp_a >= value:
                return tmp_a
            else:
                tmp_a += 1


class List(MockerList):
    def __xor__(self, other):
        assert isinstance(other, list)

        _temp_list = []
        for i, value in enumerate(other):
            assert not isinstance(value, Symbol), "不支持Symbol操作[待观察]"
            _temp_list.append(self[i] ^ value)

        return List(_temp_list)



# 应用寄存器是操作层面是否符号的。Mem层/Stack层是存储层 是无符号的
class Register(MockerRegister):
    def __init__(self, name, value:int=Int(0), alias=None, latin=None, mode=None):
        assert isinstance(value, int), "非值类型"
        self.name = name # 正常应该是x模式。可切换
        self.alias = alias # 比如x29 = FP
        self.value = value
        self.mode = RegisterFactory.check_mode(mode or RegisterFactory.DEFAULT_MODE)
        self.latin = RegisterFactory.DEFAULT_LATIN

        if latin and latin in (LATIN_BIG, LATIN_LITTLE):
            self.latin = latin

        if alias and alias not in RegisterFactory.GLOBAL_register_mapping:
            RegisterFactory.GLOBAL_register_mapping[alias] = name

    @property
    def x(self): # 切换模式
        self.mode = REGISTER_MODE_X
        return self

    @property
    def w(self): # 切换模式
        self.mode = REGISTER_MODE_W
        return self

    @property
    def q(self): # 切换模式
        self.mode = REGISTER_MODE_Q
        return self

    def toX(self):
        # 只返回x内容
        assert not isinstance(self.value, PtrSymbol) # 不建议
        return Int.toX(self.value)

    def toW(self):
        assert not isinstance(self.value, PtrSymbol)
        return Int.toW(self.value)

    def toQ(self):
        assert not isinstance(self.value, PtrSymbol)
        return Int.toQ(self.value)

    @x.setter
    def x(self, value): # 直接赋值方法
        if isinstance(value, Register):
            self.s_value(value.g_value())
        elif isinstance(value, int):
            if isinstance(value, PtrSymbol): # x是默认的，所以可支持
                self.s_value(value)
            else:
                self.s_value(value)
        else:
            raise NotImplemented

    @w.setter
    def w(self, value):
        if isinstance(value, Register):
            self.s_value(value.g_value())
        elif isinstance(value, int):
            if isinstance(value, PtrSymbol):
                raise ValueError("不支持32位修改地址")
            self.s_value(value)
        else:
            raise NotImplemented

    @q.setter
    def q(self, value):
        if isinstance(value, Register):
            self.s_value(value.g_value())
        elif isinstance(value, int):
            if isinstance(value, PtrSymbol):
                raise ValueError("不支持32位修改地址")
            self.s_value(value)
        else:
            raise NotImplemented

    def g_value(self): # get value方法。正常获取
        if isinstance(self.value, PtrSymbol):
            return self.value
        elif self.mode == REGISTER_MODE_X:
            return Int.toX(self.value)
        elif self.mode == REGISTER_MODE_W:
            return Int.toW(self.value)
        elif self.mode in [REGISTER_MODE_Q, REGISTER_MODE_V]:
            return Int.toQ(self.value)
        raise NotImplemented

    def g_uvalue(self): # get value方法。正常获取. 可能会出现：'0xffffffffcbbdf430' 实际是：0xcbbdf430
        if isinstance(self.value, PtrSymbol):
            return self.value
        elif self.mode == REGISTER_MODE_X:
            return Int.toUX(self.value)
        elif self.mode == REGISTER_MODE_W:
            return Int.toUW(self.value)
        elif self.mode in [REGISTER_MODE_Q, REGISTER_MODE_V]:
            return Int.toQ(self.value)
        raise NotImplemented

    def s_value(self, value):  #set value。正常赋值
        # 直接赋值内容
        assert isinstance(value, int), "必须整型"
        if self.mode in [REGISTER_MODE_Q, REGISTER_MODE_V]:
            assert not isinstance(value, PtrSymbol), "不能为Ptrl类型"
            value = Int.toQ(value)
        else:
            # 需要做是否为负数
            if not isinstance(value, PtrSymbol):
                # 对于PtrSymbol是属于指针类型 直接赋值
                if self.mode == REGISTER_MODE_W:
                    value = Int.toW(value)
                else:
                    value = Int.toX(value)
        self.value = value
        return self

    def to_r(self, r:str): #todo: 待思考是否移除
        if isinstance(r, Register):
            mode = r.mode
            r = mode + r.name[1:]
        return RegisterFactory.find_r(r).s_value(self.g_value())

    @property
    def ptr(self):
        # 如果是指针访问. 一般来说都是name="tmp"的寄存器读取.
        # 尽管是PtrSymbol都可以强转
        # self.s_value(PtrSymbol(self.g_value())) # 在这里将普通整型变成指针
        # return self.value.ptr
        return PtrSymbol(self.g_uvalue())

    @ptr.setter
    def ptr(self, value):
        self.ptr_v(value)

    def ptr_v(self, value, mode=None):
        if isinstance(value, Register):
            _mode = value.mode
            value = value.g_uvalue()
        else:
            _mode = ARM_DEFAULT_MEMORY_MODE
        mode = mode if mode else _mode
        assert isinstance(self.value, PtrSymbol), "非指针类型" # 此处可以 PtrSymbol(self.value)
        self.value.ptr_v(value, self.latin, mode)

    def __add__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__add__(other.g_value())
        elif isinstance(other, int): # 支持普通int类型
            value = self.g_value().__add__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __and__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__and__(other.g_value())
        elif isinstance(other, int): # 支持普通int类型
            value = self.g_value().__and__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __or__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__or__(other.g_value())
        elif isinstance(other, int): # 支持普通int类型
            value = self.g_value().__or__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __sub__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__sub__(other.g_value())
        elif isinstance(other, int):
            value = self.g_value().__sub__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __xor__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__xor__(other.g_value())
        elif isinstance(other, int):
            value = self.g_value().__xor__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __rshift__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__rshift__(other.g_value())
        elif isinstance(other, int):
            value = self.g_value().__rshift__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def __lshift__(self, other):
        if isinstance(other, Register):
            value = self.g_value().__lshift__(other.g_value())
        elif isinstance(other, int):
            value = self.g_value().__lshift__(other)
        else:
            raise ValueError(f"不支持类型操作：{other}")
        return Register(REGISTER_TMP, value)

    def to_hex(self):
        return hex(self.g_value())

    def to_list(self):
        return SymbolFactory.convert_int_2_list(self.g_value(), MODES_MAPPING[self.mode], self.latin)

    def __repr__(self):
        return f"<{self.name}|{self.alias or ''}|{hex(self.value)}>"


class PCRegister(Register):
    def __init__(self, value=Int(0)):
        super().__init__("x32", value, REGISTER_PC)

    @staticmethod
    def init_pc(address):
        pc = PCRegister(address)
        return pc

    def next_pc(self, next_address=None):
        if next_address is None:
            logging.warning("[Warning]Don't be here")
            self.value += FUNCTION_Byte_Length
        else:
            self.s_value(next_address)
        return self

    def update_pc(self, value):
        if isinstance(value, Register):
            self.value = value.g_uvalue()
        elif isinstance(value, int):
            self.value = value
        else:
            raise ValueError(f"不支持类型更新PC寄存器: {value}")
        return self

    def pc_address(self):
        return self.value


# 只取最高4位
class CPSRRegister(Register):
    def __init__(self, value=0):
        super().__init__("x33", value, REGISTER_CPSR)
        self._N = 0
        self._Z = 0
        self._C = 0
        self._V = 0
        self.fix()

    def fix(self):
        value = self.value >> 32 - 4
        self._N = value >> 3
        self._Z = (value & 0b0100) >> 2
        self._C = (value & 0b0010) >> 1
        self._V = value & 0b0001
        return self

    @property
    def N(self):
        return self._N

    @property
    def Z(self):
        return self._Z

    @property
    def C(self):
        return self._C

    @property
    def V(self):
        return self._V

    @N.setter
    def N(self, value):
        assert value in [0, 1]
        self._N = value
        self._to_value()

    @Z.setter
    def Z(self, value):
        assert value in [0, 1]
        self._Z = value
        self._to_value()

    @C.setter
    def C(self, value):
        assert value in [0, 1]
        self._C = value
        self._to_value()

    @V.setter
    def V(self, value):
        assert value in [0, 1]
        self._V = value
        self._to_value()

    def s_value(self, value):
        super().s_value(value)
        self.fix()

    def _to_value(self):
        self.value = (self._N << 3 | self._Z << 2 | self._C << 1 | self._V) << 28

    def toNZCV(self):
        return self.N << 3 | self.Z << 2 | self.C << 1 | self.V

    @property
    def eq(self):
        return self.Z == 1

    @property
    def ne(self):
        return not self.eq

    @property
    def cs(self):
        return not self.cc

    @property
    def hs(self):
        return self.cs

    @property
    def cc(self):
        return self.C == 0

    @property
    def lo(self):
        return self.cc

    @property
    def mi(self):
        return self.N == 1

    @property
    def hi(self):
        return self.C == 1 and self.Z == 0

    @property
    def ls(self):
        return self.C == 0 or self.Z == 1

    @property
    def ge(self):
        return self.N == self.V

    @property
    def lt(self):
        return self.N != self.V

    @property
    def gt(self):
        return self.Z == 0 and self.N == self.V

    @property
    def le(self):
        return self.Z == 1 or self.N != self.V

    @property
    def all(self):
        return True


class LRRegister(Register):
    def __init__(self, value=Int(0)):
        super().__init__("x30", value, REGISTER_LR)


class RegisterFactory(object):
    GLOBAL_registers = {}
    GLOBAL_register_mapping = {} # 存放部分以cpsr、fp 的别名

    MODES = {REGISTER_MODE_X, REGISTER_MODE_W, REGISTER_MODE_Q}

    DEFAULT_MODE = REGISTER_MODE_X  # 寄存器都默认x
    DEFAULT_LATIN = ARM_DEFAULT_LATIN # 默认小头模式

    GLOBAL_register_mode_mapping = {
        REGISTER_MODE_V: REGISTER_MODE_Q,
        REGISTER_MODE_Q: REGISTER_MODE_Q,
        REGISTER_MODE_W: REGISTER_MODE_X,
        REGISTER_MODE_X: REGISTER_MODE_X,
    }

    REGISTER_TMP = "tmp"

    @staticmethod
    def check_mode(mode):
        assert mode, "模式不为空"
        mode = mode.lower()
        if mode in RegisterFactory.MODES:
            return mode
        raise ValueError(f"不支持模式: {mode}")

    @classmethod
    def register(cls, reg):
        assert reg, "寄存器不能为空"
        assert isinstance(reg, Register), "注册寄存器失败"
        assert reg.name not in cls.GLOBAL_registers, "寄存器已存在"
        mode = cls.GLOBAL_register_mode_mapping[reg.name[0]]
        cls.GLOBAL_registers[mode + reg.name[1:]] = reg
        return cls

    @classmethod
    def guess_is_register(cls, value):
        value = value.lower()
        if value in RegisterFactory.GLOBAL_register_mapping:
            value = RegisterFactory.GLOBAL_register_mapping[value]
        mode = value[0]
        if mode in RegisterFactory.MODES:
            return mode

    @classmethod
    def c(cls, value):
        return cls.guess_is_register(value)

    @classmethod
    def find_r(cls, r_name:str) -> Register:
        assert r_name, "register name不能为空"
        # value 可以是x0, w0
        value = r_name.lower()
        if value in RegisterFactory.GLOBAL_register_mapping:
            value = RegisterFactory.GLOBAL_register_mapping[value]
        mode = value[0]
        _mode = cls.GLOBAL_register_mode_mapping[mode]
        register = cls.GLOBAL_registers.get(_mode + value[1:])
        if not register:
            return
        return getattr(register, mode)

    @classmethod
    def r(cls, name:str) -> Register: # 别名
        return cls.find_r(name)

    @staticmethod
    def is_func(r):
        if isinstance(r, FuncSymbol):
            return True
        return Memory.is_func(r)

    @staticmethod
    def is_ptr(r):
        if isinstance(r, Register):
            r = r.g_value()
        if isinstance(r, PtrSymbol):
            return True
        elif isinstance(r, Symbol):
            return Memory.is_ptr(r)
        elif isinstance(r, int):
            return Memory.is_exists(r)
        else:
            raise ValueError("不支持类型值")

    @classmethod
    def dumps(cls):
        text = ''''''
        for k, reg in cls.GLOBAL_registers.items():
            if reg.alias:
                name = reg.alias
            else:
                name = reg.name
            text += f"{name:4s}: {hex(reg.g_value())}\n"

        logging.info("Dump Registers ->\n%s", text)
        return text


R = RegisterFactory # 别名


# Symbol是用在栈上的
class Symbol(Int):
    # 存放函数、的引用
    def __new__(cls, value:int, body=None):
        return super().__new__(cls, value)

    def __init__(self, value, body=None):
        super().__init__()
        self.value = value
        self.body = body # 函数，或者栈区域。如果是栈区域，则value存放的是tag int值(后发现用byte表示一个对象是比较可行的方式)

    def __repr__(self):
        return "<%s>" % self.__class__


class NilSymbol(Symbol): # 空占位符
    def __repr__(self):
        return "<Nil>"

    def __str__(self):
        return repr(self)


class NtSymbol(Symbol): # 表示这个地址根据上下地址才能判断
    def __repr__(self):
        return "<Nt>"
    def __str__(self):
        return repr(self)


class PtrSymbol(Symbol): # 指针占位符号. 指针直接存储
    @property
    def ptr(self):
        # LDR x23, [x30, #0x30] -> x23 = (x30 + 0x30).ptr
        return Memory.find(self, RegisterFactory.DEFAULT_LATIN)

    @property
    def ptrw(self):
        return Memory.find(self, RegisterFactory.DEFAULT_LATIN, REGISTER_MODE_W)

    @property
    def ptrq(self):
        return Memory.find(self, RegisterFactory.DEFAULT_LATIN, REGISTER_MODE_Q)

    @property
    def ptrb(self):
        return Memory.find(self, RegisterFactory.DEFAULT_LATIN, REGISTER_MODE_BYTE)

    def ptr_v(self, value, latin=None, mode=None):
        # STR x29, [sp, #0x30] -> (sp + 0x30).ptr = x29
        if isinstance(value, Register):
            mode = value.mode
            latin = value.latin
            value = value.g_uvalue()
        else:
            if mode is None:
                mode = RegisterFactory.DEFAULT_MODE

            if latin is None:
                latin = RegisterFactory.DEFAULT_LATIN

        Memory.update(self, value, latin, mode)



    # @classmethod
    # def to_ptr(cls, address):
    #     return Memory.find(address, RegisterFactory.DEFAULT_LATIN)

    # @property
    # def ptrv(self):
    #     # 建议用这个取指针的值。 [x30, #0x30] -> (x30 + 0x30).ptr ; mem read/8x [x30, #0x30] == (x30 + 0x30).ptr.ptrv
    #     return Memory.find(self, RegisterFactory.DEFAULT_LATIN)

    # 指针类型暂时只做 +、-方面的
    def __add__(self, other):
        return PtrSymbol(super().__add__(other))

    def __sub__(self, other):
        return PtrSymbol(super().__sub__(other))


class FuncSymbol(Symbol): # 函数占位符号
    @property
    def ptr(self):
        raise NotImplemented()


class SymbolFactory(object):
    NIL = NilSymbol(0)
    Nt = NtSymbol(0)

    RW_Symbols = [PtrSymbol, FuncSymbol]
    NULL_Symbols = [NilSymbol, NtSymbol]

    @staticmethod
    def is_null(symbol):
        assert isinstance(symbol, Symbol), "非Symbol类型"
        for s in SymbolFactory.NULL_Symbols:
            if isinstance(symbol, s):
                return True
        return False

    @staticmethod
    def is_rw(symbol):
        assert isinstance(symbol, Symbol), "非Symbol类型"
        for s in SymbolFactory.RW_Symbols:
            if isinstance(symbol, s):
                return True
        return False

    @staticmethod
    def is_symbol(symbol):
        return isinstance(symbol, Symbol)

    @staticmethod
    def convert_int_2_list(int_value: int, size, reverse):
        # 888 -> [120, 3, 0, 0, 0, 0, 0, 0]
        assert not isinstance(int_value, PtrSymbol), "暂不支持PtrSymbol"
        assert int_value <= (1 << size * 8) - 1, "值超限"
        # hex_value = hex(int_value).replace("0x", "")
        # padding_value = "".join(["0" for i in range(len(hex_value), size * 2)]) + hex_value# 16进制是两个字符
        # padding_list = [int("0x" + padding_value[i:i+2], 16) for i in range(0, len(padding_value), 2)]
        # if reverse:
        #     padding_list.reverse()
        # return padding_list
        byte_value = int_value.to_bytes(size, "little" if reverse == 1 else "big")
        return [b for b in byte_value]

    @staticmethod
    def convert_int_2_list_raw(int_value: int, size, reverse):
        # 888 -> [120, 3, 0, 0, 0, 0, 0, 0]
        assert not isinstance(int_value, PtrSymbol), "暂不支持PtrSymbol"
        assert int_value <= (1 << size * 8) - 1, "值超限"
        hex_value = hex(int_value).replace("0x", "")
        padding_value = "".join(["0" for i in range(len(hex_value), size * 2)]) + hex_value# 16进制是两个字符
        padding_list = [int("0x" + padding_value[i:i+2], 16) for i in range(0, len(padding_value), 2)]
        if reverse:
            padding_list.reverse()
        return padding_list

    @staticmethod
    def convert_list_2_int(arr, reverse):
        # [120, 3, 0, 0, 0, 0, 0, 0] -> 888
        b = bytearray(arr)
        return int.from_bytes(b, "little" if reverse == 1 else "big")

    @staticmethod
    def convert_list_2_int_raw(arr, reverse):
        # [120, 3, 0, 0, 0, 0, 0, 0] -> 888
        if reverse:
            arr.reverse()
        a_str = "0x"
        for i in arr:
            if i <= 0xF:
                a_str += "0" + hex(i).replace("0x", "")
            else:
                a_str += hex(i).replace("0x", "")
        value = int(a_str, 16)
        return value


class StackFrame(object):

    SF_Swell_Min_Size = 0xFF_FF

    # 部分栈
    def __init__(self, stack:list, address, index=0, pre_sf=None, next_sf=None):
        self.stack = stack # 具体内容. 正常情况下：一个plot表示一个byte，除了PtrSymbol这种不是一个byte
        self.address = address # 下标对应的地址
        self.index = index # 下标
        self.next_sf:StackFrame = next_sf
        self.pre_sf:StackFrame = pre_sf

    def length(self):
        # 总长度
        return len(self.stack)

    def addr(self):
        # [) 开 闭区间
        return self.address - self.index, self.address + self.length() - self.index

    def size(self):
        # 空闲size. 一个值是64位大小
        s = 0
        for i, a in enumerate(self.stack):
            if isinstance(a, NilSymbol): # NilSymbol表示初始占位
                s += 1
            elif not SymbolFactory.is_symbol(a) and isinstance(a, int) and a == 0x0: # 接受非Symbol 且 整型，且为0
                s += 1
        return s

    def read(self, address, reverse, mode):
        self._check(address)
        assert mode in MODES_MAPPING.keys(), "无法执行的操作模型"
        size = MODES_MAPPING[mode] // Bytes_to_Bits
        index = address - self.address + self.index
        right_index = index + size
        min_addr, max_addr = self.addr()
        if right_index > self.length():
            if self.next_sf:
                next_min_addr, next_max_addr = self.next_sf.addr()
                if next_min_addr - max_addr == 0:
                    tmp_size = self.length() - index
                    tmp_arr = []
                    for i in range(tmp_size):
                        tmp_arr.append(self._read_b(index + i))

                    for j in range(tmp_size, size):
                        tmp_arr.append(self.next_sf._read_b(j - tmp_size))

                    if isinstance(tmp_arr[0], PtrSymbol):
                        return tmp_arr[0]
                    elif isinstance(tmp_arr[-1], PtrSymbol):
                        return tmp_arr[-1]

                    return SymbolFactory.convert_list_2_int(tmp_arr, reverse)

            raise ValueError(f"读取不存在Mem: [{index}, {right_index})")
        elif index < 0:
            assert abs(index) > size, "超限"
            if self.pre_sf:
                pre_min_addr, pre_max_addr = self.pre_sf.addr()
                if pre_max_addr - min_addr == 0:
                    tmp_arr = []
                    for i in range(index, 0):
                        tmp_arr.append(self.pre_sf._read_b(index))

                    for j in range(0, size + index):
                        tmp_arr.append(self._read_b(j))

                    if isinstance(tmp_arr[0], PtrSymbol):
                        return tmp_arr[0]
                    elif isinstance(tmp_arr[-1], PtrSymbol):
                        return tmp_arr[-1]

                    return SymbolFactory.convert_list_2_int(tmp_arr, reverse)

            raise ValueError(f"读取不存在Mem: [{index}, {right_index})")

        result = self.stack[index:right_index]
        # 这里不能判定是否reverse.
        if isinstance(result[0], PtrSymbol):
            return result[0]
        elif isinstance(result[-1], PtrSymbol):
            return result[-1]
        else:
            if size == 1:
                return result[0]
            return SymbolFactory.convert_list_2_int(result, reverse)

    def swell(self, offset):
        length = abs(offset) | StackFrame.SF_Swell_Min_Size
        self._swell(offset > 0, stack=StackFrame.create_stack(length))
        return length

    def _swell(self, po, stack):
        # po 代表正向追加
        if po is True:
            self.stack += stack
        else:
            self.stack = stack + self.stack

    def discard(self, offset):
        # 删除块
        pass

    def write(self, address, value, reverse, mode): # 64位
        self._check(address)
        assert isinstance(value, int), "非整型值"
        assert mode in MODES_MAPPING.keys(), "无法执行的操作模型"
        assert reverse == ARM_DEFAULT_LATIN, "拒绝非全局大小头" # 避免大小头切换问题. 暂全局refused
        size = MODES_MAPPING[mode] // Bytes_to_Bits
        index = address - self.address + self.index
        right_index = index + size
        min_addr, max_addr = self.addr()
        if right_index > self.length():
            # 是否要膨胀. 并且是否访问下一个地址
            if self.next_sf:
                next_min_addr, next_max_addr = self.next_sf.addr()
                if next_min_addr - max_addr == 0:
                    # 说明是连接的
                    tmp_size = self.length() - index
                    tmp_value = StackFrame.value_to_value(value, reverse, size)
                    for i in range(tmp_size):
                        self._write_b(index + i, tmp_value[i])

                    for j in range(tmp_size, size):
                        self.next_sf._write_b(j - tmp_size, tmp_value[tmp_size])
                    return
        elif index < 0:
            assert abs(index) > size, "超限"
            # 是否要反向膨胀。
            if self.pre_sf:
                pre_min_addr, pre_max_addr = self.pre_sf.addr()
                if pre_max_addr - min_addr == 0:
                    # 连接
                    tmp_value = StackFrame.value_to_value(value, reverse, size)
                    for i in range(index, 0):
                        self.pre_sf._write_b(i, tmp_value[i + abs(index)])

                    for j in range(0, size + index):
                        self._write_b(j, tmp_value[j + abs(index)])
                    return

            swell_len = self.swell(index) # -1代表 左侧扩展1
            index = swell_len + index
            right_index = index + size + 1

        if isinstance(value, PtrSymbol):
            self.stack[index:right_index] = StackFrame.value_to_value(value, reverse, size)
        elif isinstance(value, Symbol):
            raise ValueError("Symbol类型[待观察]")
        else:
            if size == 1:
                self._write_b(index, value)
                return
            arr = StackFrame.value_to_value(value, reverse, size)
            self.stack[index:right_index] = arr

    @classmethod
    def value_to_value(cls, value, reverse, size):
        if isinstance(value, PtrSymbol):
            if reverse:
                return (value, *[SymbolFactory.Nt for i in range(size)])
            else:
                return (*[SymbolFactory.Nt for i in range(size)], value)
        elif isinstance(value, Symbol):
            assert 2**(size * Bytes_to_Bits) - 1 >= value, f"值范围不对: {value} size: {size}"
            return (*[value for i in range(size)], )
        else:
            assert 2**(size * Bytes_to_Bits) - 1 >= value, f"值范围不对: {value} size: {size}"
            arr = SymbolFactory.convert_int_2_list(value, size, reverse)
            return (*arr, )

    def _write_b(self, index, b):
        assert 0xFF >= b
        self.stack[index] = b

    def _read_b(self, index):
        b = self.stack[index]
        assert -2**7 < b < 2**7 - 1
        return b

    def cover(self, address, length, obj):
        assert obj and isinstance(obj, list), "只支持List类型"
        assert length and isinstance(length, int), "只支持整型"
        index = address - self.address + self.index
        self.stack[index:index + length + 1] = (*obj, )

    def dump(self, address, length=None):
        # dump address
        pass

    def dumps(self, address, length=None):
        # dump all
        pass

    def _check(self, address):
        assert self.exists(address), f"{address} 不属于当前StackFrame:{self.address} len:{self.length()}"

    def exists(self, address):
        min_addr, max_addr = self.addr()
        return max_addr > address >= min_addr

    @staticmethod
    def create_stack(length):
        return List([SymbolFactory.NIL for i in range(length)])

    def __repr__(self):
        _addr = self.addr()
        return f"SF[{hex(_addr[0]), hex(_addr[1])}]"


class Memory(object):
    GlOBAL_Stack = [] # 存放StackFrame

    GLOBAL_Malloc_Address = MEMORY_MALLOC_ADDRESS_OFFSET

    Stack_Init_Mark = False

    @classmethod
    def init_stack(cls, address, length):
        # 初始化2倍空间，便于扩容
        sf = StackFrame(StackFrame.create_stack(length * 2), address=address, index=length)
        cls.GlOBAL_Stack.append(sf)
        cls.Stack_Init_Mark = True
        return cls

    @classmethod
    def length(cls):
        stack_length = 0
        for sf in cls.GlOBAL_Stack:
            stack_length += sf.length()
        return stack_length

    @classmethod
    def find(cls, address, latin=ARM_DEFAULT_LATIN, mode=ARM_DEFAULT_MEMORY_MODE):
        # 读64位。x模式
        assert cls.Stack_Init_Mark, "未初始化Stack"
        BP.check_anchor(address=address)
        sf = Memory._find_sf(address)
        assert sf, f"未找到地址对应的StackFrame: {hex(address)}"
        return sf.read(address, latin, mode)

    @classmethod
    def update(cls, address, value, latin, mode="x"):
        assert cls.Stack_Init_Mark, "未初始化Stack"
        sf = Memory._find_sf(address)
        assert sf, f"未找到地址对应的StackFrame: {hex(address)}"
        sf.write(address, value, latin, mode)

    @classmethod
    def malloc(cls, size):
        # malloc 申请的内存地址都以 0x8Fxx_xxxx MEMORY_MALLOC_ADDRESS_OFFSET 开头
        sf = StackFrame(List([SymbolFactory.NIL for i in range(size * 2)]), address=cls.GLOBAL_Malloc_Address + size, index=size)
        cls.GLOBAL_Malloc_Address += 2 * size
        return sf

    @classmethod
    def free(cls, address, length):
        return cls.bit(address, length, 0x0)

    @classmethod
    def bit(cls, address, length, value):
        # 赋值
        sf = cls._find_sf(address)
        for offset in range(length):
            sf.write(address + offset, value, RegisterFactory.DEFAULT_LATIN, REGISTER_MODE_BYTE)

    def swell(self, address, size):
        # 膨胀某个地址所在的栈
        raise NotImplemented

    @classmethod
    def persist(cls, obj):
        # 对address进行持久
        raise NotImplemented

    @classmethod
    def memcpy(cls, address, length):
        # length 代表多少个字节
        sf = cls._find_sf(address)
        tmp_cp = []
        for offset in range(length):
            # 如果只是copy的话，小头要变，大头不变
            reverse = RegisterFactory.DEFAULT_LATIN
            # if RegisterFactory.DEFAULT_LATIN == LATIN_LITTLE: # 非Byte读取则需要注意
            #     reverse = 0 # LATIN_BIG # 表示不转换。栈中存啥就是啥
            sf.read(address + offset, reverse, REGISTER_MODE_BYTE)
        raise NotImplemented

    # nt系列代表Nt的特殊定义方法。非基本方法，是拓展方法
    @classmethod
    def nt_free(cls, address, length):
        # 物理删除。收缩空间
        raise NotImplemented

    @classmethod
    def nt_cover(cls, arr, length):
        # 物理覆盖
        raise NotImplemented

    @classmethod
    def is_func(cls, r):
        # todo: 似乎现在非IDA流程控制，不需要判定是否为函数？？？
        raise NotImplemented("不支持函数判定")

    @classmethod
    def _find_sf(cls, address) -> StackFrame:
        assert address, "地址必须存在"
        for sf in cls.GlOBAL_Stack:
            if sf.exists(address):
                return sf

    @classmethod
    def is_exists(cls, address):
        sf = cls._find_sf(address)
        # if sf:
        #     value = sf.g_value(address)
        #     return isinstance(value, NilSymbol)
        # return False
        return sf is not None

    @classmethod
    def is_ptr(cls, r):
        if isinstance(r, NtSymbol): # 此方法待实践
            raise NotImplemented
            # for i in range(1, 4): # 默认最多往前读3个字节，因为4字节
            #     if isinstance(cls.find_b(r - i), NtSymbol):
            #         return False
            # return True
        else:
            return Memory.is_exists(r)

    @classmethod
    def create_new_sf(cls, address, length):
        # 在内存中创建一个新stackframe. stackframe之间不以加入顺序为主，主要以address排序
        # 检查是否可以创建SF
        cls._new_sf_check(address, length, length)
        sf = StackFrame(StackFrame.create_stack(length * 2), address=address, index=length)
        cls.GlOBAL_Stack.append(sf)
        cls._sort()
        return sf

    @classmethod
    def _new_sf_check(cls, address, left_offset, right_offset):
        for tmp_sf in cls.GlOBAL_Stack:
            tmp_sf_addr = tmp_sf.addr()
            if tmp_sf_addr[1] > address >= tmp_sf_addr[0]:
                raise RuntimeError(f"阻止创建已存在的SF: {address}")
            else:
                if tmp_sf_addr[1] + left_offset > address > tmp_sf_addr[1]:
                    raise RuntimeError(f"阻止创建交叉的SF: {address}")
                else:
                    if address < tmp_sf_addr[0] < address + right_offset:
                        raise RuntimeError(f"阻止创建交叉的SF: {address}")

    @classmethod
    def _sort(cls):
        cls.GlOBAL_Stack.sort(key=lambda a:a.addr()[0])
        pre_sf:StackFrame = cls.GlOBAL_Stack[0]
        for sf in cls.GlOBAL_Stack[1:]:
            pre_sf.next_sf = sf
            sf.pre_sf = pre_sf
            pre_sf = sf

    @classmethod
    def load_stack(cls, stack, address, allowed_merge=False):
        if isinstance(stack, list):
            cls._new_sf_check(address, 0, len(stack))
            sf = StackFrame(stack, address=address, index=0)
            cls.GlOBAL_Stack.append(sf)
            cls.Stack_Init_Mark = True

    @classmethod
    def _merge_stack(cls, stack, address):
        # 对于存在冲突进行合并
        pass


class SPRegister(Register):
    def __init__(self, address=Int(0)):
        super().__init__("x31", address, REGISTER_SP)
        # self.address = address # 用于对Ptr栈进行标签描述

    @classmethod
    def init_sp(cls, base_address, length=0x100):
        Memory.init_stack(base_address, length)
        sp = SPRegister(base_address)
        return sp

    @classmethod
    def create_sp(cls, offset): # offset 代表方向
        sp = RegisterFactory.find_r(REGISTER_FP)
        assert isinstance(sp, SPRegister), "非PC寄存器"
        sp.s_value(sp.value + offset)
        assert Memory.is_exists(sp.value), "栈分配出错"
        return sp


class FunctionFactory(object):
    GLOBAL_Function_Mapping = {}

    @classmethod
    def register(cls, ff):
        assert ff and ff.func_address
        assert not cls.find_f(ff.func_address), f"函数已注册或已存在: {ff.func_name}"
        cls.GLOBAL_Function_Mapping[ff.func_address] = ff
        logging.info("register function: %s", ff.func_name)
        return cls

    @classmethod
    def find_f(cls, address):
        assert address, "为空"
        if isinstance(address, str):
            for _f_address, _f in cls.GLOBAL_Function_Mapping.items():
                if address.startswith("func_"):
                    if _f.func_name == address:
                        return _f
                    continue
                elif address.startswith("0x"):
                    if _f.func_address == int(address, 16):
                        return _f
                    continue
                raise ValueError(f"不支持函数搜寻方式：{address}")
        else:
            if isinstance(address, Register):
                address = address.g_uvalue()

            if isinstance(address, int):
                func = cls.GLOBAL_Function_Mapping.get(address)
                if func:
                    return func
                else:
                    for _f_address, _f in cls.GLOBAL_Function_Mapping.items():
                        if _f.func_address <= address < _f.func_end_address:
                            return FunctionFrameWrapper(_f, address)
            else:
                raise ValueError(f"不支持该类型的函数查找方式： {address}")

    @classmethod
    def f(cls, address):
        return cls.find_f(address)

    @classmethod
    def redirect(cls, ff):
        # 重定向到某ff.
        assert isinstance(ff, FunctionFrame)
        if isinstance(ff, FunctionFrameWrapper):
            pass

    @classmethod
    def r(cls, ff):
        return cls.redirect(ff)

    @classmethod
    def create_function(cls, text, func_name=None):
        func_address, func_end_address, codes_raw = Parser.lldb_to_nt(text)
        if func_name is None:
            func_name = "func_%s" % func_address # 此处是0x..
        func = FunctionFrame(func_name, int(func_address, 16), int(func_end_address, 16) + FUNCTION_Byte_Length, text=text)
        codes = {} #
        tmp_code = None
        for code in codes_raw:
            Code.check_code(code)
            code_obj = Code.create_code(*code)
            codes[code_obj.address] = code_obj
            if tmp_code is not None:
                tmp_code.next_code = code_obj
            tmp_code = code_obj
        func.codes = codes
        return func

    @classmethod
    def dumps(cls, ff):
        text = "\n".join(["<+{}> {}".format(c.line_no, repr(c)) for c in ff.codes.values()])
        logging.info("Dumps Function->\n%s", text)
        return text

    @classmethod
    def init_function(cls, ff):
        # 初始化function环境
        pass

    @classmethod
    def run(cls):
        logging.info("nt start...")
        while True:
            pc = RegisterFactory.find_r(REGISTER_PC)
            assert isinstance(pc, PCRegister), "非PC寄存器"
            pc_address = pc.pc_address()
            try:
                ff = cls.find_f(pc_address)
                if not ff:
                    raise RetException
                # assert ff, "不存在当前地址的FF: 0x%x" % pc_address
                if isinstance(ff, FunctionFrameWrapper):
                    raise NtException
                ff()
            except OverflowFuncException:
                raise
            except StopFuncException:
                pass


F = FunctionFactory


class FunctionFrame(object):

    def __init__(self, func_name, func_address, func_end_address, text=None):
        self.func_name = func_name
        self.func_address = func_address # 起始地址
        self.func_end_address = func_end_address # 结束地址 + FUNCTION_Byte_Length
        self.codes:dict = {}
        self.text = text

    def is_dummy(self):
        return not self.codes

    @classmethod
    def is_ret(cls, code):
        return code.is_ret()

    @classmethod
    def is_redirect(cls, code):
        return code.is_b()

    def find_code(self, address):
        assert self.func_end_address > address >= self.func_address >= 0, f"指令超出函数: {self.func_address} -> {address}"
        return self.codes[address]

    def find_op_code(self, address):
        if self.func_end_address > address >= self.func_address:
            return self.codes[address]
        raise OverflowFuncException

    def __call__(self, *args, **kwargs):
        while True:
            pc = RegisterFactory.find_r(REGISTER_PC)
            assert isinstance(pc, PCRegister), "非PC寄存器"
            pc_address = pc.pc_address()
            func_code = self.find_op_code(pc_address)
            logging.info(f"execute: <+{func_code.line_no}> {func_code}")
            BP.check_anchor(op_code=repr(func_code), line_no=func_code.line_no)
            func_code() # 指令命令... loop
            if self.is_ret(func_code):
                pc.update_pc(RegisterFactory.find_r(REGISTER_LR))
                raise StopFuncException
            elif self.is_redirect(func_code) and pc_address != pc.pc_address():
                pass
            else:
                pc.next_pc(func_code.next_address)

    def __str__(self):
        return super().__str__() + f"$${self.func_name, hex(self.func_address)}"


class FunctionFrameWrapper(FunctionFrame):
    # 用于重定向函数执行。其实是函数内部的小片段
    def __init__(self, ff, address):
        super().__init__(ff.func_name, ff.func_address, ff.func_end_address, None)
        self.codes = ff.codes
        self.op_code = self.find_op_code(address)


class Code(object):
    def __init__(self, address, line_no, code, code_type=None, next_code=None):
        self.address = address
        self.line_no = line_no
        self.code = code
        self.code_type = code_type
        self.next_code = next_code

    @classmethod
    def check_code(cls, code_str):
        assert code_str, f"非法指令: {code_str}"

    @staticmethod
    def create_code(address, line_no, inst, args):
        conder = Conder.create_conder(inst, args)
        if conder:
            code_type = conder[0]
            code = conder[1]
        else:
            code_type = CODE_Normal
            code = Opera.create_op(inst, args)
            if not code:
                code = Opera.create_hit_op(inst, args)
        code_obj = Code(int(address, 16), line_no, code, code_type)
        return code_obj

    def is_ret(self):
        return self.code_type == CODE_Ret

    def is_b(self):
        return self.code_type == CODE_Redirect

    def e(self):
        # 表示run
        return eval(self.code)

    @property
    def next_address(self):
        if self.next_code:
            return self.next_code.address

    def __call__(self, *args, **kwargs):
        return self.e()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{self.code}"


class Opera(object):
    OP_Mapping = { # 指令映射
        "wzr": "0x0",
        "xzr": "0x0"
    }

    OP_Alias_Mapping = {
        "and": "and_"
    }

    OP_Ignore_Insts = [".long", "svc", "movi.16b"] # 忽略指令。如：svc #0x80
    OP_Extra_Insts = ["movi.16b"] #
    OP_Normal_Insts = [
        "sub", "stp", "add", "mov", "movk", "ldr", "str", "and_", "stur", "csel", "ldrb", "cmp", "ldrh",
        "lsl", "lsr", "bfi", "sbfx", "neg", "orr", "ldur", "sxtw", "ldursw", "strh", "ubfx", "strb",
        "ror", "mvn", "smulh", "bic", "ldrsw", "ldrsh", "ldp", "cset", "sturb", "ldurb", "tst", "sdiv",
        "asr", "umulh", "mul", "ubfiz", "msub", "cinc", "ldrsb", "bics", "bfxil", "eor", "udiv", "sbfiz",
        "madd", "sxth"

    ] # 正常指令 arg0不参与运算，结果更新arg0

    OP_Ptr_Default_Value = "ptr"

    OP_Ptr_Mapping = {
        # "ldrh": "ptrh",
        # "ldrb": "ptrb"
    }

    OP_Auto_Args_Inst = ["movk"] # 自处理指令

    @staticmethod
    def nop(*args, **kwargs):
        pass

    @staticmethod
    def hit(*args, **kwargs):
        # 用于记录命中情况. placeholder
        pass

    @staticmethod
    def dynamic_handle_ptr_inst(inst):
        if inst.startswith("ldr"):
            # return "ptr" + inst.replace("ldr", "")  # 不这样做了
            return "ptr"

    @staticmethod
    def transform_code_args(args, inst=None):
        # 该方法。可以用Op.xxx(arg0...) 代替，方法内部处理
        # 计算反转的值
        # [sp, #0x30] -> (RegisterFactory.find_r("sp") + 0x30).ptr
        # #0xbe62 -> 0xbe62
        # w8 -> RegisterFactory.find_r("w8")
        # lsl #16 ->  << 16
        args = list(args)
        args.reverse()
        art = []
        tmp_art = ""
        for i, arg in enumerate(args):
            arg = Opera.OP_Mapping.get(arg, arg)
            arg = arg.lower()

            if inst in Opera.OP_Auto_Args_Inst: # movk
                if arg.startswith("#"):
                    arg = arg.replace("#", "")
                else:
                    arg = f'"{arg}"'
                art.append(arg)
                continue

            if "lsl" in arg:
                tmp_art = arg.replace("lsl#", "")
                assert tmp_art
                tmp_art = f" << {tmp_art}"
            elif "lsr" in arg:
                tmp_art = arg.replace("lsr#", "")
                assert tmp_art
                tmp_art = f" >> {tmp_art} & {hex(ARM_DEFAULT_MASK)}" #修正逻辑右移需要处理符号问题
            elif "asr" in arg: # 算数运算符
                tmp_art = arg.replace("asr#", "")
                assert tmp_art
                tmp_art = f" >> {tmp_art}"
            elif "ror" in arg:
                raise ValueError("暂不支持循环右移")
            elif "[" in arg and "]" in arg: # 处理 [sp, #0x30] 或 [sp, #0x20]!
                re_values = re.findall("\\[(.+)\\](.?)", arg)[0] #
                values = re_values[0].split(", ")
                value_tag = re_values[1] # !
                assert not tmp_art and values
                if value_tag:
                    art.append("\"!\"") # 特殊标记
                    for j, value in enumerate(values):
                        if value.startswith("#"):
                            value = value.replace("#", "")
                            values[j] = value
                    art.append(str(values))
                else:
                    for value in values:
                        if value.startswith("#"):
                            value = value.replace("#", "")
                            if value.startswith("-"):
                                tmp_art += f" - {value.replace('-', '')}"
                            else:
                                tmp_art += f" + {value}"
                        else:
                            tmp_art += f'R.r("{value}")'

                    ptr_v = Opera.dynamic_handle_ptr_inst(inst)
                    if not ptr_v:
                        ptr_v = Opera.OP_Ptr_Mapping.get(inst, Opera.OP_Ptr_Default_Value)
                    art.append(f'({tmp_art}).{ptr_v}')
                    tmp_art = ""
            else:
                if arg.startswith("#"):
                    arg = arg.replace("#", "")

                if tmp_art:
                    if ">>" in tmp_art or "<<" in tmp_art: # 对于运算符是需要猜测是否是寄存器
                        if R.guess_is_register(arg):  # 对于某些参数是x或w开头 的寄存器
                            arg = f'R.r("{arg}")'
                        else:
                            arg = f'"{arg}"'
                    else:
                        if not Int.guess_is_int(arg):
                            arg = f'"{arg}"'

                    art.append(f'{arg}{tmp_art}')
                    tmp_art = ""
                else:
                    if not Int.guess_is_int(arg):
                        arg = f'"{arg}"'
                    art.append(arg)
        return art

    @classmethod
    def transform_ignored_code_args(cls, args, inst):
        if inst == "movi":
            pass

    @classmethod
    def check_Op(cls): # 检查Op是否被实现
        for inst in cls.OP_Normal_Insts:
            inst = cls.OP_Alias_Mapping.get(inst, inst)
            assert hasattr(cls, inst), f"不存在Inst: {inst}"

    @staticmethod
    def create_op(inst, args):
        # 有一些指令是更新Condition， 有一些指令更新arg0
        # nt格式：inst, [arg0, arg1...]
        inst = Opera.OP_Alias_Mapping.get(inst, inst)
        if inst in Opera.OP_Normal_Insts:
            art = Opera.transform_code_args(args, inst)
            art.reverse()
            art_text = ", ".join(art)
            assert art_text
            return f"Op.{inst.lower()}({art_text})"
        elif inst in Opera.OP_Extra_Insts:
            return Opera.transform_ignored_code_args(args, inst)
        elif inst in Opera.OP_Ignore_Insts:
            pass
        else:
            raise ValueError(f"不支持指令：{inst} ... {args}")

    @staticmethod
    def create_nop_op(inst, args):
        return f'Op.nop("{inst} {", ".join(args)}")'

    @staticmethod
    def create_hit_op(inst, args):
        return f'Op.hit("{inst} {", ".join(args)}")'

    @staticmethod
    def ldrsw(*args):# ldrsw  x9, [x9, #0x8]
        assert len(args) == 2
        arg0, arg1 = args
        # todo: [待观察]
        R.r(arg0).s_value(arg1)

    @staticmethod
    def ldrsh(*args):
        assert len(args) == 2
        arg0, arg1 = args
        # todo: [待观察]
        R.r(arg0).s_value(arg1 & Int.get_mask(ARM_DEFAULT_MASK_SIZE // 2)) # 取一半

    @staticmethod
    def ldp(*args): # ldp    w9, w0, [sp, #0xf8]
        # todo: [待观察]
        assert len(args) == 3
        arg0, arg1, arg2 = args
        assert isinstance(arg2, PtrSymbol)
        R.r(arg0).s_value(arg2)
        arg2_1 = (arg2 + ARM_DEFAULT_MEMORY_SIZE).ptr
        R.r(arg1).s_value(arg2_1)

    @staticmethod
    def ldrb(*args):# ldrb   w9, [sp, #0x1fb] [已检查]
        assert len(args) == 2, args
        R.r(args[0]).s_value(args[1].ptrb)

    @staticmethod
    def ldrh(*args):# ldrh   w9, [sp, #0x236]
        return Opera.ldrsh(*args)

    @staticmethod
    def ldur(*args):
        # todo: [待思考] 无符号数的处理
        return Opera.ldp(*args)

    @staticmethod
    def sturb(*args):
        # todo：[待思考]
        return Op.strb(*args)

    @staticmethod
    def ldurb(*args):
        # todo：[待思考]
        return Op.ldrb(*args)

    @staticmethod
    def ldrsb(*args):
        # todo: [待思考]
        return Op.ldrb(*args)

    @staticmethod
    def sxtw(*args):# sxtw   x9, w9
        # todo: [待观察]
        assert len(args) == 2, args
        arg0, arg1 = args
        value = R.r(arg1).g_value()
        if value < 0:
            R.r(arg0).s_value((Int.get_mask(31) & value) | Int.get_mask(ARM_DEFAULT_MASK_SIZE - 31) << 31)
        else:
            R.r(arg0).s_value(Int.get_mask(31) & value)

    @staticmethod
    def strb(*args): # [已检查]
        # strb   w9, [sp, #0x25e]
        assert len(args) == 2
        arg0, arg1 = args
        PtrSymbol(arg1).ptr_v(R.r(arg0).g_uvalue() & 0xFF, mode=REGISTER_MODE_BYTE)

    @staticmethod
    def ldursw(*args):
        # todo: [待处理]
        return Opera.ldr(*args)

    @staticmethod
    def strh(*args):# strh   w9, [sp, #0x21c]
        assert len(args) == 2
        arg0, arg1 = args
        PtrSymbol(arg1).ptr_v(R.r(arg0).g_uvalue() & Int.get_mask(ARM_DEFAULT_MASK_SIZE // 2), mode=MODES_REVERSE_MAPPING[ARM_DEFAULT_MASK_SIZE // 2])

    @staticmethod
    def ldr(*args):# ldr    x9, [x9] [已检查]
        assert len(args) == 2, args
        arg0, arg1 = args
        assert isinstance(arg1, PtrSymbol)
        r = R.r(arg0)
        # 此处直接处理。不用r.s_value(arg1.ptr)这种通用了
        if r.mode == REGISTER_MODE_W:
            r.s_value(arg1.ptrw)
        elif r.mode == REGISTER_MODE_Q:
            r.s_value(arg1.ptrq)
        else:
            r.s_value(arg1.ptr)

    @staticmethod
    def str(*args): # str    x9, [sp, #0x48]
        if len(args) == 2: # [已检查]
            arg0, arg1 = args
            if isinstance(arg0, str):
                arg0 = R.r(arg0)
            arg1.ptr_v(arg0)
        elif len(args) == 3: # ('q0', ['x8', '0x30'], '!') [已检查]
            arg0, arg1, arg3 = args
            arg1_0, arg1_1 = arg1
            if isinstance(arg0, str):
                arg0 = R.r(arg0)
            arg1_ = R.r(arg1_0) + eval(arg1_1)
            arg1 = arg1_.ptr
            arg1.ptr_v(arg0)
            arg1_.to_r(arg1_0)
        else:
            raise ValueError(args)

    @staticmethod
    def stur(*args):
        # stur   x17, [x8, #-0x18] 0x00000001701f4eb0 存入没问题。 todo: [待处理]
        if args[0].startswith("w"):
            1/3
        return Opera.str(*args)

    @staticmethod
    def stp(*args):
        # stp    x24, x23, [sp, #0x60]
        # stp    x24, x23, [sp, #0x60]!
        if len(args) == 3: # [已检查]
            arg0, arg1, arg3 = args
            if isinstance(arg0, str):
                arg0 = R.r(arg0)
            if isinstance(arg1, str):
                arg1 = R.r(arg1)
            arg3.ptr_v(arg0)
            tmp_size = MODES_MAPPING[arg1.mode]
            (arg3 + tmp_size // Bytes_to_Bits).ptr_v(arg1)
        elif len(args) == 4: # ('x28', 'x27', ['sp', '0x60'], '!') [已检查]
            arg0, arg1, arg3, arg4 = args
            assert arg4 == "!"
            if isinstance(arg0, str):
                arg0 = R.r(arg0)
            if isinstance(arg1, str):
                arg1 = R.r(arg1)
            arg3_0, arg3_1 = arg3
            arg3_ = R.r(arg3_0) + eval(arg3_1) # 将0x30 | 122 转换成整型
            arg3 = arg3_.ptr
            arg3.ptr_v(arg0)
            tmp_size = MODES_MAPPING[arg1.mode]
            (arg3 + tmp_size // Bytes_to_Bits).ptr_v(arg1)
            arg3_.to_r(arg3_0)
        else:
            assert len(args) == 3, f"args: {args}"

    @staticmethod
    def cmp(*args): # cmp    w9, w10 [已检查]
        # cmp 0x6367ffff, 0xfc9e19b6 -> 0x0；cmp 0x6367ffff, 0x39c61675 -> 0b10；
        assert len(args) == 2, args
        arg0, arg1 = args
        mode = REGISTER_MODE_X
        if isinstance(arg0, str):
            r0 = R.r(arg0)
            mode = r0.mode
            arg0 = r0.g_value()

        if isinstance(arg1, str):
            r1 = R.r(arg1)
            assert r1.mode == mode, f"CMP必须同模式处理: {args}"
            arg1 = r1.g_value()

        if isinstance(arg1, Register):
            if arg1.name == REGISTER_TMP:
                arg1 = getattr(arg1, mode).g_value()
            else:
                assert arg1.mode == mode, f"CMP必须同模式处理: {args}"
                arg1 = arg1.g_value()

        cpsr = R.r(REGISTER_CPSR)
        if arg0 == arg1:
            cpsr.Z = 1
        else:
            cpsr.Z = 0

        if arg0 < arg1:
            cpsr.N = 1
        else:
            cpsr.N = 0

        if arg0 > arg1:
            cpsr.C = 0
        else:
            cpsr.C = 1

        if mode == REGISTER_MODE_X:
            # if Int.toUX(arg0) > Int.toUX(arg1):
            #     cpsr.C = 0
            # else:
            #     cpsr.C = 1

            if (INT_Mask >> 1) - 1 > arg0 - arg1 > -(INT_Mask >> 1):
                cpsr.V = 0
            else:
                cpsr.V = 1
        elif mode == REGISTER_MODE_W:
            # if Int.toUW(arg0) > Int.toUW(arg1):
            #     cpsr.C = 0
            # else:
            #     cpsr.C = 1

            if (INT_Mask_32 >> 1) - 1 > arg0 - arg1 > -(INT_Mask_32 >> 1):
                cpsr.V = 0
            else:
                cpsr.V = 1
        else:
            raise ValueError(f"不支持模式: {mode}")

    @staticmethod
    def cmn(*args):
        # cmn x0,x1 -> x0 + x1
        assert len(args) == 2, args
        arg0, arg1 = args
        mode = ARM_DEFAULT_LATIN
        if isinstance(arg0, str):
            r0 = R.r(arg0)
            mode = r0.mode
            arg0 = r0.g_value()

        if isinstance(arg1, str):
            r1 = R.r(arg1)
            assert r1.mode != mode, f"CMP必须同模式处理: {args}"
            arg1 = r1.g_value()

        v = arg0 + arg1
        cpsr = R.r(REGISTER_CPSR)
        if v == 0:
            cpsr.Z = 1
        else:
            cpsr.Z = 0

        if v < 0:
            cpsr.N = 1
        else:
            cpsr.N = 0

        if mode == REGISTER_MODE_X:
            v_c = Int.toUX(arg0) + Int.toUX(arg1)
            v_c_max = INT_Mask
            v_v = Int.toUX(arg0) - Int.toUX(arg1)
            v_v_max = INT_Mask >> 1 - 1
        elif mode == REGISTER_MODE_W:
            v_c = Int.toUW(arg0) + Int.toUW(arg1)
            v_c_max = INT_Mask_32
            v_v = Int.toUW(arg0) - Int.toUW(arg1)
            v_v_max = INT_Mask_32 >> 1 - 1
        else:
            raise ValueError(f"不支持模式: {mode}")

        if v_c > v_c_max:
            cpsr.C = 1
        else:
            cpsr.C = 0

        # 或者：负数 + 负数、正数 + 正数
        if v_v_max >= v_v >= 0:
            cpsr.V = 0
        else:
            cpsr.V = 1

    @staticmethod
    def tst(*args):
        # tst x0,#8 -> x0 & 8
        assert len(args) == 2
        arg0, arg1 = args
        if isinstance(arg0, str):
            arg0 = R.r(arg0).g_value()

        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        cpsr = R.r(REGISTER_CPSR)
        value = arg0 & arg1
        if value == 0:
            cpsr.Z = 1
        else:
            cpsr.Z = 0

        if value < 0:
            cpsr.N = 1
        else:
            cpsr.N = 0

    @staticmethod
    def teq(*args):
        # teq x0, #8 -> x0 ^ 8
        assert len(args) == 2, args
        arg0, arg1 = args
        if isinstance(arg0, str):
            arg0 = R.r(arg0).g_value()

        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        cpsr = R.r(REGISTER_CPSR)
        value = arg0 ^ arg1
        if value == 0:
            cpsr.Z = 1
        else:
            cpsr.Z = 0

        if value < 0:
            cpsr.N = 1
        else:
            cpsr.N = 0

    @staticmethod
    def lsl(*args): # lsl    w9, w9, #16 [已检查]
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_uvalue()

        R.r(arg0).s_value(arg1 << arg2)

    @staticmethod
    def lsr(*args):# lsr    x9, x10, x9 [已检查]
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_uvalue()

        R.r(arg0).s_value(arg1 >> arg2)

    @staticmethod
    def asr(*args): # 算数右移
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()
        Int(arg1 >> arg2).to_r(arg0)

    @staticmethod
    def mul(*args):
        assert len(args) == 3, args
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        Int(arg1 * arg2).to_r(arg0)

    @staticmethod
    def sub(*args): # sub    sp, sp, #0xa0 【已检查】
        assert len(args) == 3, f"args: {args}"
        r0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()
        Int(arg1 - arg2).to_r(r0)

    @staticmethod
    def add(*args):
        if len(args) == 3:
            # add    x29, sp, #0x90 【已检查】
            r0, arg1, arg2 = args
            if isinstance(arg1, str):
                arg1 = R.r(arg1).g_value()
            if isinstance(arg2, str):
                arg2 = R.r(arg2).g_value()
            # Int(arg1 + arg2).to_r(r0)
            R.r(r0).s_value(arg1 + arg2)
        elif len(args) == 4:
            # add    x9, x10, w9, sxth
            # 0x00000001701f4eb0 + 0x000000000000fc90 -> 0x00000001701f4b40
            # 0x000000016bb58c16 + 0x0 -> 0x6bb58c16

            r0, arg1, arg2, arg3 = args
            assert arg3 == "sxth"
            if isinstance(arg1, str):
                arg1 = R.r(arg1).g_value()

            if isinstance(arg2, str):
                arg2 = R.r(arg2).g_value()
            # 暂时做 半字 == 2byte???
            tmp_value = (arg1 >> 16 << 16) + (arg1 + arg2 & 0xFF_FF)
            R.r(r0).s_value(tmp_value)
        else:
            raise NotImplemented(args)

    @staticmethod
    def madd(*args):
        assert len(args) == 4, args
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        if isinstance(arg3, str):
            arg3 = R.r(arg3).g_value()

        R.r(arg0).s_value(arg3 + arg1 * arg2)

    @staticmethod
    def mov(*args): # mov    x28, x9 [已检查]
        assert len(args) == 2, f"args: {args}"
        r0, arg1 = args
        if isinstance(arg1, str):
            R.r(arg1).to_r(r0)
        else:
            R.r(r0).s_value(arg1)

    @staticmethod
    def mvn(*args):
        # mvn x0, x1 -> -x1 => x0 => mov x0, -x1
        assert len(args) == 2, f"args: {args}"
        r0, arg1 = args
        if isinstance(arg1, str):
            R.r(r0).s_value(~R.r(arg1).g_value())
        else:
            R.r(r0).s_value(~arg1)

        # mvn    x9, x9 发现 8位的话 0x2d -> 0x2c ???

    @staticmethod
    def movk(*args): # movk   w10, #0x31b0, lsl #16
        if len(args) == 2:
            # 注意要保持高位不变。且存在. todo: 待检查，x寄存器如何替换w内容. 暂未发现此情况
            raise NotImplemented
            # arg0, arg1 = args
            # arg0_high = R.r(arg0).toX() & (Int.get_mask(ARM_DEFAULT_MASK_SIZE - 16) << 16)
            # if isinstance(arg1, str):
            #     arg1 = R.r(arg1).g_value()
            # assert arg1 <= 0xFF_FF
            # R.r(arg0).x = arg0_high | arg1
        elif len(args) == 3: # [已检查]
            arg0, arg1, arg2 = args
            if isinstance(arg1, str):
                arg1 = R.r(arg1).g_value()
            assert arg1 <= 0xFF_FF
            assert "lsl#" in arg2
            arg2 = arg2.replace("lsl#", "")
            if arg2.startswith("0x"): # 不支持负数
                arg2 = int(arg2, 16)
            else:
                arg2 = int(arg2)
            assert 48 > arg2 >= 0
            # arg0[arg2:arg2+15] = arg1
            arg0_mid = arg1 << arg2
            arg0_high = R.r(arg0).toX() & (Int.get_mask(ARM_DEFAULT_MASK_SIZE - 16 - arg2) << (16 + arg2))
            arg0_low = R.r(arg0).toX() & Int.get_mask(arg2)
            R.r(arg0).x = arg0_high | arg0_mid | arg0_low
        else:
            raise ValueError(args)

    @staticmethod
    def neg(*args): # neg    w9, w9
        assert len(args) == 2, args
        arg0, arg1 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        R.r(arg0).s_value(-arg1)

    @staticmethod
    def and_(*args): # and    x17, x11, #0xfffffffffffffff0 [已检查]
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_uvalue()

        R.r(arg0).s_value(arg1 & arg2)

    @staticmethod
    def eor(*args): # eor    x9, x10, x9
        assert len(args) == 3, args
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_uvalue()

        R.r(arg0).s_value(arg1 | arg2)

    @staticmethod
    def orr(*args): # [已检查]
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        R.r(arg0).s_value(arg1 | arg2)

    @staticmethod
    def ror(*args):
        assert len(args) == 3
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        mask_v = Int.get_mask(arg2)
        arg_0 = arg1 | mask_v
        arg_1 = arg1 >> arg2
        # arg_0 移动到最高位
        # arg_r = arg_1 | (arg_0 << ARM_DEFAULT_MASK_SIZE - Int.get_bits_size(arg_0))
        arg_r = arg_1 | (arg_0 << ARM_DEFAULT_MASK_SIZE - arg2)
        Int.toX(arg_r).to_r(arg0) # 这是有符号的

    @staticmethod
    def bic(*args): # bic    x9, x9, x10
        assert len(args) == 3, args
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()
        R.r(arg0).s_value(arg1 & arg2)

    @staticmethod
    def cset(*args):
        assert len(args) == 2
        arg0, arg1 = args
        cpsr = R.r(REGISTER_CPSR)
        if getattr(cpsr, arg1):
            R.r(arg0).s_value(1)
        else:
            R.r(arg0).s_value(0)

    @staticmethod
    def csel(*args): # csel   w28, w10, w9, eq [已检查]
        assert len(args) == 4
        arg0, arg1, arg2, arg3 = args
        cpsr = R.r(REGISTER_CPSR)
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()
        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        if getattr(cpsr, arg3):
            R.r(arg0).s_value(arg1)
        else:
            R.r(arg0).s_value(arg2)

    @staticmethod
    def sdiv(*args):
        # todo: [待观察]
        assert len(args) == 3, args
        arg0, arg1, arg2 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        if isinstance(arg2, str):
            arg2 = R.r(arg2).g_value()

        R.r(arg0).s_value(arg1 * arg2)

    @staticmethod
    def umulh(*args):
        raise NotImplemented


    @staticmethod
    def smulh(*args): # smulh  x11, x10, x9
        assert len(args) == 3, args
        raise NotImplemented

    @staticmethod
    def ubfiz(*args): # ubfiz  x10, x10, #3, #3
        assert len(args) == 4, args
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        assert isinstance(arg0, str) # 必须是寄存器
        arg0_value = R.r(arg0).toX()

        assert isinstance(arg2, int) and isinstance(arg3, int)
        assert arg2 >= arg3
        # arg0_high = arg0_value & (ARM_DEFAULT_MASK & (Int.get_mask(ARM_DEFAULT_MASK_SIZE - arg3) << (ARM_DEFAULT_MASK_SIZE - arg2)))
        # arg0_low = arg0_value & ARM_DEFAULT_MASK >> (arg2 + arg3)
        arg0_mid = arg1 & Int.get_mask(arg3) << (arg2 - arg3)
        # R.r(arg0).x = arg0_high | arg0_mid | arg0_low
        R.r(arg0).x = arg0_mid

    @staticmethod
    def bfi(*args):# bfi    w10, w9, #16, #16
        # [待处理情况]
        assert len(args) == 4
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value()

        assert isinstance(arg0, str) # 必须是寄存器
        arg0_value = R.r(arg0).toX()

        assert isinstance(arg2, int) and isinstance(arg3, int)
        assert arg2 >= arg3
        arg0_high = arg0_value & (ARM_DEFAULT_MASK & (Int.get_mask(ARM_DEFAULT_MASK_SIZE - arg3) << (ARM_DEFAULT_MASK_SIZE - arg2)))
        arg0_low = arg0_value & ARM_DEFAULT_MASK >> (arg2 + arg3)
        arg0_mid = (arg1 & Int.get_mask(arg3)) << (arg2 - arg3)
        R.r(arg0).x = arg0_high | arg0_mid | arg0_low

    @staticmethod
    def sbfx(*args):# sbfx   w9, w9, #0, #12
        # todo: 【待处理】
        assert len(args) == 4, args
        # 0x000000000000000a sbfx   w9, w9, #0, #6 ->  0x000000000000000a
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_value() # 这种bit做无符号的
        assert isinstance(arg2, int) and isinstance(arg3, int)
        bin_list = list(bin(arg1).replace("0b", ""))
        bin_list.reverse()
        bin_values = bin_list[arg2:arg2+arg3]
        bin_values.reverse()
        bin_value = "".join(bin_values) or "0"
        R.r(arg0).s_value(int("0b" + bin_value, 2))

    @staticmethod
    def ubfx(*args):# ubfx   w9, w9, #6, #6; [已检查]
        # 11001011101111011111010000110000 -> 0x11101
        # 0x00000000cbbdf430 -> 0x000000000000001d, ubfx   w9, w9, #21, #5
        # 0x00000000cbbdf430 -> 0x000000000000001d  ubfx   w9, w9, #16, #5
        assert len(args) == 4, args # 取 [arg2-arg3:arg2] 这一部分内容
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue() # 这种bit做无符号的
        assert isinstance(arg2, int) and isinstance(arg3, int)
        bin_list = list(bin(arg1).replace("0b", ""))
        bin_list.reverse()
        bin_values = bin_list[arg2:arg2+arg3]
        bin_values.reverse()
        bin_value = "".join(bin_values) or "0"
        R.r(arg0).s_value(int("0b" + bin_value, 2))

    @staticmethod
    def msub(*args):
        raise NotImplemented

    @staticmethod
    def cinc(*args):
        raise NotImplemented

    @staticmethod
    def bics(*args):
        raise NotImplemented

    @staticmethod
    def bfxil(*args):
        # 0x2、0xcbbdf430 bfxil  w11, w9, #31, #1 -> 0x3
        assert len(args) == 4
        arg0, arg1, arg2, arg3 = args
        if isinstance(arg1, str):
            arg1 = R.r(arg1).g_uvalue()

        tmp_arr = list(bin(arg1).replace("0b", ""))
        tmp_arr.reverse()
        bin_value = "".join(tmp_arr[arg2:arg2+arg3])
        bin_value = bin_value or "0"
        assert arg3 == 1
        arg0_value = R.r(arg0).g_uvalue()
        R.r(arg0).s_value(arg0_value | int("0b"+bin_value, 2))

    @staticmethod
    def udiv(*args):
        raise NotImplemented

    @staticmethod
    def sbfiz(*args):
        raise NotImplemented

    @staticmethod
    def sxth(*args):
        raise NotImplemented

Op = Opera

# 条件相关
class Conder(object):
    CONDER_Cond_Marks = ["ne", "eq"]
    CONDER_Ret_Insts = ["ret"]
    CONDER_Redirect_Insts = ["b", "bl", "br", "blr"]
    CONDER_Redirect_Like_Insts = ["b."]

    CONDER_Alias_Mapping = {}

    @staticmethod
    def is_cond_mark(inst):
        return inst in Conder.CONDER_Cond_Marks

    @staticmethod
    def create_conder(inst, args):
        if inst in Conder.CONDER_Ret_Insts:
            return CODE_Ret, f'C.{inst.lower()}()'
        elif inst in Conder.CONDER_Redirect_Insts:
            # b
            return CODE_Redirect, f"C.{inst}({args[0]})"
        else:
            for inst_ in Conder.CONDER_Redirect_Like_Insts:
                if inst.startswith(inst_):
                    inst_args = inst.split(".")
                    assert inst_args[0] == "b", "暂时只支持b.xx"
                    return CODE_Redirect, f"C.{inst_args[0]}_({args[0]}, \"{inst_args[1]}\")"

    @classmethod
    def check_Conder(cls): # 检查Op是否被实现
        for inst in cls.CONDER_Redirect_Insts:
            inst = cls.CONDER_Alias_Mapping.get(inst, inst)
            assert hasattr(cls, inst), f"不存在Inst: {inst}"

        for inst in cls.CONDER_Ret_Insts:
            inst = cls.CONDER_Alias_Mapping.get(inst, inst)
            assert hasattr(cls, inst), f"不存在Inst: {inst}"

    @staticmethod
    def b(*args, update_lr=False):
        func_address = args[0]
        ff = F.find_f(func_address)
        assert isinstance(ff, FunctionFrame)
        pc = R.find_r(REGISTER_PC)
        assert isinstance(pc, PCRegister), "非PC寄存器"
        logging.info(f">>> b to {ff.func_name}:{hex(func_address)} update_lr: {update_lr}", )
        if update_lr:
            R.r(REGISTER_LR).s_value(F.f(pc).find_op_code(pc.pc_address()).next_address)
        pc.update_pc(func_address)

    @staticmethod
    def bl(*args):
        # 更新lr
        return Conder.b(*args, update_lr=True)

    @staticmethod
    def br(*args):
        logging.warning("[Warning]是否要更新FP")
        arg0 = R.r(args[0]).g_value()
        return Conder.b(arg0)

    @staticmethod
    def blr(*args):
        logging.warning("[Warning]是否要更新FP")
        return Conder.br(*args)

    @staticmethod
    def b_(*args):
        cond = args[-1]
        cpsr = R.r(REGISTER_CPSR)
        if getattr(cpsr, cond):
            Conder.b(*args[:-1])

    @staticmethod
    def ret(*args, **kwargs):
        logging.warning("函数return...")

C = Conder

class Eleciron(object):

    ElECIRON_Init_Mark = False

    def init_environment(self, *args, **kwargs):
        raise NotImplemented

    def start(self):
        assert self.ElECIRON_Init_Mark, "未初始化"


class ARMEleciron(Eleciron):
    def init_environment(self, registers:dict, mem_stacks:dict, ffs:list, extra_registers:dict=None):
        # 初始函数
        if ffs:
            for ff in ffs:
                FunctionFactory.register(ff) # 注册进入
                FunctionFactory.init_function(ff) # 然后初始化
                logging.info("载入函数: %s", ff.func_name)
        else:
            logging.info("载入函数为空...")

        logging.info("开始检查Conder、Opera")
        # 检查函数
        Conder.check_Conder()
        Opera.check_Op()

        logging.info("开始初始化寄存器.")
        self.init_registers(registers)
        self.init_extra_registers(extra_registers)
        logging.info("开始初始化内存块.")
        self.init_mems(mem_stacks)

        self.ElECIRON_Init_Mark = True

        logging.info("环境初始化完毕.")
        return self

    def init_registers(self, registers:dict):
        # 常用寄存器初始化
        for i in range(0, 29):
            RegisterFactory.register(Register(f"x{i}"))

        RegisterFactory.register(Register("x29", alias=REGISTER_FP))
        RegisterFactory.register(LRRegister())
        RegisterFactory.register(CPSRRegister())

        # 栈初始化
        sp = SPRegister()
        RegisterFactory.register(sp)

        # pc寄存器初始化
        pc = PCRegister()
        RegisterFactory.register(pc)

        # 初始化
        for name, value in registers.items():
            if isinstance(value, str):
                if value.startswith("0x"):
                    value = Int(value, 16)
            value = Int(value)
            RegisterFactory.r(name).s_value(value)

    def init_mems(self, mem_stacks:dict):
        tmp_stack = []
        _check_addr = None
        _start_addr = None
        for addr, values in mem_stacks.items():
            if isinstance(addr, str):
                if addr.startswith("0x"):
                    addr = int(addr, 16)
                else:
                    addr = int(addr)
            if not _check_addr:
                _check_addr = addr
            if not _start_addr:
                _start_addr = addr
            if addr - _check_addr not in [0, 1]:
                logging.error(f"间断的内存块! {addr} >> {_check_addr} ")
                raise RuntimeError
            for value in values:
                _check_addr += 1
                tmp_stack.append(value)

        Memory.load_stack(tmp_stack, _start_addr)

    def init_extra_registers(self, extra_registers, size=1):
        if isinstance(extra_registers, dict):
            pass
        else:
            # 0-31个，通常只用一个
            for i in range(0, min(size, 32)):
                R.register(Register(f"q{i}", alias=f"SIMD_{i}", mode=REGISTER_MODE_Q))

    def start(self):
        super().start()
        FunctionFactory.run()


class BreakPoint(MockerBreakPoint):

    GLOBAL_OP_Line = "global_op_lines"
    GLOBAL_Address = "global_address"
    GLOBAL_Op_code = "global_op_code"

    GLOBAL_BP_Mapping = {
        GLOBAL_OP_Line: {},
        GLOBAL_Address: {},
        GLOBAL_Op_code: {},
    }

    def check_anchor(self, op_code=None, address=None, line_no=None):
        if op_code:
            mapping = self.GLOBAL_BP_Mapping[self.GLOBAL_Op_code]
            if op_code in mapping:
                mapping[op_code].anchor(op_code)
                input(f"breakpoint opcode: {op_code}... 输入[回车]继续")

        if address:
            mapping = self.GLOBAL_BP_Mapping[self.GLOBAL_Address]
            if address in mapping:
                input(f"breakpoint address: {address}... 输入[回车]继续")

        if line_no:
            mapping = self.GLOBAL_BP_Mapping[self.GLOBAL_OP_Line]
            if line_no in mapping:
                input(f"breakpoint line_no: {line_no}... 输入[回车]继续")

    def _mapping(self, position):
        if isinstance(position, OpCodePosition):
            return self.GLOBAL_BP_Mapping[self.GLOBAL_Op_code]
        elif isinstance(position, AddressPosition):
            return self.GLOBAL_BP_Mapping[self.GLOBAL_Address]
        elif isinstance(position, OpLineNoPosition):
            return self.GLOBAL_BP_Mapping[self.GLOBAL_OP_Line]

    def register(self, position):
        assert isinstance(position, Position)
        if isinstance(position, OpCodePosition):
            self.GLOBAL_BP_Mapping[self.GLOBAL_Op_code][position.op_code] = position
        elif isinstance(position, AddressPosition):
            self.GLOBAL_BP_Mapping[self.GLOBAL_Address][position.address] = position
        elif isinstance(position, OpLineNoPosition):
            self.GLOBAL_BP_Mapping[self.GLOBAL_OP_Line][position.line_no] = position


class Position(MockerPosition):
    def anchor(self, value):
        raise NotImplemented


class OpCodePosition(Position):
    def __init__(self, op_code):
        self.op_code = op_code

    def anchor(self, value):
        if value == self.op_code:
            return True


class OpLineNoPosition(Position):
    def __init__(self, line_no):
        self.line_no = str(line_no) # 本来就没强制转int，所以兼容int类型

    def anchor(self, value):
        if value == self.line_no:
            return True


class AddressPosition(Position):
    def __init__(self, address):
        self.address = address

    def anchor(self, value):
        if value == self.address:
            return True


BP = BreakPoint()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(threadName)s-%(process)d %(filename)s[%(lineno)d] %(levelname)s: %(message)s')

    '''
    add    x9, x9, w10, sxtw 。如果是0xff00 + 0x0 ，则sxtw 高位补0xfffff
    '''
    pass
    # test_main()
    # test()
    print(hex(Int.unum64(-0x2b)))
    print(hex(Int.num64(0xFFFFFFFF_FF_FF_FF_d4)))
    print(hex(Int.num8(0xd4)))
    print(bin(0x2b))
    print(bin(0x2c))
    # 00101011 - > 11010101
    print(hex(Int.num8(0b11010101)))
    print(Int.num32(~0xff))
    print(bin(~0xff))
