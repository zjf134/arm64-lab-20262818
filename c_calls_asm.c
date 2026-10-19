#include <stdio.h>

extern int asm_add18(int x);
extern int asm_call_c(int x);

int c_add3(int x)
{
    return x + 3;
}

int main(void)
{
    int direct = asm_add18(8);
    int nested = asm_call_c(8);
    printf("C -> ASM: asm_add18(8) = %d\n", direct);
    printf("C -> ASM -> C: asm_call_c(8) = %d\n", nested);
    return (direct == 26 && nested == 29) ? 0 : 1;
}
