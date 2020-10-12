import re
import base64
import hashlib
import re
import gzip

from urllib.parse import parse_qsl


class MiscUtil(object):
    @staticmethod
    def get_hex_from_stack_raw(raw_str):
        # 以DCB分块的特征
        _stack = re.findall("\sDCB\s{1,}(.+?)\s", raw_str)
        _stack = [int(i, 16) for i in _stack]
        return _stack

    @staticmethod
    def get_hex_from_DCD(raw_str):
        # 以0x开始的特征
        # _stack = re.findall("\s0(x.+?)(?:,|\s)", raw_str)
        _stack = []
        re_stack = re.findall("DCD\s(.+)", raw_str)
        for i in re_stack:
            _stack += i.split(",")

        for i, value in enumerate(_stack):
            if "0x" in value:
                _stack[i] = int(value.strip(), 16)
            else:
                _stack[i] = int(value.strip())
        return _stack

    @staticmethod
    def dcd_arr_to_ptr_stack(dcd_arr):
        _stack = []
        for i in dcd_arr:
            dcd_str = hex(i).replace("0x", "")
            while len(dcd_str) < 8 * 2: # 16个字符。8字节 * 2
                dcd_str = "0" + dcd_str
            dcd_temp_arr = [dcd_str[j:j+2] for j in range(0, len(dcd_str), 2)]
            # 默认小头
            dcd_temp_arr.reverse()
            for j in dcd_temp_arr:
                _stack.append(int("0x%s" % j, 16))
        return _stack

    @staticmethod
    def compare_diff_stack(s1, s2):
        length = min(len(s1), len(s2))
        print("length:", length, "isRight:", s1[:length] == s2[:length])

    @staticmethod
    def get_str_from_DCB(raw_str):
        _stack = []
        re_stack = re.findall("DCB\s.+;\s(.)", raw_str)
        for i in re_stack:
            _stack += str(i)
        return "".join(_stack)

    @staticmethod
    def padding(v, length):
        while len(v) < length:
            v = "0" + v
        return v

    @staticmethod
    def block(l:list, size, register_byte_size=8*8):
        return [l[i:i+size] for i in range(0, register_byte_size, size)]

    @staticmethod
    def print_stack_hex(r):
        for i in r:
            if i > 0xF:
                i = "0x" + hex(i).replace("0x", "").upper()
            print("->:", i)
        print(r)
        return r

    @staticmethod
    def parse_mem(text):
        value = re.findall("0x[a-z0-9]+: ([a-z0-9\\s]+)\\s{2}", text)
        return value

    @staticmethod
    def b64encode(s):
        return base64.b64encode(s)

    @staticmethod
    def b64decode(s):
        return base64.b64decode(s)

    @staticmethod
    def md5_hash(bvalue):
        md5 = hashlib.md5()
        md5.update(bvalue)
        return md5.digest()

    @staticmethod
    def md5_hash_str(bvalue):
        md5 = hashlib.md5()
        md5.update(bvalue)
        return md5.hexdigest()

    @staticmethod
    def gzip_encompress(data):
        return gzip.compress(data, compresslevel=8)

    @staticmethod
    def gzip_decompress(data):
        return gzip.decompress(data)

class FileUtil(object):

    @staticmethod
    def read_file(file):
        with open(file, "rt") as f:
            return f.read()

    @staticmethod
    def read_file_list(file):
        with open(file, "rt") as f:
            return f.readlines()

    @staticmethod
    def read_text(text_path):
        with open(text_path) as f:
            return f.read()

