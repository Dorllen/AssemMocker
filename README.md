The Project is “mocked” assembler by python language

20200923：新增simple目录，新增对sisc_core精简方式案例


202011月:
1. sisc_core精简方式核心补充：Mem的核心是每个slot值范围 0~255. 并且没有Register，每个slot值是Int类型且无状态。Stack类型是临时包装类型(对Mem的引用，类似于指针），最终存储的还是Int类型
2. 强调Mem特性：Mem值存储，对于不同的"值类型/值模式"存储，需进行Mem模式切，而不是Int值类型切换（类似以前的Register，sisc不同该特性）。
3. sisc_core 赋值方式：`x0[3:]=value0；x0[3]=value1` 或 `(x0 + 3).w = value2`. value0/value2可以是Int、int、Stack, value1是Int、int。x0可以是Mem、Stack
4. sisc_core Stack用途：相当于一个窗口指向Mem，并且有窗口大小
5. sisc_core 读取方式：`x0, x1 = Mem.mem_read(x16 - 0x38, 2, byte_size=8)` 或 `x0, x1 = (x16 - 0x38).ldp`
6. sisc_core 中的计算是带符号的，如遇到带符号计算与移位操作同时存在可能会有问题，需将带符号转换成无符号 （xxx & 0xFFFFFFFF_FFFFFFFF). 例：`(-3 & 0xFFFF)  >> 2 != -3 >> 2 & 0xFFFF`
7. sisc_core 新增v2版本，v1中的 `x25.w[w8 << 2]`，换成：`(x15 + w8 << 3).w`。好处在于：x0.x 不需要写成 `x0.x[0]`

sisc 和 cisc 区别在于：
1. sisc 是精简模式，cisc 是复杂/混合模式
2. sisc 值类型只有Int类型，cisc 值类型是Register类型，且Register类型很复杂
3. cisc 目标是使框架更接近真实CPU运行环境，sisc是对内存、指令代码等的精简操作工具


##Thanks For Jetbrains's Supports!!!! My Request ID is: 31122020/6422328, email is: bigpe...@163.com。Thanks!
