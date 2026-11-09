# 实验记录

本页记录已有运行，不是跨机器性能结论。原始 JSON 和 TIR 在本地 `runs/`，该目录被 Git 忽略；干净 checkout 需通过下方命令重新生成。结果文件自带 commit、模型或输入 hash、逐次样本和环境。以下各节的运行在不同 commit 和时间进行，不应将不同节的绝对耗时直接合并比较。

另有一套对应 commit `bfe7a2c` 的一键复现原始 JSON 已提交在 [results/reference](../results/reference/README.md)，包括 MLP、CNN、NoFusion 和一个 MatMul 消融；它是另一次独立运行，不与下方既有样本混用。

所有记录均在 Apple M2、macOS 26.5.2 arm64、Python 3.11.15、TVM 0.27.0.post1（其 LLVM 主版本 22）、NumPy 2.4.6 和 ONNX Runtime 1.31.1 上得到。CPU 亲和性、电源策略及其他系统负载未控制；没有实测 cache miss、硬件 SIMD 指令或运行时 kernel 调用数。每组预热 30 次、3 轮每轮 100 次，顺序而非交错计时。性能数字包括 Python 和 VM 调用及输出分配，不包括编译、输入准备及显式输出到 NumPy 的复制；因此仅适用于对应脚本的计时边界。

## MLP 和 CNN 默认基线

`runs/baseline/{mlp,cnn}-default.json` 来自 commit `21842fb`，单线程、FP32、固定种子 0、内嵌 ONNX 初始权重。输入分别为 `[1,128]` 和 `[1,3,32,32]`。TVM 与 ORT 均通过 `rtol=1e-4, atol=1e-5`；MLP 最大绝对误差 0，CNN 为 4.7684e-6。

| 模型 | TVM Default median / p95 (ms) | ORT median / p95 (ms) |
|---|---:|---:|
| MLP | 0.040792 / 0.042754 | 0.007334 / 0.008046 |
| CNN | 0.168875 / 0.188096 | 0.026958 / 0.034379 |

ORT 是不同系统且返回 NumPy 数组；它与 TVM 结果差异不是本项目 Pass 的收益。`nofusion` 为诊断配置，固定版本 CPU Default 本身没有 `FuseOps`/`FuseTIR`，不能将两者差异解释为融合消融收益。具体边界见 [基线方法](benchmark_methodology.md)。

## 线性融合与 QKV

`runs/linear-stage5/mlp-custom.json` 来自 commit `280795e`，单线程、同一 MLP 和输入。TVM Default median 0.039708 ms，项目规则加 TVM FuseTIR 的 custom median 0.039375 ms，Default/custom 为 1.0085；两者均与 ORT 一致（最大绝对误差 0）。0.8% 差异很小，在此单次未控环境中不能排除噪声，也不能据此认定稳定收益。结构性样例的静态 PrimFunc 数为 3→1，但融合后 TIR 仍有中间 buffer；静态数不是运行时调用次数。

同一 commit 的 `runs/linear-stage5/qkv-matrix-sequential.json` 使用单线程、固定输入及常量权重，Default 与 QKV 合并均采用 TVM 默认流水线。六组均通过合并前后数值对照；表中比值为 Default median / 合并后 median：

| M | K=N | Default (ms) | 合并 (ms) | 比值 |
|---:|---:|---:|---:|---:|
| 1 | 256 | 0.182875 | 0.180791 | 1.012 |
| 8 | 256 | 1.398750 | 1.394687 | 1.003 |
| 32 | 256 | 5.638959 | 5.602458 | 1.007 |
| 1 | 512 | 0.823188 | 0.809417 | 1.017 |
| 8 | 512 | 6.529896 | 6.516708 | 1.002 |
| 32 | 512 | 26.132729 | 26.051667 | 1.003 |

差异小且未控制亲和性和电源，不能推断稳定提速。该 Pass 默认禁用，实验仅为每个形状临时开启白名单，未建立自动成本模型。[线性融合说明](linear_fusion.md) 给出精确语义前提和复现命令。

## MatMul 调度消融

`runs/matmul-stage6/report.json` 来自 commit `0038b1d`，两线程。TVM Default 是 Relax MatMul 原生默认 pipeline；各手写 TIR 均通过 Relax `call_tir`、相同默认 pipeline 和相同 VM 调用边界执行。六形状六版本均与 NumPy 在容差内一致。下表为 median，单位 ms，最后一列为 Default / vectorize：

| M,K,N | Default | naive | tile | reorder | parallel | vectorize | 比值 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1,128,128 | 0.012500 | 0.012250 | 0.011042 | 0.002667 | 0.002625 | 0.002708 | 4.62 |
| 8,128,128 | 0.095146 | 0.092167 | 0.082709 | 0.012625 | 0.012625 | 0.012500 | 7.61 |
| 32,128,128 | 0.365917 | 0.365917 | 0.351667 | 0.051416 | 0.026208 | 0.025500 | 14.35 |
| 1,256,256 | 0.060666 | 0.059271 | 0.056479 | 0.009084 | 0.009083 | 0.009083 | 6.68 |
| 8,256,256 | 0.495271 | 0.495791 | 0.409937 | 0.049083 | 0.050479 | 0.051500 | 9.62 |
| 32,256,256 | 1.892813 | 1.899729 | 1.635124 | 0.194166 | 0.103125 | 0.102458 | 18.47 |

例如 `8,256,256` 中，parallel 和 vectorize 的 median 比 reorder 略慢；M 方向每 8 行一个并行块，M=8 只有一个块，可能无法抵消并行开销。这是基于调度结构的解释，并非 profiler 对因果的证明。较大的 Default 对照差异仅说明本次实验与固定版本 CPU Default 的差异，并不能推广到其他硬件、编译参数或 autotuned schedule。每个形状和阶段的 p95、每次原始值和 TIR dump 都保存在实验目录，说明及复现命令见 [调度说明](schedule_optimization.md)。

## 同一模型的代码生成和运行

`runs/stage7/evidence/manifest.json` 对应 commit `c52ca75`：MLP 的两个 MatMul 分别以 `(1,128,256)` 和 `(1,256,64)` 接入手写 vectorize schedule，实际编译产物提供 LLVM IR、汇编和 VM 文本。证据导出与工件导出是独立编译；检查用 LegalizeOps IR 不重新送入正式编译 pipeline。重新加载的 266360 字节工件与 ORT 的该次输出最大绝对误差为 0（`runs/stage7/verification.json`）。完整命令及可信原生库、跨机限制见 [IR 证据链](ir_walkthrough.md)。

以上历史运行本身未覆盖 Linux x86_64 或 CUDA；后续在 RTX 3090 验证了 CUDA 基础运行，且新增 [Linux CPU/GPU 深挖证据](../results/deep-dive-2026-11-09/README.md)。这些新的运行仍未独占服务器、控制电源或采集硬件计数，不能视为稳定性能结论。
