
FUNCTION_Byte_Length = 4 # 4字节一个指令
INT_Mask = 0xFF_FF_FF_FF_FF_FF_FF_FF # 64
INT_Mask_32 = 0xFF_FF_FF_FF
INT_Mask_64 = INT_Mask
INT_Mask_128 = 0xFF_FF_FF_FF_FF_FF_FF_FF
LATIN_LITTLE = 1
LATIN_BIG = 0


MEMORY_SIZE = 8 # 64位
MEMORY_SIZE_32 = 4


Bytes_to_Bits = 8

REGISTER_PC = "pc"
REGISTER_CPSR = "cpsr"
REGISTER_LR = "lr"
REGISTER_SP = "sp"
REGISTER_FP = "fp"
REGISTER_TMP = "tmp"

REGISTER_MODE_X = "x" # 64位
REGISTER_MODE_W = "w" # 32位
REGISTER_MODE_Q = "q" # 额外寄存器 128位
REGISTER_MODE_V = "v" # 额外寄存器 128位. V Q是同等的
REGISTER_MODE_BYTE = "b" # 8位
REGISTER_MODE_H = "h" #
REGISTER_MODE_WORD = "word" #


BASE_MODES = {REGISTER_MODE_X, REGISTER_MODE_W} # 通用寄存器
EXTRA_MODES = {REGISTER_MODE_Q, REGISTER_MODE_V} # 额外寄存器


MODES_MAPPING = {REGISTER_MODE_Q: 128, REGISTER_MODE_X: 64, REGISTER_MODE_W: 32, REGISTER_MODE_BYTE: 8}
MODES_REVERSE_MAPPING = {128: REGISTER_MODE_Q, 64: REGISTER_MODE_X, 32: REGISTER_MODE_W, 8: REGISTER_MODE_BYTE}
MEMORY_MALLOC_ADDRESS_OFFSET = 0x8f_FF_FFFF_FFFF_FFFF # malloc分配的内存，地址以此作为基准

CODE_Normal = 0
CODE_Redirect = 1
CODE_Ret = 2


EXIT_CODE_ERROR = -1
EXIT_CODE = 0


class NtException(Exception): pass
class StopException(NtException): pass
class StopFuncException(StopException): pass
class OverflowFuncException(NtException): pass
class RetException(NtException): pass
