	.file	"TVMMod"
	.text
	.globl	__tvm_ffi_matmul_kernel
	.p2align	4
	.type	__tvm_ffi_matmul_kernel,@function
__tvm_ffi_matmul_kernel:
.Lfunc_begin0:
	.file	1 "." "IRModule.CodeGenLLVM"
	.loc	1 0 0
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset %rbx, -16
	cmpl	$3, %edx
	jne	.LBB0_62
.Ltmp0:
	testq	%rsi, %rsi
	je	.LBB0_63
.Ltmp1:
	movl	(%rsi), %eax
.Ltmp2:
	cmpl	$63, %eax
	jle	.LBB0_7
.Ltmp3:
	cmpl	$70, %eax
	jne	.LBB0_9
.Ltmp4:
	movq	8(%rsi), %rax
.Ltmp5:
	addq	$24, %rax
	movl	16(%rsi), %ecx
.Ltmp6:
	cmpl	$63, %ecx
	jg	.LBB0_10
.Ltmp7:
.LBB0_5:
	cmpl	$7, %ecx
	ja	.LBB0_59
.Ltmp8:
	movl	$145, %edx
.Ltmp9:
	btl	%ecx, %edx
	jb	.LBB0_14
	jmp	.LBB0_59
.Ltmp10:
.LBB0_7:
	cmpl	$7, %eax
	ja	.LBB0_58
.Ltmp11:
	movl	$145, %ecx
	btl	%eax, %ecx
	jae	.LBB0_58
.Ltmp12:
.LBB0_9:
	movq	8(%rsi), %rax
.Ltmp13:
	movl	16(%rsi), %ecx
.Ltmp14:
	cmpl	$63, %ecx
	jle	.LBB0_5
.Ltmp15:
.LBB0_10:
	cmpl	$70, %ecx
	jne	.LBB0_14
.Ltmp16:
	movq	24(%rsi), %rcx
	addq	$24, %rcx
	movl	32(%rsi), %edx
.Ltmp17:
	cmpl	$63, %edx
	jg	.LBB0_15
.Ltmp18:
.LBB0_12:
	cmpl	$7, %edx
	ja	.LBB0_60
.Ltmp19:
	movl	$145, %edi
	btl	%edx, %edi
	jb	.LBB0_17
	jmp	.LBB0_60
.Ltmp20:
.LBB0_14:
	movq	24(%rsi), %rcx
	movl	32(%rsi), %edx
.Ltmp21:
	cmpl	$63, %edx
	jle	.LBB0_12
.Ltmp22:
.LBB0_15:
	cmpl	$70, %edx
	jne	.LBB0_17
.Ltmp23:
	movq	40(%rsi), %r8
	addq	$24, %r8
	jmp	.LBB0_18
.Ltmp24:
.LBB0_17:
	movq	40(%rsi), %r8
.Ltmp25:
.LBB0_18:
	testq	%rax, %rax
	je	.LBB0_58
.Ltmp26:
	cmpl	$2, 16(%rax)
	jne	.LBB0_64
.Ltmp27:
	cmpw	$1, 22(%rax)
	jne	.LBB0_65
.Ltmp28:
	cmpb	$32, 21(%rax)
	jne	.LBB0_65
.Ltmp29:
	cmpb	$2, 20(%rax)
	jne	.LBB0_65
.Ltmp30:
	cmpl	$1, 8(%rax)
	jne	.LBB0_66
.Ltmp31:
	testq	%rcx, %rcx
	je	.LBB0_59
.Ltmp32:
	cmpl	$2, 16(%rcx)
	jne	.LBB0_67
.Ltmp33:
	cmpw	$1, 22(%rcx)
	jne	.LBB0_68
.Ltmp34:
	cmpb	$32, 21(%rcx)
	jne	.LBB0_68
.Ltmp35:
	cmpb	$2, 20(%rcx)
	jne	.LBB0_68
.Ltmp36:
	cmpl	$1, 8(%rcx)
	jne	.LBB0_69
.Ltmp37:
	testq	%r8, %r8
	je	.LBB0_60
.Ltmp38:
	cmpl	$2, 16(%r8)
	jne	.LBB0_70
.Ltmp39:
	cmpw	$1, 22(%r8)
	jne	.LBB0_71
.Ltmp40:
	cmpb	$32, 21(%r8)
	jne	.LBB0_71
.Ltmp41:
	cmpb	$2, 20(%r8)
	jne	.LBB0_71
.Ltmp42:
	cmpl	$1, 8(%r8)
	jne	.LBB0_72
.Ltmp43:
	movq	24(%rax), %r11
.Ltmp44:
	movq	32(%rax), %rdi
.Ltmp45:
	movl	12(%rax), %edx
.Ltmp46:
	movq	24(%rcx), %r10
.Ltmp47:
	movq	32(%rcx), %rsi
.Ltmp48:
	movq	24(%r8), %r9
.Ltmp49:
	movq	32(%r8), %rbx
.Ltmp50:
	testq	%rdi, %rdi
	je	.LBB0_38
.Ltmp51:
	cmpl	$1, 8(%rdi)
	jne	.LBB0_73
.Ltmp52:
.LBB0_38:
	movq	(%rax), %rdi
.Ltmp53:
	testq	%rdi, %rdi
	je	.LBB0_74
.Ltmp54:
	testq	%rsi, %rsi
	je	.LBB0_42
.Ltmp55:
	cmpl	$256, (%rsi)
	jne	.LBB0_76
.Ltmp56:
	movl	8(%rsi), %esi
.Ltmp57:
	cmpl	$1, %esi
	jne	.LBB0_76
.Ltmp58:
.LBB0_42:
	cmpl	12(%rcx), %edx
	jne	.LBB0_75
.Ltmp59:
	movq	(%rcx), %rsi
	testq	%rsi, %rsi
	je	.LBB0_77
.Ltmp60:
	testq	%rbx, %rbx
	je	.LBB0_46
.Ltmp61:
	cmpl	$1, 8(%rbx)
	jne	.LBB0_78
.Ltmp62:
.LBB0_46:
	cmpl	12(%r8), %edx
	jne	.LBB0_80
.Ltmp63:
	movq	(%r8), %rdx
.Ltmp64:
	testq	%rdx, %rdx
	je	.LBB0_81
.Ltmp65:
	cmpl	$1, (%r11)
	jne	.LBB0_85
.Ltmp66:
	cmpl	$256, 8(%r11)
	jne	.LBB0_86
