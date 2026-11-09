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
	jne	.LBB0_64
.Ltmp0:
	testq	%rsi, %rsi
	je	.LBB0_65
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
	ja	.LBB0_61
.Ltmp8:
	movl	$145, %edx
.Ltmp9:
	btl	%ecx, %edx
	jb	.LBB0_14
	jmp	.LBB0_61
.Ltmp10:
.LBB0_7:
	cmpl	$7, %eax
	ja	.LBB0_60
.Ltmp11:
	movl	$145, %ecx
	btl	%eax, %ecx
	jae	.LBB0_60
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
	ja	.LBB0_62
.Ltmp19:
	movl	$145, %edi
	btl	%edx, %edi
	jb	.LBB0_17
	jmp	.LBB0_62
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
	je	.LBB0_60
.Ltmp26:
	cmpl	$2, 16(%rax)
	jne	.LBB0_66
.Ltmp27:
	cmpw	$1, 22(%rax)
	jne	.LBB0_67
.Ltmp28:
	cmpb	$32, 21(%rax)
	jne	.LBB0_67
.Ltmp29:
	cmpb	$2, 20(%rax)
	jne	.LBB0_67
.Ltmp30:
	cmpl	$1, 8(%rax)
	jne	.LBB0_68
.Ltmp31:
	testq	%rcx, %rcx
	je	.LBB0_61
.Ltmp32:
	cmpl	$2, 16(%rcx)
	jne	.LBB0_69
.Ltmp33:
	cmpw	$1, 22(%rcx)
	jne	.LBB0_70
.Ltmp34:
	cmpb	$32, 21(%rcx)
	jne	.LBB0_70
.Ltmp35:
	cmpb	$2, 20(%rcx)
	jne	.LBB0_70
.Ltmp36:
	cmpl	$1, 8(%rcx)
	jne	.LBB0_71
.Ltmp37:
	testq	%r8, %r8
	je	.LBB0_62
.Ltmp38:
	cmpl	$2, 16(%r8)
	jne	.LBB0_72
.Ltmp39:
	cmpw	$1, 22(%r8)
	jne	.LBB0_73
.Ltmp40:
	cmpb	$32, 21(%r8)
	jne	.LBB0_73
.Ltmp41:
	cmpb	$2, 20(%r8)
	jne	.LBB0_73
.Ltmp42:
	cmpl	$1, 8(%r8)
	jne	.LBB0_74
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
	je	.LBB0_39
.Ltmp51:
	cmpl	$256, (%rdi)
	jne	.LBB0_76
.Ltmp52:
	movl	8(%rdi), %edi
.Ltmp53:
	cmpl	$1, %edi
	jne	.LBB0_76
.Ltmp54:
.LBB0_39:
	movq	(%rax), %rdi
	testq	%rdi, %rdi
	je	.LBB0_75
.Ltmp55:
	testq	%rsi, %rsi
	je	.LBB0_43
.Ltmp56:
	cmpl	$256, (%rsi)
	jne	.LBB0_78
.Ltmp57:
	movl	8(%rsi), %esi
.Ltmp58:
	cmpl	$1, %esi
	jne	.LBB0_78
.Ltmp59:
.LBB0_43:
	cmpl	12(%rcx), %edx
	jne	.LBB0_77
.Ltmp60:
	movq	(%rcx), %rsi
	testq	%rsi, %rsi
	je	.LBB0_79
.Ltmp61:
	testq	%rbx, %rbx
	je	.LBB0_48
.Ltmp62:
	cmpl	$256, (%rbx)
	jne	.LBB0_81
.Ltmp63:
	movl	8(%rbx), %ebx
.Ltmp64:
	cmpl	$1, %ebx
	jne	.LBB0_81
.Ltmp65:
.LBB0_48:
	cmpl	12(%r8), %edx
	jne	.LBB0_80
.Ltmp66:
	movq	(%r8), %rdx
