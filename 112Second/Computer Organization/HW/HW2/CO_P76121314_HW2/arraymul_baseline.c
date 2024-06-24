"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"li t0, 0 \n\t" // t0 = 0 (i = 0)
"loop:\n\t" // loop
"addi %[others_cnt], %[others_cnt], 1\n\t"
"bge t0, %[arr_size], exit\n\t" // if i>=arr_size go to exit
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi sp, sp, -4\n\t" // sp = sp -4
"addi %[sw_cnt], %[sw_cnt], 1\n\t"
"sw t0, 0(sp)\n\t" // store i to sp
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"lh t0, 0(%[h])\n\t" // t0 = p_h[i] 
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"lh t1, 0(%[x])\n\t" // t1 = p_x[i]
"addi %[mul_cnt], %[mul_cnt], 1\n\t"
"mul t0, t0, t1\n\t" // t0 = p_h[i] * p_x[i]
"addi %[add_cnt], %[add_cnt], 1\n\t"
"add t0, t0, %[id]\n\t" // t0 = p_h[i] * p_x[i] + id
"addi %[sw_cnt], %[sw_cnt], 1\n\t"
"sh t0, 0(%[y])\n\t" // store t0 to p_y[i] address
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi  %[h], %[h], 2 \n\t" // move *h to next element
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi  %[x], %[x], 2 \n\t" // move *x to next element
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi  %[y], %[y], 2 \n\t" // move *y to next element
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"lw t0, 0(sp)\n\t" // load i to t0
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi sp, sp, 4\n\t" // sp = sp +4
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi t0, t0, 1\n\t" // i ++
"addi %[others_cnt], %[others_cnt], 1\n\t"
"jal loop\n\t"// go to loop
"exit:\n\t" // exit