.Ltmp67:
	cmpq	$0, 40(%rax)
	jne	.LBB0_88
.Ltmp68:
	cmpl	$256, (%r10)
	jne	.LBB0_92
.Ltmp69:
	cmpl	$256, 8(%r10)
	jne	.LBB0_93
.Ltmp70:
	cmpq	$0, 40(%rcx)
	jne	.LBB0_94
.Ltmp71:
	cmpl	$1, (%r9)
	jne	.LBB0_97
.Ltmp72:
	cmpl	$256, 8(%r9)
	jne	.LBB0_98
.Ltmp73:
	cmpq	$0, 40(%r8)
	jne	.LBB0_99
.Ltmp74:
	callq	matmul_kernel_compute_
.Ltmp75:
	xorl	%eax, %eax
	popq	%rbx
.Ltmp76:
	.cfi_def_cfa_offset 8
	retq
.Ltmp77:
.LBB0_58:
	.cfi_def_cfa_offset 16
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.9(%rip), %rcx
	jmp	.LBB0_61
.Ltmp78:
.LBB0_59:
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.12(%rip), %rcx
	jmp	.LBB0_61
.Ltmp79:
.LBB0_60:
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.13(%rip), %rcx
.Ltmp80:
.LBB0_61:
	leaq	.L.str.4(%rip), %r8
	leaq	.L.str.5(%rip), %r9
	jmp	.LBB0_83