.Ltmp67:
	testq	%rdx, %rdx
	je	.LBB0_83
.Ltmp68:
	cmpl	$32, (%r11)
	jne	.LBB0_87
.Ltmp69:
	cmpl	$256, 8(%r11)
	jne	.LBB0_88
.Ltmp70:
	cmpq	$0, 40(%rax)
	jne	.LBB0_90
.Ltmp71:
	cmpl	$256, (%r10)
	jne	.LBB0_93
.Ltmp72:
	cmpl	$256, 8(%r10)
	jne	.LBB0_94
.Ltmp73:
	cmpq	$0, 40(%rcx)
	jne	.LBB0_95
.Ltmp74:
	cmpl	$32, (%r9)
	jne	.LBB0_98
.Ltmp75:
	cmpl	$256, 8(%r9)
	jne	.LBB0_99
.Ltmp76:
	cmpq	$0, 40(%r8)
	jne	.LBB0_100
.Ltmp77:
	popq	%rbx
	.cfi_def_cfa_offset 8
	jmp	matmul_kernel_compute_
.Ltmp78:
.LBB0_60:
	.cfi_def_cfa_offset 16
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.9(%rip), %rcx
	jmp	.LBB0_63
.Ltmp79:
.LBB0_61:
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.12(%rip), %rcx
	jmp	.LBB0_63
