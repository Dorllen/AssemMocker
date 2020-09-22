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


class Mem(object):
    MEM_X_MODE = "x"
    MEM_W_MODE = "w"
    MEM_B_MODE = "b"
    MEM_DEFAULT_MODE = MEM_X_MODE

    MEM_BIG_LATIN = 0
    MEM_LITTLE_LATIN = 1
    MEM_DEFAULT_LATIN = MEM_LITTLE_LATIN

    MEM_MODE_MAPPING = {
        MEM_X_MODE: 8,
        MEM_W_MODE: 4,
        MEM_B_MODE: 1
    }

    def __init__(self, index:int, stack:list, mode=None, latin=None):
        self.index = index
        self.stack = stack
        self.mode = mode
        self.latin = latin

        if self.mode is None:
            self.mode = self.MEM_DEFAULT_MODE
        if self.latin is None:
            self.latin = self.MEM_DEFAULT_LATIN

    def read(self, item, mode=None):
        if mode is None:
            mode = self.mode
        byte_size = Mem.MEM_MODE_MAPPING[mode]
        return Mem.mem_read(self.stack[self.index + item:], 1, byte_size, mode)

    @property
    def x(self):
        return Stack(self.index, self.stack, self.MEM_X_MODE, self.latin)

    @property
    def w(self):
        return Stack(self.index, self.stack, self.MEM_W_MODE, self.latin)

    @property
    def b(self):
        return Stack(self.index, self.stack, self.MEM_B_MODE, self.latin)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.stack[slice(item.start + self.index, self.index + item.stop, item.step)]
        return self.stack[self.index + item]

    def __setitem__(self, key, value):
        assert isinstance(value, int) and isinstance(key, int)
        self.stack[self.index + key] = value & 0xFF

    def __add__(self, other):
        assert isinstance(other, int)
        return Mem(self.index + other, self.stack)

    def __sub__(self, other):
        assert isinstance(other, int)
        return Mem(self.index - other, self.stack)

    def __repr__(self):
        if self.stack:
            return Mem.hex(self.stack[self.index:self.index+32]) + "..."
        return "Mem is None..."

    def __len__(self):
        return len(self.stack) - self.index

    @staticmethod
    def create(size, mode="b"):
        return Mem(0, [0 for i in range(size)], mode)

    def to_list(self):
        return self.stack[self.index:]

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
        assert len(bstr) // 8 >= byte_size
        barr = re.findall("[01]{8}", bstr)
        barr = [Int("0b" + i, 2) for i in barr]
        tmp_arr = [0 for _ in range(byte_size - len(barr))]
        return tmp_arr + barr



    @staticmethod
    def read_file(file_path):
        with open(file_path) as f:
            text = f.read()
        return Mem.read_text(text)

    @staticmethod
    def read_text(text):
        results = re.findall("(0x[a-zA-Z0-9]+): (.+?)\\s\\s", text)
        stack = []
        for result in results:
            addr, value = result
            values = [Int("0x" + v, 16) for v in value.split(" ")]
            stack += values
        return Mem(0, stack)

    @staticmethod
    def hex(value):
        if isinstance(value, Mem):
            mem_size = 16
            int_list = value.to_list()
            loop_time = math.ceil(len(int_list) / mem_size)
            text = ""
            for i in range(loop_time):
                text += Mem.hex(int_list[i*mem_size:(i+1) * mem_size]) + "\n"
            return text
        elif isinstance(value, list):
            int_value = []
            for v in value:
                if v <= 0xF:
                    v = "0" + hex(v).replace("0x", "")
                else:
                    v = hex(v)
                int_value.append(v.replace("0x", ""))
            return " ".join(int_value)
        else:
            return hex(value)


class Stack(Mem):
    def __init__(self, index, stack:list, mode=None, latin=None):
        super().__init__(index, stack, mode, latin)

    def __getitem__(self, item):
        result = super().__getitem__(slice(item, item+self.MEM_MODE_MAPPING[self.mode], None))
        if self.latin:
            result.reverse()
        return Mem.merge_arr_to_int(result)

    def __setitem__(self, key, value):
        assert isinstance(value, int)
        arr = Mem.int_to_arr(value, self.mode)
        if self.latin == 1:
            arr.reverse()
        for i, _ in enumerate(arr):
            self.stack[self.index + i] = _

