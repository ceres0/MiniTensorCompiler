# 简历证据集：MiniTensorCompiler

本文件是代码、正确性测试和实验工件的索引，不代表所有实验均证明稳定加速。简历中的贡献与数字应与本人实际参与和可独立解释的工作一致。除另有标注外，代码、测试和参考 JSON 位于 Git；`runs/` 是本地生成目录，被 Git 忽略，干净检出后应按对应文档重跑。各报告以自身记录的 Git SHA 为准，不能把不同提交、机器或配置的耗时混合比较。

## 项目定位和实现边界

可表述为“基于 TVM Relax / TensorIR 的静态模型编译与优化实践”：项目实现 ONNX 校验与 IR 分析、图改写及语义守卫、CPU MatMul TIR 调度、测试和实验工件管理；ONNX frontend、TVM DPL/融合基础设施、标准 lowering、LLVM/CUDA codegen 和 VM 来自 TVM。不要表述为自行开发完整 ONNX 解析器、LLVM 后端或 GPU codegen。

| 能力 | 代码与复现证据 | 可核实的范围 |
|---|---|---|
| ONNX→Relax→LLVM CPU→VM | [前端](../minicompiler/frontend/onnx_loader.py)、[工件](../minicompiler/compiler/artifacts.py)、[端到端测试](../tests/test_evidence_end_to_end.py)、[IR 证据链](ir_walkthrough.md) | 静态 FP32 MLP/CNN；权重嵌入并导出/加载，数值与 ORT CPU 对照。证据导出和工件导出是两次独立编译。 |
| reshape 链归并 | [规则](../minicompiler/passes/redundant_reshape.py)、[测试](../tests/test_reshape_pass.py)、[语义说明](pass_correctness.md) | 已知形状、dtype、元素数条件下改写；含动态维、空张量保守跳过和共享消费者。TVM 也有类似 Pass，不把它当作性能亮点。 |
| MatMul + bias + ReLU 分组 | [规则](../minicompiler/passes/linear_bias_relu.py)、[集成测试](../tests/test_linear_fusion_integration.py)、[低层示例](../examples/05_linear_fusion.py) | 静态二维 FP32 与一维 bias 等守卫；借助 TVM FuseOpsByPattern/FuseTIR。示例中静态 PrimFunc 3→1，但仍有中间 buffer；无运行时调用数量证据。 |
| QKV 常量合并 | [规则](../minicompiler/passes/merge_qkv.py)、[测试](../tests/test_qkv_merge.py)、[矩阵脚本](../benchmarks/qkv_matrix.py) | 仅相邻、同输入、等宽常量的静态 FP32 MatMul；默认关闭、手工白名单，不是自动成本模型。 |
| CPU MatMul 调度 | [Schedule](../minicompiler/schedules/matmul_cpu.py)、[模型接入](../minicompiler/compiler/scheduled_matmul.py)、[调度测试](../tests/test_matmul_schedule.py)、[实验脚本](../benchmarks/matmul_schedule.py) | 五级 naive/tile/reorder/parallel/vectorize；支持非整除尾部；仅 CPU 静态 FP32。`vectorize` 标记本身不证明机器指令。 |
| NVIDIA GPU 基础执行 | [Dockerfile](../Dockerfile)、[CUDA Add](../examples/cuda_add.py)、[CUDA MLP](../examples/cuda_mlp.py)、[验证记录](docker_gpu.md) | RTX 3090 的 Linux x86_64 容器中验证 Add 和 MLP 的实际 CUDA 执行及数值；不是 GPU 性能基准，也不是自定义 GPU MatMul Schedule 的证明。 |
| 测试与可复现 | [一键 suite](../benchmarks/run_suite.py)、[Pass 计时](../minicompiler/profiling/pass_timing.py)、[参考 JSON](../results/reference/README.md) | 固定 seed、正确性优先、原始延迟样本和版本；静态 PrimFunc 快照与运行时 kernel 调用数严格区分。 |

## 历史实测：如何引用

本节保留早期运行的口径；其后新增的 Linux CPU、QKV 和 GPU MatMul 证据见下方“深挖实验登记”，不要将早期缺口误认为当前状态。