.Ltmp80:
.LBB0_62:
	leaq	.L.str.11(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.8(%rip), %rdx
	leaq	.L.str.13(%rip), %rcx
.Ltmp81:
.LBB0_63:
	leaq	.L.str.4(%rip), %r8
	leaq	.L.str.5(%rip), %r9
	jmp	.LBB0_85
.Ltmp82:
.LBB0_64:
	leaq	.L.str.6(%rip), %rax
	leaq	.L.str.5(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.1(%rip), %rdx
.Ltmp83:
	leaq	.L.str.2(%rip), %rcx
	leaq	.L.str.3(%rip), %r8
	jmp	.LBB0_84
.Ltmp84:
.LBB0_65:
	subq	$16, %rsp
	.cfi_adjust_cfa_offset 16
	xorps	%xmm0, %xmm0
	movups	%xmm0, (%rsp)
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.7(%rip), %rdx
.Ltmp85:
	leaq	.L.str.4(%rip), %rcx
	leaq	.L.str.5(%rip), %r8
	leaq	.L.str.6(%rip), %r9
	movl	$4, %esi
.Ltmp86:
	jmp	.LBB0_86
.Ltmp87:
.LBB0_66:
	.cfi_def_cfa_offset 16
	leaq	.L.str.13(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_103
.Ltmp88:
.LBB0_67:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_103
.Ltmp89:
.LBB0_68:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	leaq	.L.str.9(%rip), %r9
	jmp	.LBB0_103
.Ltmp90:
.LBB0_69:
	leaq	.L.str.13(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	jmp	.LBB0_97
.Ltmp91:
.LBB0_70:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	jmp	.LBB0_97
.Ltmp92:
.LBB0_71:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	jmp	.LBB0_97
.Ltmp93:
.LBB0_72:
	leaq	.L.str.13(%rip), %r9
	leaq	.L.str.10(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.17(%rip), %r8
	jmp	.LBB0_91
.Ltmp94:
.LBB0_73:
	leaq	.L.str.19(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.18(%rip), %r8
	jmp	.LBB0_102
.Ltmp95:
.LBB0_74:
	leaq	.L.str.21(%rip), %rax
	leaq	.L.str.10(%rip), %r10
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.20(%rip), %r8
	jmp	.LBB0_102
.Ltmp96:
.LBB0_75:
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp97:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.16(%rip), %rdx
.Ltmp98:
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.9(%rip), %r8
	jmp	.LBB0_84
.Ltmp99:
.LBB0_76:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp100:
	leaq	.L.str.16(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.9(%rip), %r9
.Ltmp101:
	jmp	.LBB0_82
.Ltmp102:
.LBB0_77:
	leaq	.L.str.31(%rip), %rax
	leaq	.L.str.30(%rip), %r10
.Ltmp103:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp104:
	leaq	.L.str.28(%rip), %rcx
	jmp	.LBB0_96
.Ltmp105:
.LBB0_78:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp106:
	leaq	.L.str.22(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.12(%rip), %r9
.Ltmp107:
	jmp	.LBB0_82
.Ltmp108:
.LBB0_79:
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp109:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.22(%rip), %rdx
.Ltmp110:
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.12(%rip), %r8
	jmp	.LBB0_84
.Ltmp111:
.LBB0_80:
	leaq	.L.str.31(%rip), %rax
	leaq	.L.str.30(%rip), %r10
.Ltmp112:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp113:
	leaq	.L.str.32(%rip), %rcx
	jmp	.LBB0_101
.Ltmp114:
.LBB0_81:
	leaq	.L.str.25(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.15(%rip), %rdx
.Ltmp115:
	leaq	.L.str.23(%rip), %rcx
	leaq	.L.str.24(%rip), %r8
	leaq	.L.str.13(%rip), %r9
.Ltmp116:
.LBB0_82:
	movl	$7, %esi
	pushq	$0
	.cfi_adjust_cfa_offset 8
	jmp	.LBB0_92
.Ltmp117:
.LBB0_83:
	.cfi_def_cfa_offset 16
	leaq	.L.str.27(%rip), %rax
	leaq	.L.str.5(%rip), %r10
.Ltmp118:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.23(%rip), %rdx
	leaq	.L.str.26(%rip), %rcx
	leaq	.L.str.13(%rip), %r8
.Ltmp119:
.LBB0_84:
	leaq	.L.str.4(%rip), %r9
.Ltmp120:
.LBB0_85:
	movl	$6, %esi
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	pushq	%r10
	.cfi_adjust_cfa_offset 8
.Ltmp121:
.LBB0_86:
	callq	__tvm_set_raised_6
	addq	$16, %rsp
	.cfi_adjust_cfa_offset -16
	movl	$-1, %eax
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.Ltmp122:
.LBB0_87:
	.cfi_def_cfa_offset 16
	leaq	.L.str.35(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp123:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.34(%rip), %rcx
	jmp	.LBB0_89
.Ltmp124:
.LBB0_88:
	leaq	.L.str.37(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp125:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.36(%rip), %rcx
.Ltmp126:
.LBB0_89:
	leaq	.L.str.29(%rip), %r8
	leaq	.L.str.9(%rip), %r9
.Ltmp127:
	jmp	.LBB0_103
.Ltmp128:
.LBB0_90:
	leaq	.L.str.9(%rip), %r9
.Ltmp129:
	leaq	.L.str.10(%rip), %rax
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.38(%rip), %rcx
	leaq	.L.str.29(%rip), %r8
.Ltmp130:
.LBB0_91:
	movl	$8, %esi
	pushq	%r9
	.cfi_adjust_cfa_offset 8
.Ltmp131:
.LBB0_92:
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	jmp	.LBB0_104
.Ltmp132:
.LBB0_93:
	.cfi_def_cfa_offset 16
	leaq	.L.str.37(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp133:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.39(%rip), %rcx
	jmp	.LBB0_96
.Ltmp134:
.LBB0_94:
	leaq	.L.str.37(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp135:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.40(%rip), %rcx
	jmp	.LBB0_96
.Ltmp136:
.LBB0_95:
	leaq	.L.str.9(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp137:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.41(%rip), %rcx
.Ltmp138:
.LBB0_96:
	leaq	.L.str.29(%rip), %r8
.Ltmp139:
.LBB0_97:
	leaq	.L.str.12(%rip), %r9
	jmp	.LBB0_103
.Ltmp140:
.LBB0_98:
	leaq	.L.str.35(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp141:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.42(%rip), %rcx
	jmp	.LBB0_101
.Ltmp142:
.LBB0_99:
	leaq	.L.str.37(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp143:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.43(%rip), %rcx
	jmp	.LBB0_101
.Ltmp144:
.LBB0_100:
	leaq	.L.str.9(%rip), %rax
	leaq	.L.str.10(%rip), %r10
.Ltmp145:
	leaq	.L.str.14(%rip), %rdi
	leaq	.L.str.33(%rip), %rdx
	leaq	.L.str.44(%rip), %rcx
.Ltmp146:
.LBB0_101:
	leaq	.L.str.29(%rip), %r8
.Ltmp147:
.LBB0_102:
	leaq	.L.str.13(%rip), %r9
.Ltmp148:
.LBB0_103:
	movl	$8, %esi
	pushq	%rax
	.cfi_adjust_cfa_offset 8
	pushq	%r10
	.cfi_adjust_cfa_offset 8
.Ltmp149:
.LBB0_104:
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
	subq	$24, %rsp
	.cfi_def_cfa_offset 32
.Ltmp151:
	movq	%rdx, (%rsp)
	movq	%rdi, 8(%rsp)
	movq	%rsi, 16(%rsp)
	movq	__TVMBackendParallelLaunch@GOTPCREL(%rip), %rax
	leaq	.L__tvm_parallel_lambda(%rip), %rdi
.Ltmp152:
	movq	%rsp, %rsi
.Ltmp153:
	xorl	%edx, %edx
.Ltmp154:
	callq	*(%rax)
	addq	$24, %rsp
	.cfi_def_cfa_offset 8
	retq
.Ltmp155:
.Lfunc_end3:
	.size	matmul_kernel_compute_, .Lfunc_end3-matmul_kernel_compute_
	.cfi_endproc

	.p2align	4
	.type	.L__tvm_parallel_lambda,@function
.L__tvm_parallel_lambda:
.Lfunc_begin4:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	pushq	%r15
	.cfi_def_cfa_offset 24
	pushq	%r14
	.cfi_def_cfa_offset 32
	pushq	%r13
	.cfi_def_cfa_offset 40
	pushq	%r12
	.cfi_def_cfa_offset 48
	pushq	%rbx
	.cfi_def_cfa_offset 56
	.cfi_offset %rbx, -56
	.cfi_offset %r12, -48
	.cfi_offset %r13, -40
	.cfi_offset %r14, -32
	.cfi_offset %r15, -24
	.cfi_offset %rbp, -16
	movq	%rdx, %rcx
	movl	8(%rsi), %esi
	leal	3(%rsi), %eax
	cltd
	idivl	%esi
	leal	1(%rdi), %edx
	imull	%eax, %edx
	cmpl	$4, %edx
	movl	$4, %esi
	cmovll	%edx, %esi
	imull	%edi, %eax
	movl	%esi, -20(%rsp)
	cmpl	%esi, %eax
	jge	.LBB4_9
	movq	(%rcx), %rsi
	movq	16(%rcx), %rdx
	cltq
	addq	$112, %rdx
	movq	%rdx, -8(%rsp)
	movq	%rax, %r8
	shlq	$13, %r8
	addq	8(%rcx), %r8
	xorps	%xmm0, %xmm0
.LBB4_2:
	movq	%rax, %rcx
	shlq	$11, %rcx
	movq	-8(%rsp), %r9
	xorl	%r10d, %r10d
.LBB4_3:
	movq	%r10, %r11
	shlq	$5, %r11
	movq	%r8, %rbx
	movq	%r9, -16(%rsp)
	xorl	%r15d, %r15d
	jmp	.LBB4_4
	.p2align	4
.LBB4_10:
	incq	%r15
	addq	$8192, %r9
	addq	$32, %rbx
	cmpq	$32, %r15
	je	.LBB4_11
.LBB4_4:
	movq	%rbx, %r12
	xorl	%r13d, %r13d
	jmp	.LBB4_5
	.p2align	4
.LBB4_14:
	incq	%r13
	addq	$1024, %r12
	cmpq	$8, %r13
	je	.LBB4_10
.LBB4_5:
	movq	%r13, %rbp
	shlq	$8, %rbp
	addq	%rcx, %rbp
	orq	%r11, %rbp
	movq	%r9, %r14
	xorl	%edx, %edx
	.p2align	4
.LBB4_6:
	movl	%edx, %edi
	orl	%r15d, %edi
	movss	(%r12,%rdx,4), %xmm1
	shufps	$0, %xmm1, %xmm1
	movaps	-112(%r14), %xmm2
	mulps	%xmm1, %xmm2
	jne	.LBB4_7
	addps	%xmm0, %xmm2
	movaps	%xmm2, (%rsi,%rbp,4)
	movaps	-96(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 16(%rsi,%rbp,4)
	movaps	-80(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 32(%rsi,%rbp,4)
	movaps	-64(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 48(%rsi,%rbp,4)
	movaps	-48(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 64(%rsi,%rbp,4)
	movaps	-32(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 80(%rsi,%rbp,4)
	movaps	-16(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	%xmm0, %xmm2
	movaps	%xmm2, 96(%rsi,%rbp,4)
	mulps	(%r14), %xmm1
	addps	%xmm0, %xmm1
.LBB4_13:
	movaps	%xmm1, 112(%rsi,%rbp,4)
	incq	%rdx
	addq	$1024, %r14
	cmpq	$8, %rdx
	jne	.LBB4_6
	jmp	.LBB4_14
.LBB4_7:
	addps	(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, (%rsi,%rbp,4)
	movaps	-96(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	16(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 16(%rsi,%rbp,4)
	movaps	-80(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	32(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 32(%rsi,%rbp,4)
	movaps	-64(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	48(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 48(%rsi,%rbp,4)
	movaps	-48(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	64(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 64(%rsi,%rbp,4)
	movaps	-32(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	80(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 80(%rsi,%rbp,4)
	movaps	-16(%r14), %xmm2
	mulps	%xmm1, %xmm2
	addps	96(%rsi,%rbp,4), %xmm2
	movaps	%xmm2, 96(%rsi,%rbp,4)
	mulps	(%r14), %xmm1
	addps	112(%rsi,%rbp,4), %xmm1
	jmp	.LBB4_13
	.p2align	4
.LBB4_11:
	incq	%r10
	movq	-16(%rsp), %r9
	subq	$-128, %r9
	cmpq	$8, %r10
	jne	.LBB4_3
	.p2align	4
	incq	%rax
	addq	$8192, %r8
	cmpl	%eax, -20(%rsp)
	jne	.LBB4_2
.LBB4_9:
	xorl	%eax, %eax
	popq	%rbx
	.cfi_def_cfa_offset 48
	popq	%r12
	.cfi_def_cfa_offset 40
	popq	%r13
	.cfi_def_cfa_offset 32
	popq	%r14
	.cfi_def_cfa_offset 24
	popq	%r15
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end4:
	.size	.L__tvm_parallel_lambda, .Lfunc_end4-.L__tvm_parallel_lambda
	.cfi_endproc

	.weak	__tvm_ffi_main
	.p2align	4
	.type	__tvm_ffi_main,@function
__tvm_ffi_main:
.Lfunc_begin5:
	.cfi_startproc
	jmp	__tvm_ffi_matmul_kernel@PLT
.Lfunc_end5:
	.size	__tvm_ffi_main, .Lfunc_end5-__tvm_ffi_main
	.cfi_endproc

	.section	.text.tvm.fp16.conv,"ax",@progbits
	.weak	__truncsfhf2
	.p2align	4
	.type	__truncsfhf2,@function
__truncsfhf2:
.Lfunc_begin6:
	.cfi_startproc
	movd	%xmm0, %eax
	movl	%eax, %edx
	andl	$2147483647, %edx
	leal	-947912704(%rdx), %ecx
	leal	-1199570944(%rdx), %esi
	cmpl	%esi, %ecx
	jae	.LBB6_5
	movl	%eax, %edx
	shrl	$13, %edx
	movl	%eax, %esi
	andl	$8191, %esi
	cmpl	$4097, %esi
	jb	.LBB6_3
	addl	$-114687, %edx
	movl	%edx, %ecx
	jmp	.LBB6_13
.LBB6_5:
	cmpl	$2139095041, %edx
	jb	.LBB6_7
	movl	%eax, %ecx
	shrl	$13, %ecx
	andl	$511, %ecx
	orl	$32256, %ecx
	jmp	.LBB6_13
.LBB6_3:
	leal	-114688(%rdx), %ecx
	cmpl	$4096, %esi
	jne	.LBB6_13
	andl	$1, %edx
	addl	%edx, %ecx
	jmp	.LBB6_13
.LBB6_7:
	movl	$31744, %ecx
	cmpl	$1199570943, %edx
	ja	.LBB6_13
	xorl	%ecx, %ecx
	cmpl	$754974720, %edx
	jb	.LBB6_13
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
	jb	.LBB6_11
	incl	%ecx
	jmp	.LBB6_13
.LBB6_11:
	cmpl	$4096, %esi
	jne	.LBB6_13
	movl	%ecx, %edx
	andl	$1, %edx
	addl	%edx, %ecx
.LBB6_13:
	shrl	$16, %eax
	andl	$32768, %eax
	orl	%ecx, %eax
	pinsrw	$0, %eax, %xmm0
	retq
.Lfunc_end6:
	.size	__truncsfhf2, .Lfunc_end6-__truncsfhf2
	.cfi_endproc

	.weak	__extendhfsf2
	.p2align	4
	.type	__extendhfsf2,@function
__extendhfsf2:
.Lfunc_begin7:
	.cfi_startproc
	pextrw	$0, %xmm0, %eax
	movl	%eax, %edx
	andl	$32767, %edx
	leal	-1024(%rdx), %ecx
	movzwl	%cx, %ecx
	cmpl	$30719, %ecx
	ja	.LBB7_2
	shll	$13, %edx
	addl	$939524096, %edx
	jmp	.LBB7_7
.LBB7_2:
	cmpl	$31744, %edx
	jb	.LBB7_4
	shll	$13, %edx
	orl	$2139095040, %edx
	jmp	.LBB7_7
.LBB7_4:
	testl	%edx, %edx
	je	.LBB7_5
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
	jmp	.LBB7_7
.LBB7_5:
	xorl	%edx, %edx
.LBB7_7:
	andl	$32768, %eax
	shll	$16, %eax
	orl	%edx, %eax
	movd	%eax, %xmm0
	retq
.Lfunc_end7:
	.size	__extendhfsf2, .Lfunc_end7-__extendhfsf2
	.cfi_endproc

	.type	__TVMBackendParallelLaunch,@object
	.bss
	.weak	__TVMBackendParallelLaunch
	.p2align	3, 0x0
__TVMBackendParallelLaunch:
	.quad	0
	.size	__TVMBackendParallelLaunch, 8

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
	.asciz	"matmul_kernel(A: Tensor([32, 256], float32), B: Tensor([256, 256], float32), C: Tensor([32, 256], float32))"
	.size	.L.str.5, 108

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
	.asciz	"32"
	.size	.L.str.35, 3

	.type	.L.str.36,@object
.L.str.36:
	.asciz	"A.shape[1]"
	.size	.L.str.36, 11

	.type	.L.str.37,@object
.L.str.37:
	.asciz	"256"
	.size	.L.str.37, 4

	.type	.L.str.38,@object
.L.str.38:
	.asciz	"A.byte_offset"
	.size	.L.str.38, 14

	.type	.L.str.39,@object
.L.str.39:
	.asciz	"B.shape[0]"
	.size	.L.str.39, 11

	.type	.L.str.40,@object
.L.str.40:
	.asciz	"B.shape[1]"
	.size	.L.str.40, 11

	.type	.L.str.41,@object
.L.str.41:
	.asciz	"B.byte_offset"
	.size	.L.str.41, 14

	.type	.L.str.42,@object
.L.str.42:
	.asciz	"C.shape[0]"
	.size	.L.str.42, 11

	.type	.L.str.43,@object
.L.str.43:
	.asciz	"C.shape[1]"
	.size	.L.str.43, 11

	.type	.L.str.44,@object
.L.str.44:
	.asciz	"C.byte_offset"
	.size	.L.str.44, 14

	.section	.debug_loc,"",@progbits
.Ldebug_loc0:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin0-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	.Ltmp78-.Lfunc_begin0
	.quad	.Ltmp86-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp86-.Lfunc_begin0
	.quad	.Ltmp87-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	.Ltmp87-.Lfunc_begin0
	.quad	.Ltmp96-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp96-.Lfunc_begin0
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
	.quad	.Ltmp82-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	.Ltmp82-.Lfunc_begin0
	.quad	.Ltmp83-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp83-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Ltmp85-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp85-.Lfunc_begin0
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
	.quad	.Ltmp78-.Lfunc_begin0
	.short	2
	.byte	123
	.byte	0
	.quad	.Ltmp96-.Lfunc_begin0
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
	.quad	0
	.quad	0
.Ldebug_loc7:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp46-.Lfunc_begin0
	.quad	.Ltmp67-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp96-.Lfunc_begin0
	.quad	.Ltmp98-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp99-.Lfunc_begin0
	.quad	.Ltmp100-.Lfunc_begin0
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
	.quad	.Ltmp113-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp115-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	0
	.quad	0
.Ldebug_loc8:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp96-.Lfunc_begin0
	.quad	.Ltmp97-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp99-.Lfunc_begin0
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
	.quad	.Ltmp112-.Lfunc_begin0
	.short	2
	.byte	122
	.byte	0
	.quad	.Ltmp114-.Lfunc_begin0
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
	.quad	.Ltmp58-.Lfunc_begin0
	.short	2
	.byte	116
	.byte	0
	.quad	.Ltmp96-.Lfunc_begin0
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
	.quad	.Ltmp78-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp96-.Lfunc_begin0
	.quad	.Ltmp101-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp102-.Lfunc_begin0
	.quad	.Ltmp107-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp108-.Lfunc_begin0
	.quad	.Ltmp116-.Lfunc_begin0
	.short	2
	.byte	121
	.byte	0
	.quad	.Ltmp117-.Lfunc_begin0
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
	.quad	.Ltmp64-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	.Ltmp96-.Lfunc_begin0
	.quad	.Ltmp111-.Lfunc_begin0
	.short	2
	.byte	115
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc12:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin3-.Lfunc_begin0
	.quad	.Ltmp152-.Lfunc_begin0
	.short	1
	.byte	85
	.quad	.Ltmp152-.Lfunc_begin0
	.quad	.Lfunc_end3-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	85
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc13:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin3-.Lfunc_begin0
	.quad	.Ltmp153-.Lfunc_begin0
	.short	1
	.byte	84
	.quad	.Ltmp153-.Lfunc_begin0
	.quad	.Lfunc_end3-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	84
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc14:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Lfunc_begin3-.Lfunc_begin0
	.quad	.Ltmp154-.Lfunc_begin0
	.short	1
	.byte	81
	.quad	.Ltmp154-.Lfunc_begin0
	.quad	.Lfunc_end3-.Lfunc_begin0
	.short	4
	.byte	243
	.byte	1
	.byte	81
	.byte	159
	.quad	0
	.quad	0
.Ldebug_loc15:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp151-.Lfunc_begin0
	.quad	.Ltmp152-.Lfunc_begin0
	.short	2
	.byte	117
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc16:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp151-.Lfunc_begin0
	.quad	.Ltmp153-.Lfunc_begin0
	.short	2
	.byte	116
	.byte	0
	.quad	0
	.quad	0
.Ldebug_loc17:
	.quad	-1
	.quad	.Lfunc_begin0
	.quad	.Ltmp151-.Lfunc_begin0
	.quad	.Ltmp154-.Lfunc_begin0
	.short	2
	.byte	113
	.byte	0
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
	.byte	7
	.byte	15
	.byte	0
	.byte	0
	.byte	0
	.byte	8
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

	.long	345
	.byte	3
	.long	.Linfo_string19
	.long	352
	.byte	4
	.long	.Ldebug_loc0
	.long	.Linfo_string6
	.long	352
	.byte	4
	.long	.Ldebug_loc1
	.long	.Linfo_string7
	.long	345
	.byte	3
	.long	.Linfo_string20
	.long	352
	.byte	5
	.long	.Ldebug_loc2
	.long	.Linfo_string8
	.long	345
	.byte	5
	.long	.Ldebug_loc3
	.long	.Linfo_string9
	.long	345
	.byte	5
	.long	.Ldebug_loc4
	.long	.Linfo_string10
	.long	345
	.byte	5
	.long	.Ldebug_loc5
	.long	.Linfo_string11
	.long	353
	.byte	5
	.long	.Ldebug_loc6
	.long	.Linfo_string13
	.long	353
	.byte	5
	.long	.Ldebug_loc7
	.long	.Linfo_string14
	.long	345
	.byte	5
	.long	.Ldebug_loc8
	.long	.Linfo_string15
	.long	353
	.byte	5
	.long	.Ldebug_loc9
	.long	.Linfo_string16
	.long	353
	.byte	5
	.long	.Ldebug_loc10
	.long	.Linfo_string17
	.long	353
	.byte	5
	.long	.Ldebug_loc11
	.long	.Linfo_string18
	.long	353
	.byte	0
	.byte	2
	.quad	.Lfunc_begin3
	.long	.Lfunc_end3-.Lfunc_begin3
	.byte	1
	.byte	87
	.long	.Linfo_string5

	.long	345
	.byte	4
	.long	.Ldebug_loc12
	.long	.Linfo_string21
	.long	365
	.byte	4
	.long	.Ldebug_loc13
	.long	.Linfo_string23
	.long	365
	.byte	4
	.long	.Ldebug_loc14
	.long	.Linfo_string24
	.long	365
	.byte	5
	.long	.Ldebug_loc15
	.long	.Linfo_string21
	.long	365
	.byte	5
	.long	.Ldebug_loc16
	.long	.Linfo_string23
	.long	365
	.byte	5
	.long	.Ldebug_loc17
	.long	.Linfo_string24
	.long	365
	.byte	0
	.byte	6
	.long	.Linfo_string4
	.byte	5
	.byte	4
	.byte	7
	.byte	8
	.long	358
	.byte	6
	.long	.Linfo_string12
	.byte	5
	.byte	8
	.byte	8
	.long	370
	.byte	6
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
	.section	.debug_pubnames,"",@progbits
	.long	.LpubNames_end0-.LpubNames_start0
.LpubNames_start0:
	.short	2
	.long	.Lcu_begin0
	.long	378
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
	.long	378
	.long	345
	.asciz	"int32"
	.long	358
	.asciz	"int64"
	.long	370
	.asciz	"float32"
	.long	0
.LpubTypes_end0:
	.section	".note.GNU-stack","",@progbits
	.section	.debug_line,"",@progbits
.Lline_table_start0:
