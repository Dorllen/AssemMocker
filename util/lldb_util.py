import lldb
import re


base_save_path = None # "simple/dy/lldb_result"
assert base_save_path, "提示：请设置文件保存路径"
max_loop = 2

def dump_function(debugger, command, result, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()     # 用来保存结果
    interpreter.HandleCommand('dis', return_object)  # 执行dis命令
    output = return_object.GetOutput() #获取反汇编后的结果
    result = re.findall("unnamed_(symbol.+\\$\\$[a-zA-z]+)", output)
    command = command or result[0]
    command = command.strip()
    print("dump functions:", command)
    file_path = f"{base_save_path}/lldb_func_{command}.txt"
    with open(file_path, "w") as f:
        f.write(output.replace("[33m", "").replace("[0m", ""))
    print("save to:", file_path)


def dump_registers(debugger, command, result, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()     # 用来保存结果
    interpreter.HandleCommand('register read', return_object)  # 执行dis命令
    output = return_object.GetOutput() #获取反汇编后的结果
    print("dump registers")
    file_path = f"{base_save_path}/lldb_registers.txt"
    with open(file_path, "w") as f:
        f.write(output)
    print("save to:", file_path)


def dump_mems(debugger, command, result, internal_dict):
    print("dump mems:", command)
    if not command:
        return
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()     # 用来保存结果
    count = 4096
    commands = command.strip().split(" ")
    addr = commands[0]
    if len(commands) > 1:
        count = commands[1]
    print(f'memory read -c {count} --force {addr}')
    interpreter.HandleCommand(f'memory read -c {count} --force {addr}', return_object)
    output = return_object.GetOutput()
    file_path = f"{base_save_path}/lldb_mem_{addr}.txt"
    with open(file_path, "w") as f:
        f.write(output.encode("unicode_escape").decode().replace("\\n", "\n"))
    print("save to:", file_path)


def dump_ext_registers(debugger, command, result, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()     # 用来保存结果
    text = ""
    for i in range(0, 32):
        interpreter.HandleCommand(f'register read q{i}', return_object)
        output = return_object.GetOutput()
        text += output.encode("unicode_escape").decode()
    print("dump registers ext")
    file_path = f"{base_save_path}/lldb_ext_registers.txt"
    with open(file_path, "w") as f:
        f.write(text)
    print("save to:", file_path)


def dump_line(debugger, command, result, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()     # 用来保存结果
    interpreter.HandleCommand(f'disassemble -p -c 1', return_object)
    output = return_object.GetOutput()
    result = re.findall("unnamed_(symbol.+)\\$\\$[a-zA-z]+", output)
    file_path = f"{base_save_path}/lldb_codes_{result[0]}.txt"
    with open(file_path, "a") as f:
        lines = output.split("\n")
        f.write(lines[1].encode("unicode_escape").decode() + "\n")
    debugger.HandleCommand("n")


def get_command_out(_command):
    interpreter = lldb.debugger.GetCommandInterpreter()
    return_object = lldb.SBCommandReturnObject()
    interpreter.HandleCommand(_command, return_object)
    return return_object.GetOutput().strip()


def read_ptr_value(addr):
    output = get_command_out(f"memory read/gx {addr}")
    return output.split(": ")[-1]


def read_register_value(r):
    output = get_command_out(f"po/x {r}")
    return output.split(": ")[-1]


def read_mem_from_ptr(debugger, command, result, internal_dict):
    args = command.split(" ")
    addr = args[0]
    if len(args) > 1:
        mem_size = args[1]
    else:
        mem_size = 64

    output = read_ptr_value(addr)
    _command = f"memory read -c {mem_size} {output}"
    print("_command:", _command)
    debugger.HandleCommand(_command)


def read_mem_by_easy(debugger, command, result, internal_dict):
    args = command.split(" ")
    addr = args[0]
    if len(args) > 1:
        mem_size = args[1]
    else:
        mem_size = 64

    _command = f"memory read -c {mem_size} {addr}"
    print("_command:", _command)
    debugger.HandleCommand(_command)


##### 定制化处理部分 ###########

def wechat_test_for_mem(debugger, command, result, internal_dict):
    x0 = read_register_value("$x19")
    x19_value = int(x0, 16)
    x19_0x60 = x19_value + 0x60
    _ = read_ptr_value(x19_0x60)
    print("read request body addr: (focus on +0x20)")
    _command = f"memory read -c 64 {_}"
    print(_command)
    lldb.debugger.HandleCommand(_command)
    print("\nread psk:")

    # *(*(*(x19 + 0xb8) + 8) + 0x28)
    _ = read_ptr_value(x19_value + 0xb8) #
    print("_:", _, hex(x19_value))
    _ = read_ptr_value(int(_, 16) + 8)
    print("_:", _)
    psk_addr = read_ptr_value(int(_, 16) + 0x28)
    print("_:", psk_addr)
    _command = f"memory read -c 0x94 {psk_addr}"
    lldb.debugger.HandleCommand(_command)



# command script import xxx/lldb_util.py
def __lldb_init_module(debugger, internal_dict):
    # 当采用加载脚本时会调用该方法
    debugger.HandleCommand('command script add -f lldb_util.dump_function dumpF')
    debugger.HandleCommand('command script add -f lldb_util.dump_mems dumpM')
    debugger.HandleCommand('command script add -f lldb_util.dump_registers dumpR')
    debugger.HandleCommand('command script add -f lldb_util.dump_ext_registers dumpR2')
    debugger.HandleCommand('command script add -f lldb_util.dump_line dumpL')
    debugger.HandleCommand('command script add -f lldb_util.read_mem_from_ptr readPtr')
    debugger.HandleCommand('command script add -f lldb_util.read_mem_by_easy measy')
    debugger.HandleCommand('command script add -f lldb_util.wechat_test_for_mem wechat_x19')