class OCUtil(object):
    @staticmethod
    def list_to_hex(args):
        text = ""
        for i, v in enumerate(args):
            value = hex(v).replace("0x", "")
            if v <= 0xF:
                value = "0" + value
            text += value
        return text

    @staticmethod
    def parse_mem_to_list(text):
        return OCUtil.merge_to_list(MiscUtil.parse_mem(text))

    @staticmethod
    def merge_to_list(s_list, split_key=" "):
        text = ""
        for t in s_list:
            t = t.strip()
            text += t + split_key
        text = text.strip()
        bs = text.split(split_key)
        return [int("0x" + i, 16) for i in bs]

    @staticmethod
    def int_to_bytes(int_list):
        return bytearray(int_list)

    @staticmethod
    def str_to_list(s, length=2):
        a = []
        for i in range(0, len(s), length):
            a.append(int("0x" + s[i:i+length], 16))
        return a

    @staticmethod
    def bytes_to_nsdata(bb):
        return OCUtil.str_to_nsdata(OCUtil.list_to_hex(list(bb)))

    @staticmethod
    def str_to_nsdata(bb_str):
        bb_str2 = ""
        for i in range(0, len(bb_str), 2):
            bb_str2 += bb_str[i:i+2]
            if len(bb_str2.split(" ")[-1]) % 8 == 0:
                bb_str2 += " "
        return f"<{bb_str2.strip()}>"

    @staticmethod
    def parse_nsdata(ns_data):
        # "<7b0a2020 22776f72 6c645f76 69657722 203a2022 434e222c 0a202022 6c616e67 75616765 22203a20 227a682d 48616e73 2d434e22 0a7d>"
        return OCUtil.parse_hex_array_to_byte(OCUtil.parse_nsdatastr_value_to_byte(ns_data))

    @staticmethod
    def parse_charles_hex(text):
        # 00000220  20 fa 0e 04 38 16 cd 35 6e f7 fc 38 f1 83 c8 5d
        return re.findall("[a-z0-9]{5,}\\s{2}([a-z0-9\\s]+?)\\s{2,}", text)

    @staticmethod
    def parse_nsdatastr_value_to_byte(nsdata_str):
        assert nsdata_str, "data is none"
        nsdata_str = nsdata_str.replace(">", "").replace("<", "")
        nsdata_bytes_arr = nsdata_str.split(" ")
        # print(nsdata_bytes_arr)
        byte_array = []
        for i, bytes_str in enumerate(nsdata_bytes_arr):
            for k in range(0, len(bytes_str), 2):
                byte_array.append("0x" + bytes_str[k:k+2])
        return byte_array

    @staticmethod
    def parse_hex_array_to_byte(hex_array):
        byte_array = bytearray()
        for r in hex_array:
            byte_array.append(int(r, 16))
        return byte_array

    @staticmethod
    def hex_list(l):
        ll = []
        for i in l:
            if isinstance(i, int):
                if i <= 0xF:
                    ll.append(hex(i).replace("0x", "0x0"))
                else:
                    ll.append(hex(i))
            else:
                ll.append(i)
        return ll

    @staticmethod
    def dump_matrix(values):
        ll = OCUtil.hex_list(values)
        for k in range(0, len(ll), 16):
            print(ll[k:k+16])
        return ll

    @staticmethod
    def mem_addr_to_global_args(mem_address):
        # 0x0000000282c51980. 只返回两个参数. 第三个参数在0x..cfe处
        return (int("0x"+mem_address[-2:], 16), int("0x"+mem_address[-4:-2], 16))

    @staticmethod
    def parse_url_args(url):
        "https://log-hl.snssdk.com/service/2/device_register/?device_id=&is_activated=1&aid=1128&tt_data=a&iid=2057896950772616&ac=4G&build_number=125009&os_api=18&channel=App%20Store&device_platform=iphone&app_version=12.5.0&app_name=aweme&vid=2CBC28DC-AC23-452C-A12B-40098F52ABC8&openudid=020ddcb9a2534bb5e9a09a997bff720dc6ccf523&cdid=3A014205-3F80-430B-838E-218ACA17FF81&device_type=iPhone8,1&idfa=00000000-0000-0000-0000-000000000000&version_code=12.5.0&os_version=12.4&screen_width=750&aid=1128&mcc_mnc=46011"
        kn = parse_qsl(url)
        return {k: v for k, v in kn}

    @staticmethod
    def parse_url_arg_name(url):
        "channel=App%20Store&version_code=11.5.0&app_name=aweme&vid=3A1A694D-0971-43C2-9A9B-6E2A5EC242BD&app_version=11.5.0&mcc_mnc=46011&device_id=2225054094202029&aid=1128&screen_width=750&openudid=ce4b765e03a4bc2212dd5abbd10b233c1e56099f&os_api=18&os_version=12.4&device_platform=iphone&build_number=115011&device_type=iPhone8,1&iid=4195386795242909&idfa=B4E9E277-AF9F-4ADB-AC74-D21B4B7222D6&js_sdk_version=1.68.1.0&cdid=5219731C-5A90-4E79-B207-A666EEEE8D6E"
        kn = parse_qsl(url)
        return [k for k, v in kn]

    @staticmethod
    def merge_url_arg():
        pass


