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
        f.write(output)
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
    print(f'mem read -c {count} --force {addr}')
    interpreter.HandleCommand(f'mem read -c {count} --force {addr}', return_object)
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


# command script import xxx/lldb_util.py
def __lldb_init_module(debugger, internal_dict):
    # 当采用加载脚本时会调用该方法
    debugger.HandleCommand('command script add -f lldb_util.dump_function dumpF')
    debugger.HandleCommand('command script add -f lldb_util.dump_mems dumpM')
    debugger.HandleCommand('command script add -f lldb_util.dump_registers dumpR')
    debugger.HandleCommand('command script add -f lldb_util.dump_ext_registers dumpR2')
    debugger.HandleCommand('command script add -f lldb_util.dump_line dumpL')
