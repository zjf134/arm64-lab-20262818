# ARM64 assembly lab — 20262818

在 Ubuntu2204 x86-64 虚拟机中交叉编译 AArch64 Linux 程序，使用 QEMU user mode 运行并通过 GDB remote 单步跟踪。没有使用香橙派实体硬件。

## 内容

- `hello.s`：独立 `_start`，使用 Linux AArch64 `write`/`exit` 系统调用。
- `c_calls_asm.c`、`asm_functions.s`：C→汇编以及 C→汇编→C，预期结果分别为 26、29。
- `week040120262818.c`：题目原程序，学号后两位 18，`main` 返回 30。
- `Makefile`：静态链接、关闭优化和省略帧指针，保留可观察的函数调用。
- `run-trace.sh`、`trace.py`：QEMU GDB stub + GDB Python，记录 main/f/g 的 25 条指令以及寄存器、96 字节栈内存快照。
- `check.py`：检查三个程序的输出和退出状态。
- `setup-toolchain.py`：从 Ubuntu APT 仓库下载并解包依赖到用户目录，不需要 sudo，不修改系统已安装的软件包。

## 本次验证环境

Ubuntu 22.04，AArch64 GCC 11.4.0，binutils 2.38，QEMU 6.2.0，GDB multiarch 12.1。

```bash
python3 setup-toolchain.py
source ~/.local/arm64-toolchain/env.sh
make check
./run-trace.sh
```

工具链使用 Ubuntu 已有的 APT 索引与系统 GDB Python 文件 `/usr/share/gdb`，因此须先具备 Ubuntu 22.04 的基础 GCC/GDB 运行依赖。本次虚拟机已具备这些依赖。也可以在已安装交叉工具链、qemu-user、gdb-multiarch 的环境直接执行 `make check`。

`trace.py` 中的函数偏移及 25 条指令断言针对本次 GCC 11.4.0、Makefile 参数产生的代码；换编译器或优化选项后应按新的反汇编调整，不能照搬栈地址。

## 手动调试

终端一：

```bash
source ~/.local/arm64-toolchain/env.sh
qemu-aarch64 -g 12368 build/week040120262818
```

终端二：

```bash
source ~/.local/arm64-toolchain/env.sh
gdb-multiarch --data-directory=/usr/share/gdb build/week040120262818
```

GDB 内：

```gdb
set architecture aarch64
target remote 127.0.0.1:12368
break *main
continue
disassemble /r f
display /i $pc
info registers pc sp x29 x30 w0 w1
x/8gx $sp
si
```

重复 `si`、`info registers`、`x/8gx $sp` 记录变化；`ni` 会跳过调用，观察 g 内部时应使用 `si`。

## 结果

```text
Hello World! ARM64 20262818
PASS hello: exit=0
C -> ASM: asm_add18(8) = 26
C -> ASM -> C: asm_call_c(8) = 29
PASS c_calls_asm: exit=0
PASS week040120262818: exit=30
TRACE_PASS: 25 instructions, f frame restored, main result=30
```

f 入口保存 FP/LR 并分配 48 字节；x 位于 SP+28，i 位于 SP+44；g 额外使用 16 字节。AArch64 的 `bl` 写 X30，`ret` 默认读 X30；不能套用 x86 `call` 自动将返回地址压栈的解释。

生成的二进制、工具链包和日志不进入 Git 历史。实验报告、逐指令 CSV/JSON 和未重绘的虚拟机终端截图保存在本地 Obsidian 提交包中。
