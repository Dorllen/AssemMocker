import re, math

class Int(int):
    # def __repr__(self):
    #     return hex(self)

    def __str__(self):
        return hex(self)

    def __add__(self, other):
        return Int(super().__add__(other))

    def __sub__(self, other):
        return Int(super().__sub__(other))

    def __lshift__(self, other):
        return Int(super().__lshift__(other))

    def __rshift__(self, other):
        return Int(super().__rshift__(other))

    def __xor__(self, other):
        return Int(super().__xor__(other))

    def __or__(self, other):
        return Int(super().__or__(other))

    def __and__(self, other):
        return Int(super().__and__(other))

ARM_DEFAULT_MASK = 0xFF_FF_FF_FF_FF_FF_FF_FF # 64
ARM_DEFAULT_MASK_SIZE = 64

class Mem(object):
    MEM_Q_MODE = "x"
    MEM_X_MODE = "x"
    MEM_W_MODE = "w"
    MEM_B_MODE = "b"
    MEM_DEFAULT_MODE = MEM_X_MODE

    MEM_BIG_LATIN = 0
    MEM_LITTLE_LATIN = 1
    MEM_DEFAULT_LATIN = MEM_LITTLE_LATIN

    MEM_MODE_MAPPING = {
        MEM_Q_MODE: 16,
        MEM_X_MODE: 8,
        MEM_W_MODE: 4,
        MEM_B_MODE: 1
    }

    MEM_MODE_MASK_MAPPING = {
        MEM_Q_MODE: 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFF,
        MEM_X_MODE: 0xFFFFFFFF_FFFFFFFF,
        MEM_W_MODE: 0xFFFFFFFF,
        MEM_B_MODE: 0xFF
    }

    def __init__(self, index:int, stack:list, mode=None, latin=None):
        self.index = index
        self.stack = stack
        self.latin = latin

        if self.latin is None:
            self.latin = self.MEM_DEFAULT_LATIN

    def read(self, item, mode=None):
        if mode is None:
            mode = Mem.MEM_DEFAULT_MODE
        byte_size = Mem.MEM_MODE_MAPPING[mode]
        # return Mem.mem_read(self.stack[self.index + item:], 1, byte_size, self.latin)
        value = self.stack[self.index + item:self.index + item + byte_size]
        if self.latin:
            value.reverse()
        return Mem.merge_arr_to_int(value)

    def write(self, value, mode, latin):
        # if isinstance(value, Stack):
        #     value = value.to_value()
        assert isinstance(value, int), "required int value"
        value = value & self.MEM_MODE_MASK_MAPPING[mode]
        int_values = Mem.int_to_arr(value, mode)
        if latin == 1:
            int_values.reverse()
        # self[0] = Stack(0, int_values, mode, latin)
        self[0:len(int_values)] = int_values
        return self

    @property
    def x(self):
        return self.read(0, self.MEM_X_MODE)
        # return Stack(self.index, self.stack, self.MEM_X_MODE, self.latin).to_value()

    @x.setter
    def x(self, value):
        self.write(value, self.MEM_X_MODE, self.latin)

    @property
    def w(self):
        return self.read(0, self.MEM_W_MODE)
        # return Stack(self.index, self.stack, self.MEM_W_MODE, self.latin).to_value()

    @w.setter
    def w(self, value):
        self.write(value, self.MEM_W_MODE, self.latin)

    @property
    def b(self):
        return self.read(0, self.MEM_B_MODE)
        # return Stack(self.index, self.stack, self.MEM_B_MODE, self.latin).to_value()

    @b.setter
    def b(self, value):
        self.write(value, self.MEM_B_MODE, self.latin)

    @property
    def ldp(self):
        # 只支持x，如果w和其他模式，需人工换方法
        return Mem.mem_read(self, 2, byte_size=8, mode=1)

    @ldp.setter
    def stp(self, value):
        # 只支持x
        self.x = value[0]
        (self + 0x8).x = value[1]

    def __getitem__(self, item):
        if isinstance(item, slice):
            s, e = item.start, item.stop
            s = s + self.index if s else self.index
            e = e + self.index if e else None
            assert not e or len(self.stack) > e - s
            return self.stack[slice(s, e, item.step)]
        return self.stack[self.index + item]

    def __setitem__(self, key, value):
        # 功能：1：可以超长赋值. 2：自动根据value修正覆盖范围
        """
        例：(sp + 0x390 - 0x1E0)[0x10:] = q1 或 (sp + 0x390 - 0x1E0 + 0x10)[:] = q1
        :param key:
        :param value:
        :return:
        """
        if isinstance(value, int):
            self.stack[self.index + key:self.index + key + 1] = [value & 0xFF]
            return
        elif isinstance(value, Mem):
            value = value.to_list()
        assert isinstance(value, list)
        if isinstance(key, slice):
            s, e = key.start, key.stop
            s = s + self.index if s else self.index
            if e is None:
                if s < 0:
                    e = len(self)
                else:
                    e = s + len(value)
            else:
                e = e + s
            self.stack[slice(s, e, key.step)] = value
        else:
            self.stack[self.index + key:self.index + key + len(value)] = value

    def __add__(self, other):
        assert isinstance(other, int) and other < len(self)
        return Mem(self.index + other, self.stack)

    def __sub__(self, other):
        assert isinstance(other, int) and self.index >= other
        return Mem(self.index - other, self.stack)

    def __xor__(self, other):
        _a = self.to_list()
        if isinstance(other, int):
            return Mem(0, [_ ^ other for _ in _a])
        if isinstance(other, Mem):
            other = other.to_list()
        assert isinstance(other, list)
        _len = min(len(self), len(other))
        return Mem(0, [_a[_] ^ other[_] for _ in range(_len)])

    def __and__(self, other):
        _a = self.to_list()
        if isinstance(other, int):
            return Mem(0, [_ & other for _ in _a])
        if isinstance(other, Mem):
            other = other.to_list()
        assert isinstance(other, list)
        _len = min(len(self), len(other))
        return Mem(0, [_a[_] & other[_] for _ in range(_len)])

    def __or__(self, other):
        _a = self.to_list()
        if isinstance(other, int):
            return Mem(0, [_ | other for _ in _a])
        if isinstance(other, Mem):
            other = other.to_list()
        assert isinstance(other, list)
        _len = min(len(self), len(other))
        return Mem(0, [_a[_] | other[_] for _ in range(_len)])

    def __repr__(self):
        if self.stack:
            return Mem.hex(self.stack[self.index:self.index+32]) + "..."
        return "Mem is None..."

    def __len__(self):
        return len(self.stack) - self.index

    def __ge__(self, other):
        assert isinstance(other, Mem) and self.stack == other.stack, "required same Memory"
        return self.index.__ge__(other.index)

    def __lt__(self, other):
        assert isinstance(other, Mem) and self.stack == other.stack, "required same Memory"
        return self.index.__lt__(other.index)

    def __gt__(self, other):
        assert isinstance(other, Mem) and self.stack == other.stack, "required same Memory"
        return self.index.__gt__(other.index)

    def __le__(self, other):
        assert isinstance(other, Mem) and self.stack == other.stack, "required same Memory"
        return self.index.__le__(other.index)

    @staticmethod
    def create(size, mode="b"):
        assert isinstance(size, int)
        return Mem(0, [0 for i in range(size)], mode)

    def to_list(self):
        return self.stack[self.index:]

    def to_hex_list(self):
        return [hex(_) for _ in self.stack[self.index:]]

    @staticmethod
    def mem_read(x0, return_size=1, byte_size=4, mode=1):
        # mode = 1 小头， mode = 0 大头
        return_list = []
        for i in range(return_size):
            a = x0[i*byte_size:i*byte_size+byte_size]
            if mode == 1:
                a.reverse()
            return_list.append(Mem.merge_arr_to_int(a))
        if return_size == 1:
            return return_list[0]
        return return_list

    @staticmethod
    def merge_arr_to_int(arr):
        # 如有字节序，则数组必须是处理好的
        int_value = 0
        arr.reverse()
        for i, a in enumerate(arr):
            int_value += a << i * 8
        return Int(int_value)

    @staticmethod
    def int_to_arr(int_value, mode=None):
        if mode is None:
            mode = Mem.MEM_DEFAULT_MODE
        byte_size = Mem.MEM_MODE_MAPPING[mode]
        bstr = bin(int_value).replace("0b", "")
        while len(bstr) % 8 != 0:
            bstr = "0" + bstr
        assert len(bstr) // 8 <= byte_size
        barr = re.findall("[01]{8}", bstr)
        barr = [Int("0b" + i, 2) for i in barr]
        tmp_arr = [0 for _ in range(byte_size - len(barr))]
        return tmp_arr + barr

        # vstr = "%0.16x" % int_value
        # varr = re.split("(.{2})", vstr.replace("0x", ""))
        # byte_size = Mem.MEM_MODE_MAPPING[mode]
        # rarr = [Int("0x" + _, 16) for _ in varr if _]
        # return rarr[-byte_size:]

    @staticmethod
    def read_file(file_path):
        with open(file_path) as f:
            text = f.read()
        return Mem.read_text(text)

    @staticmethod
    def read_text(text):
        results = re.findall("(0x[a-zA-Z0-9]+): (.+?)\\s\\s", text + "  ")
        stack = []
        for result in results:
            addr, value = result
            values = [Int("0x" + v, 16) for v in value.split(" ")]
            stack += values
        return Mem(0, stack)

    @staticmethod
    def from_list(l):
        return Mem(0, list(l))

    def resize(self, size):
        self.stack = self.stack[:size]
        return self

    @staticmethod
    def padding(mem, size, padding_value=0x0):
        for _ in range(size):
            mem.stack.append(padding_value)
        return mem

    @staticmethod
    def hex(value):
        if isinstance(value, Mem):
            mem_size = 16
            int_list = value.to_list()
            loop_time = math.ceil(len(int_list) / mem_size)
            text = ""
            for i in range(loop_time):
                text += Mem.hex(int_list[i*mem_size:(i+1) * mem_size]).replace("\n", "") + "\n"
            return text
        elif isinstance(value, list):
            text = ""
            for i, v in enumerate(value):
                if v <= 0xF:
                    v = "0" + hex(v).replace("0x", "")
                else:
                    v = hex(v)
                if i > 0 and i % 16 == 0:
                    v = "\n" + v
                text += v.replace("0x", "") + " "

            return text
        else:
            return hex(value)

    def dump(self):
        mem_size = 16
        int_list = self.to_list()
        loop_time = math.ceil(len(int_list) / mem_size)
        text = ""
        for i in range(loop_time):
            text += "0x%.9x: " % i + Mem.hex(int_list[i*mem_size:(i+1) * mem_size]) + "  \n"
        return text


