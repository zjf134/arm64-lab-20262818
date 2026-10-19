// AArch64 Linux: write(1, message, length), then exit(0).
.section .rodata
message:
    .ascii "Hello World! ARM64 20262818\n"
.equ message_len, . - message

.section .text
.global _start
.type _start, %function
_start:
    mov x0, #1
    adr x1, message
    mov x2, #message_len
    mov x8, #64
    svc #0
    mov x0, #0
    mov x8, #93
    svc #0
.size _start, . - _start
.section .note.GNU-stack,"",%progbits
