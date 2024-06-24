"addi %[add_cnt], %[add_cnt], 1\n\t"
"add t0, x0, x0\n\t" // i = 0
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi sp, sp, -4\n\t" // sp = sp - 4
"improved_loop:\n\t" // improved_loop
"addi %[others_cnt], %[others_cnt], 1\n\t"
"bge t0, %[arr_size], exit\n\t" // i >= arr_size
"addi %[sw_cnt], %[sw_cnt], 1\n\t"
"sw t0, 0(sp)\n\t" // store i to sp
"addi %[others_cnt], %[others_cnt], 1\n\t"
"vsetvli t0, %[arr_size], e16\n\t" // (t0 = how much elements calculated together)  ( %[arr_size] = vector length ) (e16 = element's bits number )
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"vle16.v v0, (%[h])\n\t" // load h[i] ~ h[i+t0-1] to v0
"addi %[lw_cnt], %[lw_cnt], 1\n\t" 
"vle16.v v1, (%[x])\n\t" // load x[i] ~ x[i+t0-1] to v1
"addi %[mul_cnt], %[mul_cnt], 1\n\t"
"vmul.vv v0, v0, v1\n\t" // p_h[i] * p_x[i] ~ p_h[i-t0-1] * p_x[i+t0-1]
"addi %[add_cnt], %[add_cnt], 1\n\t"
"vadd.vx v0, v0, %[id]\n\t" // v0 = v0 + id
"addi %[sw_cnt], %[sw_cnt], 1\n\t"
"vse16.v v0, (%[y])\n\t" // v0 store tp y[i] ~ y[i+t0-1]
"addi %[others_cnt], %[others_cnt], 1\n\t"
"slli t0, t0, 1\n\t" // t0 * 2
"addi %[add_cnt], %[add_cnt], 1\n\t"
"add %[h], %[h], t0\n\t" // h[i + t0]
"addi %[add_cnt], %[add_cnt], 1\n\t"
"add %[x], %[x], t0\n\t" // x[i + t0]
"addi %[add_cnt], %[add_cnt], 1\n\t"
"add %[y], %[y], t0\n\t" // y[i + t0]
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"lw t0, 0(sp)\n\t" // load i to t0
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi t0, t0, 8\n\t" // i+=8
"addi %[others_cnt], %[others_cnt], 1\n\t"
"jal improved_loop\n\t" // go to improved_loop
"exit:\n\t" // exit
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi sp, sp, 4\n\t" // sp = sp + 4