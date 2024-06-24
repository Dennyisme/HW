#include<stdio.h>
int main()
{ 
    int f, i, j;
    int h[9] = {0}, x[6] = {0}, y[6] = {0}; 
    FILE *input = fopen("../input/3.txt", "r");
    for(i = 0; i < 9; i++) fscanf(input, "%d", &h[i]);
    for(i = 0; i < 6; i++) fscanf(input, "%d", &x[i]);
    for(i = 0; i < 6; i++) fscanf(input, "%d", &y[i]);
    fclose(input);
    int *p_x = &x[0] ;
    int *p_h = &h[0] ;
    int *p_y = &y[0] ;
    for (i = 0; i < 3; i++){ 
        for (j = 0; j < 2; j++){        	
            for (f = 0; f < 3; f++)
                asm volatile(
                    // hif
                    "lw x5, 0(%[p_h])\n\t" // load hif to x5
                    // xfj
                    "lw x6, 0(%[p_x])\n\t" // load xfj to x6
                    // hif*xfj
                    "mul x6, x5, x6\n\t" // x6 = hif*xfj
                    // yij
                    "lw x7, 0(%[p_y])\n\t"
                    "add x7, x7, x6\n\t"
                    "sw x7, 0(%[p_y])\n\t"
                    : // Output section
                    : [p_h] "r"(p_h + 3*i + f), [p_x] "r"(p_x + 2*f +j), [p_y] "r"(p_y + 2*i + j) // Input section
                    : "x5", "x6", "x7" // Clobber list
                );
	}
    }
    p_y = &y[0];
    for(i = 0; i < 6; i++)
    printf("%d ", *p_y++);
    printf("\n");
    return 0; 
 
}
