#include <stdio.h>
int main ()
{
    int a[10] = {0}, b[10] = {0}, c[10] = {0}; 
    int i, arr_size = 10;
    FILE *input = fopen("../input/2.txt", "r");
    for(i = 0; i < arr_size; i++) fscanf(input, "%d", &a[i]);
    for(i = 0; i < arr_size; i++) fscanf(input, "%d", &b[i]);
    for(i = 0; i < arr_size; i++) fscanf(input, "%d", &c[i]);
    fclose(input);
    int *p_a = &a[0];
    int *p_b = &b[0];
    int *p_c = &c[0];
    /* Original C code segment
    for (int i = 0; i < arr_size; i++){
    *p_c++ = *p_a++ - *p_b++;
    }
    */
    for (int i = 0; i < arr_size; i++)
    asm volatile(
        "slli x5, %[index], 2\n\t"
        "add x6, x5, %[p_a]\n\t"
        "lw x6,0(x6)\n\t"
        "add x7, x5, %[p_b]\n\t"
        "lw x7 ,0(x7)\n\t"
        "sub x28, x6, x7\n\t"
        "add x29, x5, %[p_c]\n\t"
        "sw x28, 0(x29)\n\t"
        :[p_c] "+r"(p_c)
        :[p_a] "r"(p_a), [p_b] "r"(p_b), [index] "r"(i)
        : "x5", "x6", "x7", "x28" // Clobber list
    );
    p_c = &c[0];
    for (int i = 0; i < arr_size; i++)
    printf("%d ", *p_c++);
    printf("\n");
    return 0;
}
