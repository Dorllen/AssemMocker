import re
from util.assem_parser import AssemParser


class LLDBParser(AssemParser):
    @classmethod
    def lldb_to_nt(cls, text):
        codes = []
        text = text.replace("->", "")
        for line_raw in text.split("\n"):
            if not line_raw or "_symbol" in line_raw or "lldb" in line_raw:
                continue
            line = LLDBParser.lldb_to_nt_code(line_raw)
            codes.append(line)
        assert codes, "未解析出任何指令"
        func_address = codes[0][0]
        func_end_address = codes[-1][0]
        return func_address, func_end_address, codes

    @classmethod
    def lldb_to_nt_code(cls, line):
        # "    0x103fcc1d8 <+0>:   sub    sp, sp, #0xa0             ; =0xa0" -> sp = sp - 0xa0
        # 解析文本行
        # print("loading... ", line.strip())
        if ";" in line:
            result = re.findall("(.+?) <\\+(.+)>: +(.+);", line)[0]
        else:
            result = re.findall("(.+?) <\\+(.+)>: +(.+)", line)[0]

        codes = [a.strip() for a in result]
        address = codes[0]
        line_no = codes[1]
        inst = codes[2]

        # 解析指令
        inst_args = re.findall("(.+?)\s+(.+)", inst)
        if inst_args:
            inst_args = inst_args[0]
            inst_code = inst_args[0]
            args_text = inst_args[1]
        else: # ret 额外解析只有inst
            inst_args = re.findall("(.+)", inst)[0]
            inst_code = inst_args
            args_text = ""

        # 解析args
        values = []
        value = ""
        for i in args_text: # [sp, #0xabc]
            if "[" in value:
                value += i
            elif "]" in value:
                values.append(value)
                value = ""
            elif i == ",":
                values.append(value)
                value = ""
            elif i == " ":
                continue
            else:
                value += i

        if value:
            values.append(value)

        return address, line_no, inst_code, values
        # return text

    @classmethod
    def load_register_from_lldb_text(cls, file_path="./lldb_registers_demo.txt"):
        # text = '''
        #     x0 = 0x0000000109fd5100
        #     x1 = 0x000000016f79d000
        #     x2 = 0x0000000107e64e10
        #     x3 = 0x0000000107e64e20
        #     x4 = 0x000000016f79c9b0
        #     x5 = 0x0000000000000000
        #     x6 = 0x003a3330765f6564
        #     x7 = 0x000000016f79c7ae
        #     x8 = 0x000000016f79cff8
        #     x9 = 0x000000016f79c9c0
        #    x10 = 0x0000000104c8cd34  Aweme`___lldb_unnamed_symbol482848$$Aweme
        #    x11 = 0x0000000064162fe4
        #    x12 = 0x0000000000000000
        #    x13 = 0x000081a2030bfce9 (0x00000002030bfce9) (void *)0xa8000001a2030bfc
        #    x14 = 0x00000000187814c4
        #    x15 = 0x00000000000268c0
        #    x16 = 0x0000000104c9d044  Aweme`___lldb_unnamed_symbol482864$$Aweme + 8
        #    x17 = 0x0000000104c8b970  Aweme`___lldb_unnamed_symbol482832$$Aweme + 524
        #    x18 = 0x0000000000000000
        #    x19 = 0x000000016f79d010
        #    x20 = 0x0000000104c8ba45  Aweme`___lldb_unnamed_symbol482833$$Aweme + 201
        #    x21 = 0x0000000093e1be62
        #    x22 = 0x0000000024a9f10d
        #    x23 = 0x00000000f410ff52
        #    x24 = 0x000000001e7d8845
        #    x25 = 0x000000007b5db3ee
        #    x26 = 0x000000001e7d8846
        #    x27 = 0x0000000000000070
        #    x28 = 0x0000000000000013
        #     fp = 0x000000016f79d030
        #     lr = 0x0000000104c8c1a8  Aweme`___lldb_unnamed_symbol482837$$Aweme + 284
        #     sp = 0x000000016f79c9b0
        #     pc = 0x0000000104c8ce48  Aweme`___lldb_unnamed_symbol482849$$Aweme
        #   cpsr = 0x60000000
        # '''
        with open(file_path) as f:
            text = f.read()
        values = re.findall("([a-zA-Z0-9]{2,5}) = (0x[a-zA-Z0-9]{2,})\s", text)
        # print(values)
        # print(dict(values))
        return dict(values)

    @classmethod
    def load_mem_from_lldb_text(cls, file_path="./lldb_mem_demo.txt"):
        with open(file_path) as f:
            text = f.read()
        results = re.findall("(0x[a-zA-Z0-9]+): (.+?)\\s\\s", text)
        stacks = {}
        for result in results:
            addr, value = result
            values = [int("0x" + v, 16) for v in value.split(" ")]
            # print(addr, values)
            stacks[addr] = values
        return stacks