class Stack(Mem):
    def __init__(self, index, stack:list, mode=None, latin=None):
        self.mode = mode or Mem.MEM_DEFAULT_MODE
        super().__init__(index, stack, latin)

    def __getitem__(self, item):
        result = super().__getitem__(slice(item, item + self.MEM_MODE_MAPPING[self.mode], None))
        if self.latin:
            result.reverse()
        return Mem.merge_arr_to_int(result)

    def to_value(self):
        result = super().__getitem__(slice(0, 0 + self.MEM_MODE_MAPPING[self.mode], None))
        if self.latin:
            result.reverse()
        return Mem.merge_arr_to_int(result)

    def __setitem__(self, key, value):
        # 例子：x0[:]=value；x0[0]=value
        # x0可以是Mem或Stack. value是Int, int, Stack
        assert isinstance(value, int)
        if isinstance(value, int):
            arr = Mem.int_to_arr(value, self.mode)
            if self.latin == 1:
                arr.reverse()
        super().__setitem__(key, value)


if __name__ == '__main__':
    # x = [_ for _ in range(255)]
    # print(Mem.hex(x))
    vstr = "%0.16x" % 0xabcdef
    print(vstr, len(vstr))
    print(vstr[::2])
    t = re.split("(.{2})", vstr.replace("0x", ""))
    byte_size = 4
    l = []
    for _ in t:
        if _:
            l.append(Int("0x" + _, 16))
    print(t)
    print(l)
    print(l[-byte_size:])
