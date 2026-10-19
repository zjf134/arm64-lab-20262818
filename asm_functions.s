.text
.global asm_add18
.type asm_add18, %function
asm_add18:
    add w0, w0, #18
    ret
.size asm_add18, . - asm_add18

.global asm_call_c
.type asm_call_c, %function
asm_call_c:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    bl c_add3
    add w0, w0, #18
    ldp x29, x30, [sp], #16
    ret
.size asm_call_c, . - asm_call_c
.section .note.GNU-stack,"",%progbits
