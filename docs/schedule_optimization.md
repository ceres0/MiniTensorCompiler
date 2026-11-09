# CPU MatMul 调度实验

实验计算静态 FP32 `C[M,N] = A[M,K] @ B[K,N]`，基于 TVM 提供的 TIRx 和 `tvm.s_tir.Schedule` 实现可逐级比较的手写循环调度；LLVM 代码生成由 TVM 完成。本实验尚未接入模型级默认 pipeline。

## 逐级变换

1. `naive`：按 `i, j, k` 顺序逐元素归约。
2. `tile`：按 M/N/K 的 8/32/8 固定大小拆分循环；单独拆分不保证改善局部性。
3. `reorder`：调整为输出块、归约块、行内块、归约内块、列内块顺序，让 N 方向更连续，同时保持每个输出的 K 归约顺序。
4. `parallel`：对 M 外层输出块并行，线程写入互不重叠；归约轴保持串行。小 M 时并行块不足，开销可能不划算。
5. `vectorize`：将 N 方向最内层拆成 4 元素并标记向量化，TVM split 的边界谓词处理非整除尾部。向量化标记不等于已经验证硬件 SIMD 指令或对齐。

固定 tile 和 vector 宽度仅为消融起点，不是 autotuning；未测量 cache miss、寄存器压力或指令级硬件计数。尾部、标量、小维度、重复调用及两线程并行由自动测试对照 NumPy 和 TVM Default；浮点容差为 `rtol=1e-4, atol=1e-5`。

## 运行和比较

```bash
uv run --locked python -m benchmarks.matmul_schedule --threads 1 --output-dir runs/matmul-ablation
```

脚本默认覆盖 M=1/8/32、K=N=128/256 的六组形状；可重复使用 `--shape M,K,N` 选择其他静态正维形状，使用 `--warmup`、`--repeat`、`--rounds` 调整采样。每一组先用相同输入与 NumPy 比较，通过后记录各轮逐次耗时、median/p95、编译时间、与 TVM Default 的 median 比值，失败不报告该阶段的推理测量。

默认参考是 Relax `matmul` 经过固定 TVM 默认 Relax/TIR pipeline；手写版本由 Relax `call_tir` 包装后使用同一默认 pipeline。两者使用相同 CPU target、预先创建的输入、VM 调用边界、线程与计时方式；时间包含 Python 调用和输出分配，不包含编译、输入创建或显式 NumPy 结果复制。每一版本均保存 TIR 文本；Default 的 TIR 是独立运行 LegalizeOps 的检查工件，基准编译从原始 Relax 图开始，不重复 lowering。

脚本按固定顺序依次测量各版本，记录环境、输入 hash、Git 版本和原始样本；CPU 亲和性、电源策略与系统负载不受控。单次结果只能用于探索，不应视作跨机器、跨负载或稳定加速的证明。调度行为及性能退化应依据实际 IR 和数据解释，不能把静态函数数或预测的缓存行为当作运行时计数或硬件测量。