class Parser(object):

    @staticmethod
    def lldb_to_nt(text):
        codes = []
        text = text.replace("->", "")
        for line_raw in text.split("\n"):
            if not line_raw or "_symbol" in line_raw or "lldb" in line_raw:
                continue
            line = Parser.lldb_to_nt_code(line_raw)
            codes.append(line)
        assert codes, "未解析出任何指令"
        func_address = codes[0][0]
        func_end_address = codes[-1][0]
        return func_address, func_end_address, codes

    @staticmethod
    def lldb_to_nt_code(line):
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


if __name__ == '__main__':
    kk = OCUtil.parse_nsdata('''<e6bfd1f2 fefce9f4 f2f3bfa7 e6bfdef2 f3e9f4f3 f8f3e9bf a7e6bfde f2f9f8bf a7bfdcce bfb1bfda f8f2d3fc f0f8d4d9 bfa7abaf a8a8aca9 aab1bfdc ceded4d3 fcf0f8bf a7bfdcee f4fcbfb1 bfd3fcf0 f8bfa7bf 7927077b 292fbfe0 b1bfdef2 e8f3e9ef e4bfa7e6 bfdef2f9 f8bfa7bf ded3bfb1 bfdaf8f2 d3fcf0f8 d4d9bfa7 aca5aca9 a4a4acb1 bfdccede d4d3fcf0 f8bfa7bf cdf8f2ed f1f8baee bdcff8ed e8fff1f4 febdf2fb bddef5f4 f3fcbfb1 bfd3fcf0 f8bfa7bf 79253078 0620bfe0 b1bfcee8 fff9f4eb f4eef4f2 f3eebfa7 c6e6bfde f2f9f8bf a7f3e8f1 f1b1bfda f8f2d3fc f0f8d4d9 bfa7aca5 adabafab adb1bfdc ceded4d3 fcf0f8bf a7bfd7f4 fcf3faee e8bdcef5 f8f3fabf b1bfd3fc f0f8bfa7 bf7b2c02 751612bf b1bfd1f2 fefcf1d4 d9bfa7bf aeafbfe0 c0b1bfde f4e9e4bf a7e6bfde f2f9f8bf a7f3e8f1 f1b1bfda f8f2d3fc f0f8d4d9 bfa7acaa a4a4aaaf afb1bfdc ceded4d3 fcf0f8bf a7bfd3fc f3e9f2f3 fabfb1bf d3fcf0f8 bfa7bf78 100a741d 07bfb1bf d1f2fefc f1d4d9bf a7bfaeaf adabadad bfb1bfd0 f8e9eff2 edf2f1f4 e9fcf3de f2f9f8bf a7f3e8f1 f1e0b1bf d9f4eee9 eff4fee9 bfa7e6bf def2f9f8 bfa7f3e8 f1f1b1bf daf8f2d3 fcf0f8d4 d9bfa7ab a8abaaab a9a5b1bf dcceded4 d3fcf0f8 bfa7bfde f5f2f3fa fef5e8fc f3bdcce8 bfb1bfd3 fcf0f8bf a7bf7829 1a782a00 bfb1bfd1 f2fefcf1 d4d9bfa7 bfaeafad abadafbf e0b1bfcd f1fcfef8 bfa7e6bf dcf9f9ef f8eeeed1 f4f3f8ee bfa7c6bf 7b2c0275 16127a01 1c78100a 741d0778 251f7829 1a782a00 781127bf c0b1bfdc f9f0f4f3 dceff8fc bfa7f3e8 f1f1b1bf d3fcf0f8 bfa7f3e8 f1f1b1bf dceff8fc eed2fbd4 f3e9f8ef f8eee9bf a7f3e8f1 f1b1bfce e8ffdcf9 f0f4f3dc eff8fcbf a7f3e8f1 f1b1bfd1 f2fefcf1 f4e9e4bf a7f3e8f1 f1b1bfce e8ffd1f2 fefcf1f4 e9e4bfa7 f3e8f1f1 b1bfc9f5 f2eff2e8 faf5fbfc eff8bfa7 f3e8f1f1 b1bfcee8 ffc9f5f2 eff2e8fa f5fbfcef f8bfa7f3 e8f1f1b1 bfcdf2ee e9fcf1de f2f9f8bf a7bfbfb1 bfdbf8fc e9e8eff8 def2f9f8 bfa7f3e8 f1f1b1bf daf8f2d3 fcf0f8d4 d9bfa7f3 e8f1f1b1 bfc9f4f0 f8c7f2f3 f8bfa7bf dceef4fc b2cef5fc f3faf5fc f4bfe0b1 bfdacdce bfa7e6bf dcfefee8 effcfee4 bfa7f3e8 f1f1b1bf dcf1e9f4 e9e8f9f8 bfa7f3e8 f1f1b1bf dcf1e9f4 e9e8f9f8 dcfefee8 effcefe4 bfa7f3e8 f1f1b1bf d1fce9f4 e9e8f9f8 bfa7aeaf b3adafae aaa4ada9 aca5a5ae aba5b1bf d1f2f3fa f4e9e8f9 f8bfa7ac afadb3a5 aaa9adaa aaaba4ad a4aaafaf aeb1bfc9 f4f0f8ee e9fcf0ed bfa7acab adafa9a5 a5a4aea8 e0b1bfd4 cecdbfa7 f3e8f1f1 b1bfd1f2 fefce9f8 d0f8e9f5 f2f9bfa7 bfd9f8eb f4fef8d4 f9d1f2fe fce9f4f2 f3bfb1bf c9f4f0f8 eee9fcf0 edbfa7ac abadafa9 a5a5a4ae a8b1bfd4 eed9f4ee ede8e9f8 f9bfa7f3 e8f1f1b1 bfc9f2ea f3bfa7e6 bfdef2f9 f8bfa7f3 e8f1f1b1 bfdaf8f2 d3fcf0f8 d4d9bfa7 aeafadab adafadad acb1bfdc ceded4d3 fcf0f8bf a7bf7802 13792501 753c0a74 1c0ebfb1 bfd3fcf0 f8bfa7bf 78021379 2501753c 0a741c0e bfb1bfd1 f2fefcf1 d4d9bfa7 f3e8f1f1 e0b1bfcb f4f1f1fc faf8bfa7 e6bfdef2 f9f8bfa7 f3e8f1f1 b1bfdaf8 f2d3fcf0 f8d4d9bf a7aeafad abadafad adacadac acb1bfdc ceded4d3 fcf0f8bf a7bf7b22 3d792501 7a392378 1127782c 18783a09 792107bf b1bfd3fc f0f8bfa7 bf7b223d 7925017a 39237811 27782c18 783a0979 2107bfb1 bfd1f2fe fcf1d4d9 bfa7f3e8 f1f1e0b1 bfdbf1fc faeebfa7 ade0b1bf d4cdd1f2 fefce9f4 f2f3bfa7 e6bfdef2 f3e9f4f3 f8f3e9bf a7e6bfde f2f9f8bf a7bfdcce bfb1bfda f8f2d3fc f0f8d4d9 bfa7abaf a8a8aca9 aab1bfdc ceded4d3 fcf0f8bf a7bfdcee f4fcbfb1 bfd3fcf0 f8bfa7bf 7927077b 292fbfe0 b1bfdef2 e8f3e9ef e4bfa7e6 bfdef2f9 f8bfa7bf ded3bfb1 bfdaf8f2 d3fcf0f8 d4d9bfa7 aca5aca9 a4a4acb1 bfdccede d4d3fcf0 f8bfa7bf cdf8f2ed f1f8baee bdcff8ed e8fff1f4 febdf2fb bddef5f4 f3fcbfb1 bfd3fcf0 f8bfa7bf 79253078 0620bfe0 b1bfcee8 fff9f4eb f4eef4f2 f3eebfa7 c6e6bfde f2f9f8bf a7f3e8f1 f1b1bfda f8f2d3fc f0f8d4d9 bfa7afad aea5aea9 a4b1bfdc ceded4d3 fcf0f8bf a7bfdff8 f4f7f4f3 fabdcef5 f4bfb1bf d3fcf0f8 bfa7bf78 110a7927 31bfb1bf d1f2fefc f1d4d9bf a7bfacac bfe0c0b1 bfdef4e9 e4bfa7e6 bfdef2f9 f8bfa7f3 e8f1f1b1 bfdaf8f2 d3fcf0f8 d4d9bfa7 aca5acab abaaadb1 bfdccede d4d3fcf0 f8bfa7bf dff8f4f7 f4f3fabf b1bfd3fc f0f8bfa7 bf78110a 792731bf b1bfd1f2 fefcf1d4 d9bfa7bf acacadad adadbfb1 bfd0f8e9 eff2edf2 f1f4e9fc f3def2f9 f8bfa7f3 e8f1f1e0 b1bfd9f4 eee9eff4 fee9bfa7 f3e8f1f1 b1bfcdf1 fcfef8bf a7e6bfdc f9f9eff8 eeeed1f4 f3f8eebf a7f3e8f1 f1b1bfdc f9f0f4f3 dceff8fc bfa7f3e8 f1f1b1bf d3fcf0f8 bfa7f3e8 f1f1b1bf dceff8fc eed2fbd4 f3e9f8ef f8eee9bf a7f3e8f1 f1b1bfce e8ffdcf9 f0f4f3dc eff8fcbf a7f3e8f1 f1b1bfd1 f2fefcf1 f4e9e4bf a7f3e8f1 f1b1bfce e8ffd1f2 fefcf1f4 e9e4bfa7 f3e8f1f1 b1bfc9f5 f2eff2e8 faf5fbfc eff8bfa7 f3e8f1f1 b1bfcee8 ffc9f5f2 eff2e8fa f5fbfcef f8bfa7f3 e8f1f1b1 bfcdf2ee e9fcf1de f2f9f8bf a7bfbfb1 bfdbf8fc e9e8eff8 def2f9f8 bfa7f3e8 f1f1b1bf daf8f2d3 fcf0f8d4 d9bfa7f3 e8f1f1b1 bfc9f4f0 f8c7f2f3 f8bfa7bf dceef4fc b2cef5fc f3faf5fc f4bfe0b1 bfdacdce bfa7e6bf dcfefee8 effcfee4 bfa7f3e8 f1f1b1bf dcf1e9f4 e9e8f9f8 bfa7f3e8 f1f1b1bf dcf1e9f4 e9e8f9f8 dcfefee8 effcefe4 bfa7f3e8 f1f1b1bf d1fce9f4 e9e8f9f8 bfa7f3e8 f1f1b1bf d1f2f3fa f4e9e8f9 f8bfa7f3 e8f1f1b1 bfc9f4f0 f8eee9fc f0edbfa7 f3e8f1f1 e0b1bfd4 cecdbfa7 bf751c09 741d07b2 7a092879 223cb27a 3a267817 35bfb1bf d1f2fefc e9f8d0f8 e9f5f2f9 bfa7bfd4 cdd1f2fe fce9f4f2 f3bfb1bf c9f4f0f8 eee9fcf0 edbfa7ac abadafa9 a5a4aea8 a4b1bfd4 eed9f4ee ede8e9f8 f9bfa7f3 e8f1f1b1 bfc9f2ea f3bfa7f3 e8f1f1b1 bfcbf4f1 f1fcfaf8 bfa7f3e8 f1f1b1bf dbf1fcfa eebfa7ad e0b1bfd9 f8ebf4fe f8d4f9d1 f2fefce9 f4f2f3bf a7e6bfde f2f3e9f4 f3f8f3e9 bfa7e6bf def2f9f8 bfa7bfdc cebfb1bf daf8f2d3 fcf0f8d4 d9bfa7ab afa8a8ac a9aab1bf dcceded4 d3fcf0f8 bfa7bfdc eef4fcbf b1bfd3fc f0f8bfa7 bf792707 7b292fbf e0b1bfde f2e8f3e9 efe4bfa7 e6bfdef2 f9f8bfa7 bfded3bf b1bfdaf8 f2d3fcf0 f8d4d9bf a7aca5ac a9a4a4ac b1bfdcce ded4d3fc f0f8bfa7 bfcdf8f2 edf1f8ba eebdcff8 ede8fff1 f4febdf2 fbbddef5 f4f3fcbf b1bfd3fc f0f8bfa7 bf792530 780620bf e0b1bfce e8fff9f4 ebf4eef4 f2f3eebf a7c6e6bf def2f9f8 bfa7f3e8 f1f1b1bf daf8f2d3 fcf0f8d4 d9bfa7ac a5adabaf abadb1bf dcceded4 d3fcf0f8 bfa7bfd7 f4fcf3fa eee8bdce f5f8f3fa bfb1bfd3 fcf0f8bf a7bf7b2c 02751612 bfb1bfd1 f2fefcf1 d4d9bfa7 bfaeafbf e0c0b1bf def4e9e4 bfa7e6bf def2f9f8 bfa7f3e8 f1f1b1bf daf8f2d3 fcf0f8d4 d9bfa7ac aaa4a4aa afafb1bf dcceded4 d3fcf0f8 bfa7bfd3 fcf3e9f2 f3fabfb1 bfd3fcf0 f8bfa7bf 78100a74 1d07bfb1 bfd1f2fe fcf1d4d9 bfa7bfae afadabad adbfb1bf d0f8e9ef f2edf2f1 f4e9fcf3 def2f9f8 bfa7f3e8 f1f1e0b1 bfd9f4ee e9eff4fe e9bfa7e6 bfdef2f9 f8bfa7f3 e8f1f1b1 bfdaf8f2 d3fcf0f8 d4d9bfa7 aba8abaa aba9a5b1 bfdccede d4d3fcf0 f8bfa7bf def5f2f3 fafef5e8 fcf3bdcc e8bfb1bf d3fcf0f8 bfa7bf78 291a782a 00bfb1bf d1f2fefc f1d4d9bf a7bfaeaf adabadaf bfe0b1bf cdf1fcfe f8bfa7e6 bfdcf9f9 eff8eeee d1f4f3f8 eebfa7c6 bf7b2c02 7516127a 011c7810 0a741d07 78251f78 291a782a 00781127 bfc0b1bf dcf9f0f4 f3dceff8 fcbfa7f3 e8f1f1b1 bfd3fcf0 f8bfa7f3 e8f1f1b1 bfdceff8 fceed2fb d4f3e9f8 eff8eee9 bfa7f3e8 f1f1b1bf cee8ffdc f9f0f4f3 dceff8fc bfa7f3e8 f1f1b1bf d1f2fefc f1f4e9e4 bfa7f3e8 f1f1b1bf cee8ffd1 f2fefcf1 f4e9e4bf a7f3e8f1 f1b1bfc9 f5f2eff2 e8faf5fb fceff8bf a7f3e8f1 f1b1bfce e8ffc9f5 f2eff2e8 faf5fbfc eff8bfa7 f3e8f1f1 b1bfcdf2 eee9fcf1 def2f9f8 bfa7bfbf b1bfdbf8 fce9e8ef f8def2f9 f8bfa7f3 e8f1f1b1 bfdaf8f2 d3fcf0f8 d4d9bfa7 f3e8f1f1 b1bfc9f4 f0f8c7f2 f3f8bfa7 bfdceef4 fcb2cef5 fcf3faf5 fcf4bfe0 b1bfdacd cebfa7e6 bfdcfefe e8effcfe e4bfa7f3 e8f1f1b1 bfdcf1e9 f4e9e8f9 f8bfa7f3 e8f1f1b1 bfdcf1e9 f4e9e8f9 f8dcfefe e8effcef e4bfa7f3 e8f1f1b1 bfd1fce9 f4e9e8f9 f8bfa7ae afb3adaf aeaaa4ad a9aca5a5 aeaba5b1 bfd1f2f3 faf4e9e8 f9f8bfa7 acafadb3 a5aaa9ad aaaaaba4 ada4aaaf afaeb1bf c9f4f0f8 eee9fcf0 edbfa7ac abadafa9 a5a5a4ae a8e0b1bf d4cecdbf a7f3e8f1 f1b1bfd1 f2fefce9 f8d0f8e9 f5f2f9bf a7bfd9f8 ebf4fef8 d4f9d1f2 fefce9f4 f2f3bfb1 bfc9f4f0 f8eee9fc f0edbfa7 acabadaf a9a5a5a4 aea8b1bf d4eed9f4 eeede8e9 f8f9bfa7 f3e8f1f1 b1bfc9f2 eaf3bfa7 e6bfdef2 f9f8bfa7 f3e8f1f1 b1bfdaf8 f2d3fcf0 f8d4d9bf a7aeafad abadafad adacb1bf dcceded4 d3fcf0f8 bfa7bf78 02137925 01753c0a 741c0ebf b1bfd3fc f0f8bfa7 bf780213 79250175 3c0a741c 0ebfb1bf d1f2fefc f1d4d9bf a7f3e8f1 f1e0b1bf cbf4f1f1 fcfaf8bf a7e6bfde f2f9f8bf a7f3e8f1 f1b1bfda f8f2d3fc f0f8d4d9 bfa7aeaf adabadaf adadacad acacb1bf dcceded4 d3fcf0f8 bfa7bf7b 223d7925 017a3923 78112778 2c18783a 09792107 bfb1bfd3 fcf0f8bf a7bf7b22 3d792501 7a392378 1127782c 18783a09 792107bf b1bfd1f2 fefcf1d4 d9bfa7f3 e8f1f1e0 b1bfdbf1 fcfaeebf a7ade0b1 bfc8eef8 efcef8f1 f8fee9f8 f9d1f2fe fce9f4f2 f3bfa7f3 e8f1f1b1 bfc8eef8 efcdeff2 fbf4f1f8 d1f2fefc e9f4f2f3 bfa7f3e8 f1f1b1bf dacdced1 f2fefce9 f4f2f3bf a7f3e8f1 f1b1bfdf ceced1f2 fefce9f4 f2f3bfa7 f3e8f1f1 b1bfcaf4 dbf4d1f2 fefce9f4 f2f3bfa7 f3e8f1f1 b1bfdffc eef8cff8 eeedbfa7 e6bfcee9 fce9e8ee d0f8eeee fcfaf8bf a7bfeee8 fefef8ee eebfb1bf cee9fce9 e8eedef2 f9f8bfa7 adb1bfd8 e5e9effc bfa7e6bf ffe4e9f8 f9b0e9ef fcfef8b0 f4f9bfa7 bfabffac acaefbae adfba5ac fcaefca9 ffaea4f9 a5acfefc aaaba5fb a5a8adad aea7acae fba8ada4 aeafa8aa ada5aefe aaaca7a9 fcfeaeae aaffa4fe fbada4af a8ada8a7 acbfe0e0 e0>''')
    for i in range(len(kk)):
        kk[i] = kk[i] ^ 0x9D
    print(kk)

