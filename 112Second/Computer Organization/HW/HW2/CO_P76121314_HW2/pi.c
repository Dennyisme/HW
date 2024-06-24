"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"li t2, 0 \n\t" // t2 = 0 (i = 0)
"loop:\n\t" //
"addi %[others_cnt], %[others_cnt], 1\n\t"
"bge t2, %[N], exit\n\t" // if i>=N go to exit
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"li t3, 2\n\t" // t3 = 2
"addi %[mul_cnt], %[mul_cnt], 1\n\t"
"mul t3, t3, t2\n\t" // t3 = 2 * i
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi t3, t3, 1\n\t" // t1 = (2 * i) + 1
"addi %[lw_cnt], %[lw_cnt], 1\n\t"
"li t4, 1\n\t" // t4 = 1
"addi %[others_cnt], %[others_cnt], 1\n\t"
"fcvt.d.w f1, t3\n\t" // int -> double float
"addi %[others_cnt], %[others_cnt], 1\n\t"
"fcvt.d.w f2, t4\n\t" // int -> double float
"addi %[div_cnt], %[div_cnt], 1\n\t"
"fdiv.d f1, f2, f1\n\t" // f1 = 1 / (2 * i + 1) => positive term
"addi %[add_cnt], %[add_cnt], 1\n\t"
"add t3, t2, x0\n\t" // t3 = i
"addi %[others_cnt], %[others_cnt], 1\n\t"
"slli t3, t3, 63\n\t" // t3 left shift
"addi %[others_cnt], %[others_cnt], 1\n\t"
"beq t3, x0, add_term\n\t" // t3 == 0 go to add_term
"addi %[others_cnt], %[others_cnt], 1\n\t"
"bne t3, x0, sub_term\n\t" // t3 != 0 go to sub_term
"sub_term:\n\t" // sub_term
"addi %[sub_cnt], %[sub_cnt], 1\n\t"
"fsub.d %[pi], %[pi], f1\n\t" // pi = pi - term
"addi %[others_cnt], %[others_cnt], 1\n\t"
"jal prepare_next_loop\n\t" // go to prepare_next_loop
"add_term:\n\t" // add_term
"addi %[add_cnt], %[add_cnt], 1\n\t"
"fadd.d %[pi], %[pi], f1\n\t" // pi = pi + term
"prepare_next_loop:\n\t" // prepare_next_loop
"addi %[add_cnt], %[add_cnt], 1\n\t"
"addi t2, t2, 1\n\t" // i++
"addi %[others_cnt], %[others_cnt], 1\n\t"
"jal loop\n\t" // go to loop
"exit:\n\t" // exit