- **可引用的正确性指标**：`results/reference/mlp.json` 和 `cnn.json` 保存实际 ORT 对照、误差、CPU/版本与样本；其代码 commit 为 `bfe7a2c`，数据来自 Apple M2，单线程。数值只代表该模型、输入和环境，不是全模型支持声明。
- **CUDA 正确性记录**：[GPU Docker 文档](docker_gpu.md)记录 RTX 3090、驱动 580.105.08、CUDA Add 与 MLP、容器内测试和 MLP 与 ORT 的误差；该记录是功能验证，没有 GPU 性能数据。完整 PyTorch 镜像以及其他 GPU/驱动未验证。
- **CPU 消融已有探索数据**：[实验记录](experiments.md)列出六个 shape 的 Default 对照；原始六形状报告和 TIR 目前保存在被忽略的 `runs/matmul-stage6/`，Git 内 [matmul.json](../results/reference/matmul.json)只保存另一轮的一种形状。原六形状未控制 CPU 亲和性、电源和背景负载，顺序测量；不要把 4.62–18.47× 写成跨机器稳定收益。需要对应的 raw JSON、IR 和受控复测后再考虑引用特定数值。
- **线性融合的负例**：[参考 MLP JSON](../results/reference/mlp.json)中 Default median 0.040750 ms、custom 0.040834 ms；该单次环境下未观察到加速。Composite 和 `FuseTIR` 的构造证明不等于消除内存写回或获得稳定性能收益。
- **QKV**：[实验记录](experiments.md)中的差异很小且在未控环境中，不能声称稳定加速；原六形状报告仍在 `runs/`，不是仓库内完整原始证据。
- **计时与指标**：[方法](benchmark_methodology.md)说明 PassInstrument 的嵌套开销；静态 PrimFunc 数不等于 runtime kernel 调用次数。未实测的 codegen、schedule 单独耗时、运行时 kernel 数均不能用其他指标替代。没有严格冷编译或缓存收益结论。

## 推荐简历表述（按个人实际工作调整）

> 基于 Apache TVM Relax 构建静态 FP32 ONNX 模型的导入、IR 分析、LLVM CPU 编译、VM 执行和工件管理流程，使用 ONNX Runtime 对 MLP/CNN 进行数值校验并保存可复现实验数据。
>
> 基于 Relax DPL 实现冗余 reshape 与 MatMul–bias–ReLU 子图匹配规则，检查形状、dtype、广播和数据依赖，通过改写前后 IR 及正反例验证语义；使用 TVM 融合基础设施完成后续 lowering。
>
> 针对 FP32 MatMul 实现分块、循环重排、并行和向量化调度，建立多形状与 TVM Default 对照；在 RTX 3090 Docker 环境验证 CUDA Add 和 ONNX MLP 的数值一致性。

上述是待个人核实、可删减的表述；未完成新的受控实验前不填稳定加速百分比，也不将 TVM 提供的能力写成自主实现。

## 深挖实验登记

本轮深挖原始数据、IR、汇编、失败样例与重跑条件已保存到 [Linux/RTX 3090 证据集](../results/deep-dive-2026-11-09/README.md)。数据来自共享服务器，CPU 绑定并非独占，电源与后台负载未控制；单轮结果不作为稳定收益承诺。

| 方向 | 待补证据 | 状态 |
|---|---|---|
| Linux CPU 调度 | 两核绑定、六 shape 随机交错样本、FP32/FP64 参考、TIR 和实际汇编；首次严格容差失败保留 | 完成一轮；需独占负载、更多进程复测和硬件计数 |
| 线性融合 | 手写标量归约后 bias/relu 写回，三个 shape 与 TVM Default、graph-fused 比较；源 TIR 无完整中间张量 | 已验证数值；本次未比 graph-fused 更快，尚未测实际访存 |
| QKV 成本判断 | 六形状交错成本、拼接与 slice 诊断；候选形状换 seed 独立复测不通过 | 已有负例；无自动成本模型或峰值内存测量 |
| GPU MatMul | RTX 3090 四 shape 与 TVM Default 的同步 VM 对照、失败及修复记录 | 基础输出映射已验证；无 shared memory 或 profiler |

该轮中 AMD EPYC 的 `[32,256,256]` 默认与各版本在严格 `atol=1e-5` 下均出现数值不符；复验使用 `atol=5e-5` 并额外与 FP64 参考对照。RTX 3090 上线程映射在部分小 shape 相比 TVM 默认路径退化。应将这些真实边界与结果一起呈现，不能只摘取最快比值。

## 面试追问和证据索引

1. reshape 的 `0`/`-1`、静态元素数和共享消费者为什么影响合法性？参考 [Pass 正确性](pass_correctness.md)。
2. 图层 Composite、TIR PrimFunc 和运行时调用分别是什么？为什么 3→1 不是 kernel launch 已减少的证明？参考 [线性融合](linear_fusion.md)。
3. 为什么归约轴不能简单并行？输出初始化、split 尾部谓词和小 M 的并行粒度如何处理？参考 [CPU Schedule](schedule_optimization.md)。
4. Default、NoFusion、Custom 的同异是什么？为什么 ORT 对比不等于项目 Pass 收益？参考 [benchmark 方法](benchmark_methodology.md)。
5. `call_tir`、LLVM 和 VM 各负责什么？检查用 IR 与实际编译产物是什么关系？参考 [IR 证据链](ir_walkthrough.md)。
6. 为什么 GPU 测试必须同步？当前 CUDA 示例使用了哪些 TVM 能力，尚未实现哪些 GPU Schedule 或 profile？参考 [GPU Docker](docker_gpu.md)。
