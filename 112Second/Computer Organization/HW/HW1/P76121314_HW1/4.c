#include<stdio.h>
int main()
{ 
    int i = 0;
    int h[9] = {0}, x[6] = {0}, y[6] = {0}; 
    FILE *input = fopen("../input/4.txt", "r");
    for(i = 0; i < 9; i++) fscanf(input, "%d", &h[i]);
    for(i = 0; i < 6; i++) fscanf(input, "%d", &x[i]);
    for(i = 0; i < 6; i++) fscanf(input, "%d", &y[i]);
    fclose(input);
    
    int *p_x = &x[0];
    int *p_h = &h[0];
    int *p_y = &y[0];
    
    asm volatile(
        "li x9, 0\n\t" // i = 0
        "li x5, 3\n\t" 
        "li x6, 2\n\t"
        "outer_loop:\n\t"
        "li x18, 0\n\t" // j = 0 
        "center_loop:\n\t"
        "li x19, 0\n\t" // f = 0
        "inner_loop:\n\t"
        // hif
        "mul x7, x9, x5\n\t" // 3*i
        "add x7, x19, x7\n\t" // 3*i+f
        "slli x7, x7, 2\n\t" // 4*(3*i+f)
        "add x7, %[p_h], x7\n\t" // hij address
        "lw x7, 0(x7)\n\t"
        // xfj
        "mul x28, x19, x6\n\t" // 2*f
        "add x28, x28, x18\n\t" // 2*f + j
        "slli x28, x28, 2\n\t" // 4*(2*f + j)
        "add x28, %[p_x], x28\n\t" // xfj address
        "lw x28, 0(x28)\n\t"
        // hij*xfj
        "mul x29, x28, x7\n\t"
        // yij
        "mul x30, x9, x6\n\t" // 2*i
        "add x30, x30, x18\n\t" // 2*i+j
        "slli x30, x30, 2\n\t" // 4*(2*i+j)
        "add x30, %[p_y], x30\n\t" // yij address
        "lw x31, 0(x30)\n\t"
        "add x31, x31, x29\n\t"
        "sw x31, 0(x30)\n\t"
        "addi x19, x19, 1\n\t"
        "bne x5, x19, inner_loop\n\t"
        "addi x18, x18, 1\n\t"
        "bne x6, x18, center_loop\n\t"
        "addi x9, x9, 1\n\t"
        "bne x5, x9, outer_loop\n\t"
        : 
        : [p_h] "r"(p_h), [p_x] "r"(p_x), [p_y] "r"(p_y)
        : "x5", "x6", "x7", "x9", "x18", "x19", "x28", "x29", "x30", "x31" // Clobber list
    );

    p_y = &y[0];
    for(i = 0; i < 6; i++)
        printf("%d ", *p_y++);
    printf("\n");
    return 0; 
 
}
