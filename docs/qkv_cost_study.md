# QKV 合并成本实验

`python -m benchmarks.qkv_cost_study --output runs/qkv-cost.json --threads 1` 在同一固定版本 TVM Default pipeline 上比较三个独立投影与项目 QKV 合并图。默认覆盖 M=1/8/32、K=N=256/512；每个形状固定输入、静态 FP32 常量权重和随机种子。两路径都输出全部三个分支，先和同一 NumPy 结果进行数值对照，再依次预热并交替运行 default→packed、packed→default 的配对轮次；每轮保存全部样本及 median。使用 `--shape M,K,N` 可重复指定形状。

报告拆分以下指标：

- `pass_ms` 是一次完整的项目图改写耗时，包含从常量读取和拼接以及构图等工作；`numpy_concat_ms` 单独测量一次 numpy 拼接，仅作为编译期预打包成本的微实验，不应从 pass 时间中重复扣除。
- `slice_only` 是用预先计算的 MatMul 输出构建的独立三路 slice VM；它与完整 packed 图有不同的 buffer 生命周期和缓存状态，不能直接从 packed 延迟中相减，也不证明额外的运行时调用次数。
- `logical_bytes` 记录 FP32 原始/拼接权重、packed 中间张量和三个输出的逻辑容量，不能作为真实物理分配或进程峰值内存；要分析峰值必须使用内存 profiler。模型加载、编译和 NumPy 输出转换不计入推理计时。
- `screen` 是保守的**探索性候选筛选**：至少六个交替轮次，每轮 Default median 均须比 packed 高 5% 以上。它不是统计置信区间，不自动更改 Pass 白名单；结果必须在相同目标硬件、线程与受控环境下用独立运行进行验证，且要考虑权重预打包开销的摊销次数。

CPU 亲和性在支持的系统上记录，但脚本不自行更改；电源策略和后台负载也不受控。QKV Pass 仍默认禁用，动态权重、动态 shape、不相邻或不同输入等情况不处理；详见 [融合规则](linear_fusion.md)。
