.global conv2d
conv2d:
# a0: address of input
# a1: address of kernel
# a2: w
# a3: h
# a4: ksize
# a5: s

# prologue
	# addi sp, sp, -4
	# sw a0, 0(sp)

# start of your implementation
	sub t0, a2, a4 # w - ksize
	sub t1, a3, a4 # h - ksize
	add  t2, x0, x0 # i = 0
1:
	add  t3, x0, x0 # j = 0
2:
	add  t4, x0, x0 # sum = 0
	add  t5, x0, x0 # n = 0
3:
	add  t6, x0, x0 # m = 0
4:
	# a6, a7
	add a6, t2, t5 # (i+n)
	mul a6, a6, a2 # (i+n)*w
	add a6, a6, t3 # (i+n)*w + j
	add a6, a6, t6 # (i+n)*w + j+m
	slli a6, a6, 2
	add a6, a6, a0 # address of input[]
	lw  a6, 0(a6) # input[]

	mul a7, a4, t5 # n*ksize
	add a7, a7, t6 # n*ksize + m
	slli a7, a7, 2
	add a7, a7, a1 # address of kernel[]
	lw  a7, 0(a7) # kernel[]

	mul a6, a7, a6 # input[] * kernel[]
	add t4, t4, a6 # sum += input * kernel

	add t6, t6, a5
	blt t6, a4, 4b # if m < ksize then goto tag 4
	add t5, t5, a5
	blt t5, a4, 3b # if n < ksize then goto tag 3

	mul a6, t2, a2 # i*w
	add a6, a6, t3 # i*w + j
	slli a6, a6, 2
	add a6, a0, a6 
	sw  t4, 0(a6) # input[i*w + j] = sum

	addi t3, t3, 1
	ble t3, t0, 2b # if j < w-ksize then goto tag 2

	addi t2, t2, 1
	ble t2, t1, 1b # if i < h-ksize then goto tag 1

# end of your implementation

# epilogue
	# lw a0, 0(sp)
	# addi sp, sp, 4
	ret