.Ltmp81:
.LBB0_62:
	leaq	.L.str.6(%rip), %rax
	leaq	.L.str.5(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.1(%rip), %rdx
.Ltmp82:
	leaq	.L.str.2(%rip), %rcx
	leaq	.L.str.3(%rip), %r8
	jmp	.LBB0_82
.Ltmp83:
.LBB0_63:
	subq	$16, %rsp
	.cfi_adjust_cfa_offset 16
	xorps	%xmm0, %xmm0
	movups	%xmm0, (%rsp)
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.7(%rip), %rdx
.Ltmp84:
	leaq	.L.str.4(%rip), %rcx
	leaq	.L.str.5(%rip), %r8
	leaq	.L.str.6(%rip), %r9
	movl	$4, %esi
.Ltmp85:
	jmp	.LBB0_84
.Ltmp86:
.LBB0_64:
	.cfi_def_cfa_offset 16
	leaq	.L.str.13(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_102
.Ltmp87:
.LBB0_65:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_102
.Ltmp88:
.LBB0_66:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_102
.Ltmp89:
.LBB0_67:
	leaq	.L.str.13(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	jmp	.LBB0_96
.Ltmp90:
.LBB0_68:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	jmp	.LBB0_96
.Ltmp91:
.LBB0_69:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	jmp	.LBB0_96
.Ltmp92:
.LBB0_70:
	leaq	.L.str.13(%rip), %r9
	leaq	.L.str.10(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	jmp	.LBB0_89
.Ltmp93:
.LBB0_71:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	jmp	.LBB0_101
.Ltmp94:
.LBB0_72:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	jmp	.LBB0_101
.Ltmp95:
.LBB0_73:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
.Ltmp96:
	leaq	.L.str.15(%rip), %rdx
.Ltmp97:
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.9(%rip), %r9
.Ltmp98:
	jmp	.LBB0_79
.Ltmp99:
.LBB0_74:
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp100:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.16(%rip), %rdx
.Ltmp101:
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.9(%rip), %r8
	jmp	.LBB0_82
.Ltmp102:
.LBB0_75:
	leaq	.L.str.31(%rip), %rax
	leaq	.L.str.30(%rip), %r10
.Ltmp103:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp104:
	leaq	.L.str.28(%rip), %rcx
	jmp	.LBB0_95
.Ltmp105:
.LBB0_76:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp106:
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.12(%rip), %r9
.Ltmp107:
	jmp	.LBB0_79
.Ltmp108:
.LBB0_77:
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp109:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.22(%rip), %rdx
.Ltmp110:
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.12(%rip), %r8
	jmp	.LBB0_82
.Ltmp111:
.LBB0_78:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp112:
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.13(%rip), %r9
.Ltmp113:
.LBB0_79:
	movl	$7, %esi
	pushq	$0
	.cfi_adjust_cfa_offset 8
	jmp	.LBB0_90
.Ltmp114:
.LBB0_80:
	.cfi_def_cfa_offset 16
	leaq	.L.str.31(%rip), %rax
	leaq	.L.str.30(%rip), %r10
.Ltmp115:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp116:
	leaq	.L.str.32(%rip), %rcx
	jmp	.LBB0_100
.Ltmp117:
.LBB0_81:
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp118:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.23(%rip), %rdx
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.13(%rip), %r8
.Ltmp119:
.LBB0_82:
	leaq	.L.str.4(%rip), %r9
.Ltmp120:
.LBB0_83:
	movl	$6, %esi
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	pushq	%r10
	.cfi_adjust_cfa_offset 8
.Ltmp121:
.LBB0_84:
	callq	__tvm_set_raised_6
	addq	$16, %rsp
	.cfi_adjust_cfa_offset -16
	movl	$-1, %eax
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.Ltmp122:
.LBB0_85:
	.cfi_def_cfa_offset 16
	leaq	.L.str.12(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp123:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.34(%rip), %rcx
	jmp	.LBB0_87
.Ltmp124:
.LBB0_86:
	leaq	.L.str.36(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp125:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.35(%rip), %rcx
.Ltmp126:
.LBB0_87:
	leaq	.L.str.29(%rip), %r8
	leaq	.L.str.9(%rip), %r9
.Ltmp127:
	jmp	.LBB0_102
.Ltmp128:
.LBB0_88:
	leaq	.L.str.9(%rip), %r9
.Ltmp129:
	leaq	.L.str.10(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.37(%rip), %rcx
	leaq	.L.str.29(%rip), %r8
.Ltmp130:
.LBB0_89:
	movl	$8, %esi
	pushq	%r9
	.cfi_adjust_cfa_offset 8
.Ltmp131:
.LBB0_90:
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	jmp	.LBB0_91
.Ltmp132:
.LBB0_92:
	.cfi_def_cfa_offset 16
	leaq	.L.str.36(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp133:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.38(%rip), %rcx
	jmp	.LBB0_95
.Ltmp134:
.LBB0_93:
	leaq	.L.str.36(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp135:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.39(%rip), %rcx
	jmp	.LBB0_95
.Ltmp136:
.LBB0_94:
	leaq	.L.str.9(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp137:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.40(%rip), %rcx
.Ltmp138:
.LBB0_95:
	leaq	.L.str.29(%rip), %r8
.Ltmp139:
.LBB0_96:
	leaq	.L.str.12(%rip), %r9
	jmp	.LBB0_102
.Ltmp140:
.LBB0_97:
	leaq	.L.str.12(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp141:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.41(%rip), %rcx
	jmp	.LBB0_100
.Ltmp142:
.LBB0_98:
	leaq	.L.str.36(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp143:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.42(%rip), %rcx
	jmp	.LBB0_100
.Ltmp144:
.LBB0_99:
	leaq	.L.str.9(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp145:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.43(%rip), %rcx
.Ltmp146:
.LBB0_100:
	leaq	.L.str.29(%rip), %r8
.Ltmp147:
.LBB0_101:
	leaq	.L.str.13(%rip), %r9
.Ltmp148:
.LBB0_102:
	movl	$8, %esi
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	pushq	%r10
	.cfi_adjust_cfa_offset 8
.Ltmp149:
.LBB0_91:
	callq	__tvm_set_raised_12
	addq	$16, %rsp
	.cfi_adjust_cfa_offset -16
	movl	$-1, %eax
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.Ltmp150:
.Lfunc_end0:
	.size	__tvm_ffi_matmul_kernel, .Lfunc_end0-__tvm_ffi_matmul_kernel
	.cfi_endproc

	.p2align	4
	.type	__tvm_set_raised_6,@function
__tvm_set_raised_6:
.Lfunc_begin1:
	.cfi_startproc
	subq	$56, %rsp
	.cfi_def_cfa_offset 64
	movl	%esi, %eax
	movaps	64(%rsp), %xmm0
	movq	%rdx, 8(%rsp)
	movq	%rcx, 16(%rsp)
	movq	%r8, 24(%rsp)
	movq	%r9, 32(%rsp)
	movups	%xmm0, 40(%rsp)
	leaq	8(%rsp), %rsi
	movl	%eax, %edx
	callq	TVMFFIErrorSetRaisedFromCStrParts@PLT
	addq	$56, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	__tvm_set_raised_6, .Lfunc_end1-__tvm_set_raised_6
	.cfi_endproc

	.p2align	4
	.type	__tvm_set_raised_12,@function
__tvm_set_raised_12:
.Lfunc_begin2:
	.cfi_startproc
	subq	$104, %rsp
	.cfi_def_cfa_offset 112
	movl	%esi, %eax
	movaps	112(%rsp), %xmm0
	movq	%rdx, 8(%rsp)
	movq	%rcx, 16(%rsp)
	movq	%r8, 24(%rsp)
	movq	%r9, 32(%rsp)
	leaq	.L.str.4(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	.L.str.5(%rip), %rcx
	movq	%rcx, 48(%rsp)
	movups	%xmm0, 56(%rsp)
	xorps	%xmm0, %xmm0
	movups	%xmm0, 72(%rsp)
	movups	%xmm0, 88(%rsp)
	leaq	8(%rsp), %rsi
	movl	%eax, %edx
	callq	TVMFFIErrorSetRaisedFromCStrParts@PLT
	addq	$104, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end2:
	.size	__tvm_set_raised_12, .Lfunc_end2-__tvm_set_raised_12
	.cfi_endproc

	.p2align	4
	.type	matmul_kernel_compute_,@function
matmul_kernel_compute_:
.Lfunc_begin3:
	.loc	1 0 0
	.cfi_startproc
	pushq	%r15
	.cfi_def_cfa_offset 16
	pushq	%r14
	.cfi_def_cfa_offset 24
	pushq	%r12
	.cfi_def_cfa_offset 32
	pushq	%rbx
	.cfi_def_cfa_offset 40
	.cfi_offset %rbx, -40
	.cfi_offset %r12, -32
	.cfi_offset %r14, -24
	.cfi_offset %r15, -16
.Ltmp151:
	leaq	15360(%rsi), %rax
	xorl	%ecx, %ecx
	xorps	%xmm0, %xmm0
.Ltmp152:
.LBB3_1:
	testl	%ecx, %ecx
	jne	.LBB3_8
.Ltmp153:
	.p2align	4
	movss	(%rdi), %xmm1
	movss	4(%rdi), %xmm2
	movss	8(%rdi), %xmm3
	movss	12(%rdi), %xmm4
	movss	16(%rdi), %xmm5
	movss	20(%rdi), %xmm6
	movss	24(%rdi), %xmm7
	movss	28(%rdi), %xmm8
	movq	%rax, %r8
	xorl	%r9d, %r9d
.Ltmp154:
	.p2align	4
.LBB3_3:
	movq	%r9, %r10
	shlq	$5, %r10
.Ltmp155:
	movq	%r9, %r11
	shlq	$7, %r11
	addq	%rdx, %r11
	movq	%r8, %rbx
	xorl	%r14d, %r14d
.Ltmp156:
	.p2align	4
.LBB3_4:
	leaq	(%r10,%r14), %r15
.Ltmp157:
	movss	(%rsi,%r15,4), %xmm9
	.loc	1 28 17
	mulss	%xmm1, %xmm9
	addss	%xmm0, %xmm9
.Ltmp158:
	.loc	1 0 17 is_stmt 0
	movss	1024(%rsi,%r15,4), %xmm10
	.loc	1 28 17
	mulss	%xmm2, %xmm10
	addss	%xmm9, %xmm10
.Ltmp159:
	.loc	1 0 17
	movss	2048(%rsi,%r15,4), %xmm9
	.loc	1 28 17
	mulss	%xmm3, %xmm9
	addss	%xmm10, %xmm9
.Ltmp160:
	.loc	1 0 17
	movss	3072(%rsi,%r15,4), %xmm10
	.loc	1 28 17
	mulss	%xmm4, %xmm10
	addss	%xmm9, %xmm10
.Ltmp161:
	.loc	1 0 17
	movss	4096(%rsi,%r15,4), %xmm9
	.loc	1 28 17
	mulss	%xmm5, %xmm9
	addss	%xmm10, %xmm9
.Ltmp162:
	.loc	1 0 17
	movss	5120(%rsi,%r15,4), %xmm10
	.loc	1 28 17
	mulss	%xmm6, %xmm10
	addss	%xmm9, %xmm10
.Ltmp163:
	.loc	1 0 17
	movss	6144(%rsi,%r15,4), %xmm11
	.loc	1 28 17
	mulss	%xmm7, %xmm11
	addss	%xmm10, %xmm11
.Ltmp164:
	.loc	1 0 17
	movss	7168(%rsi,%r15,4), %xmm9
	.loc	1 28 17
	mulss	%xmm8, %xmm9
	addss	%xmm11, %xmm9
	movss	%xmm9, (%r11,%r14,4)
.Ltmp165:
	.loc	1 0 17
	movq	%rbx, %r15
	xorl	%r12d, %r12d
.Ltmp166:
	.p2align	4
.LBB3_5:
	.loc	1 28 17
	movss	32(%rdi,%r12), %xmm10
.Ltmp167:
	mulss	-7168(%r15), %xmm10
	movss	36(%rdi,%r12), %xmm11
	addss	%xmm9, %xmm10
	mulss	-6144(%r15), %xmm11
	addss	%xmm10, %xmm11
.Ltmp168:
	movss	40(%rdi,%r12), %xmm9
	mulss	-5120(%r15), %xmm9
	addss	%xmm11, %xmm9
.Ltmp169:
	movss	44(%rdi,%r12), %xmm10
	mulss	-4096(%r15), %xmm10
	addss	%xmm9, %xmm10
.Ltmp170:
	movss	48(%rdi,%r12), %xmm9
	mulss	-3072(%r15), %xmm9
	addss	%xmm10, %xmm9
.Ltmp171:
	movss	52(%rdi,%r12), %xmm10
	mulss	-2048(%r15), %xmm10
	addss	%xmm9, %xmm10
.Ltmp172:
	movss	56(%rdi,%r12), %xmm11
	mulss	-1024(%r15), %xmm11
	addss	%xmm10, %xmm11
.Ltmp173:
	movss	60(%rdi,%r12), %xmm9
	mulss	(%r15), %xmm9
	addss	%xmm11, %xmm9
.Ltmp174:
	.loc	1 0 0
	addq	$32, %r12
.Ltmp175:
	addq	$8192, %r15
	cmpq	$992, %r12
	jne	.LBB3_5
.Ltmp176:
	.loc	1 28 17
	movss	%xmm9, (%r11,%r14,4)
	incq	%r14
.Ltmp177:
	.loc	1 0 0
	addq	$4, %rbx
	cmpq	$32, %r14
	jne	.LBB3_4
.Ltmp178:
	.loc	1 28 17
	incq	%r9
.Ltmp179:
	.loc	1 0 0
	subq	$-128, %r8
	cmpq	$8, %r9
	jne	.LBB3_3
.Ltmp180:
	.p2align	4
.LBB3_8:
	.loc	1 28 17 is_stmt 1
	incl	%ecx
.Ltmp181:
	.loc	1 0 0 is_stmt 0
	cmpl	$8, %ecx
	jne	.LBB3_1
.Ltmp182:
	.loc	1 28 17 epilogue_begin
	popq	%rbx
	.cfi_def_cfa_offset 32
	popq	%r12
	.cfi_def_cfa_offset 24
	popq	%r14
	.cfi_def_cfa_offset 16
	popq	%r15
	.cfi_def_cfa_offset 8
	retq
.Ltmp183:
.Lfunc_end3:
	.size	matmul_kernel_compute_, .Lfunc_end3-matmul_kernel_compute_
	.cfi_endproc

	.weak	__tvm_ffi_main
	.p2align	4
	.type	__tvm_ffi_main,@function
__tvm_ffi_main:
.Lfunc_begin4:
	.cfi_startproc
	jmp	__tvm_ffi_matmul_kernel@PLT
.Lfunc_end4:
	.size	__tvm_ffi_main, .Lfunc_end4-__tvm_ffi_main
	.cfi_endproc

	.section	.text.tvm.fp16.conv,"ax",@progbits
	.weak	__truncsfhf2
	.p2align	4
	.type	__truncsfhf2,@function
__truncsfhf2:
.Lfunc_begin5:
	.cfi_startproc
	movd	%xmm0, %eax
	movl	%eax, %edx
	andl	$2147483647, %edx
	leal	-947912704(%rdx), %ecx
	leal	-1199570944(%rdx), %esi
	cmpl	%esi, %ecx
	jae	.LBB5_5
	movl	%eax, %edx
	shrl	$13, %edx
	movl	%eax, %esi
	andl	$8191, %esi
	cmpl	$4097, %esi
	jb	.LBB5_3
	addl	$-114687, %edx
	movl	%edx, %ecx
	jmp	.LBB5_13
.LBB5_5:
	cmpl	$2139095041, %edx
	jb	.LBB5_7
	movl	%eax, %ecx
	shrl	$13, %ecx
	andl	$511, %ecx
	orl	$32256, %ecx
	jmp	.LBB5_13
.LBB5_3:
	leal	-114688(%rdx), %ecx
	cmpl	$4096, %esi
	jne	.LBB5_13
	andl	$1, %edx
	addl	%edx, %ecx
	jmp	.LBB5_13
.LBB5_7:
	movl	$31744, %ecx
	cmpl	$1199570943, %edx
	ja	.LBB5_13
	xorl	%ecx, %ecx
	cmpl	$754974720, %edx
	jb	.LBB5_13
	shrl	$23, %edx
	movl	%eax, %esi
	andl	$8388607, %esi
	orl	$8388608, %esi
	leal	-81(%rdx), %ecx
	movl	%esi, %edi
	shll	%cl, %edi
	xorl	%r8d, %r8d
	testl	%edi, %edi
	setne	%r8b
	movb	$113, %cl
	subb	%dl, %cl
	shrl	%cl, %esi
	movl	%esi, %ecx
	shrl	$13, %ecx
	andl	$8191, %esi
	orl	%r8d, %esi
	cmpl	$4097, %esi
	jb	.LBB5_11
	incl	%ecx
	jmp	.LBB5_13
.LBB5_11:
	cmpl	$4096, %esi
	jne	.LBB5_13
	movl	%ecx, %edx
	andl	$1, %edx
	addl	%edx, %ecx
.LBB5_13:
	shrl	$16, %eax
	andl	$32768, %eax
	orl	%ecx, %eax
	pinsrw	$0, %eax, %xmm0
	retq
.Lfunc_end5:
	.size	__truncsfhf2, .Lfunc_end5-__truncsfhf2
	.cfi_endproc

	.weak	__extendhfsf2
	.p2align	4
	.type	__extendhfsf2,@function
__extendhfsf2:
.Lfunc_begin6:
	.cfi_startproc
	pextrw	$0, %xmm0, %eax
	movl	%eax, %edx
	andl	$32767, %edx
	leal	-1024(%rdx), %ecx
	movzwl	%cx, %ecx
	cmpl	$30719, %ecx
	ja	.LBB6_2
	shll	$13, %edx
	addl	$939524096, %edx
	jmp	.LBB6_7
.LBB6_2:
	cmpl	$31744, %edx
	jb	.LBB6_4
	shll	$13, %edx
	orl	$2139095040, %edx
	jmp	.LBB6_7
.LBB6_4:
	testl	%edx, %edx
	je	.LBB6_5
	movl	%edx, %ecx
	shrl	$8, %ecx
	xorl	%esi, %esi
	cmpl	$256, %edx
	setb	%sil
	cmovbl	%edx, %ecx
	leal	24(,%rsi,8), %edi
	movl	%ecx, %r8d
	shrl	$4, %r8d
	cmpl	$16, %ecx
	leal	20(,%rsi,8), %esi
	cmovbl	%ecx, %r8d
	cmovbl	%edi, %esi
	movl	%r8d, %ecx
	shrl	$2, %ecx
	leal	-2(%rsi), %edi
	cmpl	$4, %r8d
	cmovbl	%r8d, %ecx
	cmovbl	%esi, %edi
	movl	%ecx, %esi
	negl	%esi
	cmpl	$2, %ecx
	movl	$-2, %r8d
	cmovbl	%esi, %r8d
	addl	%edi, %r8d
	leal	-8(%r8), %ecx
	shll	%cl, %edx
	xorl	$8388608, %edx
	shll	$23, %r8d
	movl	$1124073472, %ecx
	subl	%r8d, %ecx
	orl	%edx, %ecx
	movl	%ecx, %edx
	jmp	.LBB6_7
.LBB6_5:
	xorl	%edx, %edx
.LBB6_7:
	andl	$32768, %eax
	shll	$16, %eax
	orl	%edx, %eax
	movd	%eax, %xmm0
	retq
.Lfunc_end6:
	.size	__extendhfsf2, .Lfunc_end6-__extendhfsf2
	.cfi_endproc

	.type	.L.str,@object
	.section	.rodata,"a",@progbits
.L.str:
	.asciz	"TypeError"
	.size	.L.str, 10

	.type	.L.str.1,@object
.L.str.1:
	.asciz	"Expected "
	.size	.L.str.1, 10

	.type	.L.str.2,@object
.L.str.2:
	.asciz	"3"
	.size	.L.str.2, 2

	.type	.L.str.3,@object
.L.str.3:
	.asciz	" arguments"
	.size	.L.str.3, 11

	.type	.L.str.4,@object
.L.str.4:
	.asciz	" when calling:\n  `"
	.size	.L.str.4, 19

	.type	.L.str.5,@object
.L.str.5:
	.asciz	"matmul_kernel(A: Tensor([1, 256], float32), B: Tensor([256, 256], float32), C: Tensor([1, 256], float32))"
	.size	.L.str.5, 106

	.type	.L.str.6,@object
.L.str.6:
	.asciz	"`"
	.size	.L.str.6, 2

	.type	.L.str.7,@object
.L.str.7:
	.asciz	"args pointer is NULL"
	.size	.L.str.7, 21

	.type	.L.str.8,@object
.L.str.8:
	.asciz	"Mismatched type on argument #"
	.size	.L.str.8, 30

	.type	.L.str.9,@object
.L.str.9:
	.asciz	"0"
	.size	.L.str.9, 2

	.type	.L.str.10,@object
.L.str.10:
	.asciz	"`,\n  expected "
	.size	.L.str.10, 15

	.type	.L.str.11,@object
.L.str.11:
	.asciz	"Tensor"
	.size	.L.str.11, 7

	.type	.L.str.12,@object
.L.str.12:
	.asciz	"1"
	.size	.L.str.12, 2

	.type	.L.str.13,@object
.L.str.13:
	.asciz	"2"
	.size	.L.str.13, 2

	.type	.L.str.14,@object
.L.str.14:
	.asciz	"ValueError"
	.size	.L.str.14, 11

	.type	.L.str.15,@object
.L.str.15:
	.asciz	"Mismatched "
	.size	.L.str.15, 12

	.type	.L.str.16,@object
.L.str.16:
	.asciz	"A"
	.size	.L.str.16, 2

	.type	.L.str.17,@object
.L.str.17:
	.asciz	".ndim on argument #"
	.size	.L.str.17, 20

	.type	.L.str.18,@object
.L.str.18:
	.asciz	".dtype on argument #"
	.size	.L.str.18, 21

	.type	.L.str.19,@object
.L.str.19:
	.asciz	"float32"
	.size	.L.str.19, 8

	.type	.L.str.20,@object
.L.str.20:
	.asciz	".device_type on argument #"
	.size	.L.str.20, 27

	.type	.L.str.21,@object
.L.str.21:
	.asciz	"cpu"
	.size	.L.str.21, 4

	.type	.L.str.22,@object
.L.str.22:
	.asciz	"B"
	.size	.L.str.22, 2

	.type	.L.str.23,@object
.L.str.23:
	.asciz	"C"
	.size	.L.str.23, 2

	.type	.L.str.24,@object
.L.str.24:
	.asciz	".strides on argument #"
	.size	.L.str.24, 23

	.type	.L.str.25,@object
.L.str.25:
	.asciz	"`,\n  expected to be compact array"
	.size	.L.str.25, 34

	.type	.L.str.26,@object
.L.str.26:
	.asciz	" data pointer is NULL on argument #"
	.size	.L.str.26, 36

	.type	.L.str.27,@object
.L.str.27:
	.asciz	"`,\n  expected non-NULL data pointer"
	.size	.L.str.27, 36

	.type	.L.str.28,@object
.L.str.28:
	.asciz	"B.device_id"
	.size	.L.str.28, 12

	.type	.L.str.29,@object
.L.str.29:
	.asciz	" on argument #"
	.size	.L.str.29, 15

	.type	.L.str.30,@object
.L.str.30:
	.asciz	"`,\n  expected to match "
	.size	.L.str.30, 24

	.type	.L.str.31,@object
.L.str.31:
	.asciz	"A.device_id"
	.size	.L.str.31, 12

	.type	.L.str.32,@object
.L.str.32:
	.asciz	"C.device_id"
	.size	.L.str.32, 12

	.type	.L.str.33,@object
.L.str.33:
	.asciz	"Invalid "
	.size	.L.str.33, 9

	.type	.L.str.34,@object
.L.str.34:
	.asciz	"A.shape[0]"
	.size	.L.str.34, 11

	.type	.L.str.35,@object
.L.str.35:
	.asciz	"A.shape[1]"
	.size	.L.str.35, 11

	.type	.L.str.36,@object
.L.str.36:
	.asciz	"256"
	.size	.L.str.36, 4

	.type	.L.str.37,@object
.L.str.37:
	.asciz	"A.byte_offset"
	.size	.L.str.37, 14

	.type	.L.str.38,@object
.L.str.38:
	.asciz	"B.shape[0]"
	.size	.L.str.38, 11

	.type	.L.str.39,@object
.L.str.39:
	.asciz	"B.shape[1]"
	.size	.L.str.39, 11

	.type	.L.str.40,@object
.L.str.40:
	.asciz	"B.byte_offset"
	.size	.L.str.40, 14

	.type	.L.str.41,@object
.L.str.41:
	.asciz	"C.shape[0]"
	.size	.L.str.41, 11

	.type	.L.str.42,@object
.L.str.42:
	.asciz	"C.shape[1]"
	.size	.L.str.42, 11

	.type	.L.str.43,@object
.L.str.43:
	.asciz	"C.byte_offset"
	.size	.L.str.43, 14

	.section	.debug_loc,"",@progbits
.Ldebug_loc0:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin0-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp77-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	.Ltmp77-.Lfunc_begin0
	.quad	.Ltmp85-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp85-.Lfunc_begin0
	.quad	.Ltmp86-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	.Ltmp86-.Lfunc_begin0
	.quad	.Ltmp95-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Lfunc_end0-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc1:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin0-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp17-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp17-.Lfunc_begin0
	.quad	.Ltmp81-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	.Ltmp81-.Lfunc_begin0
	.quad	.Ltmp82-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp82-.Lfunc_begin0
	.quad	.Ltmp83-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	.Ltmp83-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Lfunc_end0-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc2:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.short	1
	.byte	80
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.short	1
	.byte	80
	.quad	0
	.quad	0
.Ldebug_loc3:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.short	1
	.byte	82
	.quad	0
	.quad	0
.Ldebug_loc4:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp17-.Lfunc_begin0
	.quad	.Ltmp18-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	0
	.quad	0
.Ldebug_loc5:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp44-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp119-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp130-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	.Ltmp132-.Lfunc_begin0
	.quad	.Ltmp139-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	.Ltmp140-.Lfunc_begin0
	.quad	.Ltmp147-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc6:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp45-.Lfunc_begin0
	.quad	.Ltmp53-.Lfunc_begin0
	.short	2
	.byte	117
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp96-.Lfunc_begin0
	.short	2
	.byte	117
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc7:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp46-.Lfunc_begin0
	.quad	.Ltmp64-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp97-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp99-.Lfunc_begin0
	.quad	.Ltmp101-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp102-.Lfunc_begin0
	.quad	.Ltmp104-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp105-.Lfunc_begin0
	.quad	.Ltmp106-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp108-.Lfunc_begin0
	.quad	.Ltmp110-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp111-.Lfunc_begin0
	.quad	.Ltmp112-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp116-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	0
	.quad	0
.Ldebug_loc8:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp100-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp102-.Lfunc_begin0
	.quad	.Ltmp103-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp105-.Lfunc_begin0
	.quad	.Ltmp109-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp111-.Lfunc_begin0
	.quad	.Ltmp115-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp117-.Lfunc_begin0
	.quad	.Ltmp118-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp123-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp124-.Lfunc_begin0
	.quad	.Ltmp125-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp128-.Lfunc_begin0
	.quad	.Ltmp130-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp132-.Lfunc_begin0
	.quad	.Ltmp133-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp134-.Lfunc_begin0
	.quad	.Ltmp135-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp136-.Lfunc_begin0
	.quad	.Ltmp137-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp140-.Lfunc_begin0
	.quad	.Ltmp141-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp142-.Lfunc_begin0
	.quad	.Ltmp143-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp144-.Lfunc_begin0
	.quad	.Ltmp145-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc9:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp57-.Lfunc_begin0
	.short	2
	.byte	116
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp102-.Lfunc_begin0
	.short	2
	.byte	116
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc10:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp49-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp98-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp99-.Lfunc_begin0
	.quad	.Ltmp107-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp108-.Lfunc_begin0
	.quad	.Ltmp113-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp119-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp127-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp128-.Lfunc_begin0
	.quad	.Ltmp129-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp132-.Lfunc_begin0
	.quad	.Ltmp139-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp140-.Lfunc_begin0
	.quad	.Ltmp147-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc11:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp50-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp119-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp130-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	.Ltmp132-.Lfunc_begin0
	.quad	.Ltmp139-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	.Ltmp140-.Lfunc_begin0
	.quad	.Ltmp147-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc12:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp154-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.short	1
	.byte	89
	.quad	0
	.quad	0
.Ldebug_loc13:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp155-.Lfunc_begin0
	.quad	.Ltmp156-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	0
	.byte	159
	.quad	.Ltmp156-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.short	1
	.byte	94
	.quad	0
	.quad	0
.Ldebug_loc14:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp165-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	0
	.byte	159
	.quad	.Ltmp165-.Lfunc_begin0
	.quad	.Ltmp166-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	1
	.byte	159
	.quad	.Ltmp166-.Lfunc_begin0
	.quad	.Ltmp174-.Lfunc_begin0
	.short	9
	.byte	124
	.byte	0
	.byte	17
	.byte	32
	.byte	27
	.byte	17
	.byte	1
	.byte	34
	.byte	159
	.quad	.Ltmp174-.Lfunc_begin0
	.quad	.Ltmp175-.Lfunc_begin0
	.short	9
	.byte	124
	.byte	0
	.byte	17
	.byte	32
	.byte	27
	.byte	17
	.byte	2
	.byte	34
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc15:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp158-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	0
	.byte	159
	.quad	.Ltmp158-.Lfunc_begin0
	.quad	.Ltmp159-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	1
	.byte	159
	.quad	.Ltmp159-.Lfunc_begin0
	.quad	.Ltmp160-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	2
	.byte	159
	.quad	.Ltmp160-.Lfunc_begin0
	.quad	.Ltmp161-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	3
	.byte	159
	.quad	.Ltmp161-.Lfunc_begin0
	.quad	.Ltmp162-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	4
	.byte	159
	.quad	.Ltmp162-.Lfunc_begin0
	.quad	.Ltmp163-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	5
	.byte	159
	.quad	.Ltmp163-.Lfunc_begin0
	.quad	.Ltmp164-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	6
	.byte	159
	.quad	.Ltmp164-.Lfunc_begin0
	.quad	.Ltmp165-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	7
	.byte	159
	.quad	.Ltmp165-.Lfunc_begin0
	.quad	.Ltmp166-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	8
	.byte	159
	.quad	.Ltmp166-.Lfunc_begin0
	.quad	.Ltmp167-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	0
	.byte	159
	.quad	.Ltmp167-.Lfunc_begin0
	.quad	.Ltmp168-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	1
	.byte	159
	.quad	.Ltmp168-.Lfunc_begin0
	.quad	.Ltmp169-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	2
	.byte	159
	.quad	.Ltmp169-.Lfunc_begin0
	.quad	.Ltmp170-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	3
	.byte	159
	.quad	.Ltmp170-.Lfunc_begin0
	.quad	.Ltmp171-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	4
	.byte	159
	.quad	.Ltmp171-.Lfunc_begin0
	.quad	.Ltmp172-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	5
	.byte	159
	.quad	.Ltmp172-.Lfunc_begin0
	.quad	.Ltmp173-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	6
	.byte	159
	.quad	.Ltmp173-.Lfunc_begin0
	.quad	.Ltmp174-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	7
	.byte	159
	.quad	.Ltmp174-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	8
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc16:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.short	1
	.byte	90
	.quad	0
	.quad	0
.Ldebug_loc17:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp158-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	0
	.byte	159
	.quad	.Ltmp158-.Lfunc_begin0
	.quad	.Ltmp159-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	1
	.byte	159
	.quad	.Ltmp159-.Lfunc_begin0
	.quad	.Ltmp160-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	2
	.byte	159
	.quad	.Ltmp160-.Lfunc_begin0
	.quad	.Ltmp161-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	3
	.byte	159
	.quad	.Ltmp161-.Lfunc_begin0
	.quad	.Ltmp162-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	4
	.byte	159
	.quad	.Ltmp162-.Lfunc_begin0
	.quad	.Ltmp163-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	5
	.byte	159
	.quad	.Ltmp163-.Lfunc_begin0
	.quad	.Ltmp164-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	6
	.byte	159
	.quad	.Ltmp164-.Lfunc_begin0
	.quad	.Ltmp166-.Lfunc_begin0
	.short	3
	.byte	17
	.byte	7
	.byte	159
	.quad	.Ltmp166-.Lfunc_begin0
	.quad	.Ltmp167-.Lfunc_begin0
	.short	12
	.byte	124
	.byte	0
	.byte	17
	.byte	32
	.byte	27
	.byte	17
	.byte	8
	.byte	30
	.byte	17
	.byte	8
	.byte	34
	.byte	159
	.quad	.Ltmp167-.Lfunc_begin0
	.quad	.Ltmp168-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	49
	.byte	33
	.byte	159
	.quad	.Ltmp168-.Lfunc_begin0
	.quad	.Ltmp169-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	50
	.byte	33
	.byte	159
	.quad	.Ltmp169-.Lfunc_begin0
	.quad	.Ltmp170-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	51
	.byte	33
	.byte	159
	.quad	.Ltmp170-.Lfunc_begin0
	.quad	.Ltmp171-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	52
	.byte	33
	.byte	159
	.quad	.Ltmp171-.Lfunc_begin0
	.quad	.Ltmp172-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	53
	.byte	33
	.byte	159
	.quad	.Ltmp172-.Lfunc_begin0
	.quad	.Ltmp173-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	54
	.byte	33
	.byte	159
	.quad	.Ltmp173-.Lfunc_begin0
	.quad	.Ltmp175-.Lfunc_begin0
	.short	5
	.byte	124
	.byte	0
	.byte	55
	.byte	33
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc18:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp177-.Lfunc_begin0
	.short	6
	.byte	126
	.byte	0
	.byte	122
	.byte	0
	.byte	33
	.byte	159
	.quad	0
	.quad	0
	.section	.debug_abbrev,"",@progbits
	.byte	1
	.byte	17
	.byte	1
	.byte	37
	.byte	14
	.byte	19
	.byte	5
	.byte	3
	.byte	14
	.byte	16
	.byte	23
	.byte	27
	.byte	14
	.ascii	"\264B"
	.byte	25
	.byte	17
	.byte	1
	.byte	85
	.byte	23
	.byte	0
	.byte	0
	.byte	2
	.byte	46
	.byte	1
	.byte	17
	.byte	1
	.byte	18
	.byte	6
	.byte	64
	.byte	24
	.byte	3
	.byte	14
	.byte	39
	.byte	25
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	3
	.byte	5
	.byte	0
	.byte	3
	.byte	14
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	4
	.byte	5
	.byte	0
	.byte	2
	.byte	23
	.byte	3
	.byte	14
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	5
	.byte	52
	.byte	0
	.byte	2
	.byte	23
	.byte	3
	.byte	14
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	6
	.byte	46
	.byte	1
	.byte	17
	.byte	1
	.byte	18
	.byte	6
	.byte	64
	.byte	24
	.byte	3
	.byte	14
	.byte	39
	.byte	25
	.byte	54
	.byte	11
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	7
	.byte	5
	.byte	0
	.byte	2
	.byte	24
	.byte	3
	.byte	14
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	8
	.byte	52
	.byte	0
	.byte	2
	.byte	24
	.byte	3
	.byte	14
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	9
	.byte	36
	.byte	0
	.byte	3
	.byte	14
	.byte	62
	.byte	11
	.byte	11
	.byte	11
	.byte	0
	.byte	0
	.byte	10
	.byte	15
	.byte	0
	.byte	0
	.byte	0
	.byte	11
	.byte	15
	.byte	0
	.byte	73
	.byte	19
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_info,"",@progbits
.Lcu_begin0:
	.long	.Ldebug_info_end0-.Ldebug_info_start0
.Ldebug_info_start0:
	.short	4
	.long	.debug_abbrev
	.byte	8
	.byte	1
	.long	.Linfo_string0
	.short	2
	.long	.Linfo_string1
	.long	.Lline_table_start0
	.long	.Linfo_string2

	.quad	0
	.long	.Ldebug_ranges0
	.byte	2
	.quad	.Lfunc_begin0
	.long	.Lfunc_end0-.Lfunc_begin0
	.byte	4
	.byte	156
	.byte	17
	.byte	112
	.byte	34
	.long	.Linfo_string3

	.long	428
	.byte	3
	.long	.Linfo_string19
	.long	435
	.byte	4
	.long	.Ldebug_loc0
	.long	.Linfo_string6
	.long	435
	.byte	4
	.long	.Ldebug_loc1
	.long	.Linfo_string7
	.long	428
	.byte	3
	.long	.Linfo_string20
	.long	435
	.byte	5
	.long	.Ldebug_loc2
	.long	.Linfo_string8
	.long	428
	.byte	5
	.long	.Ldebug_loc3
	.long	.Linfo_string9
	.long	428
	.byte	5
	.long	.Ldebug_loc4
	.long	.Linfo_string10
	.long	428
	.byte	5
	.long	.Ldebug_loc5
	.long	.Linfo_string11
	.long	436
	.byte	5
	.long	.Ldebug_loc6
	.long	.Linfo_string13
	.long	436
	.byte	5
	.long	.Ldebug_loc7
	.long	.Linfo_string14
	.long	428
	.byte	5
	.long	.Ldebug_loc8
	.long	.Linfo_string15
	.long	436
	.byte	5
	.long	.Ldebug_loc9
	.long	.Linfo_string16
	.long	436
	.byte	5
	.long	.Ldebug_loc10
	.long	.Linfo_string17
	.long	436
	.byte	5
	.long	.Ldebug_loc11
	.long	.Linfo_string18
	.long	436
	.byte	0
	.byte	6
	.quad	.Lfunc_begin3
	.long	.Lfunc_end3-.Lfunc_begin3
	.byte	1
	.byte	87
	.long	.Linfo_string5

	.byte	3
	.long	428
	.byte	7
	.byte	1
	.byte	85
	.long	.Linfo_string21
	.long	448
	.byte	7
	.byte	1
	.byte	84
	.long	.Linfo_string23
	.long	448
	.byte	7
	.byte	1
	.byte	81
	.long	.Linfo_string24
	.long	448
	.byte	8
	.byte	2
	.byte	117
	.byte	0
	.long	.Linfo_string21
	.long	448
	.byte	8
	.byte	2
	.byte	116
	.byte	0
	.long	.Linfo_string23
	.long	448
	.byte	8
	.byte	2
	.byte	113
	.byte	0
	.long	.Linfo_string24
	.long	448
	.byte	5
	.long	.Ldebug_loc12
	.long	.Linfo_string25
	.long	428
	.byte	5
	.long	.Ldebug_loc13
	.long	.Linfo_string26
	.long	428
	.byte	5
	.long	.Ldebug_loc14
	.long	.Linfo_string27
	.long	428
	.byte	5
	.long	.Ldebug_loc15
	.long	.Linfo_string28
	.long	428
	.byte	5
	.long	.Ldebug_loc16
	.long	.Linfo_string29
	.long	428
	.byte	5
	.long	.Ldebug_loc17
	.long	.Linfo_string30
	.long	428
	.byte	5
	.long	.Ldebug_loc18
	.long	.Linfo_string31
	.long	428
	.byte	0
	.byte	9
	.long	.Linfo_string4
	.byte	5
	.byte	4
	.byte	10
	.byte	11
	.long	441
	.byte	9
	.long	.Linfo_string12
	.byte	5
	.byte	8
	.byte	11
	.long	453
	.byte	9
	.long	.Linfo_string22
	.byte	4
	.byte	4
	.byte	0
.Ldebug_info_end0:
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Lfunc_begin0
	.quad	.Lfunc_end0
	.quad	.Lfunc_begin3
	.quad	.Lfunc_end3
	.quad	0
	.quad	0
	.section	.debug_str,"MS",@progbits,1
.Linfo_string0:
	.asciz	"TVM"
.Linfo_string1:
	.asciz	"IRModule.CodeGenLLVM"
.Linfo_string2:
	.asciz	"."
.Linfo_string3:
	.asciz	"__tvm_ffi_matmul_kernel"
.Linfo_string4:
	.asciz	"int32"
.Linfo_string5:
	.asciz	"matmul_kernel_compute_"
.Linfo_string6:
	.asciz	"args"
.Linfo_string7:
	.asciz	"num_args"
.Linfo_string8:
	.asciz	"A.type_index"
.Linfo_string9:
	.asciz	"B.type_index"
.Linfo_string10:
	.asciz	"C.type_index"
.Linfo_string11:
	.asciz	"matmul_kernel.A_shape"
.Linfo_string12:
	.asciz	"int64"
.Linfo_string13:
	.asciz	"matmul_kernel.A_strides"
.Linfo_string14:
	.asciz	"dev_id"
.Linfo_string15:
	.asciz	"matmul_kernel.B_shape"
.Linfo_string16:
	.asciz	"matmul_kernel.B_strides"
.Linfo_string17:
	.asciz	"matmul_kernel.C_shape"
.Linfo_string18:
	.asciz	"matmul_kernel.C_strides"
.Linfo_string19:
	.asciz	"self_handle"
.Linfo_string20:
	.asciz	"result"
.Linfo_string21:
	.asciz	"A"
.Linfo_string22:
	.asciz	"float32"
.Linfo_string23:
	.asciz	"B"
.Linfo_string24:
	.asciz	"C"
.Linfo_string25:
	.asciz	"j_0"
.Linfo_string26:
	.asciz	"j_1"
.Linfo_string27:
	.asciz	"r_0"
.Linfo_string28:
	.asciz	"r_1"
.Linfo_string29:
	.asciz	"cse_v1"
.Linfo_string30:
	.asciz	"cse_v2"
.Linfo_string31:
	.asciz	"cse_v3"
	.section	.debug_pubnames,"",@progbits
	.long	.LpubNames_end0-.LpubNames_start0
.LpubNames_start0:
	.short	2
	.long	.Lcu_begin0
	.long	461
	.long	42
	.asciz	"__tvm_ffi_matmul_kernel"
	.long	243
	.asciz	"matmul_kernel_compute_"
	.long	0
.LpubNames_end0:
	.section	.debug_pubtypes,"",@progbits
	.long	.LpubTypes_end0-.LpubTypes_start0
.LpubTypes_start0:
	.short	2
	.long	.Lcu_begin0
	.long	461
	.long	428
	.asciz	"int32"
	.long	441
	.asciz	"int64"
	.long	453
	.asciz	"float32"
	.long	0
.LpubTypes_end0:
	.section	".note.GNU-stack","",@progbits
	.section	.debug_line,"",@progbits
.Lline_table_start0:
