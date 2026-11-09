# 线性子图：标量 epilogue 实验

`make_fused_linear(M,K,N)` 实现静态正维 FP32 `relu(A @ W + bias)` 的标量实验 kernel。每个 `C[i,j]` 在局部标量中依次归约 K，随后加 bias、ReLU 并写一次 C；源 TIR 不包含 `[M,N]` 的 matmul 或 bias 中间 buffer。局部标量是否进入寄存器、实际读写次数及 SIMD 指令需要进一步由 LLVM 汇编或硬件 profiler 验证；静态 TIR 不能证明。该实现只接受不别名的 buffer，为实验用途，未经形状条件接入 ONNX 编译路径。

比较对象是 TVM 原生 Default 和项目现有 DPL + TVM `FuseOpsByPattern`/`FuseTIR` 的线性图融合。图融合与标量 kernel 使用同一 `linear_fused_pipeline`，Default 使用其原生 pipeline；三条路径使用相同 LLVM CPU、Relax VM、预创建输入和计时边界。默认固定顺序测量，不控制亲和性、电源或负载；该标量实现没有 tiling，并不保证比图融合快，不声称稳定收益。样本的参考值来自 NumPy，FP32 舍入次序可能不同，使用 rtol=1e-4、atol=1e-5；本实验只对有限输入作数值验证，不声称特殊 NaN/Inf 行为完全一致。

```bash
uv run --locked python -m benchmarks.fused_linear --output-dir runs/fused-linear --threads 1
```

报告包含每种形状的输入 hash、环境、逐次样本、median/p95、编译时间和数值误差；各形状分别保存图融合 TIR 与标量融合 TIR。可以重复 `--shape M,K,N` 指定形状。文件路径必须是新目录。原生函数的 LLVM 生成和 VM 由 TVM 提供，手写融合 kernel 和实验框架为项目实现。
