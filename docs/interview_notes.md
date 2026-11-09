# 项目技术问答提纲

这些问题用于复盘当前仓库可验证的实现，不代表已测得某项性能收益。实际设备、shape 和结果应引用对应实验 JSON，而不是预先填写加速数字。

1. **ONNX、Relax、TensorIR 各负责什么？** ONNX 是交换图；Relax 描述图层调用与类型；TensorIR/TIRx 描述低层张量计算及循环。项目调用 TVM frontend、lowering、LLVM codegen 与 VM，不自称实现了这些组件。见 [架构](architecture.md)及 [IR 证据链](ir_walkthrough.md)。
2. **`call_tir` 有什么作用？** Relax 通过它调用低层 PrimFunc，目标输出类型与内存由后续 lowering 和 runtime 处理。`03_legalized_inspection.py` 是独立检查产物，不能冒充正式编译 pipeline 的输入。
3. **reshape 链如何证明安全？** 检查输入、中间和输出的静态形状、dtype 与元素总数，从已证明的输出类型构造目标形状；动态或含零长度的维度保守跳过。额外消费者保留其原中间值，异常回退原图。见 [Pass 正确性](pass_correctness.md)。
4. **线性融合如何处理广播和消费者？** 仅接受正维静态 FP32 的 `x[M,K] @ w[K,N] + bias[N]` 与 ReLU；检查 add 实际操作数顺序和中间结果的外部消费者。图上 Composite 分组不自动证明去掉内存写回：示例融合 TIR 仍有中间 buffer。见 [线性融合](linear_fusion.md)。
5. **QKV 合并为何不是默认启用？** 只处理同一输入、相邻的三个静态二维常量权重投影，编译期拼接后使用一次 MatMul 和三个 slice；显式 shape 白名单是调用者配置，不是自动成本模型。切片、缓存和权重尺寸都可能使性能退化。
6. **MatMul 的并行和向量化为什么合法？** 并行划分不同 M 输出块，K 归约保持串行；向量化 N 方向，并依赖 split 的尾部谓词。固定分块不是调优，TIR 向量化标注本身不能证明机器码 SIMD 或 cache 命中改善。见 [调度说明](schedule_optimization.md)。
7. **如何公平解释结果？** 图优化比较 Custom 与相同模型、输入、目标和线程的 TVM Default；NoFusion 只是诊断。手写 MatMul 和默认 MatMul 都经 Relax VM 与相同默认编译流程测量。ORT 是不同系统，不能将 ORT 与 TVM 的差异归为项目优化。见 [benchmark 方法](benchmark_methodology.md)。
8. **静态 PrimFunc 数和 runtime 调用数一样吗？** 不一样；代码结构统计只说明静态 IR，运行时调用数需要实际 profiler；未测得时应保留空值，不可用前者替代。
9. **工件为何不能随便跨机器或跨来源加载？** 工件是内嵌权重的原生库，哈希仅检测误配，版本、系统和架构检查不能证明可信来源或跨 CPU/ABI 兼容。只加载可信来源，并在目标设备测试。
10. **下一步扩展有哪些边界？** 动态形状、CUDA、FP16、新硬件均需单独实现与真实设备验证；GPU 调度和异步计时不能照搬 CPU 实验。先确认数值，再收集同条件下的延迟分布及退化案例。
